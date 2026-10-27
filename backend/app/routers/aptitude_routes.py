from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import time
import random
from datetime import datetime, timezone
from ..database import get_db_connection
from ..models import (
    AptitudeQuestionResponse, AptitudeTestSubmit, AptitudeResultResponse,
    AptitudeSessionResponse, AptitudeSaveProgressRequest, AptitudeStartRequest
)
from ..auth import get_current_user
from ..services.llm_service import LLMService, gemini_model, _gemini_quota_exhausted, _gemini_quota_exhausted_until
from ..services.cross_module_engine import CrossModuleEngine
from ..services.attempt_service import AttemptService, _parse_ts
from ..config import APTITUDE_TIME_LIMIT_SECONDS, DEADLINE_GRACE_PERIOD_SECONDS

router = APIRouter(prefix="/aptitude", tags=["Aptitude"])

ALL_CATEGORIES = [
    "Quantitative Aptitude",
    "Logical Reasoning",
    "Verbal Reasoning",
    "Data Interpretation"
]

def normalize_category_name(cat: Optional[str]) -> Optional[str]:
    if not cat or cat == "All":
        return None
    c_lower = cat.strip().lower()
    if "quant" in c_lower:
        return "Quantitative Aptitude"
    if "logic" in c_lower:
        return "Logical Reasoning"
    if "verb" in c_lower:
        return "Verbal Reasoning"
    if "data" in c_lower or "interpret" in c_lower:
        return "Data Interpretation"
    return cat.strip()


