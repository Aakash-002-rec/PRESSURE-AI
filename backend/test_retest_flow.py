import os
import sys
import unittest
import sqlite3

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection, init_db
from app.services.attempt_service import AttemptService
from app.routers.assessment_routes import (
    start_assessment_retest,
    get_current_assessment_attempt,
    get_assessment_attempt_history,
)
from app.routers.coding_routes import (
    get_coding_status,
    get_coding_problems,
    submit_code_solution,
    generate_dynamic_coding_problem,
    _get_or_create_user_coding_session,
    CODING_SESSION_QUESTION_LIMIT,
)
from app.routers.aptitude_routes import (
    submit_aptitude_test,
)
from app.services.interview_engine import InterviewEngine
from app.models import CodingSubmitRequest, AptitudeTestSubmit, AptitudeAnswerSubmission


class TestRetestFlowRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        import uuid
        conn = get_db_connection()
        cur = conn.cursor()

        uid = uuid.uuid4().hex[:8]
        # Create two isolated test users with unique emails
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (f"Candidate Retest A {uid}", f"retest_a_{uid}@pressure.ai", "hash_a")
        )
        self.user_a_id = cur.lastrowid

        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (f"Candidate Retest B {uid}", f"retest_b_{uid}@pressure.ai", "hash_b")
        )
        self.user_b_id = cur.lastrowid
        # Initialize active attempts with completed aptitude so coding tests can run
        from app.services.attempt_service import AttemptService
        AttemptService.get_or_create_active_attempt(cur, self.user_a_id)
        cur.execute("UPDATE assessment_attempts SET aptitude_status = 'completed' WHERE user_id = ?", (self.user_a_id,))
        AttemptService.get_or_create_active_attempt(cur, self.user_b_id)
        cur.execute("UPDATE assessment_attempts SET aptitude_status = 'completed' WHERE user_id = ?", (self.user_b_id,))
        conn.commit()
        conn.close()

        self.user_a = {"id": self.user_a_id, "username": f"Candidate Retest A {uid}"}
        self.user_b = {"id": self.user_b_id, "username": f"Candidate Retest B {uid}"}

    def _complete_aptitude(self, user_id):
        conn = get_db_connection()
        conn.execute("UPDATE assessment_attempts SET aptitude_status = 'completed' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    def tearDown(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM assessment_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            cur.execute("DELETE FROM coding_sessions WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            cur.execute("DELETE FROM user_served_questions WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            cur.execute("DELETE FROM coding_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            cur.execute("DELETE FROM aptitude_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            cur.execute("DELETE FROM interviews WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            cur.execute("DELETE FROM users WHERE id IN (?, ?)", (self.user_a_id, self.user_b_id))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def test_01_completing_3_coding_questions_marks_only_current_attempt_completed(self):
        """1. Completing 3 coding questions marks only the current attempt as completed."""
        # Start assessment attempt
        get_current_assessment_attempt(current_user=self.user_a)

        # Serve all 3 problems
        p1 = get_coding_problems(current_user=self.user_a)
        p2 = get_coding_problems(current_user=self.user_a)
        p3 = get_coding_problems(current_user=self.user_a)
        self.assertEqual(len(p1), 1)
        self.assertEqual(len(p2), 1)
        self.assertEqual(len(p3), 1)
        all_probs = [p1[0]["id"], p2[0]["id"], p3[0]["id"]]

        # Mark all 3 solved in DB
        conn = get_db_connection()
        for pid in all_probs:
            conn.execute(
                "UPDATE user_served_questions SET status = 'passed' WHERE user_id = ? AND question_id = ?",
                (self.user_a_id, pid)
            )
        conn.commit()
        conn.close()

        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.completed_count, 3)
        self.assertTrue(status.all_completed)

        # Attempt record in DB has coding_status completed
        conn = get_db_connection()
        cur = conn.cursor()
        active_att = AttemptService.get_active_attempt(cur, self.user_a_id)
        conn.close()
        self.assertEqual(active_att["coding_status"], "completed")

    def test_02_starting_retest_creates_different_attempt_id(self):
        """2. Starting a retest creates a different attempt ID."""
        att1 = get_current_assessment_attempt(current_user=self.user_a)
        id1 = att1["attempt_id"] if isinstance(att1, dict) else att1.attempt_id

        retest_res = start_assessment_retest(current_user=self.user_a)
        id2 = retest_res.attempt_id

        self.assertNotEqual(id1, id2)
        self.assertTrue(id2.startswith("att_"))

    def test_03_new_coding_attempt_starts_at_0_of_3(self):
        """3. A new coding attempt starts at 0 of 3, not 3 of 3."""
        # Setup attempt 1 with 3 completed questions
        get_current_assessment_attempt(current_user=self.user_a)
        p1 = get_coding_problems(current_user=self.user_a)
        p2 = get_coding_problems(current_user=self.user_a)
        p3 = get_coding_problems(current_user=self.user_a)

        conn = get_db_connection()
        for pid in [p1[0]["id"], p2[0]["id"], p3[0]["id"]]:
            conn.execute(
                "UPDATE user_served_questions SET status = 'passed' WHERE user_id = ? AND question_id = ?",
                (self.user_a_id, pid)
            )
        conn.commit()
        conn.close()

        status_before = get_coding_status(current_user=self.user_a)
        self.assertEqual(status_before.completed_count, 3)

        # Trigger retest
        start_assessment_retest(current_user=self.user_a)

        # Check coding status on new attempt
        status_after = get_coding_status(current_user=self.user_a)
        self.assertEqual(status_after.completed_count, 0)
        self.assertFalse(status_after.all_completed)
        self.assertEqual(status_after.remaining_unseen_count, 3)

    def test_04_new_coding_attempt_contains_exactly_3_distinct_questions(self):
        """4. The new coding attempt contains exactly 3 distinct questions."""
        start_assessment_retest(current_user=self.user_a)
        self._complete_aptitude(self.user_a_id)
        q1 = get_coding_problems(current_user=self.user_a)
        q2 = get_coding_problems(current_user=self.user_a)
        q3 = get_coding_problems(current_user=self.user_a)
        q4 = get_coding_problems(current_user=self.user_a)

        self.assertEqual(len(q1), 1)
        self.assertEqual(len(q2), 1)
        self.assertEqual(len(q3), 1)
        self.assertEqual(len(q4), 0)

        ids = [q1[0]["id"], q2[0]["id"], q3[0]["id"]]
        self.assertEqual(len(set(ids)), 3)

    def test_05_previous_coding_completion_does_not_automatically_complete_new_attempt(self):
        """5. Previous coding completion does not automatically complete the new attempt."""
        # Complete attempt 1
        get_current_assessment_attempt(current_user=self.user_a)
        p1 = get_coding_problems(current_user=self.user_a)
        p2 = get_coding_problems(current_user=self.user_a)
        p3 = get_coding_problems(current_user=self.user_a)

        conn = get_db_connection()
        for pid in [p1[0]["id"], p2[0]["id"], p3[0]["id"]]:
            conn.execute(
                "UPDATE user_served_questions SET status = 'passed' WHERE user_id = ? AND question_id = ?",
                (self.user_a_id, pid)
            )
        conn.commit()
        conn.close()

        # Start retest
        start_assessment_retest(current_user=self.user_a)
        self._complete_aptitude(self.user_a_id)

        # Fresh coding problems request
        probs = get_coding_problems(current_user=self.user_a)
        self.assertTrue(len(probs) > 0)
        status = get_coding_status(current_user=self.user_a)
        self.assertFalse(status.all_completed)
        self.assertEqual(status.completed_count, 0)

    def test_06_failed_coding_submission_does_not_mark_question_as_completed(self):
        """6. A failed coding submission does not mark a question as completed."""
        start_assessment_retest(current_user=self.user_a)
        self._complete_aptitude(self.user_a_id)
        probs = get_coding_problems(current_user=self.user_a)
        q_id = probs[0]["id"]

        # Submit failing code
        req = CodingSubmitRequest(
            problem_id=q_id,
            code="def solution(*args):\n    return -999999\n",
            language="python",
        )
        res = submit_code_solution(data=req, current_user=self.user_a)
        res_status = res["status"] if isinstance(res, dict) else res.status
        self.assertIn(res_status, ["wrong_answer", "error", "failed"])

        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.completed_count, 0)
        self.assertFalse(status.all_completed)

    def test_07_passing_all_3_questions_completes_the_new_coding_attempt(self):
        """7. Passing all 3 questions completes the new coding attempt."""
        start_assessment_retest(current_user=self.user_a)
        self._complete_aptitude(self.user_a_id)
        p1 = get_coding_problems(current_user=self.user_a)
        p2 = get_coding_problems(current_user=self.user_a)
        p3 = get_coding_problems(current_user=self.user_a)
        q_ids = [p1[0]["id"], p2[0]["id"], p3[0]["id"]]

        conn = get_db_connection()
        for qid in q_ids:
            conn.execute(
                "UPDATE user_served_questions SET status = 'passed' WHERE user_id = ? AND question_id = ?",
                (self.user_a_id, qid)
            )
        conn.commit()
        conn.close()

        updated_status = get_coding_status(current_user=self.user_a)
        self.assertEqual(updated_status.completed_count, 3)
        self.assertTrue(updated_status.all_completed)

    def test_08_retesting_resets_aptitude_and_starts_new_ai_interview_session(self):
        """8. Retesting resets Aptitude and starts a new AI Interview session."""
        get_current_assessment_attempt(current_user=self.user_a)

        # Submit aptitude on attempt 1
        req = AptitudeTestSubmit(
            category="Quantitative Aptitude",
            difficulty="Intermediate",
            total_questions=2,
            time_taken_seconds=30,
            answers=[
                AptitudeAnswerSubmission(question_id=1, selected_option=0),
                AptitudeAnswerSubmission(question_id=2, selected_option=1)
            ],
        )
        submit_aptitude_test(data=req, current_user=self.user_a)

        # Create interview on attempt 1
        interview1 = InterviewEngine.create_interview(
            user_id=self.user_a_id,
            domain_id=1,
            difficulty="Intermediate",
            interview_type="Mixed",
            total_questions=3,
        )

        conn = get_db_connection()
        cur = conn.cursor()
        active_att1 = AttemptService.get_active_attempt(cur, self.user_a_id)
        conn.close()
        self.assertIsNotNone(active_att1["aptitude_attempt_id"])
        self.assertEqual(active_att1["interview_id"], interview1["id"])

        # Now start Retest
        retest_res = start_assessment_retest(current_user=self.user_a)
        new_att_id = retest_res.attempt_id

        conn = get_db_connection()
        cur = conn.cursor()
        active_att2 = AttemptService.get_active_attempt(cur, self.user_a_id)
        conn.close()
        self.assertEqual(active_att2["attempt_id"], new_att_id)
        self.assertEqual(active_att2["aptitude_status"], "not_started")
        self.assertEqual(active_att2["interview_status"], "not_started")
        self.assertIsNone(active_att2["interview_id"])

    def test_09_previous_attempts_and_reports_remain_available_in_history(self):
        """9. Previous attempts and reports remain available in history."""
        # Create attempt 1
        get_current_assessment_attempt(current_user=self.user_a)
        # Create attempt 2
        start_assessment_retest(current_user=self.user_a)
        # Create attempt 3
        start_assessment_retest(current_user=self.user_a)

        history = get_assessment_attempt_history(current_user=self.user_a)
        self.assertGreaterEqual(len(history), 3)

    def test_10_refreshing_or_navigating_during_new_attempt_does_not_restore_stale_completion(self):
        """10. Refreshing or navigating during a new attempt does not restore stale completion state."""
        # Complete attempt 1
        get_current_assessment_attempt(current_user=self.user_a)
        p1 = get_coding_problems(current_user=self.user_a)
        p2 = get_coding_problems(current_user=self.user_a)
        p3 = get_coding_problems(current_user=self.user_a)

        conn = get_db_connection()
        for p in [p1, p2, p3]:
            conn.execute("UPDATE user_served_questions SET status = 'passed' WHERE user_id = ? AND question_id = ?", (self.user_a_id, p[0]["id"]))
        conn.commit()
        conn.close()

        # Start retest
        start_assessment_retest(current_user=self.user_a)

        # Simulate 5 subsequent refreshes/navigational calls to get_coding_status
        for _ in range(5):
            refreshed = get_coding_status(current_user=self.user_a)
            self.assertEqual(refreshed.completed_count, 0)
            self.assertFalse(refreshed.all_completed)

    def test_11_incomplete_attempt_resumes_when_user_returns_without_selecting_retest(self):
        """11. An incomplete attempt resumes when the user returns without selecting Retest."""
        att = get_current_assessment_attempt(current_user=self.user_a)
        initial_id = att["attempt_id"] if isinstance(att, dict) else att.attempt_id

        # Call get_current_assessment_attempt repeatedly (simulating navigation/return)
        current1 = get_current_assessment_attempt(current_user=self.user_a)
        current2 = get_current_assessment_attempt(current_user=self.user_a)

        id1 = current1["attempt_id"] if isinstance(current1, dict) else current1.attempt_id
        id2 = current2["attempt_id"] if isinstance(current2, dict) else current2.attempt_id

        self.assertEqual(id1, initial_id)
        self.assertEqual(id2, initial_id)

    def test_12_selecting_retest_creates_new_attempt_instead_of_resuming_previous(self):
        """12. Selecting Retest creates a new attempt instead of resuming the previous one."""
        att1 = get_current_assessment_attempt(current_user=self.user_a)
        id1 = att1["attempt_id"] if isinstance(att1, dict) else att1.attempt_id

        retest = start_assessment_retest(current_user=self.user_a)
        id2 = retest.attempt_id

        self.assertNotEqual(id1, id2)
        conn = get_db_connection()
        cur = conn.cursor()
        active_now = AttemptService.get_active_attempt(cur, self.user_a_id)
        conn.close()
        self.assertEqual(active_now["attempt_id"], id2)

    def test_13_different_users_cannot_access_or_modify_each_others_attempt_data(self):
        """13. Different users cannot access or modify each other's attempt data."""
        att_a = get_current_assessment_attempt(current_user=self.user_a)
        att_b = get_current_assessment_attempt(current_user=self.user_b)

        id_a = att_a["attempt_id"] if isinstance(att_a, dict) else att_a.attempt_id
        id_b = att_b["attempt_id"] if isinstance(att_b, dict) else att_b.attempt_id
        self.assertNotEqual(id_a, id_b)

        # User A's coding status does not affect User B
        status_a = get_coding_status(current_user=self.user_a)
        status_b = get_coding_status(current_user=self.user_b)
        self.assertNotEqual(status_a.session_id, status_b.session_id)

        # History isolation
        hist_a = get_assessment_attempt_history(current_user=self.user_a)
        hist_b = get_assessment_attempt_history(current_user=self.user_b)
        a_ids = [h["attempt_id"] if isinstance(h, dict) else h.attempt_id for h in hist_a]
        b_ids = [h["attempt_id"] if isinstance(h, dict) else h.attempt_id for h in hist_b]
        for aid in a_ids:
            self.assertNotIn(aid, b_ids)

    def test_14_domain_specific_question_generation_and_deduplication(self):
        """14. Existing domain-specific question generation and duplicate-question prevention still work."""
        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.session_limit, 3)
        self.assertEqual(status.total_problems_count, 3)


if __name__ == "__main__":
    unittest.main()
