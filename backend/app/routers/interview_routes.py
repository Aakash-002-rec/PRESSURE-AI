from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
import json
from datetime import datetime
from ..database import get_db_connection
from ..models import (
    InterviewCreate, InterviewSummary, QuestionResponse, AnswerSubmit,
    AnswerEvaluationResponse, HintResponse, InterviewReportResponse,
    LearningRecommendation
)
from ..auth import get_current_user
from ..services.interview_engine import InterviewEngine
from ..services.learning_engine import LearningEngine
from ..services.llm_service import LLMService
from ..services.attempt_service import AttemptService, _calc_remaining_seconds
from ..config import (
    INTERVIEW_TIME_LIMIT_SECONDS,
    INTERVIEW_QUESTION_TIME_LIMIT_SECONDS,
    DEADLINE_GRACE_PERIOD_SECONDS
)

router = APIRouter(tags=["Interviews"])

@router.post("/interviews", response_model=InterviewSummary)
def create_interview(data: InterviewCreate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Enforce strict assessment order (Aptitude -> Coding -> Interview)
        AttemptService.check_stage_access(cursor, current_user["id"], target_stage="interview")
        active_att = AttemptService.get_or_create_active_attempt(cursor, current_user["id"])
        attempt_id = active_att.get("attempt_id")
        conn.commit()
    finally:
        conn.close()

    interview = InterviewEngine.create_interview(
        user_id=current_user["id"],
        domain_id=data.domain_id,
        difficulty=data.difficulty,
        interview_type=data.interview_type,
        total_questions=data.total_questions,
        topic_id=data.topic_id,
        attempt_id=attempt_id
    )

    # Start interview session timer
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        AttemptService.start_interview_session(
            cursor=cursor,
            user_id=current_user["id"],
            attempt_id=attempt_id,
            interview_id=interview["id"],
            duration_seconds=INTERVIEW_TIME_LIMIT_SECONDS
        )
        # Re-fetch interview with updated deadline
        cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview["id"],))
        iv_row = dict(cursor.fetchone())
        conn.commit()
    finally:
        conn.close()

    rem_seconds = _calc_remaining_seconds(iv_row.get("deadline"), INTERVIEW_TIME_LIMIT_SECONDS)

    return {
        "id": interview["id"],
        "user_id": interview["user_id"],
        "domain_id": interview["domain_id"],
        "domain_name": interview["domain_name"],
        "topic_id": interview.get("topic_id"),
        "topic_name": interview.get("topic_name"),
        "difficulty": interview["difficulty"],
        "current_difficulty": interview["current_difficulty"],
        "interview_type": interview["interview_type"],
        "total_questions": interview["total_questions"],
        "answered_questions": 0,
        "overall_score": interview.get("overall_score"),
        "status": interview["status"],
        "pressure_mode_active": bool(interview["pressure_mode_active"]),
        "pressure_topic_name": None,
        "started_at": str(iv_row.get("started_at") or interview["started_at"]),
        "completed_at": str(iv_row.get("completed_at")) if iv_row.get("completed_at") else None,
        "deadline": str(iv_row.get("deadline")) if iv_row.get("deadline") else None,
        "duration_seconds": iv_row.get("duration_seconds") or INTERVIEW_TIME_LIMIT_SECONDS,
        "remaining_seconds": rem_seconds,
        "is_timeout": bool(iv_row.get("is_timeout")),
        "completion_reason": iv_row.get("completion_reason") or "normal",
        "question_time_limit_seconds": INTERVIEW_QUESTION_TIME_LIMIT_SECONDS
    }

