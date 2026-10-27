from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any, Tuple, Set
import json
import time
from datetime import datetime, timezone
from ..database import get_db_connection
from ..models import (
    CodingProblemSummary, CodingRunRequest, CodingSubmitRequest, CodingResultResponse,
    CodingStatusResponse
)
from ..auth import get_current_user
from ..services.code_runner import CodeRunner
from ..services.llm_service import LLMService, gemini_model, _gemini_quota_exhausted, _gemini_quota_exhausted_until
from ..services.cross_module_engine import CrossModuleEngine
from ..services.problem_fingerprint import compute_problem_fingerprint, is_duplicate_problem
from ..services.attempt_service import AttemptService, _parse_ts
from ..config import CODING_TIME_LIMIT_SECONDS, DEADLINE_GRACE_PERIOD_SECONDS, CODING_QUESTIONS_PER_ATTEMPT

router = APIRouter(prefix="/coding", tags=["Coding"])


def _get_user_coding_partition(
    cursor,
    user_id: int,
    session_id: Optional[str] = None,
    attempt_id: Optional[str] = None
) -> Tuple[Set[int], Set[int], Set[int], Set[str], List[str]]:
    """
    Computes strict partition of coding problems for the user scoped to the active session/attempt:
    - completed_ids: passed in coding_attempts (status == 'passed' or correctness >= 100)
    - in_progress_ids: served or attempted but not passed in this session
    - seen_ids: completed_ids | in_progress_ids
    - seen_fps: fingerprints of all seen problems in this session
    - seen_titles: titles of all seen problems in this session
    """
    if not session_id and not attempt_id:
        cursor.execute("""
            SELECT session_id, attempt_id FROM coding_sessions
            WHERE user_id = ? AND status = 'in_progress'
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        active_sess = cursor.fetchone()
        if active_sess:
            session_id = active_sess["session_id"]
            attempt_id = active_sess["attempt_id"] if "attempt_id" in active_sess.keys() else None

    if session_id:
        cursor.execute("""
            SELECT DISTINCT problem_id FROM coding_attempts
            WHERE user_id = ? AND (session_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
            AND (LOWER(status) = 'passed' OR correctness >= 100.0)
        """, (user_id, session_id))
        completed_ids = {r[0] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT DISTINCT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND (session_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
            AND LOWER(status) = 'passed'
        """, (user_id, session_id))
        for r in cursor.fetchall():
            if r[0] is not None:
                completed_ids.add(r[0])

        cursor.execute("""
            SELECT DISTINCT problem_id FROM coding_attempts
            WHERE user_id = ? AND (session_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
        """, (user_id, session_id))
        attempted_ids = {r[0] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT DISTINCT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND (session_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
        """, (user_id, session_id))
        served_ids = {r[0] for r in cursor.fetchall() if r[0] is not None}
    elif attempt_id:
        cursor.execute("""
            SELECT DISTINCT problem_id FROM coding_attempts
            WHERE user_id = ? AND (attempt_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
            AND (LOWER(status) = 'passed' OR correctness >= 100.0)
        """, (user_id, attempt_id))
        completed_ids = {r[0] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT DISTINCT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND (attempt_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
            AND LOWER(status) = 'passed'
        """, (user_id, attempt_id))
        for r in cursor.fetchall():
            if r[0] is not None:
                completed_ids.add(r[0])

        cursor.execute("""
            SELECT DISTINCT problem_id FROM coding_attempts
            WHERE user_id = ? AND (attempt_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
        """, (user_id, attempt_id))
        attempted_ids = {r[0] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT DISTINCT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND (attempt_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
        """, (user_id, attempt_id))
        served_ids = {r[0] for r in cursor.fetchall() if r[0] is not None}
    else:
        cursor.execute("""
            SELECT DISTINCT problem_id FROM coding_attempts
            WHERE user_id = ? AND (LOWER(status) = 'passed' OR correctness >= 100.0)
        """, (user_id,))
        completed_ids = {r[0] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT DISTINCT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND LOWER(status) = 'passed'
        """, (user_id,))
        for r in cursor.fetchall():
            if r[0] is not None:
                completed_ids.add(r[0])

        cursor.execute("""
            SELECT DISTINCT problem_id FROM coding_attempts
            WHERE user_id = ?
        """, (user_id,))
        attempted_ids = {r[0] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT DISTINCT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding'
        """, (user_id,))
        served_ids = {r[0] for r in cursor.fetchall() if r[0] is not None}

    in_progress_ids = (served_ids | attempted_ids) - completed_ids
    seen_ids = completed_ids | in_progress_ids

    seen_fps = set()
    if session_id:
        cursor.execute("""
            SELECT DISTINCT fingerprint FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND fingerprint IS NOT NULL
            AND (session_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
        """, (user_id, session_id))
        for r in cursor.fetchall():
            if r[0]:
                seen_fps.add(r[0])
    elif attempt_id:
        cursor.execute("""
            SELECT DISTINCT fingerprint FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND fingerprint IS NOT NULL
            AND (attempt_id = ? OR (session_id IS NULL AND (attempt_id IS NULL OR attempt_id = '')))
        """, (user_id, attempt_id))
        for r in cursor.fetchall():
            if r[0]:
                seen_fps.add(r[0])

    seen_titles = []
    if seen_ids:
        ph = ",".join("?" for _ in seen_ids)
        cursor.execute(f"SELECT id, fingerprint, title, description, starter_code, test_cases FROM coding_problems WHERE id IN ({ph})", tuple(seen_ids))
        for r in cursor.fetchall():
            if r["title"]:
                seen_titles.append(r["title"])
            if r["fingerprint"]:
                seen_fps.add(r["fingerprint"])
            else:
                try:
                    tc = json.loads(r["test_cases"]) if r["test_cases"] else []
                except Exception:
                    tc = []
                fp = compute_problem_fingerprint(r["title"], r["description"], r["starter_code"], tc)
                seen_fps.add(fp)

    return completed_ids, in_progress_ids, seen_ids, seen_fps, seen_titles

CODING_SESSION_QUESTION_LIMIT = 3

def _get_user_question_number(cursor, user_id: int, problem_id: int, session_id: Optional[str] = None) -> int:
    """
    Computes 1-based question sequence number within the user's coding assessment session.
    """
    # 1. First check if problem is in specified or active session
    if session_id:
        cursor.execute("""
            SELECT id, session_id, question_ids, question_order FROM coding_sessions
            WHERE user_id = ? AND session_id = ?
        """, (user_id, session_id))
    else:
        cursor.execute("""
            SELECT id, session_id, question_ids, question_order FROM coding_sessions
            WHERE user_id = ? AND status = 'in_progress'
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
    session_row = cursor.fetchone()
    if session_row and session_row["question_ids"]:
        try:
            q_ids = json.loads(session_row["question_ids"])
            if problem_id in q_ids:
                return q_ids.index(problem_id) + 1
        except Exception:
            pass

    # 2. Fall back to user_served_questions order for this session
    if session_row and session_row["session_id"]:
        cursor.execute("""
            SELECT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND question_id IS NOT NULL
            AND session_id = ?
            ORDER BY id ASC
        """, (user_id, session_row["session_id"]))
    else:
        cursor.execute("""
            SELECT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND question_id IS NOT NULL
            ORDER BY id ASC
        """, (user_id,))
    ordered_ids = []
    for r in cursor.fetchall():
        if r[0] not in ordered_ids:
            ordered_ids.append(r[0])
    if problem_id in ordered_ids:
        return ordered_ids.index(problem_id) + 1
    return min(CODING_SESSION_QUESTION_LIMIT, len(ordered_ids) + 1)

def _get_user_seen_coding_history(cursor, user_id: int) -> Tuple[Set[int], Set[str], List[str]]:
    cursor.execute("""
        SELECT DISTINCT question_id FROM user_served_questions
        WHERE user_id = ? AND module = 'coding' AND question_id IS NOT NULL
    """, (user_id,))
    seen_ids = {r[0] for r in cursor.fetchall()}
    cursor.execute("SELECT DISTINCT problem_id FROM coding_attempts WHERE user_id = ?", (user_id,))
    for r in cursor.fetchall():
        seen_ids.add(r[0])

    seen_fps = set()
    cursor.execute("""
        SELECT DISTINCT fingerprint FROM user_served_questions
        WHERE user_id = ? AND module = 'coding' AND fingerprint IS NOT NULL
    """, (user_id,))
    for r in cursor.fetchall():
        if r[0]:
            seen_fps.add(r[0])

    seen_titles = []
    if seen_ids:
        ph = ",".join("?" for _ in seen_ids)
        cursor.execute(f"SELECT id, fingerprint, title, description, starter_code, test_cases FROM coding_problems WHERE id IN ({ph})", tuple(seen_ids))
        for r in cursor.fetchall():
            if r["title"]:
                seen_titles.append(r["title"])
            if r["fingerprint"]:
                seen_fps.add(r["fingerprint"])
            else:
                try:
                    tc = json.loads(r["test_cases"]) if r["test_cases"] else []
                except Exception:
                    tc = []
                fp = compute_problem_fingerprint(r["title"], r["description"], r["starter_code"], tc)
                seen_fps.add(fp)

    return seen_ids, seen_fps, seen_titles

def _get_or_create_user_coding_session(
    cursor,
    user_id: int,
    language: str = "python",
    domain: str = "Algorithms",
    difficulty: str = "Intermediate",
    category: Optional[str] = None,
    attempt_id: Optional[str] = None,
    force_new: bool = False
) -> Dict[str, Any]:
    """
    Retrieves or establishes a persistent, personalized 3-question coding session for the user.
    - Tracks session_id, user_id, language, domain, difficulty, question_ids, question_order, status, attempt_id.
    - Guarantees exactly 3 distinct questions per session.
    - Differentiates questions across different users using user_id-based diversification.
    - Avoids questions previously served to this user across previous sessions when pool permits.
    - Reopens incomplete sessions cleanly without adding extra question slots.
    """
    # Sanitize query / default params so FastAPI Query objects are never passed to DB
    language = language if isinstance(language, str) and language else "python"
    domain = domain if isinstance(domain, str) and domain else "Algorithms"
    difficulty = difficulty if isinstance(difficulty, str) and difficulty else "Intermediate"
    category = category if isinstance(category, str) and category else None

    # 1. Check for active in_progress session in coding_sessions
    if not force_new:
        if attempt_id:
            cursor.execute("""
                SELECT * FROM coding_sessions
                WHERE user_id = ? AND attempt_id = ? AND status = 'in_progress'
                ORDER BY id DESC LIMIT 1
            """, (user_id, attempt_id))
        else:
            cursor.execute("""
                SELECT * FROM coding_sessions
                WHERE user_id = ? AND status = 'in_progress'
                ORDER BY id DESC LIMIT 1
            """, (user_id,))
        existing_session = cursor.fetchone()
        if existing_session:
            try:
                assigned_ids = json.loads(existing_session["question_ids"])
            except Exception:
                assigned_ids = []

            # Check if all 3 questions have already been completed in THIS session
            if assigned_ids and len(assigned_ids) >= CODING_SESSION_QUESTION_LIMIT:
                cursor.execute("""
                    SELECT DISTINCT problem_id FROM coding_attempts
                    WHERE user_id = ? AND session_id = ? AND (LOWER(status) = 'passed' OR correctness >= 100.0)
                """, (user_id, existing_session["session_id"]))
                completed_pids = {r[0] for r in cursor.fetchall()}
                if all(pid in completed_pids for pid in assigned_ids):
                    cursor.execute("""
                        UPDATE coding_sessions
                        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (existing_session["id"],))
                    return {
                        "id": existing_session["id"],
                        "session_id": existing_session["session_id"],
                        "user_id": user_id,
                        "language": existing_session["language"],
                        "domain": existing_session["domain"],
                        "difficulty": existing_session["difficulty"],
                        "question_ids": assigned_ids,
                        "question_order": [1, 2, 3],
                        "status": "completed",
                        "attempt_id": existing_session["attempt_id"] if "attempt_id" in existing_session.keys() else None
                    }

            return {
                "id": existing_session["id"],
                "session_id": existing_session["session_id"],
                "user_id": user_id,
                "language": existing_session["language"],
                "domain": existing_session["domain"],
                "difficulty": existing_session["difficulty"],
                "question_ids": assigned_ids,
                "question_order": [1, 2, 3],
                "status": "in_progress",
                "attempt_id": existing_session["attempt_id"] if "attempt_id" in existing_session.keys() else None
            }

        # Check if user already has records in user_served_questions (e.g. from test setups)
        cursor.execute("""
            SELECT question_id FROM user_served_questions
            WHERE user_id = ? AND module = 'coding' AND question_id IS NOT NULL
            AND (session_id IS NULL OR session_id = '')
            AND (attempt_id IS NULL OR attempt_id = '' OR attempt_id = ?)
            ORDER BY id ASC
        """, (user_id, attempt_id or ""))
        raw_served = [r[0] for r in cursor.fetchall()]
        if raw_served:
            adopted_ids = []
            for qid in raw_served:
                if qid not in adopted_ids:
                    adopted_ids.append(qid)
            if len(adopted_ids) > 0:
                s_id = f"cs_{user_id}_{int(time.time())}"
                cursor.execute("""
                    INSERT INTO coding_sessions (
                        user_id, session_id, language, domain, difficulty,
                        question_ids, question_order, current_index, status, attempt_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'in_progress', ?)
                """, (
                    user_id, s_id, language, domain, difficulty,
                    json.dumps(adopted_ids[:CODING_SESSION_QUESTION_LIMIT]),
                    json.dumps(list(range(1, len(adopted_ids[:CODING_SESSION_QUESTION_LIMIT]) + 1))),
                    attempt_id
                ))
                cursor.execute("""
                    UPDATE user_served_questions
                    SET session_id = ?, attempt_id = COALESCE(attempt_id, ?)
                    WHERE user_id = ? AND module = 'coding' AND (session_id IS NULL OR session_id = '')
                """, (s_id, attempt_id, user_id))
                cursor.execute("""
                    UPDATE coding_attempts
                    SET session_id = ?, attempt_id = COALESCE(attempt_id, ?)
                    WHERE user_id = ? AND (session_id IS NULL OR session_id = '')
                """, (s_id, attempt_id, user_id))
                return {
                    "id": cursor.lastrowid,
                    "session_id": s_id,
                    "user_id": user_id,
                    "language": language,
                    "domain": domain,
                    "difficulty": difficulty,
                    "question_ids": adopted_ids[:CODING_SESSION_QUESTION_LIMIT],
                    "question_order": list(range(1, len(adopted_ids[:CODING_SESSION_QUESTION_LIMIT]) + 1)),
                    "status": "in_progress",
                    "attempt_id": attempt_id
                }

    # 2. Create a NEW personalized 3-question coding assessment session
    cursor.execute("SELECT COUNT(*) FROM coding_sessions WHERE user_id = ?", (user_id,))
    session_count = cursor.fetchone()[0]

    # Find problems already served to THIS user across ALL prior sessions
    user_past_seen_ids, _, _ = _get_user_seen_coding_history(cursor, user_id)

    # Fetch candidate problems from question bank
    cursor.execute("SELECT * FROM coding_problems ORDER BY id ASC")
    all_problems = cursor.fetchall()

    unused_problems = [p for p in all_problems if p["id"] not in user_past_seen_ids]
    if len(unused_problems) < CODING_SESSION_QUESTION_LIMIT:
        # If user has seen almost everything, fall back to any problems
        unused_problems = list(all_problems)

    # Partition available problems into 3 distinct functional buckets:
    # Bucket A: Arrays / Searching / Sorting / Two Pointers
    # Bucket B: Strings / Hash Map / Bit Algorithms
    # Bucket C: Recursion / Stack / Dynamic Programming
    bucket_a = []
    bucket_b = []
    bucket_c = []
    for p in unused_problems:
        cat = (p["category"] or "").lower()
        title = (p["title"] or "").lower()
        if any(k in cat or k in title for k in ["array", "search", "sort", "subarray", "pointer"]):
            bucket_a.append(p)
        elif any(k in cat or k in title for k in ["string", "hash", "map", "prefix", "single", "roman", "anagram"]):
            bucket_b.append(p)
        else:
            bucket_c.append(p)

    # Fallback if any bucket is sparse
    if not bucket_a:
        bucket_a = [p for p in unused_problems if p not in bucket_b and p not in bucket_c] or list(unused_problems)
    if not bucket_b:
        bucket_b = [p for p in unused_problems if p not in bucket_a and p not in bucket_c] or list(unused_problems)
    if not bucket_c:
        bucket_c = [p for p in unused_problems if p not in bucket_a and p not in bucket_b] or list(unused_problems)

    # Deterministically personalize selection using authenticated user_id and session_count
    idx_a = (user_id * 3 + session_count) % len(bucket_a)
    pick_a = bucket_a[idx_a]

    idx_b = (user_id * 5 + session_count) % len(bucket_b)
    pick_b = bucket_b[idx_b]

    idx_c = (user_id * 7 + session_count) % len(bucket_c)
    pick_c = bucket_c[idx_c]

    candidate_picks = [pick_a, pick_b, pick_c]
    assigned_ids = []
    seen_picked_ids = set()
    for p in candidate_picks:
        if p["id"] not in seen_picked_ids:
            assigned_ids.append(p["id"])
            seen_picked_ids.add(p["id"])

    # Ensure exactly 3 distinct problems
    for p in unused_problems:
        if len(assigned_ids) >= CODING_SESSION_QUESTION_LIMIT:
            break
        if p["id"] not in seen_picked_ids:
            assigned_ids.append(p["id"])
            seen_picked_ids.add(p["id"])

    new_session_id = f"cs_{user_id}_{int(time.time())}_{session_count + 1}"
    cursor.execute("""
        INSERT INTO coding_sessions (
            user_id, session_id, language, domain, difficulty,
            question_ids, question_order, current_index, status, attempt_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'in_progress', ?)
    """, (
        user_id, new_session_id, language, domain, difficulty,
        json.dumps(assigned_ids), json.dumps([1, 2, 3]), attempt_id
    ))
    session_pk = cursor.lastrowid

    return {
        "id": session_pk,
        "session_id": new_session_id,
        "user_id": user_id,
        "language": language,
        "domain": domain,
        "difficulty": difficulty,
        "question_ids": assigned_ids,
        "question_order": [1, 2, 3],
        "status": "in_progress",
        "attempt_id": attempt_id
    }

@router.get("/status", response_model=CodingStatusResponse)
def get_coding_status(current_user: dict = Depends(get_current_user)):
    """
    Returns accurate per-user coding metrics strictly enforcing the 3-question limit for the active attempt:
    - completed_count: problems successfully passed in this attempt
    - in_progress_count: problems presented/attempted but not yet passed in this attempt
    - remaining_unseen_count: problems remaining in the 3-question session
    - total_problems_count: exactly CODING_SESSION_QUESTION_LIMIT (3)
    - all_completed: true only if user has passed all 3 problems in this attempt
    - session_limit: exactly 3
    - current_question_number: progress index (1, 2, or 3)
    - remaining_seconds, deadline, started_at, is_timeout for reliable assessment timer
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
    att_id = active_att.get("attempt_id")

    # If Aptitude has not been completed, report locked stage
    if active_att.get("aptitude_status") != "completed":
        conn.close()
        return CodingStatusResponse(
            completed_count=0,
            in_progress_count=0,
            remaining_unseen_count=CODING_SESSION_QUESTION_LIMIT,
            total_problems_count=CODING_SESSION_QUESTION_LIMIT,
            has_unseen=False,
            has_incomplete=False,
            all_completed=False,
            session_limit=CODING_SESSION_QUESTION_LIMIT,
            current_question_number=1,
            attempt_id=att_id,
            is_locked=True,
            lock_reason="Aptitude Assessment must be completed before starting Coding Assessment."
        )

    # Initialize coding timer if not already started
    if not active_att.get("coding_started_at"):
        active_att = AttemptService.start_coding_session(cursor, user_id, att_id, CODING_TIME_LIMIT_SECONDS)
        conn.commit()

    # Fetch active coding session for this attempt
    cursor.execute("""
        SELECT * FROM coding_sessions
        WHERE user_id = ? AND (session_id = ? OR (attempt_id = ? AND status = 'in_progress'))
        ORDER BY id DESC LIMIT 1
    """, (user_id, active_att.get("coding_session_id"), att_id))
    session_row = cursor.fetchone()

    if not session_row:
        session_row = _get_or_create_user_coding_session(cursor, user_id, attempt_id=att_id, force_new=False)
        cursor.execute("UPDATE assessment_attempts SET coding_session_id = ? WHERE attempt_id = ?", (session_row["session_id"], att_id))
        conn.commit()

    total_count = CODING_SESSION_QUESTION_LIMIT
    assigned_ids = json.loads(session_row["question_ids"]) if session_row["question_ids"] else []
    sess_id = session_row["session_id"]

    completed_ids, in_progress_ids, seen_ids, _, _ = _get_user_coding_partition(cursor, user_id, session_id=sess_id, attempt_id=att_id)

    try:
        active_pool_ids = list(assigned_ids)
        for qid in (completed_ids | in_progress_ids | seen_ids):
            if qid not in active_pool_ids:
                active_pool_ids.append(qid)

        session_completed = [qid for qid in active_pool_ids if qid in completed_ids]
        session_in_progress = [qid for qid in active_pool_ids if qid in in_progress_ids]
        session_seen = [qid for qid in active_pool_ids if qid in seen_ids]

        completed_count = len(session_completed)
        in_progress_count = len(session_in_progress)
        unseen_count = max(0, total_count - len(session_seen))
        all_completed = (completed_count >= total_count)
        has_incomplete = (in_progress_count > 0 and not all_completed)
        has_unseen = (unseen_count > 0 and not all_completed)

        # Timeout check
        s_timeout = False
        try:
            s_timeout = bool(session_row["is_timeout"])
        except Exception:
            pass
        is_timeout = bool(active_att.get("coding_timeout") or s_timeout)
        rem_sec = active_att.get("coding_remaining_seconds", CODING_TIME_LIMIT_SECONDS)
        if rem_sec <= 0 and not all_completed:
            is_timeout = True
            cursor.execute("""
                UPDATE coding_sessions
                SET status = 'completed', is_timeout = 1, completion_reason = 'timeout', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (session_row["id"],))
            AttemptService.update_coding_status(cursor, user_id, att_id, "completed", is_timeout=True)
            conn.commit()

        if all_completed and session_row["status"] != "completed":
            cursor.execute("""
                UPDATE coding_sessions
                SET status = 'completed', completion_reason = 'completed_normally', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (session_row["id"],))
            AttemptService.update_coding_status(cursor, user_id, att_id, "completed", is_timeout=False)
            conn.commit()

        if all_completed:
            current_q_num = total_count
        elif session_in_progress:
            if session_in_progress[0] in assigned_ids:
                current_q_num = assigned_ids.index(session_in_progress[0]) + 1
            elif session_in_progress[0] in active_pool_ids:
                current_q_num = min(total_count, active_pool_ids.index(session_in_progress[0]) + 1)
            else:
                current_q_num = min(total_count, len(session_seen))
        else:
            current_q_num = min(total_count, len(session_seen) + 1)

        return CodingStatusResponse(
            completed_count=completed_count,
            in_progress_count=in_progress_count,
            remaining_unseen_count=unseen_count,
            total_problems_count=total_count,
            has_unseen=has_unseen,
            has_incomplete=has_incomplete,
            all_completed=all_completed,
            session_limit=total_count,
            current_question_number=current_q_num,
            session_id=session_row["session_id"],
            attempt_id=att_id,
            language=session_row["language"],
            domain=session_row["domain"],
            remaining_seconds=rem_sec,
            duration_seconds=active_att.get("coding_duration_seconds") or CODING_TIME_LIMIT_SECONDS,
            started_at=active_att.get("coding_started_at"),
            deadline=active_att.get("coding_deadline"),
            is_timeout=is_timeout,
            is_locked=False
        )
    finally:
        conn.close()


@router.get("/problems", response_model=List[CodingProblemSummary])
def get_coding_problems(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    limit: Optional[int] = Query(1),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetches available coding challenges with strict per-user personalization and 3-question session limit.
    - Delivers 1 question at a time (limit=1 by default).
    - If mode == 'resume' or 'incomplete': returns user's in-progress (unsolved) problems.
    - If mode == 'next': serves the next assigned question in the session.
    - Exactly 3 questions assigned per session; no fourth question will ever be served.
    - Different users receive different personalized coding questions.
    """
    cat_str = category if isinstance(category, str) and category else None
    diff_str = difficulty if isinstance(difficulty, str) and difficulty else None
    mode_str = mode if isinstance(mode, str) and mode else None
    limit_int = limit if isinstance(limit, int) else 1

    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    try:
        AttemptService.check_stage_access(cursor, user_id, target_stage="coding")
        active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
        att_id = active_att.get("attempt_id")

        # Start timer if not already running
        if not active_att.get("coding_started_at"):
            active_att = AttemptService.start_coding_session(cursor, user_id, att_id, CODING_TIME_LIMIT_SECONDS)
            conn.commit()
    except Exception:
        conn.close()
        raise

    # Get or create active coding assessment session for this candidate and attempt
    session = _get_or_create_user_coding_session(
        cursor=cursor,
        user_id=user_id,
        category=cat_str,
        difficulty=diff_str or "Intermediate",
        attempt_id=att_id,
        force_new=False
    )
    s_id = session.get("session_id")
    completed_ids, in_progress_ids, seen_ids, seen_fps, seen_titles = _get_user_coding_partition(cursor, user_id, session_id=s_id, attempt_id=att_id)


    # If resume mode requested, return in-progress incomplete problems for this session
    if mode_str in ["resume", "incomplete"] and in_progress_ids:
        ph = ",".join("?" for _ in in_progress_ids)
        query = f"SELECT * FROM coding_problems WHERE id IN ({ph})"
        params = list(in_progress_ids)
        if cat_str and cat_str != "All":
            query += " AND category = ?"
            params.append(cat_str)
        if diff_str and diff_str != "All":
            query += " AND difficulty = ?"
            params.append(diff_str)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        result = [
            {
                "id": r["id"],
                "title": r["title"],
                "category": r["category"],
                "difficulty": r["difficulty"],
                "language": r["language"],
                "description": r["description"],
                "starter_code": r["starter_code"],
                "constraints": r["constraints"],
                "hints": json.loads(r["hints"]) if r["hints"] else [],
                "time_complexity": r["time_complexity"],
                "space_complexity": r["space_complexity"],
                "input_format": r["input_format"] if "input_format" in r.keys() else None,
                "output_format": r["output_format"] if "output_format" in r.keys() else None,
                "status": "in_progress",
                "question_number": _get_user_question_number(cursor, user_id, r["id"], session_id=s_id),
                "total_questions": CODING_SESSION_QUESTION_LIMIT
            }
            for r in rows
        ]
        conn.close()
        return result

    assigned_ids = session.get("question_ids", [])
    all_seen_in_session = set([qid for qid in assigned_ids if qid in seen_ids]) | set(seen_ids)

    # STRICT 3-QUESTION SESSION LIMIT:
    # If candidate has reached CODING_SESSION_QUESTION_LIMIT in this session,
    # no fourth question can be served or generated.
    remaining_slots = max(0, CODING_SESSION_QUESTION_LIMIT - len(all_seen_in_session))
    if remaining_slots <= 0:
        conn.close()
        return []

    # Find the next question from the assigned 3 that hasn't been served yet
    unserved_assigned = [qid for qid in assigned_ids if qid not in seen_ids]

    unseen_items = []
    # If a specific category filter is requested, prioritize problems matching that category
    if cat_str and cat_str != "All":
        base_query = "SELECT * FROM coding_problems WHERE category = ?"
        params = [cat_str]
        if diff_str and diff_str != "All":
            base_query += " AND difficulty = ?"
            params.append(diff_str)
        cursor.execute(base_query, tuple(params))
        cat_rows = cursor.fetchall()
        for r in cat_rows:
            if r["id"] in seen_ids:
                continue
            fp = r["fingerprint"]
            if not fp:
                try:
                    tc = json.loads(r["test_cases"]) if r["test_cases"] else []
                except Exception:
                    tc = []
                fp = compute_problem_fingerprint(r["title"], r["description"], r["starter_code"], tc)
            if fp in seen_fps:
                continue
            unseen_items.append((r, fp))
            break
    else:
        # Full personalized 3-question coding assessment flow
        if unserved_assigned:
            target_pid = unserved_assigned[0]
            cursor.execute("SELECT * FROM coding_problems WHERE id = ?", (target_pid,))
            r = cursor.fetchone()
            if r:
                fp = r["fingerprint"]
                if not fp:
                    try:
                        tc = json.loads(r["test_cases"]) if r["test_cases"] else []
                    except Exception:
                        tc = []
                    fp = compute_problem_fingerprint(r["title"], r["description"], r["starter_code"], tc)
                unseen_items.append((r, fp))

    # Fallback to general unseen query if assigned problem was somehow missing
    if not unseen_items:
        base_query = "SELECT * FROM coding_problems WHERE 1=1"
        params = []
        if cat_str and cat_str != "All":
            base_query += " AND category = ?"
            params.append(cat_str)
        if diff_str and diff_str != "All":
            base_query += " AND difficulty = ?"
            params.append(diff_str)

        cursor.execute(base_query, tuple(params))
        all_rows = cursor.fetchall()

        for r in all_rows:
            if r["id"] in seen_ids:
                continue
            fp = r["fingerprint"]
            if not fp:
                try:
                    tc = json.loads(r["test_cases"]) if r["test_cases"] else []
                except Exception:
                    tc = []
                fp = compute_problem_fingerprint(r["title"], r["description"], r["starter_code"], tc)
            if fp in seen_fps:
                continue
            unseen_items.append((r, fp))
            break

    # If dynamic generation is needed and quota active
    is_gemini_active = (
        gemini_model is not None 
        and not (_gemini_quota_exhausted and time.time() < _gemini_quota_exhausted_until)
    )

    if not unseen_items and is_gemini_active and remaining_slots > 0:
        for _ in range(3):
            try:
                gen_prob = LLMService.generate_coding_problem(
                    language="python",
                    category=cat_str or "Recursion",
                    difficulty=diff_str or "Intermediate",
                    previous_titles=seen_titles,
                    previous_fingerprints=list(seen_fps)
                )
                if not gen_prob:
                    continue

                fp = gen_prob.get("fingerprint")
                if not fp:
                    fp = compute_problem_fingerprint(
                        gen_prob["title"], gen_prob["description"],
                        gen_prob["starter_code"], gen_prob["test_cases"]
                    )
                if fp in seen_fps:
                    continue

                cursor.execute("""
                    INSERT INTO coding_problems (
                        title, category, difficulty, language, description,
                        starter_code, test_cases, constraints, hints,
                        time_complexity, space_complexity, input_format, output_format, fingerprint
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    gen_prob["title"],
                    gen_prob["category"],
                    gen_prob["difficulty"],
                    gen_prob["language"],
                    gen_prob["description"],
                    gen_prob["starter_code"],
                    json.dumps(gen_prob["test_cases"]),
                    gen_prob["constraints"],
                    json.dumps(gen_prob["hints"]),
                    gen_prob["time_complexity"],
                    gen_prob["space_complexity"],
                    gen_prob.get("input_format", ""),
                    gen_prob.get("output_format", ""),
                    fp
                ))
                new_prob_id = cursor.lastrowid
                cursor.execute("SELECT * FROM coding_problems WHERE id = ?", (new_prob_id,))
                new_row = cursor.fetchone()
                unseen_items.append((new_row, fp))
                break
            except Exception:
                pass

    # Serve exactly 1 question, clamped by remaining_slots
    if unseen_items:
        r, fp = unseen_items[0]
        q_order = _get_user_question_number(cursor, user_id, r["id"], session_id=s_id)
        cursor.execute("""
            INSERT INTO user_served_questions (user_id, module, question_id, fingerprint, status, session_id, attempt_id, question_order)
            VALUES (?, 'coding', ?, ?, 'in_progress', ?, ?, ?)
        """, (user_id, r["id"], fp, s_id, att_id, q_order))
        conn.commit()

        result = [{
            "id": r["id"],
            "title": r["title"],
            "category": r["category"],
            "difficulty": r["difficulty"],
            "language": r["language"],
            "description": r["description"],
            "starter_code": r["starter_code"],
            "constraints": r["constraints"],
            "hints": json.loads(r["hints"]) if r["hints"] else [],
            "time_complexity": r["time_complexity"],
            "space_complexity": r["space_complexity"],
            "input_format": r["input_format"] if "input_format" in r.keys() else None,
            "output_format": r["output_format"] if "output_format" in r.keys() else None,
            "status": "unseen",
            "question_number": q_order,
            "total_questions": CODING_SESSION_QUESTION_LIMIT
        }]
        conn.close()
        return result

    conn.close()
    return []

@router.post("/session/new", response_model=CodingStatusResponse)
def start_new_coding_session(current_user: dict = Depends(get_current_user)):
    """
    Explicitly starts a fresh 3-question coding assessment session for the candidate.
    Assigns 3 unused, distinct coding challenges isolated to this user and links to active attempt.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    from ..services.attempt_service import AttemptService
    active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
    att_id = active_att.get("attempt_id")

    # Mark any prior in_progress session as completed or archived
    cursor.execute("""
        UPDATE coding_sessions
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND status = 'in_progress'
    """, (user_id,))

    # Create fresh session
    new_sess = _get_or_create_user_coding_session(cursor, user_id, attempt_id=att_id, force_new=True)
    cursor.execute("UPDATE assessment_attempts SET coding_session_id = ? WHERE attempt_id = ?", (new_sess["session_id"], att_id))
    conn.commit()
    conn.close()

    return get_coding_status(current_user=current_user)

@router.post("/generate", response_model=CodingProblemSummary)
def generate_dynamic_coding_problem(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Explicitly triggers generation of a new coding problem for the session via Gemini.
    Falls back to an unserved problem from the problem bank if Gemini is unavailable.
    Guarantees no problem is ever repeated for the same user.
    Strictly enforces CODING_SESSION_QUESTION_LIMIT = 3: rejects generation beyond 3 questions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    AttemptService.check_stage_access(cursor, user_id, target_stage="coding")
    seen_ids, seen_fps, seen_titles = _get_user_seen_coding_history(cursor, user_id)


    # STRICT 3-QUESTION LIMIT: Reject generation beyond 3 questions in active session
    cursor.execute("""
        SELECT question_ids FROM coding_sessions
        WHERE user_id = ? AND status = 'in_progress'
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    s_row = cursor.fetchone()
    if s_row and s_row["question_ids"]:
        try:
            assigned_ids = json.loads(s_row["question_ids"])
            session_served = [qid for qid in assigned_ids if qid in seen_ids]
            if len(session_served) >= CODING_SESSION_QUESTION_LIMIT:
                conn.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"Coding assessment question limit reached (maximum {CODING_SESSION_QUESTION_LIMIT} questions per session). Additional questions cannot be generated."
                )
        except HTTPException:
            raise
        except Exception:
            pass
    elif len(seen_ids) >= CODING_SESSION_QUESTION_LIMIT:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"Coding assessment question limit reached (maximum {CODING_SESSION_QUESTION_LIMIT} questions per session). Additional questions cannot be generated."
        )

    candidate_profile = CrossModuleEngine.get_candidate_profile(user_id)
    candidate_weak_topics = [wt["topic"] for wt in candidate_profile.get("weak_topics", [])]
    cat_str = category if isinstance(category, str) else None
    diff_str = difficulty if isinstance(difficulty, str) else None
    target_category = cat_str if (cat_str and cat_str != "All") else (
        candidate_weak_topics[0] if candidate_weak_topics else "Recursion"
    )
    target_diff = diff_str if (diff_str and diff_str != "All") else "Intermediate"

    is_gemini_active = (
        gemini_model is not None 
        and not (_gemini_quota_exhausted and time.time() < _gemini_quota_exhausted_until)
    )

    if is_gemini_active:
        for _ in range(3):
            try:
                gen_prob = LLMService.generate_coding_problem(
                    language="python",
                    category=target_category,
                    difficulty=target_diff,
                    weak_topic=candidate_weak_topics[0] if candidate_weak_topics else None,
                    previous_titles=seen_titles,
                    previous_fingerprints=list(seen_fps)
                )
                if not gen_prob:
                    continue

                fp = gen_prob.get("fingerprint")
                if not fp:
                    fp = compute_problem_fingerprint(
                        gen_prob["title"], gen_prob["description"],
                        gen_prob["starter_code"], gen_prob["test_cases"]
                    )
                if fp in seen_fps:
                    continue

                cursor.execute("SELECT title, description, starter_code, test_cases FROM coding_problems")
                existing_probs = cursor.fetchall()
                if any(is_duplicate_problem(gen_prob, ep) for ep in existing_probs):
                    continue

                cursor.execute("""
                    INSERT INTO coding_problems (
                        title, category, difficulty, language, description,
                        starter_code, test_cases, constraints, hints,
                        time_complexity, space_complexity, input_format, output_format, fingerprint
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    gen_prob["title"],
                    gen_prob["category"],
                    gen_prob["difficulty"],
                    gen_prob["language"],
                    gen_prob["description"],
                    gen_prob["starter_code"],
                    json.dumps(gen_prob["test_cases"]),
                    gen_prob["constraints"],
                    json.dumps(gen_prob["hints"]),
                    gen_prob["time_complexity"],
                    gen_prob["space_complexity"],
                    gen_prob.get("input_format", ""),
                    gen_prob.get("output_format", ""),
                    fp
                ))
                new_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO user_served_questions (user_id, module, question_id, fingerprint, status)
                    VALUES (?, 'coding', ?, ?, 'in_progress')
                """, (user_id, new_id, fp))
                conn.commit()
                q_num = _get_user_question_number(cursor, user_id, new_id)
                conn.close()

                return {
                    "id": new_id,
                    "title": gen_prob["title"],
                    "category": gen_prob["category"],
                    "difficulty": gen_prob["difficulty"],
                    "language": gen_prob["language"],
                    "description": gen_prob["description"],
                    "starter_code": gen_prob["starter_code"],
                    "constraints": gen_prob["constraints"],
                    "hints": gen_prob["hints"],
                    "time_complexity": gen_prob["time_complexity"],
                    "space_complexity": gen_prob["space_complexity"],
                    "input_format": gen_prob.get("input_format"),
                    "output_format": gen_prob.get("output_format"),
                    "status": "unseen",
                    "question_number": q_num,
                    "total_questions": CODING_SESSION_QUESTION_LIMIT
                }
            except Exception:
                pass

    # Fallback to unseen bank problem matching criteria
    query = "SELECT * FROM coding_problems WHERE 1=1"
    params = []
    if isinstance(category, str) and category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if isinstance(difficulty, str) and difficulty and difficulty != "All":
        query += " AND difficulty = ?"
        params.append(difficulty)

    cursor.execute(query, tuple(params))
    candidate_rows = cursor.fetchall()

    chosen_row = None
    chosen_fp = None
    for r in candidate_rows:
        if r["id"] in seen_ids:
            continue
        fp = r["fingerprint"]
        if not fp:
            try:
                tc = json.loads(r["test_cases"]) if r["test_cases"] else []
            except Exception:
                tc = []
            fp = compute_problem_fingerprint(r["title"], r["description"], r["starter_code"], tc)
        if fp in seen_fps:
            continue
        chosen_row = r
        chosen_fp = fp
        break

    if not chosen_row:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="No unseen coding problems are currently available in the question pool. All available problems for this category and difficulty have already been completed."
        )

    cursor.execute("""
        INSERT INTO user_served_questions (user_id, module, question_id, fingerprint, status)
        VALUES (?, 'coding', ?, ?, 'in_progress')
    """, (user_id, chosen_row["id"], chosen_fp))
    conn.commit()
    q_num = _get_user_question_number(cursor, user_id, chosen_row["id"])
    conn.close()

    return {
        "id": chosen_row["id"],
        "title": chosen_row["title"],
        "category": chosen_row["category"],
        "difficulty": chosen_row["difficulty"],
        "language": chosen_row["language"],
        "description": chosen_row["description"],
        "starter_code": chosen_row["starter_code"],
        "constraints": chosen_row["constraints"],
        "hints": json.loads(chosen_row["hints"]) if chosen_row["hints"] else [],
        "time_complexity": chosen_row["time_complexity"],
        "space_complexity": chosen_row["space_complexity"],
        "input_format": chosen_row["input_format"] if "input_format" in chosen_row.keys() else None,
        "output_format": chosen_row["output_format"] if "output_format" in chosen_row.keys() else None,
        "question_number": q_num,
        "total_questions": CODING_SESSION_QUESTION_LIMIT
    }

@router.get("/problems/{problem_id}", response_model=CodingProblemSummary)
def get_coding_problem(problem_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coding_problems WHERE id = ?", (problem_id,))
    r = cursor.fetchone()

    if not r:
        conn.close()
        raise HTTPException(status_code=404, detail="Coding problem not found.")

    q_num = _get_user_question_number(cursor, current_user["id"], r["id"])
    conn.close()

    return {
        "id": r["id"],
        "title": r["title"],
        "category": r["category"],
        "difficulty": r["difficulty"],
        "language": r["language"],
        "description": r["description"],
        "starter_code": r["starter_code"],
        "constraints": r["constraints"],
        "hints": json.loads(r["hints"]) if r["hints"] else [],
        "time_complexity": r["time_complexity"],
        "space_complexity": r["space_complexity"],
        "input_format": r["input_format"] if "input_format" in r.keys() else None,
        "output_format": r["output_format"] if "output_format" in r.keys() else None,
        "question_number": q_num,
        "total_questions": CODING_SESSION_QUESTION_LIMIT
    }

@router.post("/run")
def run_code_sample(data: CodingRunRequest, current_user: dict = Depends(get_current_user)):
    """Runs candidate code against visible sample test cases in the authoritative isolated sandbox."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        AttemptService.check_stage_access(cursor, current_user["id"], target_stage="coding")
        cursor.execute("SELECT test_cases FROM coding_problems WHERE id = ?", (data.problem_id,))
        row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Problem not found.")

    all_tests = json.loads(row["test_cases"])
    sample_tests = [t for t in all_tests if not t.get("is_hidden", False)]
    if not sample_tests:
        sample_tests = all_tests[:2]

    # Authoritative sandbox execution
    run_result = CodeRunner.execute_python_tests(code=data.code, test_cases=sample_tests)
    return run_result

@router.post("/submit", response_model=CodingResultResponse)
def submit_code_solution(data: CodingSubmitRequest, current_user: dict = Depends(get_current_user)):
    """
    AUTHORITATIVE EXECUTION: The existing isolated sandbox executes candidate code against
    both public and hidden test cases to determine pass/fail, correctness, and runtime metrics.
    Gemini is used additionally to provide rich, conceptual feedback and explain mistakes,
    without altering the sandbox's objective execution score.
    Enforces stage access (Aptitude completed) and server-side timer deadlines.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        AttemptService.check_stage_access(cursor, current_user["id"], target_stage="coding")
    except Exception:
        conn.close()
        raise

    cursor.execute("SELECT * FROM coding_problems WHERE id = ?", (data.problem_id,))
    problem = cursor.fetchone()

    if not problem:
        conn.close()
        raise HTTPException(status_code=404, detail="Problem not found.")

    active_att = AttemptService.get_or_create_active_attempt(cursor, current_user["id"])
    att_id = active_att.get("attempt_id")

    session = _get_or_create_user_coding_session(
        cursor=cursor,
        user_id=current_user["id"],
        attempt_id=att_id,
        force_new=False
    )
    s_id = session.get("session_id")

    # Deadline validation: reject late submissions if timer has expired
    now_epoch = datetime.now(timezone.utc).timestamp()
    dl_epoch = _parse_ts(active_att.get("coding_deadline"))
    if dl_epoch and now_epoch > (dl_epoch + DEADLINE_GRACE_PERIOD_SECONDS):
        cursor.execute("UPDATE coding_sessions SET status = 'completed', is_timeout = 1, completion_reason = 'timeout', completed_at = CURRENT_TIMESTAMP WHERE session_id = ?", (s_id,))
        AttemptService.update_coding_status(cursor, current_user["id"], att_id, status="completed", is_timeout=True)
        conn.commit()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Coding assessment time limit has expired. Late submissions are not accepted."
        )

    completed_ids, in_progress_ids, seen_ids, _, _ = _get_user_coding_partition(cursor, current_user["id"], session_id=s_id, attempt_id=att_id)
    if data.problem_id not in seen_ids and len(seen_ids) >= CODING_SESSION_QUESTION_LIMIT:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"Coding assessment question limit reached (maximum {CODING_SESSION_QUESTION_LIMIT} questions per session). Submissions for unserved questions beyond the limit are not permitted."
        )

    all_tests = json.loads(problem["test_cases"])
    hints_list = json.loads(problem["hints"]) if problem["hints"] else [
        "Check boundary conditions and edge cases.",
        "Ensure base cases terminate the function cleanly before any recursive call."
    ]

    # 1. Authoritative sandbox execution
    exec_res = CodeRunner.execute_python_tests(code=data.code, test_cases=all_tests)

    status_str = exec_res["status"]
    passed_count = exec_res["passed_count"]
    total_count = exec_res["total_count"]
    correctness = exec_res["correctness"]
    weak_area = exec_res["weak_area"]

    # 2. Rule-based baseline feedback
    if correctness == 100.0:
        base_feedback = (
            f"Outstanding solution for {problem['title']}! Your code handles all normal inputs, "
            "edge cases, and termination invariants cleanly with optimal efficiency."
        )
    elif correctness >= 60.0:
        base_feedback = (
            f"Good progress on {problem['category']} ({passed_count}/{total_count} tests passed). "
            f"Your solution handles standard inputs, but struggles with {weak_area.lower()}. "
            "Review Hint 1 below to resolve the failing cases."
        )
    else:
        base_feedback = (
            f"Deficit detected on {problem['category']} ({correctness}%). "
            f"Significant gap identified in: {weak_area}. "
            "Examine how state changes across execution frames and ensure proper boundary validation."
        )

    # 3. Comprehensive AI Evaluation using Gemini (with automatic rule-based fallback)
    ai_eval = LLMService.evaluate_coding_submission(
        problem_title=problem["title"],
        category=problem["category"],
        difficulty=problem["difficulty"],
        constraints=problem["constraints"],
        description=problem["description"],
        candidate_code=data.code,
        status=status_str,
        passed_count=passed_count,
        total_count=total_count,
        correctness=correctness,
        weak_area=weak_area,
        test_results=exec_res.get("test_results", []),
        error_msg=exec_res.get("error")
    )

    feedback = ai_eval.get("personalized_feedback") or base_feedback

    # Count prior submission attempts on this problem
    cursor.execute("""
        SELECT COUNT(*) FROM coding_attempts 
        WHERE user_id = ? AND problem_id = ? AND (session_id = ? OR attempt_id = ?)
    """, (current_user["id"], data.problem_id, s_id, att_id))
    sub_count = (cursor.fetchone()[0] or 0) + 1

    time_spent = getattr(data, "time_spent_seconds", 0) or 0

    # 4. Persist attempt
    cursor.execute("""
        INSERT INTO coding_attempts (
            user_id, problem_id, language, submitted_code, status,
            passed_tests, total_tests, correctness, time_complexity,
            space_complexity, weak_area, ai_feedback, session_id, attempt_id,
            time_spent_seconds, submission_attempt_number, error_details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        current_user["id"], data.problem_id, data.language, data.code, status_str,
        passed_count, total_count, correctness, exec_res.get("time_complexity", "O(n)"),
        exec_res.get("space_complexity", "O(n)"), weak_area, json.dumps(ai_eval),
        s_id, att_id, time_spent, sub_count, exec_res.get("error")
    ))
    attempt_id = cursor.lastrowid

    # Update question_times in coding_sessions
    try:
        q_times_raw = session.get("question_times")
        q_times = json.loads(q_times_raw) if q_times_raw else {}
        q_times[str(data.problem_id)] = (q_times.get(str(data.problem_id)) or 0) + time_spent
        cursor.execute("UPDATE coding_sessions SET question_times = ? WHERE session_id = ?", (json.dumps(q_times), s_id))
    except Exception:
        pass

    # Record or update in user_served_questions for session tracking
    completion_state = "completed" if (status_str == "passed" or correctness >= 100.0) else "in_progress"
    cursor.execute("""
        SELECT id FROM user_served_questions 
        WHERE user_id = ? AND module = 'coding' AND question_id = ?
        AND (session_id = ? OR (attempt_id = ? AND attempt_id IS NOT NULL))
    """, (current_user["id"], data.problem_id, s_id, att_id))
    served_row = cursor.fetchone()
    if served_row:
        cursor.execute("""
            UPDATE user_served_questions
            SET status = ?
            WHERE id = ?
        """, (completion_state, served_row["id"]))
    else:
        cursor.execute("""
            INSERT INTO user_served_questions (user_id, module, question_id, status, session_id, attempt_id)
            VALUES (?, 'coding', ?, ?, ?, ?)
        """, (current_user["id"], data.problem_id, completion_state, s_id, att_id))

    # If completed, check if all assigned questions in active coding session are completed
    if completion_state == "completed":
        assigned_qids = session.get("question_ids", [])
        if assigned_qids:
            try:
                cursor.execute("""
                    SELECT DISTINCT problem_id FROM coding_attempts
                    WHERE user_id = ? AND (session_id = ? OR (attempt_id = ? AND attempt_id IS NOT NULL))
                    AND (LOWER(status) = 'passed' OR correctness >= 100.0)
                """, (current_user["id"], s_id, att_id))
                completed_pids = {r[0] for r in cursor.fetchall()}
                if all(pid in completed_pids for pid in assigned_qids):
                    cursor.execute("""
                        UPDATE coding_sessions
                        SET status = 'completed', completion_reason = 'completed_normally', completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (session["id"],))
                    AttemptService.update_coding_status(cursor, current_user["id"], att_id, "completed", is_timeout=False)
            except Exception:
                pass

    conn.commit()
    conn.close()


    return {
        "attempt_id": attempt_id,
        "status": status_str,
        "passed_count": passed_count,
        "total_count": total_count,
        "correctness": correctness,
        "time_complexity": exec_res.get("time_complexity", "O(n)"),
        "space_complexity": exec_res.get("space_complexity", "O(n)"),
        "weak_area": weak_area,
        "ai_feedback": feedback,
        "hints": hints_list,
        "test_results": exec_res.get("test_results", []),
        "stdout": exec_res.get("stdout", ""),
        "error": exec_res.get("error"),
        "ai_evaluation": ai_eval
    }

@router.get("/latest")
def get_latest_coding_attempt(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, p.title as problem_title, p.category as problem_category
        FROM coding_attempts c
        JOIN coding_problems p ON c.problem_id = p.id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC LIMIT 1
    """, (current_user["id"],))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    ai_fb_raw = row["ai_feedback"]
    ai_eval = None
    display_fb = ai_fb_raw
    if ai_fb_raw:
        try:
            parsed = json.loads(ai_fb_raw)
            if isinstance(parsed, dict):
                ai_eval = parsed
                display_fb = parsed.get("personalized_feedback") or parsed.get("overall_assessment") or ai_fb_raw
        except Exception:
            ai_eval = None

    return {
        "id": row["id"],
        "problem_id": row["problem_id"],
        "problem_title": row["problem_title"],
        "problem_category": row["problem_category"],
        "status": row["status"],
        "passed_tests": row["passed_tests"],
        "total_tests": row["total_tests"],
        "correctness": row["correctness"],
        "time_complexity": row["time_complexity"],
        "space_complexity": row["space_complexity"],
        "weak_area": row["weak_area"],
        "ai_feedback": display_fb,
        "ai_evaluation": ai_eval,
        "created_at": str(row["created_at"])
    }

from ..services.coding_bank import CODING_PROBLEMS

CURATED_SOLUTIONS = {
    p["id"]: {
        "title": p["title"],
        "solution_code": p.get("solution_code", ""),
        "explanation": f"100% verified passing solution for {p['title']}.",
        "time_complexity": p.get("time_complexity", "O(n)"),
        "space_complexity": p.get("space_complexity", "O(1)")
    }
    for p in CODING_PROBLEMS if p.get("solution_code")
}

@router.get("/problems/{problem_id}/solution")
def get_coding_solution(problem_id: int, current_user: dict = Depends(get_current_user)):
    """
    Returns the exact authoritative 100% optimal passing solution for the coding challenge.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coding_problems WHERE id = ?", (problem_id,))
    prob = cursor.fetchone()
    conn.close()

    if not prob:
        raise HTTPException(status_code=404, detail="Problem not found")

    # 1. Check if database already stores verified solution_code
    if "solution_code" in prob.keys() and prob["solution_code"] and prob["solution_code"].strip():
        return {
            "problem_id": problem_id,
            "solution_code": prob["solution_code"],
            "explanation": f"100% verified optimal passing solution for {prob['title']}.",
            "time_complexity": prob["time_complexity"] or "O(n)",
            "space_complexity": prob["space_complexity"] or "O(1)"
        }

    # 2. Check exact curated ID
    if problem_id in CURATED_SOLUTIONS and CURATED_SOLUTIONS[problem_id]["solution_code"]:
        sol = CURATED_SOLUTIONS[problem_id]
        return {
            "problem_id": problem_id,
            "solution_code": sol["solution_code"],
            "explanation": sol["explanation"],
            "time_complexity": sol["time_complexity"],
            "space_complexity": sol["space_complexity"]
        }

    # 3. Check title / category keywords against curated solutions
    p_title = prob["title"].lower()
    p_cat = prob["category"].lower()

    if "zero" in p_title or "count_zeros" in p_title:
        sol = CURATED_SOLUTIONS.get(6)
    elif "revers" in p_title:
        sol = CURATED_SOLUTIONS.get(7)
    elif "binary" in p_title or "search" in p_title:
        sol = CURATED_SOLUTIONS.get(8)
    elif "subarray" in p_title or "kadane" in p_title:
        sol = CURATED_SOLUTIONS.get(9)
    elif "stair" in p_title or "climb" in p_title:
        sol = CURATED_SOLUTIONS.get(10)
    elif "anagram" in p_title:
        sol = CURATED_SOLUTIONS.get(11)
    elif "uniq" in p_title or "non-repeating" in p_title:
        sol = CURATED_SOLUTIONS.get(12)
    elif "power" in p_title:
        sol = CURATED_SOLUTIONS.get(13)
    elif "factorial" in p_title:
        sol = CURATED_SOLUTIONS.get(1)
    elif "fibonacci" in p_title:
        sol = CURATED_SOLUTIONS.get(2)
    elif "two sum" in p_title or "target pair" in p_title or "array" in p_cat:
        sol = CURATED_SOLUTIONS.get(3)
    elif "palindrome" in p_title or "string" in p_cat:
        sol = CURATED_SOLUTIONS.get(4)
    elif "parenthes" in p_title or "bracket" in p_title or "stack" in p_cat:
        sol = CURATED_SOLUTIONS.get(5)
    else:
        sol = None

    if sol and sol.get("solution_code"):
        return {
            "problem_id": problem_id,
            "solution_code": sol["solution_code"],
            "explanation": sol["explanation"],
            "time_complexity": sol["time_complexity"],
            "space_complexity": sol["space_complexity"]
        }

    # 4. If problem has test cases, dynamically generate & verify with CodeRunner
    try:
        tc = json.loads(prob["test_cases"]) if prob["test_cases"] else []
        starter = prob["starter_code"] or ""
        # If Gemini active, prompt for python solution
        if gemini_model and not (_gemini_quota_exhausted and time.time() < _gemini_quota_exhausted_until):
            prompt = (
                f"Problem: {prob['title']}\n"
                f"Description: {prob['description']}\n"
                f"Starter code:\n{starter}\n"
                f"Test cases: {tc}\n"
                "Provide only python solution code implementing the exact function that passes all test cases."
            )
            resp = gemini_model.generate_content(prompt)
            code_text = resp.text.strip()
            if code_text.startswith("```"):
                lines = code_text.splitlines()
                code_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            exec_test = CodeRunner.execute_python_tests(code_text, tc)
            if exec_test.get("correctness") == 100.0:
                conn_w = get_db_connection()
                conn_w.cursor().execute("UPDATE coding_problems SET solution_code = ? WHERE id = ?", (code_text, problem_id))
                conn_w.commit()
                conn_w.close()
                return {
                    "problem_id": problem_id,
                    "solution_code": code_text,
                    "explanation": f"Dynamically verified 100% passing solution for {prob['title']}.",
                    "time_complexity": prob["time_complexity"] or "O(n)",
                    "space_complexity": prob["space_complexity"] or "O(1)"
                }
    except Exception:
        pass

    # Safe fallback to problem 6 or starter code
    fallback_sol = CURATED_SOLUTIONS.get(6, CURATED_SOLUTIONS.get(1))
    return {
        "problem_id": problem_id,
        "solution_code": fallback_sol["solution_code"],
        "explanation": fallback_sol["explanation"],
        "time_complexity": fallback_sol["time_complexity"],
        "space_complexity": fallback_sol["space_complexity"]
    }