def _fetch_unique_aptitude_questions(cursor, user_id: int, category: Optional[str] = None, difficulty: Optional[str] = None, limit: int = 10, attempt_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Selects or dynamically generates aptitude questions for this user and attempt,
    thoroughly excluding questions previously served or answered across previous attempts.
    """
    # 1. Fetch ALL questions candidate has seen or answered across all attempts
    cursor.execute("""
        SELECT DISTINCT question_id FROM user_served_questions
        WHERE user_id = ? AND module = 'aptitude' AND question_id IS NOT NULL
    """, (user_id,))
    served_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT aa.question_id 
        FROM aptitude_answers aa
        JOIN aptitude_attempts at ON aa.attempt_id = at.id
        WHERE at.user_id = ? AND aa.question_id IS NOT NULL
    """, (user_id,))
    answered_ids = [r[0] for r in cursor.fetchall()]

    all_seen_ids = list(dict.fromkeys(served_ids + answered_ids))

    # Retrieve texts of recently seen questions to exclude in Gemini prompt
    recent_q_texts = []
    if all_seen_ids:
        placeholders = ",".join("?" for _ in all_seen_ids[:30])
        cursor.execute(f"SELECT question FROM aptitude_questions WHERE id IN ({placeholders})", tuple(all_seen_ids[:30]))
        recent_q_texts = [r["question"] for r in cursor.fetchall()]

    # 2. Check candidate skill state & weak areas for personalization
    candidate_profile = CrossModuleEngine.get_candidate_profile(user_id)
    apt_categories_perf = candidate_profile.get("aptitude_categories", {})
    weak_cats = [c for c, sc in apt_categories_perf.items() if sc < 60.0]

    normalized_cat = normalize_category_name(category)

    # 3. Determine category distribution
    if not normalized_cat:
        base_per_cat = limit // len(ALL_CATEGORIES)
        remainder = limit % len(ALL_CATEGORIES)
        cat_targets = {}
        for idx, cat_name in enumerate(ALL_CATEGORIES):
            cat_targets[cat_name] = base_per_cat + (1 if idx < remainder else 0)
    else:
        cat_targets = {normalized_cat: limit}

    selected_questions: List[Dict[str, Any]] = []
    session_ids: List[int] = []
    session_texts: List[str] = []

    # 4. Generate / select questions for each target category
    for cat_name, cat_count in cat_targets.items():
        needed_for_cat = cat_count

        target_diff = difficulty if (difficulty and difficulty != "All") else None
        if not target_diff:
            cat_score = apt_categories_perf.get(cat_name, 70.0)
            if cat_score < 55.0:
                target_diff = "Beginner"
            elif cat_score > 80.0:
                target_diff = "Advanced"
            else:
                target_diff = "Intermediate"

        is_gemini_active = (
            gemini_model is not None 
            and not (_gemini_quota_exhausted and time.time() < _gemini_quota_exhausted_until)
        )

        cat_weakness = cat_name if cat_name in weak_cats else None

        if is_gemini_active:
            for _ in range(needed_for_cat):
                try:
                    gen_q = LLMService.generate_aptitude_question(
                        category=cat_name,
                        difficulty=target_diff,
                        topic=cat_weakness,
                        exclude_questions=session_texts + recent_q_texts
                    )
                    if gen_q and gen_q.get("question") not in session_texts:
                        cursor.execute("""
                            INSERT INTO aptitude_questions (
                                category, topic, difficulty, question, options, correct_answer, explanation
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            gen_q["category"],
                            gen_q.get("topic", cat_name),
                            gen_q["difficulty"],
                            gen_q["question"],
                            json.dumps(gen_q["options"]),
                            gen_q["correct_answer"],
                            gen_q["explanation"]
                        ))
                        new_q_id = cursor.lastrowid
                        cursor.execute("""
                            INSERT INTO user_served_questions (user_id, module, question_id, attempt_id)
                            VALUES (?, 'aptitude', ?, ?)
                        """, (user_id, new_q_id, attempt_id))

                        session_ids.append(new_q_id)
                        session_texts.append(gen_q["question"])
                        selected_questions.append({
                            "id": new_q_id,
                            "category": gen_q["category"],
                            "difficulty": gen_q["difficulty"],
                            "topic": gen_q.get("topic", cat_name),
                            "question": gen_q["question"],
                            "options": gen_q["options"]
                        })
                except Exception:
                    break

        still_needed = cat_count - sum(1 for q in selected_questions if q["category"] == cat_name or (cat_name == "Verbal Reasoning" and q["category"] in ["Verbal Reasoning", "Verbal Ability"]))
        if still_needed > 0:
            cat_filters = [cat_name]
            if cat_name == "Verbal Reasoning":
                cat_filters.append("Verbal Ability")

            cat_ph = ",".join("?" for _ in cat_filters)
            base_q = f"SELECT id, category, difficulty, question, options, topic FROM aptitude_questions WHERE category IN ({cat_ph})"
            params: List[Any] = list(cat_filters)

            if target_diff and target_diff != "All":
                base_q += " AND difficulty = ?"
                params.append(target_diff)

            # Strictly exclude all questions previously seen by this user across past attempts
            all_exclude = list(dict.fromkeys(all_seen_ids + session_ids))
            if all_exclude:
                excl_ph = ",".join("?" for _ in all_exclude)
                unseen_q = base_q + f" AND id NOT IN ({excl_ph}) ORDER BY RANDOM() LIMIT ?"
                cursor.execute(unseen_q, tuple(params + all_exclude + [still_needed]))
            else:
                cursor.execute(base_q + " ORDER BY RANDOM() LIMIT ?", tuple(params + [still_needed]))

            bank_rows = cursor.fetchall()
            for r in bank_rows:
                session_ids.append(r["id"])
                session_texts.append(r["question"])
                cursor.execute("""
                    INSERT INTO user_served_questions (user_id, module, question_id, attempt_id)
                    VALUES (?, 'aptitude', ?, ?)
                """, (user_id, r["id"], attempt_id))
                selected_questions.append({
                    "id": r["id"],
                    "category": r["category"],
                    "difficulty": r["difficulty"],
                    "topic": r["topic"] if "topic" in r.keys() and r["topic"] else r["category"],
                    "question": r["question"],
                    "options": json.loads(r["options"])
                })

            # If user has seen all questions in bank, fallback to least recently seen not in current session
            current_cat_count = sum(1 for q in selected_questions if q["category"] in cat_filters)
            if current_cat_count < cat_count:
                extra_needed = cat_count - current_cat_count
                if session_ids:
                    s_ph = ",".join("?" for _ in session_ids)
                    cursor.execute(f"SELECT id, category, difficulty, question, options, topic FROM aptitude_questions WHERE category IN ({cat_ph}) AND id NOT IN ({s_ph}) ORDER BY RANDOM() LIMIT ?", tuple(cat_filters + session_ids + [extra_needed]))
                else:
                    cursor.execute(f"SELECT id, category, difficulty, question, options, topic FROM aptitude_questions WHERE category IN ({cat_ph}) ORDER BY RANDOM() LIMIT ?", tuple(cat_filters + [extra_needed]))
                extra_rows = cursor.fetchall()
                for r in extra_rows:
                    session_ids.append(r["id"])
                    session_texts.append(r["question"])
                    cursor.execute("""
                        INSERT INTO user_served_questions (user_id, module, question_id, attempt_id)
                        VALUES (?, 'aptitude', ?, ?)
                    """, (user_id, r["id"], attempt_id))
                    selected_questions.append({
                        "id": r["id"],
                        "category": r["category"],
                        "difficulty": r["difficulty"],
                        "topic": r["topic"] if "topic" in r.keys() and r["topic"] else r["category"],
                        "question": r["question"],
                        "options": json.loads(r["options"])
                    })

    random.shuffle(selected_questions)
    return selected_questions[:limit]


@router.get("/questions", response_model=List[AptitudeQuestionResponse])
def get_aptitude_questions(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(10, ge=5, le=30),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetches dynamic aptitude questions, guaranteeing session-aware variation and
    excluding questions seen by this user across previous attempts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
    att_id = active_att.get("attempt_id")

    questions = _fetch_unique_aptitude_questions(cursor, user_id, category, difficulty, limit, att_id)

    conn.commit()
    conn.close()
    return questions


@router.get("/session", response_model=AptitudeSessionResponse)
def get_aptitude_session(current_user: dict = Depends(get_current_user)):
    """
    Retrieves the active in-progress Aptitude assessment session for the logged-in user.
    Restores the exact remaining time, assigned questions, and draft answers upon page refresh.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
    conn.commit()

    att_id = active_att["attempt_id"]
    status = active_att.get("aptitude_status", "not_started")
    in_test = (status == "in_progress")
    completed = (status == "completed")

    questions = []
    q_ids_raw = active_att.get("aptitude_question_ids")
    if q_ids_raw:
        try:
            q_ids = json.loads(q_ids_raw)
            if q_ids:
                ph = ",".join("?" for _ in q_ids)
                cursor.execute(f"SELECT id, category, difficulty, question, options, topic FROM aptitude_questions WHERE id IN ({ph})", tuple(q_ids))
                q_map = {r["id"]: r for r in cursor.fetchall()}
                for qid in q_ids:
                    if qid in q_map:
                        r = q_map[qid]
                        questions.append({
                            "id": r["id"],
                            "category": r["category"],
                            "difficulty": r["difficulty"],
                            "topic": r["topic"] if "topic" in r.keys() and r["topic"] else r["category"],
                            "question": r["question"],
                            "options": json.loads(r["options"]) if r["options"] else []
                        })
        except Exception:
            questions = []

    # Parse draft answers
    draft_answers = {}
    if active_att.get("aptitude_answers_draft"):
        try:
            draft_answers = json.loads(active_att["aptitude_answers_draft"])
        except Exception:
            draft_answers = {}

    # Latest result if completed
    latest_res = None
    if completed:
        cursor.execute("SELECT * FROM aptitude_attempts WHERE user_id = ? AND attempt_id = ? ORDER BY id DESC LIMIT 1", (user_id, att_id))
        row = cursor.fetchone()
        if not row:
            cursor.execute("SELECT * FROM aptitude_attempts WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
            row = cursor.fetchone()
        if row:
            ai_eval = None
            if "ai_feedback" in row.keys() and row["ai_feedback"]:
                try:
                    ai_eval = json.loads(row["ai_feedback"])
                except Exception:
                    ai_eval = {"summary": str(row["ai_feedback"])}
            latest_res = {
                "attempt_id": row["id"],
                "category": row["category"],
                "difficulty": row["difficulty"],
                "overall_score": row["score"],
                "total_questions": row["total_questions"],
                "correct_count": row["correct_count"],
                "incorrect_count": row["incorrect_count"],
                "time_taken_seconds": row["time_taken_seconds"],
                "category_performance": json.loads(row["category_breakdown"]) if row["category_breakdown"] else {},
                "weak_categories": json.loads(row["weak_categories"]) if row["weak_categories"] else [],
                "ai_evaluation": ai_eval,
                "is_timeout": bool(row["is_timeout"]) if "is_timeout" in row.keys() else False,
                "created_at": str(row["created_at"])
            }

    conn.close()

    rem_seconds = active_att.get("aptitude_remaining_seconds", APTITUDE_TIME_LIMIT_SECONDS)

    return AptitudeSessionResponse(
        attempt_id=att_id,
        in_test=in_test,
        completed=completed,
        questions=questions,
        current_answers=draft_answers,
        started_at=active_att.get("aptitude_started_at"),
        deadline=active_att.get("aptitude_deadline"),
        remaining_seconds=rem_seconds,
        duration_seconds=active_att.get("aptitude_duration_seconds") or APTITUDE_TIME_LIMIT_SECONDS,
        is_timeout=bool(active_att.get("aptitude_timeout")),
        total_questions=len(questions) if questions else 10,
        answered_count=len(draft_answers),
        category="All",
        difficulty="Intermediate",
        latest_result=latest_res
    )


@router.post("/start", response_model=AptitudeSessionResponse)
def start_aptitude_test(payload: AptitudeStartRequest, current_user: dict = Depends(get_current_user)):
    """
    Explicitly starts the candidate Aptitude Assessment attempt and initializes the server countdown timer.
    Generates/locks the 10 distinct questions for this attempt and establishes the authoritative server deadline.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
    att_id = active_att["attempt_id"]

    # If already in_progress and has questions, return existing session so timer isn't reset
    if active_att.get("aptitude_status") == "in_progress" and active_att.get("aptitude_question_ids"):
        conn.commit()
        conn.close()
        return get_aptitude_session(current_user=current_user)

    # Generate fresh 10 questions for this attempt
    limit = payload.total_questions or 10
    questions = _fetch_unique_aptitude_questions(
        cursor=cursor,
        user_id=user_id,
        category=payload.category,
        difficulty=payload.difficulty,
        limit=limit,
        attempt_id=att_id
    )

    q_ids = [q["id"] for q in questions]

    # Start timer and update attempt record
    updated_att = AttemptService.start_aptitude_test(
        cursor=cursor,
        user_id=user_id,
        attempt_id=att_id,
        question_ids=q_ids,
        duration_seconds=APTITUDE_TIME_LIMIT_SECONDS
    )

    conn.commit()
    conn.close()

    return AptitudeSessionResponse(
        attempt_id=att_id,
        in_test=True,
        completed=False,
        questions=questions,
        current_answers={},
        started_at=updated_att.get("aptitude_started_at"),
        deadline=updated_att.get("aptitude_deadline"),
        remaining_seconds=updated_att.get("aptitude_remaining_seconds", APTITUDE_TIME_LIMIT_SECONDS),
        duration_seconds=updated_att.get("aptitude_duration_seconds", APTITUDE_TIME_LIMIT_SECONDS),
        is_timeout=False,
        total_questions=len(questions),
        answered_count=0,
        category=payload.category or "All",
        difficulty=payload.difficulty or "Intermediate"
    )


@router.post("/save-progress")
def save_aptitude_progress(payload: AptitudeSaveProgressRequest, current_user: dict = Depends(get_current_user)):
    """Saves candidate draft answers and time spent for seamless resumption across refreshes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = current_user["id"]

    active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
    att_id = active_att["attempt_id"]

    AttemptService.save_aptitude_progress(
        cursor=cursor,
        user_id=user_id,
        attempt_id=att_id,
        answers=payload.answers,
        elapsed_seconds=payload.elapsed_seconds
    )

    conn.commit()
    conn.close()
    return {"status": "saved", "attempt_id": att_id}


@router.post("/submit", response_model=AptitudeResultResponse)
def submit_aptitude_test(
    data: AptitudeTestSubmit,
    current_user: dict = Depends(get_current_user)
):
    """
    Evaluates candidate aptitude answers deterministically against stored answer keys.
    Authoritative objective scoring is calculated in the backend.
    Enforces server-side deadline verification: late submissions are saved with is_timeout=True.
    Updates assessment attempt status to 'completed', unlocking the Coding Assessment.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = current_user["id"]

    active_att = AttemptService.get_or_create_active_attempt(cursor, user_id)
    att_id = active_att.get("attempt_id")

    # Deadline validation
    now_epoch = datetime.now(timezone.utc).timestamp()
    dl_epoch = _parse_ts(active_att.get("aptitude_deadline"))
    is_timeout = bool(data.is_timeout)
    if dl_epoch and now_epoch > (dl_epoch + DEADLINE_GRACE_PERIOD_SECONDS):
        is_timeout = True

    completion_reason = "timeout" if is_timeout else "completed_normally"

    correct_count = 0
    incorrect_count = 0
    category_stats: Dict[str, Dict[str, int]] = {}
    evaluated_answers = []
    question_breakdown: List[Dict[str, Any]] = []

    for item in data.answers:
        cursor.execute(
            "SELECT id, category, topic, difficulty, question, options, correct_answer, explanation FROM aptitude_questions WHERE id = ?",
            (item.question_id,)
        )
        q_row = cursor.fetchone()
        if not q_row:
            continue

        raw_cat = q_row["category"]
        cat = "Verbal Reasoning" if raw_cat in ["Verbal Reasoning", "Verbal Ability"] else raw_cat

        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "correct": 0}
        category_stats[cat]["total"] += 1

        is_corr = (item.selected_option is not None) and (item.selected_option == q_row["correct_answer"])
        if is_corr:
            correct_count += 1
            category_stats[cat]["correct"] += 1
        else:
            incorrect_count += 1

        evaluated_answers.append({
            "question_id": item.question_id,
            "selected_option": item.selected_option,
            "is_correct": 1 if is_corr else 0
        })

        question_breakdown.append({
            "question_id": item.question_id,
            "category": cat,
            "topic": q_row["topic"] if "topic" in q_row.keys() and q_row["topic"] else cat,
            "difficulty": q_row["difficulty"],
            "question": q_row["question"],
            "selected_option": item.selected_option,
            "correct_answer": q_row["correct_answer"],
            "is_correct": bool(is_corr),
            "explanation": q_row["explanation"] or ""
        })

    total_q = max(len(data.answers), 1)
    overall_score = round((correct_count / total_q) * 100, 1)
    accuracy = round((correct_count / max(correct_count + incorrect_count, 1)) * 100, 1)

    # Category breakdown %
    category_performance = {}
    weak_categories = []
    all_standard_cats = ["Quantitative Aptitude", "Logical Reasoning", "Verbal Reasoning", "Data Interpretation"]

    for c in all_standard_cats:
        if c in category_stats and category_stats[c]["total"] > 0:
            score = round((category_stats[c]["correct"] / category_stats[c]["total"]) * 100, 1)
            category_performance[c] = score
            if score < 60.0:
                weak_categories.append(c)
        else:
            category_performance[c] = 70.0

    if not weak_categories:
        lowest_cat = min(category_performance, key=category_performance.get)
        if category_performance[lowest_cat] < 70.0:
            weak_categories.append(lowest_cat)

    if is_timeout:
        recommendation = f"Assessment completed due to timer limit. Scored {overall_score}% ({correct_count}/{total_q} correct). Proceed to Stage 2: Coding Assessment."
    elif weak_categories:
        recommendation = (
            f"Targeted Recommendation: Prioritize practice on {', '.join(weak_categories)} "
            "before attempting advanced company assessment tests. Proceed to Stage 2: Coding Assessment."
        )
    else:
        recommendation = "Outstanding aptitude proficiency across all evaluated categories! Proceed directly to Stage 2: Coding Assessment."

    ai_evaluation = LLMService.evaluate_aptitude_performance(
        total_questions=total_q,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        overall_score=overall_score,
        category_performance=category_performance,
        weak_categories=weak_categories,
        question_breakdown=question_breakdown
    )

    started_at = active_att.get("aptitude_started_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Save to aptitude_attempts table including timing, timeout, and attempt_id
    cursor.execute("""
        INSERT INTO aptitude_attempts (
            user_id, category, difficulty, total_questions, correct_count,
            incorrect_count, score, time_taken_seconds, category_breakdown, weak_categories,
            ai_feedback, attempt_id, is_timeout, completion_reason, started_at, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        user_id, data.category, data.difficulty, total_q, correct_count,
        incorrect_count, overall_score, data.time_taken_seconds,
        json.dumps(category_performance), json.dumps(weak_categories),
        json.dumps(ai_evaluation), att_id, 1 if is_timeout else 0, completion_reason, started_at
    ))
    attempt_id = cursor.lastrowid

    # Update attempt status in assessment_attempts to completed and unlock Coding
    AttemptService.update_aptitude_status(
        cursor=cursor,
        user_id=user_id,
        attempt_id=att_id,
        aptitude_attempt_id=attempt_id,
        status="completed",
        time_taken=data.time_taken_seconds,
        is_timeout=is_timeout
    )

    # Persist into aptitude_answers to record answer history
    for ans in evaluated_answers:
        cursor.execute("""
            INSERT INTO aptitude_answers (attempt_id, question_id, selected_option, is_correct)
            VALUES (?, ?, ?, ?)
        """, (attempt_id, ans["question_id"], ans["selected_option"], ans["is_correct"]))

    conn.commit()
    conn.close()

    return {
        "attempt_id": attempt_id,
        "overall_score": overall_score,
        "total_questions": total_q,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "accuracy": accuracy,
        "time_taken_seconds": data.time_taken_seconds,
        "category_performance": category_performance,
        "weak_categories": weak_categories,
        "recommendation": recommendation,
        "ai_evaluation": ai_evaluation,
        "is_timeout": is_timeout,
        "completion_reason": completion_reason,
        "attempt_id_str": att_id
    }


@router.get("/latest")
def get_latest_aptitude(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM aptitude_attempts
        WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 1
    """, (current_user["id"],))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    ai_eval = None
    if "ai_feedback" in row.keys() and row["ai_feedback"]:
        try:
            ai_eval = json.loads(row["ai_feedback"])
        except Exception:
            ai_eval = {"summary": str(row["ai_feedback"])}

    return {
        "attempt_id": row["id"],
        "category": row["category"],
        "difficulty": row["difficulty"],
        "overall_score": row["score"],
        "total_questions": row["total_questions"],
        "correct_count": row["correct_count"],
        "incorrect_count": row["incorrect_count"],
        "time_taken_seconds": row["time_taken_seconds"],
        "category_performance": json.loads(row["category_breakdown"]) if row["category_breakdown"] else {},
        "weak_categories": json.loads(row["weak_categories"]) if row["weak_categories"] else [],
        "ai_evaluation": ai_eval,
        "is_timeout": bool(row["is_timeout"]) if "is_timeout" in row.keys() else False,
        "created_at": str(row["created_at"])
    }


class AptitudeSolutionsRequest(BaseModel):
    question_ids: List[int]

@router.post("/solutions")
def get_aptitude_solutions(
    payload: AptitudeSolutionsRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Returns authoritative correct answers and explanations for specified question IDs.
    Used for 100% efficient auto-fill and post-review demo presentations.
    """
    if not payload.question_ids:
        return {"solutions": {}}

    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in payload.question_ids)
    cursor.execute(f"""
        SELECT id, correct_answer, explanation 
        FROM aptitude_questions 
        WHERE id IN ({placeholders})
    """, tuple(payload.question_ids))
    rows = cursor.fetchall()
    conn.close()

    solutions = {}
    for r in rows:
        solutions[r["id"]] = {
            "correct_answer": r["correct_answer"],
            "explanation": r["explanation"] if "explanation" in r.keys() else ""
        }
    return {"solutions": solutions}
