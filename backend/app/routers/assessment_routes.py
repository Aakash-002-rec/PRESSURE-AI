from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from ..database import get_db_connection
from ..models import (
    CombinedAssessmentResponse, PracticeQuestionResponse, PracticeSubmitRequest,
    PracticeResultResponse, RoadmapTaskItem, RoadmapTaskUpdate,
    AssessmentAttemptResponse, AssessmentRetestResponse, AssessmentDetailReportResponse
)
from ..auth import get_current_user
from ..services.cross_module_engine import CrossModuleEngine
from ..services.attempt_service import AttemptService

router = APIRouter(tags=["Placement Assessment"])

@router.get("/assessments/combined", response_model=CombinedAssessmentResponse)
def get_combined_assessment(current_user: dict = Depends(get_current_user)):
    """Generates the unified Candidate Skill Profile synthesizing Aptitude, Coding, and AI Mock Interviews."""
    profile = CrossModuleEngine.get_candidate_profile(current_user["id"])
    return profile

@router.get("/roadmap/tasks", response_model=List[RoadmapTaskItem])
def get_roadmap_tasks(topic: Optional[str] = Query(None), current_user: dict = Depends(get_current_user)):
    """Fetches the 5-step personalized learning roadmap tasks with candidate interactive status."""
    conn = get_db_connection()
    cursor = conn.cursor()

    user_id = current_user["id"]
    if not topic:
        topic = CrossModuleEngine.get_candidate_recent_weak_topic(user_id) or "Recursion"

    cursor.execute("""
        SELECT * FROM roadmap_tasks
        WHERE user_id = ? AND topic = ?
        ORDER BY stage_number ASC
    """, (user_id, topic))
    rows = cursor.fetchall()

    if not rows:
        # Generate default 5-step roadmap tasks for this topic
        default_stages = [
            (1, f"Phase 1: Revise {topic} Core Mechanics & Syntax", "Build fundamental understanding of core invariants without relying on hints."),
            (2, f"Phase 2: Practice Basic {topic} Exercises", "Implement canonical baseline problems to establish confident muscle memory."),
            (3, f"Phase 3: Boundary Conditions & Edge Case Drills", "Stress test solutions with empty inputs, negative numbers, and boundary limits."),
            (4, f"Phase 4: Attempt {topic} Mini-Assessment Under Time Limit", "Solve timed problems to simulate interview stress conditions."),
            (5, "Phase 5: Retake PRESSURE-AI Adaptive Interview", "Conquer the AI interviewer in Pressure Mode and prove measurable score improvement.")
        ]
        for s_num, title, obj in default_stages:
            cursor.execute("""
                INSERT OR IGNORE INTO roadmap_tasks (user_id, topic, stage_number, title, objective, status)
                VALUES (?, ?, ?, ?, ?, 'not_started')
            """, (user_id, topic, s_num, title, obj))
        conn.commit()

        cursor.execute("""
            SELECT * FROM roadmap_tasks
            WHERE user_id = ? AND topic = ?
            ORDER BY stage_number ASC
        """, (user_id, topic))
        rows = cursor.fetchall()

    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "topic": r["topic"],
            "stage_number": r["stage_number"],
            "title": r["title"],
            "objective": r["objective"],
            "status": r["status"],
            "completed_at": str(r["completed_at"]) if r["completed_at"] else None
        })
    return result

@router.post("/roadmap/tasks/update")
def update_roadmap_task_status(data: RoadmapTaskUpdate, current_user: dict = Depends(get_current_user)):
    """Updates candidate roadmap task state ('not_started', 'in_progress', 'completed')."""
    conn = get_db_connection()
    cursor = conn.cursor()

    completed_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if data.status == "completed" else None
    cursor.execute("""
        UPDATE roadmap_tasks
        SET status = ?, completed_at = ?
        WHERE id = ? AND user_id = ?
    """, (data.status, completed_ts, data.task_id, current_user["id"]))
    conn.commit()
    conn.close()

    return {"status": "success", "task_id": data.task_id, "new_status": data.status}

@router.get("/practice/questions", response_model=List[PracticeQuestionResponse])
def get_practice_questions(
    topic: Optional[str] = Query("Recursion"),
    difficulty: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Fetches targeted practice questions for weak concepts (3 Easy, 3 Medium, 2 Advanced)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, topic, difficulty, question, options FROM practice_questions WHERE topic = ?"
    params = [topic]

    if difficulty and difficulty != "All":
        query += " AND difficulty = ?"
        params.append(difficulty)

    query += " ORDER BY id ASC"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "topic": r["topic"],
            "difficulty": r["difficulty"],
            "question": r["question"],
            "options": json.loads(r["options"]) if r["options"] else []
        })
    return result

