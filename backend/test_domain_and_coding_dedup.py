import os
import sys
import json
import sqlite3
import unittest

# Ensure app is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection, init_db
from app.services.fallback_bank import FALLBACK_QUESTIONS, find_fallback_question
from app.services.llm_service import LLMService, DOMAIN_CODE_LANG_MAP
from app.services.interview_engine import InterviewEngine
from app.services.problem_fingerprint import compute_problem_fingerprint, is_duplicate_problem
from app.services.code_runner import CodeRunner

ALL_13_DOMAINS = [
    "C",
    "C++",
    "Java",
    "JavaScript",
    "Python",
    "Algorithms",
    "Computer Networks",
    "DBMS",
    "Data Structures",
    "HTML/CSS",
    "OOP",
    "Operating Systems",
    "SQL"
]

class TestDomainSpecificInterviews(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_all_13_domains_have_fallback_banks(self):
        """Every supported domain must have a populated fallback question bank."""
        for domain in ALL_13_DOMAINS:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == domain.lower()]
            self.assertGreater(len(pool), 0, f"Empty fallback pool for domain: {domain}")
            
            # Verify every question in this pool belongs to this domain
            for q in pool:
                self.assertEqual(q["domain"].lower(), domain.lower(), f"Question domain mismatch in {domain} pool: {q['domain']}")

    def test_non_python_fallback_does_not_leak_python(self):
        """Selecting any non-Python domain fallback must NOT return Python-specific content."""
        python_indicators = ["in python", "python's", "def __init__", "def ", "self.", "list comprehension"]
        for domain in ALL_13_DOMAINS:
            if domain == "Python":
                continue
            fb = find_fallback_question(domain=domain, topic="Core", difficulty="Intermediate")
            self.assertIsNotNone(fb)
            self.assertEqual(fb["domain"].lower(), domain.lower())
            q_text = fb["question_text"].lower()
            for ind in python_indicators:
                self.assertNotIn(ind, q_text, f"Python leakage found in {domain} fallback: {fb['question_text']}")

    def test_domain_code_language_mapping(self):
        """Verify proper code language mapping for code snippets."""
        expected_langs = {
            "c": "c",
            "c++": "cpp",
            "java": "java",
            "javascript": "javascript",
            "python": "python",
            "sql": "sql",
            "html/css": "html"
        }
        for d, expected_lang in expected_langs.items():
            self.assertEqual(DOMAIN_CODE_LANG_MAP.get(d.lower()), expected_lang)

    def test_interview_session_respects_selected_domain_and_topic(self):
        """Creating an interview with a specific domain and focus topic generates matching questions."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get or create test user
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_row = cursor.fetchone()
        if not user_row:
            cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES ('domain_tester', 'domain@test.com', 'hash')")
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user_row[0]

        # Test domains: JavaScript, C++, SQL
        test_cases = [
            ("JavaScript", "Closures"),
            ("C++", "STL"),
            ("SQL", "Joins"),
            ("Operating Systems", "Deadlocks")
        ]

        for domain_name, focus_topic in test_cases:
            cursor.execute("SELECT id FROM domains WHERE LOWER(name) = ?", (domain_name.lower(),))
            domain_row = cursor.fetchone()
            self.assertIsNotNone(domain_row, f"Domain {domain_name} not found in DB")
            domain_id = domain_row[0]

            cursor.execute("SELECT id FROM topics WHERE domain_id = ? AND LOWER(name) LIKE ?", (domain_id, f"%{focus_topic.lower()}%"))
            topic_row = cursor.fetchone()
            topic_id = topic_row[0] if topic_row else None

            # Create interview
            interview = InterviewEngine.create_interview(
                user_id=user_id,
                domain_id=domain_id,
                difficulty="Intermediate",
                interview_type="Technical",
                total_questions=3,
                topic_id=topic_id
            )
            self.assertEqual(interview["domain_name"].lower(), domain_name.lower())

            # Get question
            q = InterviewEngine.get_next_question(interview["id"])
            self.assertIsNotNone(q)
            self.assertIn("question_text", q)
            # Question must not have Python leakage
            q_lower = q["question_text"].lower()
            self.assertNotIn("in python", q_lower)
            self.assertNotIn("python's", q_lower)

            # Code language must match domain, not python
            expected_code_lang = DOMAIN_CODE_LANG_MAP.get(domain_name.lower(), "text")
            self.assertEqual(q.get("code_language"), expected_code_lang)

            if topic_id:
                self.assertEqual(q["topic_id"], topic_id)

        conn.close()

    def test_pressure_mode_and_adaptive_difficulty(self):
        """Adaptive transitions and Pressure Mode should remain fully functional."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM domains WHERE LOWER(name) = 'c'")
        c_domain_id = cursor.fetchone()[0]

        interview = InterviewEngine.create_interview(
            user_id=user_id,
            domain_id=c_domain_id,
            difficulty="Beginner",
            interview_type="Technical",
            total_questions=4
        )
        interview_id = interview["id"]

        q1 = InterviewEngine.get_next_question(interview_id)
        self.assertIsNotNone(q1)

        # Submit weak answer to trigger pressure mode
        ans_res = InterviewEngine.submit_answer(
            question_id=q1["id"],
            answer_text="I do not know how pointers work in C."
        )
        self.assertIn("overall_score", ans_res)

        # Check next question
        q2 = InterviewEngine.get_next_question(interview_id)
        self.assertIsNotNone(q2)
        # Verify domain remains C
        self.assertEqual(q2.get("code_language"), "c")
        conn.close()


class TestCodingProblemDeduplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()
        # Create two distinct test users
        self.cursor.execute("INSERT INTO users (name, email, password_hash) VALUES ('user_dedup_a', 'dedup_a@test.com', 'h')")
        self.user_a_id = self.cursor.lastrowid
        self.cursor.execute("INSERT INTO users (name, email, password_hash) VALUES ('user_dedup_b', 'dedup_b@test.com', 'h')")
        self.user_b_id = self.cursor.lastrowid
        self.conn.commit()

    def tearDown(self):
        self.cursor.execute("DELETE FROM user_served_questions WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.cursor.execute("DELETE FROM coding_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.cursor.execute("DELETE FROM users WHERE id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.conn.commit()
        self.conn.close()

    def test_fingerprint_deterministic_and_paraphrase_resistant(self):
        """Fingerprints should identify identical tasks even with cosmetic title/variable renames."""
        tests1 = [{"input": "5", "expected_output": "120"}]
        starter1 = "def factorial(n: int) -> int:\n    pass"
        fp1 = compute_problem_fingerprint("Factorial Problem", "Compute factorial of integer n.", tests1, starter1)

        tests2 = [{"input": "5", "expected_output": "120"}]
        starter2 = "def solve_fact(val: int) -> int:\n    pass"
        fp2 = compute_problem_fingerprint("Calculate Factorial", "Given an integer n, return its factorial.", tests2, starter2)

        p1 = {"title": "Factorial Problem", "description": "Compute factorial of integer n.", "starter_code": starter1, "test_cases": tests1}
        p2 = {"title": "Calculate Factorial", "description": "Given an integer n, return its factorial.", "starter_code": starter2, "test_cases": tests2}
        
        self.assertTrue(is_duplicate_problem(p1, p2), "Paraphrased problem should be detected as duplicate")

    def test_user_never_receives_same_coding_problem_twice(self):
        """User A receives problems once, and subsequent calls exclude already-served problems."""
        from app.routers.coding_routes import get_coding_problems

        user_a = {"id": self.user_a_id, "username": "user_dedup_a"}
        
        # Call 1: user A gets first batch
        batch1 = get_coding_problems(category="Recursion", current_user=user_a)
        self.assertGreater(len(batch1), 0)
        served_ids_1 = [p["id"] for p in batch1]

        # Call 2: user A requests problems again
        batch2 = get_coding_problems(category="Recursion", current_user=user_a)
        served_ids_2 = [p["id"] for p in batch2]

        # None of the problems in batch2 should have been in batch1
        overlap = set(served_ids_1).intersection(set(served_ids_2))
        self.assertEqual(len(overlap), 0, f"User received duplicate problem IDs: {overlap}")

    def test_multi_user_independence(self):
        """Problem served to User A can still be served to User B (per-user history, not global)."""
        from app.routers.coding_routes import get_coding_problems

        user_a = {"id": self.user_a_id, "username": "user_dedup_a"}
        user_b = {"id": self.user_b_id, "username": "user_dedup_b"}

        batch_a = get_coding_problems(category="Recursion", current_user=user_a)
        self.assertGreater(len(batch_a), 0)
        a_first_id = batch_a[0]["id"]

        # User B should still be able to receive that problem
        batch_b = get_coding_problems(category="Recursion", current_user=user_b)
        self.assertGreater(len(batch_b), 0)
        b_ids = [p["id"] for p in batch_b]
        self.assertIn(a_first_id, b_ids, "User B should be able to receive unseen problem even if User A has seen it")

    def test_dedup_persists_across_database_reconnect(self):
        """Database reconnect (simulating server restart) maintains exclusion."""
        from app.routers.coding_routes import get_coding_problems

        user_a = {"id": self.user_a_id, "username": "user_dedup_a"}
        batch1 = get_coding_problems(category="Recursion", current_user=user_a)
        seen_id = batch1[0]["id"]

        # Simulate fresh connection / server restart
        new_conn = get_db_connection()
        new_cur = new_conn.cursor()
        new_cur.execute("SELECT question_id FROM user_served_questions WHERE user_id = ? AND question_id = ?", (self.user_a_id, seen_id))
        row = new_cur.fetchone()
        new_conn.close()

        self.assertIsNotNone(row, "Served problem must persist in user_served_questions")

        # Next query must not serve seen_id
        batch2 = get_coding_problems(category="Recursion", current_user=user_a)
        for p in batch2:
            self.assertNotEqual(p["id"], seen_id)

    def test_pool_exhaustion_does_not_repeat_problem(self):
        """When all problems in a category are seen, generate endpoint returns clear 404 rather than duplicates."""
        from app.routers.coding_routes import generate_dynamic_coding_problem
        from fastapi import HTTPException

        user_a = {"id": self.user_a_id, "username": "user_dedup_a"}

        # Mark all Arrays problems as served for user A (1 problem, so session limit 3 is not hit)
        self.cursor.execute("SELECT id, fingerprint FROM coding_problems WHERE category = 'Arrays'")
        for r in self.cursor.fetchall():
            self.cursor.execute("INSERT OR IGNORE INTO user_served_questions (user_id, module, question_id, fingerprint) VALUES (?, 'coding', ?, ?)", (self.user_a_id, r[0], r[1]))
        self.conn.commit()

        # Disable gemini temporarily to test deterministic fallback exhaustion
        import app.routers.coding_routes as cr
        orig_active = cr.gemini_model
        cr.gemini_model = None

        try:
            with self.assertRaises(HTTPException) as cm:
                generate_dynamic_coding_problem(category="Arrays", current_user=user_a)
            self.assertEqual(cm.exception.status_code, 404)
            self.assertIn("No unseen coding problems are currently available", cm.exception.detail)
        finally:
            cr.gemini_model = orig_active

    def test_code_runner_authoritative_evaluation(self):
        """Code Runner test cases execute and validate correctly."""
        code = """def factorial(n: int) -> int:
    if n < 0: return -1
    if n in (0, 1): return 1
    res = 1
    for i in range(2, n + 1):
        res *= i
    return res"""
        tests = [
            {"input": "5", "expected_output": "120", "is_hidden": False},
            {"input": "0", "expected_output": "1", "is_hidden": True}
        ]
        res = CodeRunner.execute_python_tests(code, tests, "factorial")
        self.assertEqual(res["status"].lower(), "passed")
        self.assertEqual(res["passed_count"], 2)
        self.assertEqual(res["total_count"], 2)

if __name__ == "__main__":
    unittest.main()