@router.get("/interviews", response_model=List[InterviewSummary])
def list_interviews(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, d.name as domain_name, t.name as topic_name,
               (SELECT COUNT(*) FROM answers a JOIN questions q ON a.question_id = q.id WHERE q.interview_id = i.id) as answered_questions,
               pt.name as pressure_topic_name
        FROM interviews i
        JOIN domains d ON i.domain_id = d.id
        LEFT JOIN topics t ON i.topic_id = t.id
        LEFT JOIN topics pt ON i.pressure_topic_id = pt.id
        WHERE i.user_id = ?
        ORDER BY i.started_at DESC
    """, (current_user["id"],))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        rem_sec = None
        if r["status"] == "in_progress" and r["deadline"]:
            rem_sec = _calc_remaining_seconds(r["deadline"], r["duration_seconds"] or INTERVIEW_TIME_LIMIT_SECONDS)
        result.append({
            "id": r["id"],
            "user_id": r["user_id"],
            "domain_id": r["domain_id"],
            "domain_name": r["domain_name"],
            "topic_id": r["topic_id"],
            "topic_name": r["topic_name"],
            "difficulty": r["difficulty"],
            "current_difficulty": r["current_difficulty"],
            "interview_type": r["interview_type"],
            "total_questions": r["total_questions"],
            "answered_questions": r["answered_questions"],
            "overall_score": r["overall_score"],
            "status": r["status"],
            "pressure_mode_active": bool(r["pressure_mode_active"]),
            "pressure_topic_name": r["pressure_topic_name"],
            "started_at": str(r["started_at"]),
            "completed_at": str(r["completed_at"]) if r["completed_at"] else None,
            "deadline": str(r["deadline"]) if r["deadline"] else None,
            "duration_seconds": r["duration_seconds"] or INTERVIEW_TIME_LIMIT_SECONDS,
            "remaining_seconds": rem_sec,
            "is_timeout": bool(r["is_timeout"]),
            "completion_reason": r["completion_reason"] or "normal",
            "question_time_limit_seconds": INTERVIEW_QUESTION_TIME_LIMIT_SECONDS
        })
    return result

@router.get("/interviews/{interview_id}", response_model=InterviewSummary)
def get_interview(interview_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.*, d.name as domain_name, t.name as topic_name,
               (SELECT COUNT(*) FROM answers a JOIN questions q ON a.question_id = q.id WHERE q.interview_id = i.id) as answered_questions,
               pt.name as pressure_topic_name
        FROM interviews i
        JOIN domains d ON i.domain_id = d.id
        LEFT JOIN topics t ON i.topic_id = t.id
        LEFT JOIN topics pt ON i.pressure_topic_id = pt.id
        WHERE i.id = ?
    """, (interview_id,))
    r = cursor.fetchone()

    if not r:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    # Candidate can only view their own unless admin
    if current_user["role"] != "admin" and r["user_id"] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Forbidden")

    rem_sec = None
    if r["status"] == "in_progress" and r["deadline"]:
        rem_sec = _calc_remaining_seconds(r["deadline"], r["duration_seconds"] or INTERVIEW_TIME_LIMIT_SECONDS)
        # Check if deadline passed
        if rem_sec <= 0:
            InterviewEngine.finalize_timeout_interview(interview_id, conn)
            cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
            r = cursor.fetchone()
            rem_sec = 0

    conn.close()

    return {
        "id": r["id"],
        "user_id": r["user_id"],
        "domain_id": r["domain_id"],
        "domain_name": r["domain_name"],
        "topic_id": r["topic_id"],
        "topic_name": r["topic_name"],
        "difficulty": r["difficulty"],
        "current_difficulty": r["current_difficulty"],
        "interview_type": r["interview_type"],
        "total_questions": r["total_questions"],
        "answered_questions": r["answered_questions"],
        "overall_score": r["overall_score"],
        "status": r["status"],
        "pressure_mode_active": bool(r["pressure_mode_active"]),
        "pressure_topic_name": r["pressure_topic_name"],
        "started_at": str(r["started_at"]),
        "completed_at": str(r["completed_at"]) if r["completed_at"] else None,
        "deadline": str(r["deadline"]) if r["deadline"] else None,
        "duration_seconds": r["duration_seconds"] or INTERVIEW_TIME_LIMIT_SECONDS,
        "remaining_seconds": rem_sec,
        "is_timeout": bool(r["is_timeout"]),
        "completion_reason": r["completion_reason"] or "normal",
        "question_time_limit_seconds": INTERVIEW_QUESTION_TIME_LIMIT_SECONDS
    }

