import unittest
import json
import sqlite3
from app.database import get_db_connection
from app.services.interview_engine import InterviewEngine, determine_target_question_type, NON_CODING_DOMAINS
from app.services.llm_service import LLMService, DOMAIN_CODE_LANG_MAP
from app.services.fallback_bank import FALLBACK_QUESTIONS, find_fallback_question
from fastapi import HTTPException
from app.models import CodingSubmitRequest
from app.routers.coding_routes import (
    _get_user_coding_partition,
    get_coding_status,
    get_coding_problems,
    submit_code_solution,
    generate_dynamic_coding_problem,
    CODING_SESSION_QUESTION_LIMIT
)


class TestRegressionCodingCompletionAndInterviewMix(unittest.TestCase):
    def setUp(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

        # Create isolated test user
        self.test_email = "regression_user_v2@example.com"
        self.cursor.execute("DELETE FROM users WHERE email = ?", (self.test_email,))
        self.cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES ('Regression User', ?, 'hashed', 'candidate')",
            (self.test_email,)
        )
        self.user_id = self.cursor.lastrowid
        self.current_user = {"id": self.user_id, "email": self.test_email, "role": "candidate"}

        # Clear any prior served records for this user
        self.cursor.execute("DELETE FROM user_served_questions WHERE user_id = ?", (self.user_id,))
        self.cursor.execute("DELETE FROM coding_attempts WHERE user_id = ?", (self.user_id,))
        self.conn.commit()

    def tearDown(self):
        self.cursor.execute("DELETE FROM user_served_questions WHERE user_id = ?", (self.user_id,))
        self.cursor.execute("DELETE FROM coding_attempts WHERE user_id = ?", (self.user_id,))
        self.cursor.execute("DELETE FROM users WHERE id = ?", (self.user_id,))
        self.conn.commit()
        self.conn.close()

    # -------------------------------------------------------------------------
    # ISSUE 1 REGRESSION TESTS: Coding Problem Serving, Attempt & Completion States
    # -------------------------------------------------------------------------
    def test_new_user_has_zero_completed_and_not_all_completed(self):
        """New user with no attempts: must NOT show all completed."""
        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 0)
        self.assertEqual(status.in_progress_count, 0)
        self.assertFalse(status.all_completed)
        self.assertTrue(status.has_unseen)
        self.assertFalse(status.has_incomplete)

    def test_served_problem_is_in_progress_not_completed(self):
        """Serving a problem to a user sets status to 'in_progress', NOT 'completed'."""
        probs = get_coding_problems(current_user=self.current_user)
        self.assertGreater(len(probs), 0)
        prob_id = probs[0]["id"]

        # Check DB state
        completed_ids, in_progress_ids, seen_ids, _, _ = _get_user_coding_partition(self.cursor, self.user_id)
        self.assertIn(prob_id, seen_ids)
        self.assertIn(prob_id, in_progress_ids)
        self.assertNotIn(prob_id, completed_ids)

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 0)
        self.assertGreater(status.in_progress_count, 0)
        self.assertFalse(status.all_completed)
        self.assertTrue(status.has_incomplete)

    def test_incorrect_submission_remains_in_progress(self):
        """User who submits failing/incorrect code remains in_progress and NOT completed."""
        probs = get_coding_problems(current_user=self.current_user)
        prob_id = probs[0]["id"]

        req = CodingSubmitRequest(
            problem_id=prob_id,
            code="def solution():\n    return 'wrong answer'",
            language="python"
        )
        sub_res = submit_code_solution(data=req, current_user=self.current_user)
        self.assertEqual(sub_res["status"], "failed")

        # Partition check
        completed_ids, in_progress_ids, _, _, _ = _get_user_coding_partition(self.cursor, self.user_id)
        self.assertNotIn(prob_id, completed_ids)
        self.assertIn(prob_id, in_progress_ids)

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 0)
        self.assertFalse(status.all_completed)

    def test_successful_submission_marks_problem_completed(self):
        """User who submits correct code passing all tests is marked completed."""
        # Get problem 1 (Factorial)
        prob_id = 1
        correct_code = (
            "def factorial(n: int) -> int:\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be non-negative')\n"
            "    if n == 0 or n == 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
        )
        req = CodingSubmitRequest(
            problem_id=prob_id,
            code=correct_code,
            language="python"
        )
        sub_res = submit_code_solution(data=req, current_user=self.current_user)
        self.assertEqual(sub_res["status"], "passed", f"Submission failed: {sub_res.get('error')}")
        self.assertEqual(sub_res["status"], "passed")

        completed_ids, in_progress_ids, _, _, _ = _get_user_coding_partition(self.cursor, self.user_id)
        self.assertIn(prob_id, completed_ids)
        self.assertNotIn(prob_id, in_progress_ids)

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 1)

    def test_exhausted_pool_with_incomplete_problems_shows_incomplete_state(self):
        """When 3 problems in session have been seen but not all solved, shows has_incomplete=True and all_completed=False."""
        self.cursor.execute("SELECT id, fingerprint, title, description, starter_code, test_cases FROM coding_problems LIMIT 3")
        three_probs = self.cursor.fetchall()
        for p in three_probs:
            self.cursor.execute("""
                INSERT INTO user_served_questions (user_id, module, question_id, fingerprint, status)
                VALUES (?, 'coding', ?, ?, 'in_progress')
            """, (self.user_id, p["id"], p["fingerprint"] or f"fp_{p['id']}"))
        self.conn.commit()

        status = get_coding_status(current_user=self.current_user)
        self.assertFalse(status.has_unseen)
        self.assertTrue(status.has_incomplete)
        self.assertFalse(status.all_completed)
        self.assertEqual(status.completed_count, 0)
        self.assertEqual(status.in_progress_count, 3)
        self.assertEqual(status.remaining_unseen_count, 0)
        self.assertEqual(status.total_problems_count, 3)

        # Calling get_coding_problems by default returns [] because 3-question session limit is reached
        probs = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(probs), 0)

        # Calling with mode='resume' successfully returns the incomplete problems
        resumed = get_coding_problems(mode="resume", current_user=self.current_user)
        self.assertEqual(len(resumed), 3)
        for p in resumed:
            self.assertEqual(p["status"], "in_progress")

    def test_genuine_all_completed_requires_all_passed(self):
        """Completion screen appears ONLY when actual persistent records confirm all 3 problems are passed."""
        self.cursor.execute("SELECT id FROM coding_problems LIMIT 3")
        prob_ids = [r[0] for r in self.cursor.fetchall()]

        # Mark all 3 as passed in coding_attempts
        for pid in prob_ids:
            self.cursor.execute("""
                INSERT INTO coding_attempts (user_id, problem_id, submitted_code, language, status, passed_tests, total_tests, correctness)
                VALUES (?, ?, 'correct_code', 'python', 'passed', 5, 5, 100.0)
            """, (self.user_id, pid))
            self.cursor.execute("""
                INSERT INTO user_served_questions (user_id, module, question_id, status)
                VALUES (?, 'coding', ?, 'completed')
            """, (self.user_id, pid))
        self.conn.commit()

        status = get_coding_status(current_user=self.current_user)
        self.assertTrue(status.all_completed)
        self.assertEqual(status.completed_count, 3)
        self.assertEqual(status.in_progress_count, 0)
        self.assertEqual(status.remaining_unseen_count, 0)
        self.assertEqual(status.total_problems_count, 3)

    def test_coding_session_strict_limit_3_questions(self):
        """A coding assessment session allows at most 3 questions; fourth question cannot be served."""
        # 1st question
        q1 = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(q1), 1)
        self.assertEqual(q1[0]["question_number"], 1)
        self.assertEqual(q1[0]["total_questions"], 3)

        # 2nd question
        q2 = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(q2), 1)
        self.assertEqual(q2[0]["question_number"], 2)

        # 3rd question
        q3 = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(q3), 1)
        self.assertEqual(q3[0]["question_number"], 3)

        # 4th question fetch attempt must return empty list (cannot exceed 3 questions!)
        q4 = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(q4), 0, "Backend must not serve a 4th question")

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.total_problems_count, 3)
        self.assertEqual(status.remaining_unseen_count, 0)
        self.assertFalse(status.has_unseen)

    def test_fourth_question_cannot_be_generated(self):
        """After 3 questions are served, generating a fourth question raises 400 Bad Request."""
        # Serve 3 questions
        for _ in range(3):
            probs = get_coding_problems(current_user=self.current_user)
            self.assertEqual(len(probs), 1)

        # Attempt to generate a 4th question via /coding/generate
        with self.assertRaises(HTTPException) as ctx:
            generate_dynamic_coding_problem(current_user=self.current_user)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("limit reached", ctx.exception.detail.lower())

    def test_completion_shown_only_after_all_3_pass(self):
        """Coding assessment is completed only when all 3 questions pass."""
        self.cursor.execute("SELECT id FROM coding_problems LIMIT 3")
        prob_ids = [r[0] for r in self.cursor.fetchall()]

        # Question 1 passes
        self.cursor.execute("""
            INSERT INTO coding_attempts (user_id, problem_id, submitted_code, language, status, passed_tests, total_tests, correctness)
            VALUES (?, ?, 'code', 'python', 'passed', 5, 5, 100.0)
        """, (self.user_id, prob_ids[0]))
        self.cursor.execute("""
            INSERT INTO user_served_questions (user_id, module, question_id, status)
            VALUES (?, 'coding', ?, 'completed')
        """, (self.user_id, prob_ids[0]))
        self.conn.commit()

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 1)
        self.assertFalse(status.all_completed)

        # Question 2 passes
        self.cursor.execute("""
            INSERT INTO coding_attempts (user_id, problem_id, submitted_code, language, status, passed_tests, total_tests, correctness)
            VALUES (?, ?, 'code', 'python', 'passed', 5, 5, 100.0)
        """, (self.user_id, prob_ids[1]))
        self.cursor.execute("""
            INSERT INTO user_served_questions (user_id, module, question_id, status)
            VALUES (?, 'coding', ?, 'completed')
        """, (self.user_id, prob_ids[1]))
        self.conn.commit()

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 2)
        self.assertFalse(status.all_completed)

        # Question 3 fails
        self.cursor.execute("""
            INSERT INTO coding_attempts (user_id, problem_id, submitted_code, language, status, passed_tests, total_tests, correctness)
            VALUES (?, ?, 'code', 'python', 'failed', 2, 5, 40.0)
        """, (self.user_id, prob_ids[2]))
        self.cursor.execute("""
            INSERT INTO user_served_questions (user_id, module, question_id, status)
            VALUES (?, 'coding', ?, 'in_progress')
        """, (self.user_id, prob_ids[2]))
        self.conn.commit()

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 2)
        self.assertFalse(status.all_completed)
        self.assertTrue(status.has_incomplete)

        # Question 3 passes
        self.cursor.execute("""
            INSERT INTO coding_attempts (user_id, problem_id, submitted_code, language, status, passed_tests, total_tests, correctness)
            VALUES (?, ?, 'correct_code', 'python', 'passed', 5, 5, 100.0)
        """, (self.user_id, prob_ids[2]))
        self.cursor.execute("""
            UPDATE user_served_questions SET status = 'completed'
            WHERE user_id = ? AND module = 'coding' AND question_id = ?
        """, (self.user_id, prob_ids[2]))
        self.conn.commit()

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.completed_count, 3)
        self.assertTrue(status.all_completed)
        self.assertFalse(status.has_incomplete)

    def test_refreshing_or_reopening_session_does_not_reset_limit(self):
        """Refreshing or reopening a session preserves seen questions and cannot exceed 3."""
        # User receives 2 questions
        q1 = get_coding_problems(current_user=self.current_user)
        q2 = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(q1), 1)
        self.assertEqual(len(q2), 1)

        # Simulate page refresh / new connection
        conn2 = get_db_connection()
        cursor2 = conn2.cursor()
        _, _, seen_ids, _, _ = _get_user_coding_partition(cursor2, self.user_id)
        self.assertEqual(len(seen_ids), 2)
        conn2.close()

        status = get_coding_status(current_user=self.current_user)
        self.assertEqual(status.remaining_unseen_count, 1)

        # Receive 3rd question
        q3 = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(q3), 1)

        # Reopening session again must still respect the 3 question limit
        status_after = get_coding_status(current_user=self.current_user)
        self.assertEqual(status_after.remaining_unseen_count, 0)
        self.assertFalse(status_after.has_unseen)

        # Further fetch returns []
        q_extra = get_coding_problems(current_user=self.current_user)
        self.assertEqual(len(q_extra), 0)

    # -------------------------------------------------------------------------
    # ISSUE 2 REGRESSION TESTS: Question Types, Mix Distribution, Non-Code Domains
    # -------------------------------------------------------------------------
    def test_10_question_mix_distribution_standard_domains(self):
        """For standard coding domains (Python, Java, C, etc.), achieves 4 conceptual, 3 scenario, 2 coding, 1 tradeoff."""
        for domain in ["Python", "JavaScript", "C", "C++", "Java"]:
            types = [determine_target_question_type(seq, 10, domain) for seq in range(1, 11)]
            self.assertEqual(types.count("conceptual"), 4, f"Mismatch in {domain} conceptual count")
            self.assertEqual(types.count("scenario"), 3, f"Mismatch in {domain} scenario count")
            self.assertEqual(types.count("coding"), 2, f"Mismatch in {domain} coding count")
            self.assertEqual(types.count("tradeoff"), 1, f"Mismatch in {domain} tradeoff count")

    def test_non_coding_domains_have_zero_coding_questions(self):
        """For Computer Networks and Operating Systems, coding questions are strictly 0."""
        for domain in NON_CODING_DOMAINS:
            types = [determine_target_question_type(seq, 10, domain) for seq in range(1, 11)]
            self.assertEqual(types.count("coding"), 0, f"Coding question leaked into {domain}")
            self.assertGreaterEqual(types.count("conceptual"), 4)
            self.assertGreaterEqual(types.count("scenario"), 3)

    def test_conceptual_questions_have_null_code_snippets_and_starter_code(self):
        """Conceptual and scenario fallback questions do NOT have code snippets or starter code."""
        for q in FALLBACK_QUESTIONS:
            q_type = q.get("question_type", "").lower()
            if q_type in ("conceptual", "scenario", "tradeoff", "comparison", "design"):
                self.assertIsNone(
                    q.get("code_snippet"),
                    f"Conceptual question has non-null code_snippet in domain {q['domain']}: {q['question_text'][:50]}"
                )
                self.assertIsNone(
                    q.get("starter_code"),
                    f"Conceptual question has non-null starter_code in domain {q['domain']}: {q['question_text'][:50]}"
                )

    def test_all_13_domains_supported_in_fallback_with_proper_types(self):
        """Every domain in fallback has valid questions respecting domain and question_type."""
        all_domains = [
            "C", "C++", "Java", "JavaScript", "Python", "SQL", "DBMS",
            "Computer Networks", "Operating Systems", "Data Structures",
            "Algorithms", "HTML/CSS", "OOP"
        ]
        for domain in all_domains:
            fb = find_fallback_question(domain=domain, question_type="conceptual")
            self.assertEqual(fb["domain"].lower(), domain.lower())
            self.assertIsNone(fb.get("code_snippet"))
            self.assertIsNone(fb.get("starter_code"))

    def test_interview_session_question_sanitization(self):
        """When interview engine fetches a conceptual question, code_snippet and starter_code are None."""
        self.cursor.execute("SELECT id FROM domains WHERE LOWER(name) = 'python'")
        dom_row = self.cursor.fetchone()
        dom_id = dom_row[0]

        interview = InterviewEngine.create_interview(
            user_id=self.user_id,
            domain_id=dom_id,
            difficulty="Intermediate",
            interview_type="Technical",
            total_questions=10
        )
        q1 = InterviewEngine.get_next_question(interview["id"])
        self.assertIsNotNone(q1)
        self.assertEqual(q1["sequence_number"], 1)
        self.assertEqual(q1["question_type"].lower(), "conceptual")
        self.assertIsNone(q1["code_snippet"])
        self.assertIsNone(q1["starter_code"])

if __name__ == "__main__":
    unittest.main()
