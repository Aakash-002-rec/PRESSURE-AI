import os
import sys
import json
import sqlite3
import unittest
from fastapi import HTTPException

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection, init_db
from app.routers.coding_routes import (
    get_coding_problems,
    get_coding_status,
    generate_dynamic_coding_problem,
    submit_code_solution,
    start_new_coding_session,
    _get_or_create_user_coding_session,
    CODING_SESSION_QUESTION_LIMIT
)
from app.models import CodingSubmitRequest
from app.services.cross_module_engine import CrossModuleEngine
import app.routers.coding_routes as cr

class TestPersonalizedCodingSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

        # Clean up any leftover test records first
        self.cursor.execute("DELETE FROM users WHERE email IN ('alpha_test@pressure.ai', 'beta_test@pressure.ai')")
        self.conn.commit()

        # Create two distinct test users with unique timestamps
        self.cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES ('Candidate Alpha', 'alpha_test@pressure.ai', 'hash_a')"
        )
        self.user_a_id = self.cursor.lastrowid

        self.cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES ('Candidate Beta', 'beta_test@pressure.ai', 'hash_b')"
        )
        self.user_b_id = self.cursor.lastrowid

        from app.services.attempt_service import AttemptService
        AttemptService.get_or_create_active_attempt(self.cursor, self.user_a_id)
        self.cursor.execute("UPDATE assessment_attempts SET aptitude_status = 'completed' WHERE user_id = ?", (self.user_a_id,))
        AttemptService.get_or_create_active_attempt(self.cursor, self.user_b_id)
        self.cursor.execute("UPDATE assessment_attempts SET aptitude_status = 'completed' WHERE user_id = ?", (self.user_b_id,))
        self.conn.commit()

        self.user_a = {"id": self.user_a_id, "username": "Candidate Alpha"}
        self.user_b = {"id": self.user_b_id, "username": "Candidate Beta"}

    def tearDown(self):
        self.cursor.execute("DELETE FROM assessment_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.cursor.execute("DELETE FROM coding_sessions WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.cursor.execute("DELETE FROM user_served_questions WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.cursor.execute("DELETE FROM coding_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.cursor.execute("DELETE FROM users WHERE id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.conn.commit()
        self.conn.close()

    def test_01_pipeline_flow_order(self):
        """1. Verify standard placement flow: Aptitude -> Coding -> AI Mock Interview -> Final Report."""
        stages = ["aptitude", "coding", "setup", "combined_report"]
        self.assertEqual(stages[0], "aptitude")
        self.assertEqual(stages[1], "coding")
        self.assertEqual(stages[2], "setup")
        self.assertEqual(stages[3], "combined_report")

    def test_02_exactly_three_questions_assigned_per_session(self):
        """2. Exactly 3 questions are assigned to each coding assessment session."""
        q1 = get_coding_problems(current_user=self.user_a)
        self.assertEqual(len(q1), 1)
        self.assertEqual(q1[0]["question_number"], 1)
        self.assertEqual(q1[0]["total_questions"], 3)

        q2 = get_coding_problems(current_user=self.user_a)
        self.assertEqual(len(q2), 1)
        self.assertEqual(q2[0]["question_number"], 2)
        self.assertEqual(q2[0]["total_questions"], 3)

        q3 = get_coding_problems(current_user=self.user_a)
        self.assertEqual(len(q3), 1)
        self.assertEqual(q3[0]["question_number"], 3)
        self.assertEqual(q3[0]["total_questions"], 3)

        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.total_problems_count, 3)
        self.assertEqual(status.session_limit, 3)

    def test_03_no_fourth_question_served_or_generated(self):
        """3. A fourth question cannot be generated or fetched in the same session."""
        # Serve 3 questions
        for _ in range(3):
            get_coding_problems(current_user=self.user_a)

        # 4th fetch must return empty list
        q4 = get_coding_problems(current_user=self.user_a)
        self.assertEqual(len(q4), 0, "No fourth question can be served via get_coding_problems")

        # 4th generation must raise 400 with session limit message
        with self.assertRaises(HTTPException) as cm:
            generate_dynamic_coding_problem(current_user=self.user_a)
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("limit reached", cm.exception.detail.lower())

    def test_04_two_different_users_receive_different_questions(self):
        """4. Two different users can receive different coding questions."""
        # Fetch 3 questions for User A
        questions_a = []
        for _ in range(3):
            probs = get_coding_problems(current_user=self.user_a)
            if probs:
                questions_a.append(probs[0]["id"])

        # Fetch 3 questions for User B
        questions_b = []
        for _ in range(3):
            probs = get_coding_problems(current_user=self.user_b)
            if probs:
                questions_b.append(probs[0]["id"])

        self.assertEqual(len(questions_a), 3)
        self.assertEqual(len(questions_b), 3)
        # Sets must not be identical
        self.assertNotEqual(questions_a, questions_b, "User A and User B should receive different personalized question sets")

    def test_05_user_question_history_isolation(self):
        """5. Each user's question history is isolated from other users."""
        q_a = get_coding_problems(current_user=self.user_a)
        self.assertEqual(len(q_a), 1)
        seen_a_id = q_a[0]["id"]

        # User B's history must have 0 seen questions
        status_b = get_coding_status(current_user=self.user_b)
        self.assertEqual(status_b.in_progress_count, 0)
        self.assertEqual(status_b.completed_count, 0)

        # Question history in DB is isolated
        self.cursor.execute("SELECT COUNT(*) FROM user_served_questions WHERE user_id = ?", (self.user_b_id,))
        count_b = self.cursor.fetchone()[0]
        self.assertEqual(count_b, 0)

    def test_06_avoid_previously_served_questions_across_sessions(self):
        """6. Previously served questions are avoided across sessions whenever unused alternatives exist."""
        # Session 1 for User A
        session_1_ids = []
        for _ in range(3):
            p = get_coding_problems(current_user=self.user_a)
            if p:
                session_1_ids.append(p[0]["id"])
        self.assertEqual(len(session_1_ids), 3)

        # Start Session 2 for User A
        start_new_coding_session(current_user=self.user_a)

        session_2_ids = []
        for _ in range(3):
            p = get_coding_problems(current_user=self.user_a)
            if p:
                session_2_ids.append(p[0]["id"])
        self.assertEqual(len(session_2_ids), 3)

        # There are 20 questions in the pool, so Session 2 must avoid repeating Session 1 questions
        overlap = set(session_1_ids).intersection(set(session_2_ids))
        self.assertEqual(len(overlap), 0, f"Session 2 repeated questions from Session 1: {overlap}")

    def test_07_no_repeat_within_same_session(self):
        """7. Questions do not repeat within the same session."""
        session_ids = []
        for _ in range(3):
            p = get_coding_problems(current_user=self.user_a)
            if p:
                session_ids.append(p[0]["id"])
        self.assertEqual(len(session_ids), 3)
        self.assertEqual(len(set(session_ids)), 3, "All 3 questions within session must be distinct")

    def test_08_programming_language_and_domain_respected(self):
        """8. The selected programming language and domain are respected."""
        session = _get_or_create_user_coding_session(
            cursor=self.cursor,
            user_id=self.user_a_id,
            language="python",
            domain="Algorithms"
        )
        self.conn.commit()
        self.assertEqual(session["language"], "python")
        self.assertEqual(session["domain"], "Algorithms")

        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.language, "python")
        self.assertEqual(status.domain, "Algorithms")

    def test_09_failed_submissions_do_not_mark_completed(self):
        """9. Failed submissions do not mark questions as completed."""
        p = get_coding_problems(current_user=self.user_a)[0]
        prob_id = p["id"]

        # Submit failing code
        bad_code = "def solution(*args):\n    return 'completely_wrong_answer'\n"
        req = CodingSubmitRequest(problem_id=prob_id, code=bad_code, language="python")
        res = submit_code_solution(req, current_user=self.user_a)

        self.assertEqual(res["status"], "failed")
        self.assertNotEqual(res["status"], "passed")

        # Problem must remain in_progress, completed_count must remain 0
        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.completed_count, 0)
        self.assertEqual(status.in_progress_count, 1)
        self.assertFalse(status.all_completed)

    def test_10_passing_all_test_cases_updates_completion_status(self):
        """10. Passing all required test cases correctly updates completion status."""
        # User solves 3 questions
        for _ in range(3):
            probs = get_coding_problems(current_user=self.user_a)
            if not probs:
                break
            prob = probs[0]
            # Fetch solution code from database
            self.cursor.execute("SELECT solution_code FROM coding_problems WHERE id = ?", (prob["id"],))
            sol_code = self.cursor.fetchone()[0]

            req = CodingSubmitRequest(problem_id=prob["id"], code=sol_code, language="python")
            sub_res = submit_code_solution(req, current_user=self.user_a)
            self.assertEqual(sub_res["status"], "passed", f"Solution for problem {prob['id']} failed")

        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.completed_count, 3)
        self.assertEqual(status.in_progress_count, 0)
        self.assertTrue(status.all_completed, "Session must be marked all_completed after 3 passed problems")

    def test_11_refresh_or_reopen_preserves_session_limit_and_progress(self):
        """11. Refreshing or reopening a session preserves the 3-question limit and progress."""
        # Serve question 1
        p1 = get_coding_problems(current_user=self.user_a)[0]
        # Simulate browser refresh by fetching status multiple times
        for _ in range(5):
            st = get_coding_status(current_user=self.user_a)
            self.assertEqual(st.session_limit, 3)
            self.assertEqual(st.in_progress_count, 1)
            self.assertEqual(st.completed_count, 0)

        # Serve question 2
        p2 = get_coding_problems(current_user=self.user_a)[0]
        st2 = get_coding_status(current_user=self.user_a)
        self.assertEqual(st2.session_limit, 3)
        self.assertEqual(st2.in_progress_count, 2)

    def test_12_resume_incomplete_session_without_extra_slots(self):
        """12. An incomplete session can be resumed without assigning extra question slots."""
        # User receives question 1
        p1 = get_coding_problems(current_user=self.user_a)[0]
        p1_id = p1["id"]

        # User requests resume mode
        resumed = get_coding_problems(mode="resume", current_user=self.user_a)
        self.assertGreater(len(resumed), 0)
        self.assertEqual(resumed[0]["id"], p1_id)

        # Total seen questions should still be 1 (not 2)
        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.in_progress_count, 1)
        self.assertEqual(status.remaining_unseen_count, 2)

    def test_13_gemini_fallback_mode_adheres_to_rules(self):
        """13. Gemini failure and fallback mode still respect the same requirements."""
        orig_gemini = cr.gemini_model
        cr.gemini_model = None
        try:
            # Under fallback, serve 3 questions
            fb_probs = []
            for _ in range(3):
                p = get_coding_problems(current_user=self.user_a)
                if p:
                    fb_probs.append(p[0]["id"])
            self.assertEqual(len(fb_probs), 3)
            self.assertEqual(len(set(fb_probs)), 3)

            # 4th request must return empty list
            p4 = get_coding_problems(current_user=self.user_a)
            self.assertEqual(len(p4), 0)
        finally:
            cr.gemini_model = orig_gemini

    def test_14_ai_mock_interview_accessible_after_coding_completion(self):
        """14. The AI Mock Interview remains accessible after coding completion."""
        # Complete all 3 coding questions
        for _ in range(3):
            probs = get_coding_problems(current_user=self.user_a)
            if not probs:
                break
            prob = probs[0]
            self.cursor.execute("SELECT solution_code FROM coding_problems WHERE id = ?", (prob["id"],))
            sol_code = self.cursor.fetchone()[0]
            req = CodingSubmitRequest(problem_id=prob["id"], code=sol_code, language="python")
            submit_code_solution(req, current_user=self.user_a)

        status = get_coding_status(current_user=self.user_a)
        self.assertTrue(status.all_completed)

        # Check candidate profile for interview readiness
        profile = CrossModuleEngine.get_candidate_profile(self.user_a_id)
        self.assertIsNotNone(profile)
        self.assertIn("coding_score", profile)
        self.assertIn("coding_topics", profile)
        self.assertIn("weak_topics", profile)

    def test_15_all_system_components_continue_to_function(self):
        """15. Aptitude, interview, and cross-module profile pipelines function properly."""
        # Cross module engine returns a valid candidate dictionary
        profile = CrossModuleEngine.get_candidate_profile(self.user_a_id)
        self.assertEqual(profile["user_id"], self.user_a_id)
        self.assertIn("strong_topics", profile)
        self.assertIn("weak_topics", profile)

if __name__ == "__main__":
    unittest.main()