@router.post("/interviews/{interview_id}/questions", response_model=Optional[QuestionResponse])
@router.get("/interviews/{interview_id}/questions/next", response_model=Optional[QuestionResponse])
def get_next_question(interview_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    timeout_triggered = False
    try:
        cursor.execute("SELECT user_id, status, deadline, attempt_id, duration_seconds FROM interviews WHERE id = ?", (interview_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Interview not found.")
        if current_user["role"] != "admin" and row["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

        # Check stage access
        AttemptService.check_stage_access(cursor, current_user["id"], target_stage="interview", attempt_id=row["attempt_id"])

        # Deadline validation
        if row["deadline"] and row["status"] == "in_progress":
            rem = _calc_remaining_seconds(row["deadline"], row["duration_seconds"] or INTERVIEW_TIME_LIMIT_SECONDS)
            if rem <= 0:
                InterviewEngine.finalize_timeout_interview(interview_id, conn)
                timeout_triggered = True
    finally:
        conn.close()

    if timeout_triggered:
        return None

    q = InterviewEngine.get_next_question(interview_id)
    return q

@router.post("/questions/{question_id}/answer", response_model=AnswerEvaluationResponse)
def submit_answer(question_id: int, answer: AnswerSubmit, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT i.id as interview_id, i.user_id, i.status, i.deadline, i.attempt_id, i.duration_seconds
            FROM questions q
            JOIN interviews i ON q.interview_id = i.id
            WHERE q.id = ?
        """, (question_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Question not found")
        if current_user["role"] != "admin" and row["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

        # Check stage access
        AttemptService.check_stage_access(cursor, current_user["id"], target_stage="interview", attempt_id=row["attempt_id"])

        # Deadline validation
        if row["deadline"] and row["status"] == "in_progress":
            rem = _calc_remaining_seconds(row["deadline"], row["duration_seconds"] or INTERVIEW_TIME_LIMIT_SECONDS)
            if rem <= -DEADLINE_GRACE_PERIOD_SECONDS:
                InterviewEngine.finalize_timeout_interview(row["interview_id"], conn)
                raise HTTPException(
                    status_code=400,
                    detail="Interview deadline has expired. Submissions are closed."
                )
    finally:
        conn.close()

    try:
        res = InterviewEngine.submit_answer(
            question_id=question_id,
            answer_text=answer.answer_text,
            code_answer=answer.code_answer,
            time_spent_seconds=answer.time_spent_seconds or 0
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer processing error: {str(e)}")

@router.post("/questions/{question_id}/hint", response_model=HintResponse)
def request_hint(question_id: int, current_user: dict = Depends(get_current_user)):
    try:
        res = InterviewEngine.request_hint(question_id)
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/{question_id}/model-answer")
def get_model_answer(question_id: int, current_user: dict = Depends(get_current_user)):
    """
    Returns an authoritative 100% comprehensive model answer for the interview question,
    guaranteeing maximum evaluation scores on correctness, completeness, and conceptual depth.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.*, t.name as topic_name, d.name as domain_name, i.user_id
        FROM questions q
        JOIN interviews i ON q.interview_id = i.id
        JOIN topics t ON q.topic_id = t.id
        JOIN domains d ON i.domain_id = d.id
        WHERE q.id = ?
    """, (question_id,))
    q_row = cursor.fetchone()
    conn.close()

    if not q_row:
        raise HTTPException(status_code=404, detail="Question not found")

    expected_concepts = []
    if q_row["expected_concepts"]:
        try:
            expected_concepts = json.loads(q_row["expected_concepts"])
        except Exception:
            expected_concepts = [q_row["topic_name"]]

    model_answer = LLMService.generate_model_interview_answer(
        question_text=q_row["question_text"],
        topic=q_row["topic_name"],
        expected_concepts=expected_concepts,
        evaluation_criteria=q_row["evaluation_criteria"],
        question_type=q_row["question_type"],
        difficulty=q_row["difficulty"],
        starter_code=q_row["starter_code"],
        code_snippet=q_row["code_snippet"],
        domain=q_row["domain_name"]
    )

    return {
        "question_id": question_id,
        "answer_text": model_answer["answer_text"],
        "code_answer": model_answer.get("code_answer", ""),
        "expected_concepts": expected_concepts
    }

@router.get("/interviews/{interview_id}/report", response_model=InterviewReportResponse)
def get_interview_report(interview_id: int, current_user: dict = Depends(get_current_user)):
    try:
        report = LearningEngine.get_interview_report(interview_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/interviews/{interview_id}/recommendations", response_model=List[LearningRecommendation])
def get_recommendations(interview_id: int, current_user: dict = Depends(get_current_user)):
    try:
        report = LearningEngine.get_interview_report(interview_id)
        return report.get("recommendations", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
