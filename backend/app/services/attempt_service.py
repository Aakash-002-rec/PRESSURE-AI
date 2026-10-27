import json
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from ..config import (
    APTITUDE_TIME_LIMIT_SECONDS,
    CODING_TIME_LIMIT_SECONDS,
    INTERVIEW_TIME_LIMIT_SECONDS,
    DEADLINE_GRACE_PERIOD_SECONDS
)

logger = logging.getLogger("pressure_ai.attempt_service")


def _get_utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _parse_ts(ts_str: Optional[str]) -> Optional[float]:
    if not ts_str:
        return None
    try:
        # Support formats: 2026-10-23 10:00:00 or ISO format
        clean_ts = str(ts_str).replace("T", " ")
        if "." in clean_ts:
            clean_ts = clean_ts.split(".")[0]
        dt = datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return None


def _calc_remaining_seconds(deadline_str: Optional[str], duration_seconds: int) -> int:
    if not deadline_str:
        return duration_seconds
    dl_epoch = _parse_ts(deadline_str)
    if dl_epoch is None:
        return duration_seconds
    now_epoch = datetime.now(timezone.utc).timestamp()
    rem = int(dl_epoch - now_epoch)
    return max(0, rem)


class AttemptService:
    @staticmethod
    def get_active_attempt(cursor, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves the currently active in-progress assessment attempt for the user,
        evaluates live deadlines, and handles timeouts automatically.
        """
        cursor.execute("""
            SELECT * FROM assessment_attempts
            WHERE user_id = ? AND status = 'in_progress'
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        attempt = dict(row)

        now_epoch = datetime.now(timezone.utc).timestamp()

        # Check Aptitude deadline timeout if in_progress
        if attempt.get("aptitude_status") == "in_progress" and attempt.get("aptitude_deadline"):
            dl_epoch = _parse_ts(attempt["aptitude_deadline"])
            if dl_epoch and now_epoch > (dl_epoch + DEADLINE_GRACE_PERIOD_SECONDS):
                # Auto-timeout Aptitude
                cursor.execute("""
                    UPDATE assessment_attempts
                    SET aptitude_status = 'completed',
                        aptitude_timeout = 1,
                        aptitude_completed_at = CURRENT_TIMESTAMP,
                        current_stage = 'coding'
                    WHERE id = ?
                """, (attempt["id"],))
                attempt["aptitude_status"] = "completed"
                attempt["aptitude_timeout"] = 1
                attempt["current_stage"] = "coding"

        # Check Coding deadline timeout if in_progress
        if attempt.get("coding_status") == "in_progress" and attempt.get("coding_deadline"):
            dl_epoch = _parse_ts(attempt["coding_deadline"])
            if dl_epoch and now_epoch > (dl_epoch + DEADLINE_GRACE_PERIOD_SECONDS):
                cursor.execute("""
                    UPDATE assessment_attempts
                    SET coding_status = 'completed',
                        coding_timeout = 1,
                        current_stage = 'interview'
                    WHERE id = ?
                """, (attempt["id"],))
                if attempt.get("coding_session_id"):
                    cursor.execute("""
                        UPDATE coding_sessions
                        SET status = 'completed',
                            is_timeout = 1,
                            completion_reason = 'timeout',
                            completed_at = CURRENT_TIMESTAMP
                        WHERE session_id = ?
                    """, (attempt["coding_session_id"],))
                attempt["coding_status"] = "completed"
                attempt["coding_timeout"] = 1
                attempt["current_stage"] = "interview"

        # Check Interview deadline timeout if in_progress
        if attempt.get("interview_status") == "in_progress" and attempt.get("interview_deadline"):
            dl_epoch = _parse_ts(attempt["interview_deadline"])
            if dl_epoch and now_epoch > (dl_epoch + DEADLINE_GRACE_PERIOD_SECONDS):
                cursor.execute("""
                    UPDATE assessment_attempts
                    SET interview_status = 'completed',
                        interview_timeout = 1,
                        status = 'completed',
                        completed_at = CURRENT_TIMESTAMP,
                        current_stage = 'completed'
                    WHERE id = ?
                """, (attempt["id"],))
                if attempt.get("interview_id"):
                    cursor.execute("""
                        UPDATE interviews
                        SET status = 'completed',
                            is_timeout = 1,
                            completion_reason = 'timeout',
                            completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (attempt["interview_id"],))
                attempt["interview_status"] = "completed"
                attempt["interview_timeout"] = 1
                attempt["status"] = "completed"
                attempt["current_stage"] = "completed"

        return AttemptService._enrich_attempt_record(attempt)

    @staticmethod
    def _enrich_attempt_record(att: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates live remaining seconds and formatted metadata."""
        apt_dur = att.get("aptitude_duration_seconds") or APTITUDE_TIME_LIMIT_SECONDS
        coding_dur = att.get("coding_duration_seconds") or CODING_TIME_LIMIT_SECONDS
        iv_dur = att.get("interview_duration_seconds") or INTERVIEW_TIME_LIMIT_SECONDS

        apt_rem = _calc_remaining_seconds(att.get("aptitude_deadline"), apt_dur) if att.get("aptitude_started_at") else apt_dur
        coding_rem = _calc_remaining_seconds(att.get("coding_deadline"), coding_dur) if att.get("coding_started_at") else coding_dur
        iv_rem = _calc_remaining_seconds(att.get("interview_deadline"), iv_dur) if att.get("interview_started_at") else iv_dur

        att["aptitude_remaining_seconds"] = apt_rem
        att["coding_remaining_seconds"] = coding_rem
        att["interview_remaining_seconds"] = iv_rem
        att["aptitude_duration_seconds"] = apt_dur
        att["coding_duration_seconds"] = coding_dur
        att["interview_duration_seconds"] = iv_dur
        att["aptitude_timeout"] = bool(att.get("aptitude_timeout"))
        att["coding_timeout"] = bool(att.get("coding_timeout"))
        att["interview_timeout"] = bool(att.get("interview_timeout"))
        att["attempt_number"] = att.get("attempt_number") or 1
        att["current_stage"] = att.get("current_stage") or "aptitude"

        return att

    @staticmethod
    def get_or_create_active_attempt(cursor, user_id: int) -> Dict[str, Any]:
        """
        Returns the existing active attempt or creates a fresh initial assessment attempt.
        Associates a dedicated 3-question Coding Session with this attempt.
        """
        active = AttemptService.get_active_attempt(cursor, user_id)
        if active:
            # Verify it has an active coding session
            if not active.get("coding_session_id"):
                from ..routers.coding_routes import _get_or_create_user_coding_session
                coding_sess = _get_or_create_user_coding_session(
                    cursor=cursor,
                    user_id=user_id,
                    attempt_id=active["attempt_id"],
                    force_new=False
                )
                cursor.execute("""
                    UPDATE assessment_attempts
                    SET coding_session_id = ?
                    WHERE id = ?
                """, (coding_sess["session_id"], active["id"]))
                active["coding_session_id"] = coding_sess["session_id"]
            return active

        # Compute next attempt number for this user
        cursor.execute("SELECT COUNT(*) FROM assessment_attempts WHERE user_id = ?", (user_id,))
        attempt_count = cursor.fetchone()[0]
        attempt_num = attempt_count + 1

        # Create fresh initial attempt
        new_att_id = f"att_{user_id}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
        from ..routers.coding_routes import _get_or_create_user_coding_session
        coding_sess = _get_or_create_user_coding_session(
            cursor=cursor,
            user_id=user_id,
            attempt_id=new_att_id,
            force_new=True
        )

        cursor.execute("""
            INSERT INTO assessment_attempts (
                attempt_id, user_id, status, coding_session_id,
                aptitude_status, coding_status, interview_status,
                attempt_number, current_stage,
                aptitude_duration_seconds, coding_duration_seconds, interview_duration_seconds
            ) VALUES (?, ?, 'in_progress', ?, 'not_started', 'not_started', 'not_started', ?, 'aptitude', ?, ?, ?)
        """, (
            new_att_id, user_id, coding_sess["session_id"],
            attempt_num,
            APTITUDE_TIME_LIMIT_SECONDS, CODING_TIME_LIMIT_SECONDS, INTERVIEW_TIME_LIMIT_SECONDS
        ))
        att_pk = cursor.lastrowid

        cursor.execute("SELECT * FROM assessment_attempts WHERE id = ?", (att_pk,))
        new_att = dict(cursor.fetchone())
        return AttemptService._enrich_attempt_record(new_att)

    @staticmethod
    def start_retest_attempt(cursor, user_id: int) -> Dict[str, Any]:
        """
        Explicitly starts a brand-new assessment attempt across all 3 modules.
        - Archives any existing in-progress attempts, coding sessions, or interviews.
        - Increments attempt_number.
        - Generates a fresh unique attempt_id.
        - Creates a fresh Coding Session with exactly 3 questions.
        - Resets Aptitude, Coding, and AI Interview to not_started with fresh timers.
        - Preserves all historical attempts, answers, and reports in the database.
        """
        now_ts = _get_utc_now_str()

        # 1. Archive prior in-progress attempts
        cursor.execute("""
            UPDATE assessment_attempts
            SET status = 'completed', completed_at = ?, completion_reason = COALESCE(completion_reason, 'archived_for_retest')
            WHERE user_id = ? AND status = 'in_progress'
        """, (now_ts, user_id))

        # 2. Archive prior in-progress coding sessions
        cursor.execute("""
            UPDATE coding_sessions
            SET status = 'completed', completed_at = ?, completion_reason = COALESCE(completion_reason, 'archived_for_retest')
            WHERE user_id = ? AND status = 'in_progress'
        """, (now_ts, user_id))

        # 3. Abandon prior in-progress interviews
        cursor.execute("""
            UPDATE interviews
            SET status = 'abandoned', completed_at = ?, completion_reason = 'archived_for_retest'
            WHERE user_id = ? AND status = 'in_progress'
        """, (now_ts, user_id))

        # Tag any unattached historical records with prior attempt tag so they don't leak
        cursor.execute("""
            UPDATE user_served_questions
            SET attempt_id = 'archived_prior'
            WHERE user_id = ? AND (attempt_id IS NULL OR attempt_id = '')
        """, (user_id,))
        cursor.execute("""
            UPDATE coding_attempts
            SET attempt_id = 'archived_prior'
            WHERE user_id = ? AND (attempt_id IS NULL OR attempt_id = '')
        """, (user_id,))

        # 4. Compute next attempt number
        cursor.execute("SELECT COUNT(*) FROM assessment_attempts WHERE user_id = ?", (user_id,))
        attempt_count = cursor.fetchone()[0]
        attempt_num = attempt_count + 1

        # 5. Generate new attempt ID
        new_att_id = f"att_{user_id}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"

        # 6. Initialize fresh 3-question Coding Session for this new attempt
        from ..routers.coding_routes import _get_or_create_user_coding_session
        new_coding_sess = _get_or_create_user_coding_session(
            cursor=cursor,
            user_id=user_id,
            attempt_id=new_att_id,
            force_new=True
        )

        # 7. Insert new attempt record
        cursor.execute("""
            INSERT INTO assessment_attempts (
                attempt_id, user_id, status, coding_session_id,
                aptitude_status, coding_status, interview_status,
                attempt_number, current_stage,
                aptitude_duration_seconds, coding_duration_seconds, interview_duration_seconds
            ) VALUES (?, ?, 'in_progress', ?, 'not_started', 'not_started', 'not_started', ?, 'aptitude', ?, ?, ?)
        """, (
            new_att_id, user_id, new_coding_sess["session_id"],
            attempt_num,
            APTITUDE_TIME_LIMIT_SECONDS, CODING_TIME_LIMIT_SECONDS, INTERVIEW_TIME_LIMIT_SECONDS
        ))
        att_pk = cursor.lastrowid

        cursor.execute("SELECT * FROM assessment_attempts WHERE id = ?", (att_pk,))
        new_row = dict(cursor.fetchone())
        logger.info(f"Initialized fresh assessment retest attempt: {new_att_id} (Attempt #{attempt_num}) for user {user_id}")
        return AttemptService._enrich_attempt_record(new_row)

    @staticmethod
    def get_attempt_history(cursor, user_id: int) -> List[Dict[str, Any]]:
        """
        Returns past assessment attempts for this user, ordered newest first,
        with calculated durations and scores.
        """
        cursor.execute("""
            SELECT * FROM assessment_attempts
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            enriched = AttemptService._enrich_attempt_record(dict(r))
            result.append(enriched)
        return result

    @staticmethod
    def check_stage_access(cursor, user_id: int, target_stage: str, attempt_id: Optional[str] = None):
        """
        Enforces strict assessment order:
        Login -> Aptitude -> Coding -> AI Mock Interview -> Final Performance Report.
        Raises HTTP 403 Forbidden with descriptive error if required preceding stages are incomplete.
        """
        if attempt_id:
            cursor.execute("SELECT * FROM assessment_attempts WHERE user_id = ? AND attempt_id = ?", (user_id, attempt_id))
        else:
            cursor.execute("""
                SELECT * FROM assessment_attempts
                WHERE user_id = ? AND status = 'in_progress'
                ORDER BY id DESC LIMIT 1
            """, (user_id,))
        att = cursor.fetchone()

        if not att:
            # If no attempt, initialize one
            att = AttemptService.get_or_create_active_attempt(cursor, user_id)

        apt_status = att["aptitude_status"]
        coding_status = att["coding_status"]
        interview_status = att["interview_status"]

        if target_stage == "coding":
            if apt_status != "completed":
                raise HTTPException(
                    status_code=403,
                    detail="Access Blocked: Aptitude Assessment must be completed before starting the Coding Assessment."
                )

        elif target_stage in ["interview", "setup"]:
            if apt_status != "completed":
                raise HTTPException(
                    status_code=403,
                    detail="Access Blocked: Aptitude Assessment must be completed before accessing the AI Mock Interview."
                )
            if coding_status != "completed":
                raise HTTPException(
                    status_code=403,
                    detail="Access Blocked: Coding Assessment must be completed before starting the AI Mock Interview."
                )

        elif target_stage in ["combined_report", "final_report"]:
            if interview_status != "completed":
                raise HTTPException(
                    status_code=403,
                    detail="Access Blocked: Complete all assessment modules (Aptitude, Coding, and AI Mock Interview) to unlock the Final Performance Report."
                )

    @staticmethod
    def start_aptitude_test(cursor, user_id: int, attempt_id: str, question_ids: List[int], duration_seconds: int = APTITUDE_TIME_LIMIT_SECONDS) -> Dict[str, Any]:
        """
        Starts the Aptitude timer on the server side when the user initiates the test.
        """
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        dl_dt = datetime.fromtimestamp(now_dt.timestamp() + duration_seconds, tz=timezone.utc)
        dl_str = dl_dt.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE assessment_attempts
            SET aptitude_status = 'in_progress',
                aptitude_started_at = COALESCE(aptitude_started_at, ?),
                aptitude_deadline = COALESCE(aptitude_deadline, ?),
                aptitude_duration_seconds = ?,
                aptitude_question_ids = ?,
                current_stage = 'aptitude'
            WHERE user_id = ? AND attempt_id = ?
        """, (now_str, dl_str, duration_seconds, json.dumps(question_ids), user_id, attempt_id))

        cursor.execute("SELECT * FROM assessment_attempts WHERE user_id = ? AND attempt_id = ?", (user_id, attempt_id))
        row = cursor.fetchone()
        return AttemptService._enrich_attempt_record(dict(row))

    @staticmethod
    def save_aptitude_progress(cursor, user_id: int, attempt_id: str, answers: Dict[Any, Any], elapsed_seconds: Optional[int] = None):
        """Saves candidate draft answers for seamless refresh/resume."""
        cursor.execute("""
            UPDATE assessment_attempts
            SET aptitude_answers_draft = ?,
                aptitude_time_taken_seconds = COALESCE(?, aptitude_time_taken_seconds)
            WHERE user_id = ? AND attempt_id = ?
        """, (json.dumps(answers), elapsed_seconds, user_id, attempt_id))

    @staticmethod
    def update_aptitude_status(cursor, user_id: int, attempt_id: str, aptitude_attempt_id: int, status: str = "completed", time_taken: int = 0, is_timeout: bool = False):
        now_str = _get_utc_now_str()
        cursor.execute("""
            UPDATE assessment_attempts
            SET aptitude_attempt_id = ?,
                aptitude_status = ?,
                aptitude_completed_at = ?,
                aptitude_time_taken_seconds = ?,
                aptitude_timeout = ?,
                current_stage = 'coding'
            WHERE user_id = ? AND attempt_id = ?
        """, (aptitude_attempt_id, status, now_str, time_taken, 1 if is_timeout else 0, user_id, attempt_id))

    @staticmethod
    def start_coding_session(cursor, user_id: int, attempt_id: str, duration_seconds: int = CODING_TIME_LIMIT_SECONDS) -> Dict[str, Any]:
        """
        Starts the Coding timer on server side when candidate accesses Coding Assessment.
        """
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        dl_dt = datetime.fromtimestamp(now_dt.timestamp() + duration_seconds, tz=timezone.utc)
        dl_str = dl_dt.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE assessment_attempts
            SET coding_status = CASE WHEN coding_status = 'not_started' THEN 'in_progress' ELSE coding_status END,
                coding_started_at = COALESCE(coding_started_at, ?),
                coding_deadline = COALESCE(coding_deadline, ?),
                coding_duration_seconds = ?,
                current_stage = 'coding'
            WHERE user_id = ? AND attempt_id = ?
        """, (now_str, dl_str, duration_seconds, user_id, attempt_id))

        # Also update coding_sessions table
        cursor.execute("""
            UPDATE coding_sessions
            SET started_at = COALESCE(started_at, ?),
                deadline = COALESCE(deadline, ?),
                duration_seconds = ?
            WHERE user_id = ? AND attempt_id = ?
        """, (now_str, dl_str, duration_seconds, user_id, attempt_id))

        cursor.execute("SELECT * FROM assessment_attempts WHERE user_id = ? AND attempt_id = ?", (user_id, attempt_id))
        row = cursor.fetchone()
        return AttemptService._enrich_attempt_record(dict(row))

    @staticmethod
    def update_coding_status(cursor, user_id: int, attempt_id: str, status: str = "completed", time_taken: int = 0, is_timeout: bool = False):
        cursor.execute("""
            UPDATE assessment_attempts
            SET coding_status = ?,
                coding_timeout = ?,
                coding_time_taken_seconds = CASE WHEN ? > 0 THEN ? ELSE coding_time_taken_seconds END,
                current_stage = 'interview'
            WHERE user_id = ? AND attempt_id = ?
        """, (status, 1 if is_timeout else 0, time_taken, time_taken, user_id, attempt_id))

    @staticmethod
    def start_interview_session(cursor, user_id: int, attempt_id: str, interview_id: int, duration_seconds: int = INTERVIEW_TIME_LIMIT_SECONDS):
        now_dt = datetime.now(timezone.utc)
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        dl_dt = datetime.fromtimestamp(now_dt.timestamp() + duration_seconds, tz=timezone.utc)
        dl_str = dl_dt.strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE assessment_attempts
            SET interview_id = ?,
                interview_status = 'in_progress',
                interview_started_at = COALESCE(interview_started_at, ?),
                interview_deadline = COALESCE(interview_deadline, ?),
                interview_duration_seconds = ?,
                current_stage = 'interview'
            WHERE user_id = ? AND attempt_id = ?
        """, (interview_id, now_str, dl_str, duration_seconds, user_id, attempt_id))

        cursor.execute("""
            UPDATE interviews
            SET attempt_id = ?,
                deadline = COALESCE(deadline, ?),
                duration_seconds = ?
            WHERE id = ?
        """, (attempt_id, dl_str, duration_seconds, interview_id))

    @staticmethod
    def update_interview_status(cursor, user_id: int, attempt_id: str, interview_id: int, status: str = "completed", time_taken: int = 0, is_timeout: bool = False):
        now_str = _get_utc_now_str()
        cursor.execute("""
            UPDATE assessment_attempts
            SET interview_id = ?,
                interview_status = ?,
                interview_timeout = ?,
                interview_time_taken_seconds = CASE WHEN ? > 0 THEN ? ELSE interview_time_taken_seconds END,
                current_stage = 'completed'
            WHERE user_id = ? AND attempt_id = ?
        """, (interview_id, status, 1 if is_timeout else 0, time_taken, time_taken, user_id, attempt_id))

        if status == "completed":
            # Check if all modules in this attempt are completed
            cursor.execute("""
                SELECT aptitude_status, coding_status, interview_status FROM assessment_attempts
                WHERE user_id = ? AND attempt_id = ?
            """, (user_id, attempt_id))
            r = cursor.fetchone()
            if r and r["aptitude_status"] == "completed" and r["coding_status"] == "completed":
                cursor.execute("""
                    UPDATE assessment_attempts
                    SET status = 'completed', completed_at = ?, current_stage = 'completed'
                    WHERE user_id = ? AND attempt_id = ?
                """, (now_str, user_id, attempt_id))
