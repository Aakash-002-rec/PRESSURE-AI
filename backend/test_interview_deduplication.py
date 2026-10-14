import os
import sys
import json
import sqlite3
import unittest
from unittest.mock import patch, MagicMock

# Ensure app is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection, init_db
from app.services.question_deduplicator import (
    is_semantic_duplicate,
    compute_question_fingerprint,
    clean_text,
    normalize_question_core
)
from app.services.fallback_bank import (
    FALLBACK_QUESTIONS,
    find_fallback_question,
    is_duplicate_against_history
)
from app.services.interview_engine import InterviewEngine
from app.services.llm_service import LLMService


class TestInterviewDeduplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def _create_isolated_user(self, prefix="tester"):
        import uuid
        uid_str = uuid.uuid4().hex[:8]
        username = f"{prefix}_{uid_str}"
        email = f"{prefix}_{uid_str}@test.com"
        self.cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, 'testhash', 'candidate')",
            (username, email)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def _get_or_create_user(self, username="dedup_tester", email="dedup@test.com"):
        return self._create_isolated_user(username)

    def _create_test_interview(self, user_id, domain_name="Python", topic_name=None, total_questions=10):
        self.cursor.execute("SELECT id FROM domains WHERE LOWER(name) = ?", (domain_name.lower(),))
        d_row = self.cursor.fetchone()
        self.assertIsNotNone(d_row, f"Domain {domain_name} not found")
        domain_id = d_row["id"]

        topic_id = None
        if topic_name:
            self.cursor.execute(
                "SELECT id FROM topics WHERE domain_id = ? AND LOWER(name) = ?",
                (domain_id, topic_name.lower())
            )
            t_row = self.cursor.fetchone()
            if t_row:
                topic_id = t_row["id"]

        self.cursor.execute("""
            INSERT INTO interviews (user_id, domain_id, topic_id, difficulty, current_difficulty, interview_type, total_questions, status)
            VALUES (?, ?, ?, 'Intermediate', 'Intermediate', 'Mixed', ?, 'in_progress')
        """, (user_id, domain_id, topic_id, total_questions))
        self.conn.commit()
        return self.cursor.lastrowid

    def _fetch_and_answer_question(
        self,
        interview_id: int,
        answer_text: str = "This is a detailed technical response covering the core concepts, runtime mechanics, memory management, and trade-offs."
    ):
        q = InterviewEngine.get_next_question(interview_id)
        if q:
            InterviewEngine.submit_answer(
                question_id=q["id"],
                answer_text=answer_text
            )
        return q

    # -------------------------------------------------------------------------
    # Test 1: A 10-question interview contains no exact duplicates
    # -------------------------------------------------------------------------
    def test_1_ten_question_interview_contains_no_exact_duplicates(self):
        """A full 10-question interview session must produce zero exact duplicate questions."""
        user_id = self._get_or_create_user("user_exact_dedup", "exact@test.com")
        interview_id = self._create_test_interview(user_id, domain_name="Python", total_questions=10)

        questions = []
        fingerprints = []
        normalized_texts = []

        for seq in range(1, 11):
            q = self._fetch_and_answer_question(interview_id)
            self.assertIsNotNone(q, f"Failed to fetch question #{seq}")
            self.assertEqual(q["sequence_number"], seq)

            q_text = q["question_text"]
            fp = q.get("fingerprint") or compute_question_fingerprint(q_text, domain="Python")
            norm = normalize_question_core(q_text)

            self.assertNotIn(norm, normalized_texts, f"Question #{seq} is an exact normalized duplicate: {q_text}")
            self.assertNotIn(fp, fingerprints, f"Question #{seq} has identical fingerprint to previous question: {fp}")

            questions.append(q)
            fingerprints.append(fp)
            normalized_texts.append(norm)

        self.assertEqual(len(questions), 10)
        self.assertEqual(len(set(fingerprints)), 10)
        self.assertEqual(len(set(normalized_texts)), 10)

    # -------------------------------------------------------------------------
    # Test 2: A 10-question interview contains no semantically equivalent questions
    # -------------------------------------------------------------------------
    def test_2_ten_question_interview_contains_no_semantic_duplicates(self):
        """No two questions delivered in the same 10-question session may be semantically equivalent."""
        user_id = self._get_or_create_user("user_sem_dedup", "semantic@test.com")
        interview_id = self._create_test_interview(user_id, domain_name="JavaScript", total_questions=10)

        delivered = []
        for seq in range(1, 11):
            q = self._fetch_and_answer_question(interview_id)
            self.assertIsNotNone(q)

            # Compare against all previously delivered questions in this session
            for prev in delivered:
                is_dup, reason = is_semantic_duplicate(q, prev)
                self.assertFalse(
                    is_dup,
                    f"Question #{seq} is a semantic duplicate of Question #{prev['sequence_number']} ({reason}):\n"
                    f"Current: {q['question_text']}\nPrevious: {prev['question_text']}"
                )
            delivered.append(q)

        self.assertEqual(len(delivered), 10)

    # -------------------------------------------------------------------------
    # Test 3: Similar wording with same underlying expected answer is rejected
    # -------------------------------------------------------------------------
    def test_3_similar_wording_same_underlying_answer_is_rejected(self):
        """Semantically equivalent questions with different phrasing must be recognized as duplicates."""
        test_pairs = [
            (
                {"question_text": "Explain how the JavaScript Event Loop works.", "domain": "JavaScript", "expected_concepts": ["event loop", "call stack", "callback queue"]},
                {"question_text": "Describe how JavaScript schedules synchronous code, Promises, and setTimeout callbacks using the event loop and microtask queue.", "domain": "JavaScript", "expected_concepts": ["event loop", "microtasks", "macrotasks"]}
            ),
            (
                {"question_text": "What are Python decorators and how does the @syntax wrap functions?", "domain": "Python", "expected_concepts": ["decorator", "higher-order function", "wrapper"]},
                {"question_text": "Explain how a decorator function wraps another callable to modify its behavior in Python.", "domain": "Python", "expected_concepts": ["decorator", "wrapper function", "callable"]}
            ),
            (
                {"question_text": "Explain database indexing and how B-trees speed up lookups.", "domain": "SQL", "expected_concepts": ["indexing", "b-tree", "query optimization"]},
                {"question_text": "How do B-tree indexes accelerate query lookups and search times in relational databases?", "domain": "SQL", "expected_concepts": ["b-tree index", "lookups", "performance"]}
            )
        ]

        for q1, q2 in test_pairs:
            is_dup, reason = is_semantic_duplicate(q1, q2)
            self.assertTrue(
                is_dup,
                f"Failed to identify paraphrase duplicate:\nQ1: {q1['question_text']}\nQ2: {q2['question_text']}"
            )

    # -------------------------------------------------------------------------
    # Test 4: Different concepts in same domain are accepted
    # -------------------------------------------------------------------------
    def test_4_different_concepts_in_same_domain_are_accepted(self):
        """Distinct topics within the same domain must NOT be falsely flagged as duplicates."""
        distinct_pairs = [
            (
                {"question_text": "Explain JavaScript closures and lexical scope with practical examples.", "domain": "JavaScript", "expected_concepts": ["closure", "lexical scope"]},
                {"question_text": "Explain how Promises and async/await handle asynchronous operations in JavaScript.", "domain": "JavaScript", "expected_concepts": ["promise", "async/await"]}
            ),
            (
                {"question_text": "Explain Python generators and the yield keyword for lazy evaluation.", "domain": "Python", "expected_concepts": ["generator", "yield", "lazy evaluation"]},
                {"question_text": "Explain Python decorators and higher-order function wrappers.", "domain": "Python", "expected_concepts": ["decorator", "wrapper", "higher-order function"]}
            ),
            (
                {"question_text": "Explain SQL JOIN types (INNER, LEFT, RIGHT, FULL) and when to use each.", "domain": "SQL", "expected_concepts": ["inner join", "left join", "relational tables"]},
                {"question_text": "Explain database normalization forms from 1NF to 3NF and Boyce-Codd normal form.", "domain": "SQL", "expected_concepts": ["normalization", "1nf", "3nf", "bcnf"]}
            ),
            (
                {"question_text": "Explain CPU scheduling algorithms such as Round Robin, FCFS, and Shortest Job First.", "domain": "Operating Systems", "expected_concepts": ["cpu scheduling", "round robin", "preemption"]},
                {"question_text": "What are the four necessary conditions for deadlock in operating systems and how can it be prevented?", "domain": "Operating Systems", "expected_concepts": ["deadlock", "mutual exclusion", "hold and wait", "circular wait"]}
            )
        ]

        for q1, q2 in distinct_pairs:
            is_dup, reason = is_semantic_duplicate(q1, q2)
            self.assertFalse(
                is_dup,
                f"False positive duplicate detection between distinct concepts ({reason}):\nQ1: {q1['question_text']}\nQ2: {q2['question_text']}"
            )

    # -------------------------------------------------------------------------
    # Test 5: All 10 questions respect the intended question-type distribution
    # -------------------------------------------------------------------------
    def test_5_intended_question_type_distribution_preserved(self):
        """A 10-question interview must follow the distribution: 4 conceptual, 3 scenario, 2 coding, 1 tradeoff."""
        user_id = self._get_or_create_user("user_dist", "dist@test.com")
        interview_id = self._create_test_interview(user_id, domain_name="Python", total_questions=10)

        questions = [self._fetch_and_answer_question(interview_id) for _ in range(10)]
        types = [q["question_type"] for q in questions]

        type_counts = {}
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1

        self.assertEqual(type_counts.get("conceptual", 0), 4, f"Expected 4 conceptual questions, got {type_counts.get('conceptual')}")
        self.assertEqual(type_counts.get("scenario", 0), 3, f"Expected 3 scenario questions, got {type_counts.get('scenario')}")
        self.assertEqual(type_counts.get("coding", 0), 2, f"Expected 2 coding questions, got {type_counts.get('coding')}")
        self.assertEqual(type_counts.get("tradeoff", 0), 1, f"Expected 1 tradeoff question, got {type_counts.get('tradeoff')}")

        # Also verify that for non-coding domains like Operating Systems, questions do not force code snippets
        os_interview_id = self._create_test_interview(user_id, domain_name="Operating Systems", total_questions=10)
        os_questions = [self._fetch_and_answer_question(os_interview_id) for _ in range(10)]
        for q in os_questions:
            self.assertIsNone(q.get("code_snippet"), f"Operating Systems question must not include code snippet: {q['code_snippet']}")
            self.assertIsNone(q.get("starter_code"), f"Operating Systems question must not include starter code: {q['starter_code']}")

    # -------------------------------------------------------------------------
    # Test 6: Domain and focus-topic selection remain correct
    # -------------------------------------------------------------------------
    def test_6_domain_and_focus_topic_isolation(self):
        """All questions must strictly match the selected domain with no cross-domain leakage."""
        user_id = self._get_or_create_user("user_isolation", "iso@test.com")
        test_domains = ["Java", "SQL", "Operating Systems", "C++"]

        python_leakage_keywords = ["python", "def __init__", "def ", "self.", "list comprehension", "pip install"]

        for d_name in test_domains:
            interview_id = self._create_test_interview(user_id, domain_name=d_name, total_questions=5)
            for _ in range(5):
                q = self._fetch_and_answer_question(interview_id)
                self.assertIsNotNone(q)
                text = q["question_text"].lower()
                for leak in python_leakage_keywords:
                    self.assertNotIn(
                        leak,
                        text,
                        f"Domain {d_name} received question with Python leakage: {q['question_text']}"
                    )

    # -------------------------------------------------------------------------
    # Test 7: Fallback questions do not duplicate questions already asked in session
    # -------------------------------------------------------------------------
    def test_7_fallback_questions_do_not_duplicate_in_session(self):
        """When relying entirely on the fallback question bank, all 10 delivered questions must be unique."""
        # Force fallback by mocking LLMService to simulate quota/unavailable
        with patch.object(LLMService, "generate_question", side_effect=lambda *args, **kwargs: find_fallback_question(
            domain=kwargs.get("domain", "Python"),
            topic=kwargs.get("topic", "Core"),
            difficulty=kwargs.get("difficulty", "Intermediate"),
            question_type=kwargs.get("question_type", "conceptual"),
            exclude_question_texts=kwargs.get("exclude_questions_full", [])
        )):
            user_id = self._get_or_create_user("user_fb_dedup", "fb_dedup@test.com")
            interview_id = self._create_test_interview(user_id, domain_name="Python", total_questions=10)

            delivered_texts = []
            for seq in range(1, 11):
                q = self._fetch_and_answer_question(interview_id)
                self.assertIsNotNone(q)
                self.assertNotIn(q["question_text"], delivered_texts, f"Fallback repeated question on seq #{seq}: {q['question_text']}")
                delivered_texts.append(q["question_text"])

            self.assertEqual(len(set(delivered_texts)), 10)

    # -------------------------------------------------------------------------
    # Test 8: A new session for the same user avoids recently asked questions
    # -------------------------------------------------------------------------
    def test_8_new_session_for_same_user_avoids_recently_asked_questions(self):
        """A subsequent interview session for the same user avoids repeating questions from the previous session."""
        user_id = self._get_or_create_user("user_cross_session", "cross@test.com")
        # Session 1: 5 questions in Python
        session1_id = self._create_test_interview(user_id, domain_name="Python", total_questions=5)
        session1_texts = set()
        for _ in range(5):
            q = self._fetch_and_answer_question(session1_id)
            session1_texts.add(q["question_text"])

        # Session 2: New interview in Python for same user
        session2_id = self._create_test_interview(user_id, domain_name="Python", total_questions=5)
        session2_texts = set()
        for _ in range(5):
            q = self._fetch_and_answer_question(session2_id)
            session2_texts.add(q["question_text"])

        # Intersection between early questions of Session 1 and Session 2 should be zero given the bank of 15+ questions
        intersection = session1_texts.intersection(session2_texts)
        self.assertEqual(len(intersection), 0, f"Session 2 repeated questions from Session 1: {intersection}")

    # -------------------------------------------------------------------------
    # Test 9: Question history persists after database reconnection or restart
    # -------------------------------------------------------------------------
    def test_9_question_history_persists_across_reconnect(self):
        """Delivered questions and their fingerprints persist in DB and are respected after connection reset."""
        user_id = self._get_or_create_user("user_persist", "persist@test.com")
        interview_id = self._create_test_interview(user_id, domain_name="Python", total_questions=3)

        q1 = self._fetch_and_answer_question(interview_id)
        self.assertIsNotNone(q1)

        # Close active connection to simulate restart / new process
        self.conn.close()
        self.conn = get_db_connection()
        self.cursor = self.conn.cursor()

        # Check DB directly
        self.cursor.execute("SELECT fingerprint, question_text FROM questions WHERE id = ?", (q1["id"],))
        db_row = self.cursor.fetchone()
        self.assertIsNotNone(db_row)
        self.assertIsNotNone(db_row["fingerprint"])
        self.assertGreater(len(db_row["fingerprint"]), 0)

        # Check user_served_questions
        self.cursor.execute("SELECT question_id FROM user_served_questions WHERE user_id = ? AND question_id = ?", (user_id, q1["id"]))
        sq_row = self.cursor.fetchone()
        self.assertIsNotNone(sq_row)

        # Next question in session should not be q1
        q2 = self._fetch_and_answer_question(interview_id)
        self.assertNotEqual(q1["id"], q2["id"])
        self.assertNotEqual(q1.get("fingerprint"), q2.get("fingerprint"))

    # -------------------------------------------------------------------------
    # Test 10: Pressure Mode and adaptive difficulty continue to work
    # -------------------------------------------------------------------------
    def test_10_pressure_mode_and_adaptive_difficulty(self):
        """Pressure Mode and adaptive difficulty work alongside deduplication."""
        user_id = self._get_or_create_user("user_pressure", "pressure@test.com")
        interview_id = self._create_test_interview(user_id, domain_name="Python", total_questions=5)

        q1 = InterviewEngine.get_next_question(interview_id)
        self.assertIsNotNone(q1)

        # Submit a low score on q1 to trigger weakness
        eval_low = InterviewEngine.submit_answer(
            question_id=q1["id"],
            answer_text="I don't know anything about this topic."
        )
        self.assertLess(eval_low["overall_score"], 6.0)

        # Next question should adapt difficulty or topic
        q2 = InterviewEngine.get_next_question(interview_id)
        self.assertIsNotNone(q2)
        self.assertNotEqual(q1["id"], q2["id"])

        # Submit another low score to ignite pressure mode
        eval_low_2 = InterviewEngine.submit_answer(
            question_id=q2["id"],
            answer_text="No idea, completely blank."
        )

        # Next question under pressure
        q3 = InterviewEngine.get_next_question(interview_id)
        self.assertIsNotNone(q3)
        self.assertNotEqual(q2["id"], q3["id"])
        dup1, _ = is_semantic_duplicate(q1, q3)
        self.assertFalse(dup1)
        dup2, _ = is_semantic_duplicate(q2, q3)
        self.assertFalse(dup2)

    # -------------------------------------------------------------------------
    # Test 11: Duplicate retries do not create infinite loops
    # -------------------------------------------------------------------------
    def test_11_duplicate_retries_do_not_create_infinite_loops(self):
        """If generator repeatedly generates duplicates, retry limit stops the loop and returns a fallback."""
        user_id = self._get_or_create_user("user_loop", "loop@test.com")
        interview_id = self._create_test_interview(user_id, domain_name="Python", total_questions=3)

        q1 = self._fetch_and_answer_question(interview_id)

        # Mock LLMService to always return identical question as q1
        duplicate_response = {
            "question_text": q1["question_text"],
            "difficulty": "Intermediate",
            "question_type": "conceptual",
            "expected_concepts": ["decorator"],
            "hints": ["Hint 1", "Hint 2"],
            "model_answer": "Model answer",
            "evaluation_criteria": {}
        }

        with patch.object(LLMService, "generate_question", return_value=duplicate_response):
            # Engine must NOT enter infinite loop; it must reject the duplicate 4 times and switch to fallback
            q2 = InterviewEngine.get_next_question(interview_id)
            self.assertIsNotNone(q2)
            self.assertNotEqual(q2["question_text"], q1["question_text"])
            dup, _ = is_semantic_duplicate(q1, q2)
            self.assertFalse(dup)

    # -------------------------------------------------------------------------
    # Test 12: Handled gracefully when static question pool is exhausted
    # -------------------------------------------------------------------------
    def test_12_graceful_handling_when_question_pool_exhausted(self):
        """When static fallbacks are completely exhausted, dynamically synthesize a unique question."""
        # Create a mock history that excludes all existing questions in Python
        existing_python_questions = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == "python"]
        mock_history = [
            {"question_text": q["question_text"], "domain": "Python", "expected_concepts": q.get("expected_concepts", [])}
            for q in existing_python_questions
        ]

        # Call find_fallback_question with all static questions in history
        novel_q = find_fallback_question(
            domain="Python",
            topic="OOP & Inheritance",
            difficulty="Advanced",
            question_type="scenario",
            exclude_question_texts=mock_history
        )

        self.assertIsNotNone(novel_q)
        self.assertEqual(novel_q["domain"], "Python")
        # Ensure it does not duplicate any of the exhausted questions
        for prev in mock_history:
            dup, _ = is_semantic_duplicate(novel_q, prev)
            self.assertFalse(
                dup,
                f"Synthesized question duplicated an exhausted question:\nSynthesized: {novel_q['question_text']}\nExhausted: {prev['question_text']}"
            )


if __name__ == "__main__":
    unittest.main()
