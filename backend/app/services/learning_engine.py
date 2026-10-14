import json
from typing import Dict, List, Any, Optional
from ..database import get_db_connection

class LearningEngine:
    @staticmethod
    def get_interview_report(interview_id: int) -> Dict[str, Any]:
        """Compiles the comprehensive post-interview performance report and roadmap."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch interview + user info
        cursor.execute("""
            SELECT i.*, u.name as candidate_name, d.name as domain_name
            FROM interviews i
            JOIN users u ON i.user_id = u.id
            JOIN domains d ON i.domain_id = d.id
            WHERE i.id = ?
        """, (interview_id,))
        interview = cursor.fetchone()
        if not interview:
            conn.close()
            raise ValueError(f"Interview {interview_id} not found.")

        # Category scores
        category_scores = {
            "Technical Knowledge": round(interview["technical_score"] or 0.0, 1),
            "Conceptual Understanding": round(interview["conceptual_score"] or 0.0, 1),
            "Problem Solving": round(interview["problem_solving_score"] or 0.0, 1),
            "Communication": round(interview["communication_score"] or 0.0, 1),
        }

        # Topic performances
        cursor.execute("""
            SELECT 
                q.topic_id, t.name as topic_name,
                AVG(a.overall_score) * 10 as score,
                COUNT(a.id) as attempts
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            JOIN topics t ON q.topic_id = t.id
            WHERE q.interview_id = ?
            GROUP BY q.topic_id
            ORDER BY score DESC
        """, (interview_id,))
        topic_rows = cursor.fetchall()

        topic_performances = []
        strong_areas = []
        weak_areas = []

        for row in topic_rows:
            score = round(row["score"], 1)
            # Find missing concepts for this topic
            cursor.execute("""
                SELECT a.missing_concepts FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE q.interview_id = ? AND q.topic_id = ?
            """, (interview_id, row["topic_id"]))
            missing_set = []
            for mc in cursor.fetchall():
                if mc["missing_concepts"]:
                    try:
                        missing_set.extend(json.loads(mc["missing_concepts"]))
                    except Exception:
                        pass
            
            w_level = "Strong" if score >= 75.0 else ("Average" if score >= 60.0 else "Weak")
            if score >= 75.0:
                strong_areas.append(row["topic_name"])
            elif score < 65.0:
                weak_areas.append(row["topic_name"])

            topic_performances.append({
                "topic_id": row["topic_id"],
                "topic_name": row["topic_name"],
                "score": score,
                "attempts": row["attempts"],
                "weakness_level": w_level,
                "missing_concepts": list(dict.fromkeys(missing_set))
            })

        # Pressure mode topics
        cursor.execute("""
            SELECT DISTINCT t.name FROM questions q
            JOIN topics t ON q.topic_id = t.id
            WHERE q.interview_id = ? AND q.is_pressure_mode = 1
        """, (interview_id,))
        pressure_topics = [r["name"] for r in cursor.fetchall()]

        # Questions detail
        cursor.execute("""
            SELECT 
                q.sequence_number, t.name as topic_name, q.question_text,
                q.difficulty, q.question_type, q.is_pressure_mode,
                a.answer_text, a.overall_score * 10 as score, a.feedback,
                a.missing_concepts, a.hints_used
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            LEFT JOIN answers a ON q.id = a.question_id
            WHERE q.interview_id = ?
            ORDER BY q.sequence_number ASC
        """, (interview_id,))
        q_rows = cursor.fetchall()

        questions_detail = []
        for qr in q_rows:
            missing = []
            if qr["missing_concepts"]:
                try:
                    missing = json.loads(qr["missing_concepts"])
                except Exception:
                    pass
            questions_detail.append({
                "sequence_number": qr["sequence_number"],
                "topic_name": qr["topic_name"],
                "question_text": qr["question_text"],
                "difficulty": qr["difficulty"],
                "question_type": qr["question_type"],
                "is_pressure_mode": bool(qr["is_pressure_mode"]),
                "answer_text": qr["answer_text"],
                "score": round(qr["score"], 1) if qr["score"] is not None else 0.0,
                "feedback": qr["feedback"],
                "missing_concepts": missing,
                "hints_used": qr["hints_used"] or 0
            })

        # Recommendations from DB
        cursor.execute("""
            SELECT * FROM recommendations WHERE interview_id = ?
        """, (interview_id,))
        rec_rows = cursor.fetchall()

        recommendations = []
        for rr in rec_rows:
            recommendations.append({
                "topic_id": rr["topic_id"],
                "topic_name": rr["topic_name"],
                "performance_score": rr["performance_score"],
                "why_weak": json.loads(rr["why_weak"]),
                "concepts_to_learn": json.loads(rr["concepts_to_learn"]),
                "action_plan": json.loads(rr["action_plan"]),
                "practice_questions": json.loads(rr["practice_questions"])
            })

        # Generate 5-Stage Roadmap based on weak or primary topics
        lead_weak_topic = weak_areas[0] if weak_areas else (topic_performances[-1]["topic_name"] if topic_performances else interview["domain_name"])
        second_topic = weak_areas[1] if len(weak_areas) > 1 else (strong_areas[0] if strong_areas else f"{interview['domain_name']} Core Architecture")

        learning_roadmap = [
            {
                "stage_number": 1,
                "title": f"Phase 1: {lead_weak_topic} Fundamentals & Core Syntax",
                "focus_topic": lead_weak_topic,
                "action_items": [
                    f"Review official documentation and core conventions for {lead_weak_topic}",
                    "Trace 3 code patterns step-by-step using visual flowcharts or print debugging",
                    "Eliminate reliance on hints for standard definition and baseline syntax"
                ],
                "estimated_duration": "2 - 3 Days",
                "objective": "Build unshakeable foundation on standard syntax and execution primitives."
            },
            {
                "stage_number": 2,
                "title": f"Phase 2: Boundary Conditions & Edge Case Drills",
                "focus_topic": lead_weak_topic,
                "action_items": [
                    f"Solve 4 medium exercises focusing strictly on empty inputs, null pointers, and limits",
                    "Trace stack depth or memory footprint for non-trivial executions",
                    "Write unit tests verifying failure modes and defensive checks"
                ],
                "estimated_duration": "3 - 4 Days",
                "objective": "Ensure robust handling of non-standard and stress parameters."
            },
            {
                "stage_number": 3,
                "title": f"Phase 3: Deep Architectural Mechanics & {second_topic}",
                "focus_topic": second_topic,
                "action_items": [
                    f"Analyze runtime internals: how memory and threads operate for {second_topic}",
                    "Compare performance trade-offs (time complexity vs space complexity)",
                    "Implement a modular demo combining both concepts"
                ],
                "estimated_duration": "4 - 5 Days",
                "objective": "Bridge theoretical understanding with industrial-grade software engineering."
            },
            {
                "stage_number": 4,
                "title": "Phase 4: Pressure Simulation & Time-Constrained Coding",
                "focus_topic": f"{interview['domain_name']} Advanced Problem Solving",
                "action_items": [
                    "Complete 5 timed problems (15 minutes each) without looking at solutions",
                    "Practice verbalizing trade-offs before writing the first line of code",
                    "Review top interview pitfalls for modern senior-level roles"
                ],
                "estimated_duration": "3 Days",
                "objective": "Eliminate interview panic and execute accurately under simulated pressure."
            },
            {
                "stage_number": 5,
                "title": "Phase 5: Retake PRESSURE-AI Adaptive Interview",
                "focus_topic": "Verification & Progress Comparison",
                "action_items": [
                    "Launch a 10-question Advanced adaptive interview on PRESSURE-AI",
                    "Verify topic scores surpass 80% with zero pressure mode activations",
                    "Inspect longitudinal progress chart and track upward delta"
                ],
                "estimated_duration": "1 Day",
                "objective": "Certify measurable score improvement and readiness for live technical interviews."
            }
        ]

        conn.close()

        return {
            "interview_id": interview_id,
            "candidate_name": interview["candidate_name"],
            "domain_name": interview["domain_name"],
            "difficulty_configured": interview["difficulty"],
            "final_difficulty": interview["current_difficulty"],
            "interview_type": interview["interview_type"],
            "total_questions": interview["total_questions"],
            "questions_attempted": len(questions_detail),
            "started_at": str(interview["started_at"]),
            "completed_at": str(interview["completed_at"]) if interview["completed_at"] else None,
            "overall_score": round(interview["overall_score"] or 0.0, 1),
            "category_scores": category_scores,
            "topic_performance": topic_performances,
            "strong_areas": strong_areas,
            "weak_areas": weak_areas,
            "pressure_mode_topics": pressure_topics,
            "hints_used_total": interview["hints_used_total"],
            "questions_detail": questions_detail,
            "recommendations": recommendations,
            "learning_roadmap": learning_roadmap
        }

    @staticmethod
    def get_user_progress(user_id: int) -> Dict[str, Any]:
        """Calculates multi-interview progress tracking and topic improvement deltas."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all completed interviews for user
        cursor.execute("""
            SELECT i.*, d.name as domain_name
            FROM interviews i
            JOIN domains d ON i.domain_id = d.id
            WHERE i.user_id = ? AND i.status = 'completed'
            ORDER BY i.completed_at ASC
        """, (user_id,))
        interviews = cursor.fetchall()

        if not interviews:
            conn.close()
            return {
                "total_interviews_completed": 0,
                "average_score": 0.0,
                "best_score": 0.0,
                "strongest_topics": [],
                "persistent_weak_topics": [],
                "topic_improvements": [],
                "history": []
            }

        history = []
        scores = []
        for iv in interviews:
            score = round(iv["overall_score"] or 0.0, 1)
            scores.append(score)

            # Check weak topics count and pressure mode for this interview
            cursor.execute("SELECT COUNT(*) FROM weaknesses WHERE interview_id = ?", (iv["id"],))
            weak_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM questions WHERE interview_id = ? AND is_pressure_mode = 1", (iv["id"],))
            pressure_count = cursor.fetchone()[0]

            history.append({
                "interview_id": iv["id"],
                "domain_name": iv["domain_name"],
                "started_at": str(iv["started_at"]),
                "completed_at": str(iv["completed_at"]),
                "total_questions": iv["total_questions"],
                "overall_score": score,
                "difficulty": iv["difficulty"],
                "weak_topics_count": weak_count,
                "pressure_mode_triggered": pressure_count > 0
            })

        # Calculate topic progress deltas across interviews
        cursor.execute("""
            SELECT 
                t.name as topic_name,
                a.overall_score * 10 as score,
                i.completed_at
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            JOIN topics t ON q.topic_id = t.id
            JOIN interviews i ON q.interview_id = i.id
            WHERE i.user_id = ? AND i.status = 'completed'
            ORDER BY i.completed_at ASC
        """, (user_id,))
        records = cursor.fetchall()

        # Group scores by topic
        topic_timeline: Dict[str, List[float]] = {}
        for r in records:
            t_name = r["topic_name"]
            if t_name not in topic_timeline:
                topic_timeline[t_name] = []
            topic_timeline[t_name].append(round(r["score"], 1))

        topic_improvements = []
        strongest_topics = []
        persistent_weak = []

        for t_name, sc_list in topic_timeline.items():
            first_score = sc_list[0]
            latest_score = sc_list[-1]
            delta = round(latest_score - first_score, 1)
            attempts = len(sc_list)

            if latest_score >= 75.0:
                strongest_topics.append(t_name)
            elif latest_score < 60.0:
                persistent_weak.append(t_name)

            if attempts > 1 or delta != 0:
                trend = "improved" if delta > 0 else ("declined" if delta < 0 else "stable")
                if delta > 0:
                    msg = f"Your {t_name} performance improved from {first_score}% to {latest_score}% (+{delta}%)."
                elif delta < 0:
                    msg = f"Your {t_name} performance slipped from {first_score}% to {latest_score}% ({delta}%)."
                else:
                    msg = f"Your {t_name} performance remained consistent at {latest_score}% across {attempts} evaluations."

                topic_improvements.append({
                    "topic_name": t_name,
                    "first_score": first_score,
                    "latest_score": latest_score,
                    "delta": delta,
                    "trend": trend,
                    "attempts_count": attempts,
                    "message": msg
                })

        conn.close()

        return {
            "total_interviews_completed": len(interviews),
            "average_score": round(sum(scores) / len(scores), 1),
            "best_score": max(scores),
            "strongest_topics": list(dict.fromkeys(strongest_topics))[:5],
            "persistent_weak_topics": list(dict.fromkeys(persistent_weak))[:5],
            "topic_improvements": sorted(topic_improvements, key=lambda x: x["delta"], reverse=True),
            "history": history
        }
