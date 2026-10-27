import unittest
import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from app.database import get_db_connection, init_db
from app.services.attempt_service import AttemptService
from app.services.interview_engine import InterviewEngine
from app.services.cross_module_engine import CrossModuleEngine
from app.routers.aptitude_routes import (
    get_aptitude_session,
    start_aptitude_test,
    save_aptitude_progress,
    submit_aptitude_test,
)
from app.routers.coding_routes import (
    get_coding_status,
    get_coding_problems,
    submit_code_solution,
)
from app.routers.interview_routes import (
    create_interview,
    get_interview,
    get_next_question,
    submit_answer,
)
from app.routers.assessment_routes import (
    get_current_assessment_attempt,
    start_assessment_retest,
    get_assessment_attempt_history,
    get_assessment_attempt_report,
)
from app.models import (
    AptitudeStartRequest,
    AptitudeSaveProgressRequest,
    AptitudeTestSubmit,
    AptitudeAnswerSubmission,
    CodingSubmitRequest,
    InterviewCreate,
    AnswerSubmit,
)
from app.config import (
    APTITUDE_TIME_LIMIT_SECONDS,
    CODING_TIME_LIMIT_SECONDS,
    INTERVIEW_TIME_LIMIT_SECONDS,
)


def _v(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


class TestAssessmentWorkflowAndTimers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.conn = get_db_connection()
        self.cur = self.conn.cursor()

        self.uid_a = uuid.uuid4().hex[:8]
        self.email_a = f"wf_a_{self.uid_a}@pressure.ai"
        self.cur.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, 'h', 'candidate')",
            (f"Candidate Workflow A {self.uid_a}", self.email_a)
        )
        self.user_a_id = self.cur.lastrowid

        self.uid_b = uuid.uuid4().hex[:8]
        self.email_b = f"wf_b_{self.uid_b}@pressure.ai"
        self.cur.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, 'h', 'candidate')",
            (f"Candidate Workflow B {self.uid_b}", self.email_b)
        )
        self.user_b_id = self.cur.lastrowid
        self.conn.commit()

        self.user_a = {"id": self.user_a_id, "email": self.email_a, "role": "candidate"}
        self.user_b = {"id": self.user_b_id, "email": self.email_b, "role": "candidate"}

        import app.routers.aptitude_routes as apt_module
        import app.routers.coding_routes as cod_module
        self._orig_apt_gemini = apt_module.gemini_model
        self._orig_cod_gemini = cod_module.gemini_model
        apt_module.gemini_model = None
        cod_module.gemini_model = None

    def tearDown(self):
        try:
            import app.routers.aptitude_routes as apt_module
            import app.routers.coding_routes as cod_module
            apt_module.gemini_model = getattr(self, "_orig_apt_gemini", None)
            cod_module.gemini_model = getattr(self, "_orig_cod_gemini", None)
            self.cur.execute("DELETE FROM assessment_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            self.cur.execute("DELETE FROM coding_sessions WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            self.cur.execute("DELETE FROM user_served_questions WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            self.cur.execute("DELETE FROM coding_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            self.cur.execute("DELETE FROM aptitude_attempts WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            self.cur.execute("DELETE FROM interviews WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
            self.cur.execute("DELETE FROM users WHERE id IN (?, ?)", (self.user_a_id, self.user_b_id))
            self.conn.commit()
            self.conn.close()
        except Exception:
            pass

    # 1. Login begins assessment workflow at Aptitude
    def test_01_login_begins_workflow_at_aptitude(self):
        att = get_current_assessment_attempt(current_user=self.user_a)
        self.assertEqual(_v(att, "current_stage"), "aptitude")
        self.assertEqual(_v(att, "aptitude_status"), "not_started")
        self.assertEqual(_v(att, "coding_status"), "not_started")
        self.assertEqual(_v(att, "interview_status"), "not_started")
        self.assertEqual(_v(att, "status"), "in_progress")

    # 2. Coding is blocked until Aptitude is completed
    def test_02_coding_blocked_until_aptitude_completed(self):
        # Coding status shows is_locked = True
        status = get_coding_status(current_user=self.user_a)
        self.assertTrue(status.is_locked)

        # Direct fetch must raise 403 Forbidden
        with self.assertRaises(HTTPException) as ctx:
            get_coding_problems(current_user=self.user_a)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("Aptitude Assessment must be completed", ctx.exception.detail)

    # 3. AI Mock Interview is blocked until Coding is completed
    def test_03_interview_blocked_until_coding_completed(self):
        # 1. Blocked when aptitude not even started
        with self.assertRaises(HTTPException) as ctx1:
            create_interview(
                data=InterviewCreate(domain_id=1, difficulty="Intermediate", interview_type="Mixed", total_questions=5),
                current_user=self.user_a
            )
        self.assertEqual(ctx1.exception.status_code, 403)

        # 2. Complete Aptitude but keep Coding incomplete
        AttemptService.get_or_create_active_attempt(self.cur, self.user_a_id)
        self.cur.execute("UPDATE assessment_attempts SET aptitude_status = 'completed' WHERE user_id = ?", (self.user_a_id,))
        self.conn.commit()

        # Still blocked because coding is incomplete
        with self.assertRaises(HTTPException) as ctx2:
            create_interview(
                data=InterviewCreate(domain_id=1, difficulty="Intermediate", interview_type="Mixed", total_questions=5),
                current_user=self.user_a
            )
        self.assertEqual(ctx2.exception.status_code, 403)
        self.assertIn("Coding Assessment must be completed", ctx2.exception.detail)

    # 4. Timer starts when user actually starts assessment (not on login)
    def test_04_timer_starts_only_when_user_starts_assessment(self):
        sess = get_aptitude_session(current_user=self.user_a)
        self.assertFalse(sess.in_test)
        self.assertFalse(sess.completed)
        self.assertIsNone(sess.started_at)
        self.assertIsNone(sess.deadline)
        self.assertEqual(sess.remaining_seconds, APTITUDE_TIME_LIMIT_SECONDS)

        # Candidate clicks "Start Aptitude"
        started = start_aptitude_test(
            payload=AptitudeStartRequest(category="Quantitative Aptitude", difficulty="Intermediate"),
            current_user=self.user_a
        )
        self.assertTrue(started.in_test)
        self.assertFalse(started.completed)
        self.assertIsNotNone(started.started_at)
        self.assertIsNotNone(started.deadline)
        self.assertLessEqual(started.remaining_seconds, APTITUDE_TIME_LIMIT_SECONDS)

    # 5. Refreshing browser restores correct remaining time and does NOT reset timer
    def test_05_browser_refresh_does_not_reset_timer(self):
        start_aptitude_test(
            payload=AptitudeStartRequest(category="Quantitative Aptitude", difficulty="Intermediate"),
            current_user=self.user_a
        )

        # Simulate 20 seconds passing on server by adjusting started_at & deadline
        past_start = (datetime.now(timezone.utc) - timedelta(seconds=20)).strftime("%Y-%m-%d %H:%M:%S")
        past_dl = (datetime.now(timezone.utc) + timedelta(seconds=APTITUDE_TIME_LIMIT_SECONDS - 20)).strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("""
            UPDATE assessment_attempts
            SET aptitude_started_at = ?, aptitude_deadline = ?
            WHERE user_id = ?
        """, (past_start, past_dl, self.user_a_id))
        self.conn.commit()

        # Simulate browser refresh by fetching session again
        refreshed = get_aptitude_session(current_user=self.user_a)
        # Remaining time must be approximately 20 seconds less, NOT reset to 900
        self.assertLessEqual(refreshed.remaining_seconds, APTITUDE_TIME_LIMIT_SECONDS - 18)
        self.assertGreater(refreshed.remaining_seconds, 0)

    # 6. Candidate draft answers are preserved and resumed on refresh
    def test_06_draft_answers_saved_and_restored(self):
        start_aptitude_test(
            payload=AptitudeStartRequest(category="Quantitative Aptitude", difficulty="Intermediate"),
            current_user=self.user_a
        )

        # Candidate selects answers for Q1 and Q2
        draft = {1: 2, 2: 0}
        save_aptitude_progress(
            payload=AptitudeSaveProgressRequest(answers=draft, elapsed_seconds=35),
            current_user=self.user_a
        )

        # Browser reloads session
        reloaded = get_aptitude_session(current_user=self.user_a)
        self.assertEqual(reloaded.current_answers.get("1") if "1" in reloaded.current_answers else reloaded.current_answers.get(1), 2)
        self.assertEqual(reloaded.current_answers.get("2") if "2" in reloaded.current_answers else reloaded.current_answers.get(2), 0)

    # 7. Expired assessment rejects late submission
    def test_07_expired_assessment_rejects_late_submission(self):
        start_aptitude_test(
            payload=AptitudeStartRequest(category="Quantitative Aptitude", difficulty="Intermediate"),
            current_user=self.user_a
        )

        # Set deadline in the past
        past_dl = (datetime.now(timezone.utc) - timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute("""
            UPDATE assessment_attempts
            SET aptitude_deadline = ?
            WHERE user_id = ?
        """, (past_dl, self.user_a_id))
        self.conn.commit()

        # Submitting regular answers after deadline is marked as timeout
        sub = AptitudeTestSubmit(
            category="Quantitative Aptitude",
            difficulty="Intermediate",
            total_questions=2,
            time_taken_seconds=930,
            answers=[
                AptitudeAnswerSubmission(question_id=1, selected_option=1),
                AptitudeAnswerSubmission(question_id=2, selected_option=2)
            ]
        )
        res = submit_aptitude_test(data=sub, current_user=self.user_a)
        self.assertTrue(_v(res, "is_timeout"))
        self.assertEqual(_v(res, "completion_reason"), "timeout")

    # 8. Coding assessment contains exactly 3 questions
    def test_08_coding_contains_exactly_three_questions(self):
        # Mark aptitude completed
        AttemptService.get_or_create_active_attempt(self.cur, self.user_a_id)
        self.cur.execute("UPDATE assessment_attempts SET aptitude_status = 'completed' WHERE user_id = ?", (self.user_a_id,))
        self.conn.commit()

        # Start coding and fetch 3 questions
        q1 = get_coding_problems(current_user=self.user_a)
        q2 = get_coding_problems(current_user=self.user_a)
        q3 = get_coding_problems(current_user=self.user_a)
        q4 = get_coding_problems(current_user=self.user_a)

        self.assertEqual(len(q1), 1)
        self.assertEqual(len(q2), 1)
        self.assertEqual(len(q3), 1)
        self.assertEqual(len(q4), 0, "No fourth question allowed")

        status = get_coding_status(current_user=self.user_a)
        self.assertEqual(status.total_problems_count, 3)
        self.assertEqual(status.session_limit, 3)

    # 9. Retest creates a new unique attempt_id without overwriting historical records
    def test_09_retest_creates_new_attempt_and_preserves_history(self):
        att1 = get_current_assessment_attempt(current_user=self.user_a)
        id1 = _v(att1, "attempt_id")

        # Complete attempt 1
        self.cur.execute("""
            UPDATE assessment_attempts
            SET status = 'completed', aptitude_status = 'completed', coding_status = 'completed', interview_status = 'completed'
            WHERE user_id = ? AND attempt_id = ?
        """, (self.user_a_id, id1))
        self.conn.commit()

        # Click Retest
        retest_res = start_assessment_retest(current_user=self.user_a)
        id2 = _v(retest_res, "attempt_id")

        self.assertNotEqual(id1, id2)
        new_att = _v(retest_res, "new_attempt")
        self.assertEqual(_v(new_att, "attempt_number"), 2)
        self.assertEqual(_v(new_att, "aptitude_status"), "not_started")
        self.assertEqual(_v(new_att, "coding_status"), "not_started")
        self.assertEqual(_v(new_att, "interview_status"), "not_started")

        # History contains both attempts
        hist = get_assessment_attempt_history(current_user=self.user_a)
        self.assertEqual(len(hist), 2)
        hist_ids = [_v(h, "attempt_id") for h in hist]
        self.assertIn(id1, hist_ids)
        self.assertIn(id2, hist_ids)

    # 10. User isolation: User A cannot access User B's report or questions
    def test_10_user_isolation_enforced(self):
        att_a = get_current_assessment_attempt(current_user=self.user_a)
        att_b = get_current_assessment_attempt(current_user=self.user_b)
        id_b = _v(att_b, "attempt_id")

        # Complete both
        self.cur.execute("UPDATE assessment_attempts SET status = 'completed', interview_status = 'completed' WHERE user_id IN (?, ?)", (self.user_a_id, self.user_b_id))
        self.conn.commit()

        # User A tries to open User B's attempt report
        with self.assertRaises(HTTPException) as ctx:
            get_assessment_attempt_report(attempt_id=id_b, current_user=self.user_a)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("cannot access another candidate", ctx.exception.detail)

    # 11. Final performance report computes time-based efficiency metrics accurately
    def test_11_performance_report_metrics_and_speed_archetype(self):
        att = get_current_assessment_attempt(current_user=self.user_a)
        att_id = _v(att, "attempt_id")

        # Insert aptitude attempt
        self.cur.execute("""
            INSERT INTO aptitude_attempts (
                user_id, category, difficulty, total_questions, correct_count,
                incorrect_count, score, time_taken_seconds, category_breakdown, weak_categories,
                attempt_id, is_timeout, completion_reason, started_at, completed_at
            ) VALUES (?, 'Quantitative Aptitude', 'Intermediate', 10, 8, 2, 80.0, 300, ?, ?, ?, 0, 'completed_normally', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (self.user_a_id, json.dumps({"Math": 80.0, "Logic": 80.0}), json.dumps([]), att_id))
        apt_id = self.cur.lastrowid

        # Insert interview attempt
        self.cur.execute("""
            INSERT INTO interviews (
                user_id, domain_id, difficulty, current_difficulty, interview_type, total_questions,
                status, overall_score, technical_score, conceptual_score,
                problem_solving_score, communication_score, attempt_id, started_at, completed_at
            ) VALUES (?, 1, 'Intermediate', 'Intermediate', 'Mixed', 3, 'completed', 85.0, 85.0, 90.0, 80.0, 85.0, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (self.user_a_id, att_id))
        iv_id = self.cur.lastrowid

        # Mark attempt completed
        self.cur.execute("""
            UPDATE assessment_attempts
            SET status = 'completed', current_stage = 'completed',
                aptitude_status = 'completed', aptitude_attempt_id = ?, aptitude_time_taken_seconds = 300,
                coding_status = 'completed', coding_time_taken_seconds = 600,
                interview_status = 'completed', interview_id = ?, interview_time_taken_seconds = 400
            WHERE user_id = ? AND attempt_id = ?
        """, (apt_id, iv_id, self.user_a_id, att_id))
        self.conn.commit()

        # Fetch detailed performance report
        report = get_assessment_attempt_report(attempt_id=att_id, current_user=self.user_a)

        self.assertEqual(_v(report, "attempt_id"), att_id)
        apt_data = _v(report, "aptitude")
        self.assertEqual(apt_data["score"], 80.0)
        self.assertEqual(apt_data["time_taken_seconds"], 300)
        iv_data = _v(report, "interview")
        self.assertEqual(iv_data["overall_score"], 85.0)

        # Efficiency metrics
        eff = _v(report, "efficiency")
        self.assertEqual(eff["total_time_taken_seconds"], 1300)
        self.assertGreater(eff["correct_answers_per_minute"], 0)
        self.assertTrue(len(eff["speed_vs_accuracy_archetype"]) > 0)
        self.assertIn("speed_vs_accuracy_archetype", eff)

        # Recommendations
        recs = _v(report, "recommendations")
        self.assertIn("recommended_difficulty", recs)
        self.assertIn("strongest_topics", recs)
        self.assertIn("next_steps", recs)
        self.assertIn("next_steps", recs)


if __name__ == "__main__":
    unittest.main()