@router.post("/practice/submit", response_model=PracticeResultResponse)
def submit_practice_answers(data: PracticeSubmitRequest, current_user: dict = Depends(get_current_user)):
    """
    Grades targeted practice exercises, updates candidate topic score,
    and logs the measurable improvement delta.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    correct_count = 0
    details = []

    for item in data.answers:
        cursor.execute("SELECT correct_answer, explanation FROM practice_questions WHERE id = ?", (item.question_id,))
        row = cursor.fetchone()
        if not row:
            continue
        is_corr = (item.selected_option == row["correct_answer"])
        if is_corr:
            correct_count += 1
        details.append({
            "question_id": item.question_id,
            "is_correct": is_corr,
            "correct_answer": row["correct_answer"],
            "explanation": row["explanation"]
        })

    total_q = max(len(data.answers), 1)
    score = round((correct_count / total_q) * 100, 1)

    # Persist practice attempt
    cursor.execute("""
        INSERT INTO practice_attempts (user_id, topic, difficulty, score, total_questions, correct_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (current_user["id"], data.topic, data.difficulty, score, total_q, correct_count))

    # Calculate updated topic score reflecting actual practice result (e.g. 42% -> 71% -> 81%)
    cursor.execute("""
        SELECT score FROM practice_attempts
        WHERE user_id = ? AND topic = ?
        ORDER BY created_at ASC
    """, (current_user["id"], data.topic))
    all_scores = [r["score"] for r in cursor.fetchall()]

    initial_score = all_scores[0]
    latest_score = all_scores[-1]
    delta = round(latest_score - initial_score, 1)

    # Calculate effective updated score
    updated_topic_score = round(latest_score, 1)
    if delta > 0:
        improvement_msg = f"Your mastery of {data.topic} improved by +{delta} percentage points ({initial_score}% → {latest_score}%)!"
    else:
        improvement_msg = f"Practice recorded: {latest_score}% on {data.topic}. Keep practicing to solidify mastery!"

    conn.commit()
    conn.close()

    return {
        "topic": data.topic,
        "difficulty": data.difficulty,
        "score": score,
        "total_questions": total_q,
        "correct_count": correct_count,
        "updated_topic_score": updated_topic_score,
        "improvement_message": improvement_msg,
        "details": details
    }

@router.get("/assessment/attempt/current", response_model=AssessmentAttemptResponse)
def get_current_assessment_attempt(current_user: dict = Depends(get_current_user)):
    """
    Returns the currently active assessment attempt for the logged-in user.
    If no active attempt exists, initializes a fresh unified attempt.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    attempt = AttemptService.get_or_create_active_attempt(cursor, current_user["id"])
    conn.commit()
    conn.close()
    return attempt

@router.post("/assessment/retest", response_model=AssessmentRetestResponse)
@router.post("/assessment/attempt/new", response_model=AssessmentRetestResponse)
def start_assessment_retest(current_user: dict = Depends(get_current_user)):
    """
    Starts a fresh full retest across Aptitude, Coding Assessment (0 of 3), and AI Mock Interview.
    - Generates a unique attempt_id.
    - Preserves historical records in the database.
    - Resets all completion flags and question counters for the new attempt.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    new_attempt = AttemptService.start_retest_attempt(cursor, current_user["id"])
    conn.commit()
    conn.close()

    from .coding_routes import get_coding_status
    c_status = get_coding_status(current_user=current_user)

    return AssessmentRetestResponse(
        success=True,
        message="Fresh assessment attempt initialized successfully across Aptitude, Coding, and AI Mock Interview.",
        new_attempt=new_attempt,
        coding_status=c_status,
        attempt_id=new_attempt["attempt_id"],
        coding_session_id=new_attempt.get("coding_session_id")
    )

@router.get("/assessment/attempts/history", response_model=List[AssessmentAttemptResponse])
def get_assessment_attempt_history(current_user: dict = Depends(get_current_user)):
    """Returns past assessment attempts for this user, newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    history = AttemptService.get_attempt_history(cursor, current_user["id"])
    conn.close()
    return history

@router.get("/assessment/attempt/{attempt_id}/report", response_model=AssessmentDetailReportResponse)
def get_assessment_attempt_report(attempt_id: str, current_user: dict = Depends(get_current_user)):
    """
    Returns the comprehensive synthesized performance report for a specific assessment attempt.
    Enforces user ownership check.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, aptitude_status, coding_status, interview_status FROM assessment_attempts WHERE attempt_id = ?", (attempt_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Assessment attempt not found.")
    if current_user["role"] != "admin" and row["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot access another candidate's assessment report.")

    report = CrossModuleEngine.get_attempt_performance_report(user_id=current_user["id"], attempt_id=attempt_id)
    return report

@router.get("/assessment/report/latest", response_model=AssessmentDetailReportResponse)
def get_latest_assessment_report(current_user: dict = Depends(get_current_user)):
    """Returns the performance report for the candidate's latest attempt."""
    report = CrossModuleEngine.get_attempt_performance_report(user_id=current_user["id"], attempt_id=None)
    return report


