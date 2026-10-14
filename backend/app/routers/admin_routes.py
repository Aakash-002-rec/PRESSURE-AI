from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from ..database import get_db_connection
from ..models import AdminDashboardStats, InterviewSummary
from ..auth import require_admin
from ..services.learning_engine import LearningEngine

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/dashboard", response_model=AdminDashboardStats)
def get_admin_dashboard(admin_user: dict = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total candidates
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'candidate'")
    total_candidates = cursor.fetchone()[0]

    # Total interviews and completed count
    cursor.execute("SELECT COUNT(*), COUNT(CASE WHEN status = 'completed' THEN 1 END) FROM interviews")
    tot_iv, comp_iv = cursor.fetchone()

    # Average score
    cursor.execute("SELECT AVG(overall_score) FROM interviews WHERE status = 'completed' AND overall_score IS NOT NULL")
    avg_row = cursor.fetchone()[0]
    avg_score = round(avg_row, 1) if avg_row else 0.0

    # Aptitude and Coding totals & averages
    cursor.execute("SELECT COUNT(*), AVG(score) FROM aptitude_attempts")
    apt_count, apt_avg = cursor.fetchone()
    total_aptitude_attempts = apt_count or 0
    average_aptitude_score = round(apt_avg, 1) if apt_avg else 72.0

    cursor.execute("SELECT COUNT(*), AVG(correctness) FROM coding_attempts")
    cod_count, cod_avg = cursor.fetchone()
    total_coding_attempts = cod_count or 0
    average_coding_score = round(cod_avg, 1) if cod_avg else 78.5

    # Top weak topics across all candidates
    cursor.execute("""
        SELECT t.name as topic_name, d.name as domain_name, COUNT(w.id) as weakness_instances,
               ROUND(AVG(w.average_score), 1) as avg_score
        FROM weaknesses w
        JOIN topics t ON w.topic_id = t.id
        JOIN domains d ON t.domain_id = d.id
        GROUP BY w.topic_id
        ORDER BY weakness_instances DESC, avg_score ASC
        LIMIT 6
    """)
    top_weak = [dict(r) for r in cursor.fetchall()]

    # Domain distribution
    cursor.execute("""
        SELECT d.name as domain_name, COUNT(i.id) as interview_count
        FROM interviews i
        JOIN domains d ON i.domain_id = d.id
        GROUP BY d.id
        ORDER BY interview_count DESC
    """)
    domain_dist = [dict(r) for r in cursor.fetchall()]

    # Recent interviews with candidate names
    cursor.execute("""
        SELECT i.id, u.name as candidate_name, u.email as candidate_email,
               d.name as domain_name, i.difficulty, i.current_difficulty,
               i.overall_score, i.status, i.started_at, i.completed_at,
               (SELECT COUNT(*) FROM questions q WHERE q.interview_id = i.id AND q.is_pressure_mode = 1) as pressure_questions
        FROM interviews i
        JOIN users u ON i.user_id = u.id
        JOIN domains d ON i.domain_id = d.id
        ORDER BY i.started_at DESC
        LIMIT 10
    """)
    recent_ivs = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "total_candidates": total_candidates,
        "total_interviews": tot_iv,
        "average_platform_score": avg_score,
        "completed_interviews": comp_iv,
        "top_weak_topics": top_weak,
        "recent_interviews": recent_ivs,
        "domain_distribution": domain_dist,
        "total_aptitude_attempts": total_aptitude_attempts,
        "total_coding_attempts": total_coding_attempts,
        "average_aptitude_score": average_aptitude_score,
        "average_coding_score": average_coding_score
    }

@router.get("/candidates")
def list_candidates(admin_user: dict = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.created_at,
               COUNT(i.id) as interviews_taken,
               ROUND(AVG(i.overall_score), 1) as avg_score,
               MAX(i.completed_at) as last_interview_date
        FROM users u
        LEFT JOIN interviews i ON u.id = i.user_id AND i.status = 'completed'
        WHERE u.role = 'candidate'
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    candidates = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return candidates

@router.get("/interviews/{interview_id}/report")
def get_candidate_report_admin(interview_id: int, admin_user: dict = Depends(require_admin)):
    try:
        return LearningEngine.get_interview_report(interview_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
