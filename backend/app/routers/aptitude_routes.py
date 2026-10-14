from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import time
import random
from ..database import get_db_connection
from ..models import (
    AptitudeQuestionResponse, AptitudeTestSubmit, AptitudeResultResponse
)
from ..auth import get_current_user
from ..services.llm_service import LLMService, gemini_model, _gemini_quota_exhausted, _gemini_quota_exhausted_until
from ..services.cross_module_engine import CrossModuleEngine

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

@router.get("/questions", response_model=List[AptitudeQuestionResponse])
def get_aptitude_questions(
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(10, ge=5, le=30),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetches dynamic aptitude questions.
    Uses Gemini when available to dynamically generate questions tailored to candidate difficulty and weakness.
    Seamlessly falls back to the curated question bank if Gemini is unavailable or rate-limited.
    Guarantees session-aware variation: tracks questions served to this user in recent sessions,
    avoids duplicates within the session, and preserves authoritative objective answer keys.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = current_user["id"]

    # 1. Fetch questions candidate has seen or answered recently
    cursor.execute("""
        SELECT question_id FROM user_served_questions
        WHERE user_id = ? AND module = 'aptitude'
        ORDER BY id DESC LIMIT 100
    """, (user_id,))
    served_ids = [r[0] for r in cursor.fetchall()]

    cursor.execute("""
        SELECT aa.question_id 
        FROM aptitude_answers aa
        JOIN aptitude_attempts at ON aa.attempt_id = at.id
        WHERE at.user_id = ?
        ORDER BY aa.id DESC LIMIT 100
    """, (user_id,))
    answered_ids = [r[0] for r in cursor.fetchall()]

    recent_q_ids = list(dict.fromkeys(served_ids + answered_ids))

    # Retrieve texts of recently seen questions to exclude in prompt
    recent_q_texts = []
    if recent_q_ids:
        placeholders = ",".join("?" for _ in recent_q_ids[:20])
        cursor.execute(f"SELECT question FROM aptitude_questions WHERE id IN ({placeholders})", tuple(recent_q_ids[:20]))
        recent_q_texts = [r["question"] for r in cursor.fetchall()]

    # 2. Check candidate skill state & weak areas for personalization (Requirement 7)
    candidate_profile = CrossModuleEngine.get_candidate_profile(user_id)
    apt_categories_perf = candidate_profile.get("aptitude_categories", {})
    weak_cats = [c for c, sc in apt_categories_perf.items() if sc < 60.0]

    normalized_cat = normalize_category_name(category)

    # 3. Determine category distribution
    if not normalized_cat:
        # Multi-category balanced test
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

        # Target difficulty adaptation
        target_diff = difficulty if (difficulty and difficulty != "All") else None
        if not target_diff:
            cat_score = apt_categories_perf.get(cat_name, 70.0)
            if cat_score < 55.0:
                target_diff = "Beginner"
            elif cat_score > 80.0:
                target_diff = "Advanced"
            else:
                target_diff = "Intermediate"

        # Try Gemini dynamic generation if available and not on quota cooldown
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
                        # Authoritative validation and persistence into DB
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
                            INSERT INTO user_served_questions (user_id, module, question_id)
                            VALUES (?, 'aptitude', ?)
                        """, (user_id, new_q_id))
                        conn.commit()

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
                    break  # If Gemini fails mid-batch, break to fallback bank

        # 5. If needed questions remain for this category (Gemini unavailable or quota), use question bank fallback
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

            # Avoid recently seen questions and avoid questions already in this session
            all_exclude = list(dict.fromkeys(recent_q_ids + session_ids))
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
                    INSERT INTO user_served_questions (user_id, module, question_id)
                    VALUES (?, 'aptitude', ?)
                """, (user_id, r["id"]))
                selected_questions.append({
                    "id": r["id"],
                    "category": r["category"],
                    "difficulty": r["difficulty"],
                    "topic": r["topic"] if "topic" in r.keys() and r["topic"] else r["category"],
                    "question": r["question"],
                    "options": json.loads(r["options"])
                })

            # If still short (e.g. exhausted unattempted questions in bank), pick least recent not in session
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
                        INSERT INTO user_served_questions (user_id, module, question_id)
                        VALUES (?, 'aptitude', ?)
                    """, (user_id, r["id"]))
                    selected_questions.append({
                        "id": r["id"],
                        "category": r["category"],
                        "difficulty": r["difficulty"],
                        "topic": r["topic"] if "topic" in r.keys() and r["topic"] else r["category"],
                        "question": r["question"],
                        "options": json.loads(r["options"])
                    })

    conn.commit()
    conn.close()

    # Shuffle final questions so categories and difficulty order are pleasantly randomized
    random.shuffle(selected_questions)
    return selected_questions[:limit]

@router.post("/submit", response_model=AptitudeResultResponse)
def submit_aptitude_test(
    data: AptitudeTestSubmit,
    current_user: dict = Depends(get_current_user)
):
    """
    Evaluates candidate aptitude answers deterministically against stored answer keys.
    Authoritative objective scoring is calculated in the backend.
    Tracks answers and attempts so future sessions avoid repeating these questions.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = current_user["id"]
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

    recommendation = (
        f"Targeted Recommendation: Prioritize practice on {', '.join(weak_categories)} "
        "(percentages, ratios, data tables, and graph interpretations) before attempting advanced company assessment tests."
        if weak_categories else
        "Outstanding aptitude proficiency across all evaluated categories! Proceed directly to the Coding Session."
    )

    # Generate rich AI evaluation using Gemini (with automatic rule-based fallback if unavailable)
    # Gemini NEVER overrides the authoritative objective score calculated above.
    ai_evaluation = LLMService.evaluate_aptitude_performance(
        total_questions=total_q,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        overall_score=overall_score,
        category_performance=category_performance,
        weak_categories=weak_categories,
        question_breakdown=question_breakdown
    )

    # Save to aptitude_attempts table including ai_feedback
    cursor.execute("""
        INSERT INTO aptitude_attempts (
            user_id, category, difficulty, total_questions, correct_count,
            incorrect_count, score, time_taken_seconds, category_breakdown, weak_categories, ai_feedback
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, data.category, data.difficulty, total_q, correct_count,
        incorrect_count, overall_score, data.time_taken_seconds,
        json.dumps(category_performance), json.dumps(weak_categories),
        json.dumps(ai_evaluation)
    ))
    attempt_id = cursor.lastrowid

    # Persist into aptitude_answers to record answer history for candidate
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
        "ai_evaluation": ai_evaluation
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

