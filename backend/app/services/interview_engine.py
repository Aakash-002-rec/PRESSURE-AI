import json
import logging
import threading
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from ..database import get_db_connection
from .llm_service import LLMService, DOMAIN_CODE_LANG_MAP
from .fallback_bank import find_fallback_question
from .question_deduplicator import is_duplicate_against_history, compute_question_fingerprint

logger = logging.getLogger("pressure_ai.engine")

_session_locks = defaultdict(threading.Lock)

DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"]
QUESTION_TYPES = [
    "Definition", "Conceptual", "Example-based", "Scenario-based", 
    "Debugging", "Coding", "Output prediction", "Comparison", 
    "Why/how", "Problem-solving"
]

NON_CODING_DOMAINS = {"computer networks", "operating systems"}

def determine_target_question_type(
    sequence_number: int,
    total_questions: int,
    domain_name: str,
    interview_type: str = "Technical"
) -> str:
    """
    Determines balanced target question type ensuring a varied mix across the session.
    For a 10-question interview, targets:
    - 4 conceptual technical questions
    - 3 scenario-based or problem-solving questions
    - 2 practical coding, SQL-query, or technical-task questions where appropriate
    - 1 debugging, design, or trade-off question

    For domains where writing code is inappropriate (Networks, OS), replaces coding
    questions with technical scenarios, architecture, and system trade-offs.
    """
    domain_clean = (domain_name or "").strip().lower()
    is_non_code_domain = domain_clean in NON_CODING_DOMAINS

    if interview_type == "Conceptual":
        types = ["conceptual", "conceptual", "tradeoff", "conceptual", "scenario", "conceptual", "comparison", "conceptual", "tradeoff", "scenario"]
        return types[(sequence_number - 1) % len(types)]
    elif interview_type == "Coding" and not is_non_code_domain:
        types = ["coding", "debugging", "coding", "debugging", "coding", "coding", "debugging", "coding", "debugging", "coding"]
        return types[(sequence_number - 1) % len(types)]

    slot = (sequence_number - 1) % 10

    if is_non_code_domain:
        # Non-code domains: 4 conceptual, 4 scenario, 1 design, 1 tradeoff (0 coding)
        pattern = [
            "conceptual",  # 1
            "scenario",    # 2
            "conceptual",  # 3
            "scenario",    # 4
            "scenario",    # 5
            "conceptual",  # 6
            "design",      # 7
            "conceptual",  # 8
            "tradeoff",    # 9
            "scenario",    # 10
        ]
        return pattern[slot]

    if domain_clean in ("sql", "dbms"):
        # SQL/DBMS: practical tasks are query-focused
        pattern = [
            "conceptual",  # 1 (Normalization / ACID)
            "scenario",    # 2 (Scaling / Index trade-offs)
            "conceptual",  # 3 (JOINs / Aggregations)
            "coding",      # 4 (SQL query task)
            "scenario",    # 5 (Transaction isolation / Concurrency)
            "conceptual",  # 6 (Index structures B-Tree)
            "coding",      # 7 (Complex query / Schema task)
            "conceptual",  # 8 (Constraints / Keys)
            "tradeoff",    # 9 (Normalization vs Denormalization)
            "scenario",    # 10 (Production query optimization)
        ]
        return pattern[slot]

    # Standard programming domains (Python, JavaScript, C, C++, Java, etc.):
    # 4 conceptual, 3 scenario, 2 coding, 1 tradeoff/debugging
    pattern = [
        "conceptual",  # 1
        "scenario",    # 2
        "conceptual",  # 3
        "coding",      # 4
        "scenario",    # 5
        "conceptual",  # 6
        "coding",      # 7
        "conceptual",  # 8
        "tradeoff",    # 9
        "scenario",    # 10
    ]
    return pattern[slot]

class InterviewEngine:
    @staticmethod
    def create_interview(
        user_id: int,
        domain_id: int,
        difficulty: str,
        interview_type: str,
        total_questions: int,
        topic_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Initializes a new interview session."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO interviews (
                user_id, domain_id, topic_id, difficulty, current_difficulty,
                interview_type, total_questions, status, pressure_mode_active,
                consecutive_weak_count, hints_used_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'in_progress', 0, 0, 0)
        """, (user_id, domain_id, topic_id, difficulty, difficulty, interview_type, total_questions))
        
        interview_id = cursor.lastrowid
        conn.commit()

        # Fetch the created interview details
        cursor.execute("""
            SELECT i.*, d.name as domain_name, t.name as topic_name
            FROM interviews i
            JOIN domains d ON i.domain_id = d.id
            LEFT JOIN topics t ON i.topic_id = t.id
            WHERE i.id = ?
        """, (interview_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row)

    @staticmethod
    def get_next_question(interview_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets the current unanswered question, or generates the next adaptive question.
        Returns None if total questions completed.
        """
        with _session_locks[interview_id]:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check interview status
            cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
            interview = cursor.fetchone()
            if not interview or interview["status"] != "in_progress":
                conn.close()
                return None

            # Check if there is already an unanswered question
            cursor.execute("""
                SELECT q.*, t.name as topic_name, d.name as domain_name,
                       (SELECT COUNT(*) FROM hint_logs h WHERE h.question_id = q.id) as hints_used
                FROM questions q
                JOIN topics t ON q.topic_id = t.id
                JOIN interviews i ON q.interview_id = i.id
                JOIN domains d ON i.domain_id = d.id
                LEFT JOIN answers a ON q.id = a.question_id
                WHERE q.interview_id = ? AND a.id IS NULL
                ORDER BY q.sequence_number ASC LIMIT 1
            """, (interview_id,))
            existing_question = cursor.fetchone()

            if existing_question:
                q_dict = dict(existing_question)
                hints_used = q_dict.get("hints_used", 0)
                dom_name = q_dict.get("domain_name", "General")
                mapped_lang = DOMAIN_CODE_LANG_MAP.get(dom_name.strip().lower(), "text")
                conn.close()
                q_type_str = str(q_dict.get("question_type") or "").strip().lower()
                if q_type_str in ("conceptual", "scenario", "tradeoff", "design", "comparison", "definition") or dom_name.strip().lower() in ("computer networks", "operating systems"):
                    curr_code_snip = None
                    curr_starter_cd = None
                else:
                    curr_code_snip = q_dict.get("code_snippet")
                    curr_starter_cd = q_dict.get("starter_code")

                return {
                    "id": q_dict["id"],
                    "interview_id": q_dict["interview_id"],
                    "topic_id": q_dict["topic_id"],
                    "topic_name": q_dict["topic_name"],
                    "sequence_number": q_dict["sequence_number"],
                    "total_questions": interview["total_questions"],
                    "question_text": q_dict["question_text"],
                    "difficulty": q_dict["difficulty"],
                    "question_type": q_dict["question_type"],
                    "hints_used": hints_used,
                    "hints_available": max(0, 3 - hints_used),
                    "is_pressure_mode": bool(q_dict["is_pressure_mode"]),
                    "difficulty_transition_reason": q_dict.get("difficulty_transition_reason"),
                    "code_snippet": curr_code_snip,
                    "code_language": q_dict.get("code_language") or mapped_lang,
                    "starter_code": curr_starter_cd,
                    "fingerprint": q_dict.get("fingerprint")
                }

            # Check if interview is finished
            cursor.execute("SELECT COUNT(*) FROM questions WHERE interview_id = ?", (interview_id,))
            current_count = cursor.fetchone()[0]

            if current_count >= interview["total_questions"]:
                conn.close()
                return None

            next_sequence = current_count + 1
            is_pressure = bool(interview["pressure_mode_active"])
            target_difficulty = interview["current_difficulty"]

            # Query all questions delivered in current session with full details
            cursor.execute("""
                SELECT q.id, q.question_text, q.topic_id, q.difficulty, q.question_type,
                       q.expected_concepts, q.fingerprint, t.name as topic_name, d.name as domain_name
                FROM questions q
                JOIN topics t ON q.topic_id = t.id
                JOIN interviews i ON q.interview_id = i.id
                JOIN domains d ON i.domain_id = d.id
                WHERE q.interview_id = ?
                ORDER BY q.sequence_number ASC
            """, (interview_id,))
            curr_session_questions = []
            for r in cursor.fetchall():
                exp_c = []
                if r["expected_concepts"]:
                    try:
                        exp_c = json.loads(r["expected_concepts"])
                    except Exception:
                        exp_c = [r["topic_name"]]
                curr_session_questions.append({
                    "id": r["id"],
                    "question_text": r["question_text"],
                    "topic_id": r["topic_id"],
                    "topic": r["topic_name"],
                    "domain": r["domain_name"],
                    "difficulty": r["difficulty"],
                    "question_type": r["question_type"],
                    "expected_concepts": exp_c,
                    "fingerprint": r["fingerprint"]
                })

            # Query cross-session recent questions for the same user and domain
            cursor.execute("""
                SELECT q.id, q.question_text, q.topic_id, q.difficulty, q.question_type,
                       q.expected_concepts, q.fingerprint, t.name as topic_name, d.name as domain_name
                FROM questions q
                JOIN topics t ON q.topic_id = t.id
                JOIN interviews i ON q.interview_id = i.id
                JOIN domains d ON i.domain_id = d.id
                WHERE i.user_id = ? AND i.domain_id = ? AND i.id != ?
                ORDER BY q.id DESC LIMIT 40
            """, (interview["user_id"], interview["domain_id"], interview_id))
            cross_session_questions = []
            for r in cursor.fetchall():
                exp_c = []
                if r["expected_concepts"]:
                    try:
                        exp_c = json.loads(r["expected_concepts"])
                    except Exception:
                        exp_c = [r["topic_name"]]
                cross_session_questions.append({
                    "id": r["id"],
                    "question_text": r["question_text"],
                    "topic_id": r["topic_id"],
                    "topic": r["topic_name"],
                    "domain": r["domain_name"],
                    "difficulty": r["difficulty"],
                    "question_type": r["question_type"],
                    "expected_concepts": exp_c,
                    "fingerprint": r["fingerprint"]
                })

            # Select topic ensuring diversity
            target_topic_id = None
            if is_pressure and interview["pressure_topic_id"]:
                target_topic_id = interview["pressure_topic_id"]
            elif interview["topic_id"]:
                target_topic_id = interview["topic_id"]
            else:
                if next_sequence <= 2:
                    try:
                        from .cross_module_engine import CrossModuleEngine
                        prior_weak = CrossModuleEngine.get_candidate_recent_weak_topic(interview["user_id"])
                        if prior_weak:
                            cursor.execute("""
                                SELECT id, name FROM topics 
                                WHERE domain_id = ? AND LOWER(name) LIKE ?
                                LIMIT 1
                            """, (interview["domain_id"], f"%{prior_weak.lower()}%"))
                            p_match = cursor.fetchone()
                            if p_match:
                                last_topics = [q["topic_id"] for q in cross_session_questions[:5]]
                                if p_match["id"] not in last_topics:
                                    target_topic_id = p_match["id"]
                    except Exception:
                        pass

                if not target_topic_id:
                    recent_user_topics = [q["topic_id"] for q in cross_session_questions[:15]]
                    curr_interview_topics = [q["topic_id"] for q in curr_session_questions if "topic_id" in q]
                    if not curr_interview_topics:
                        cursor.execute("SELECT topic_id FROM questions WHERE interview_id = ?", (interview_id,))
                        curr_interview_topics = [r[0] for r in cursor.fetchall()]

                    excluded_topic_ids = list(dict.fromkeys(recent_user_topics + curr_interview_topics))
                    topic_row = None
                    if excluded_topic_ids:
                        ph = ",".join("?" for _ in excluded_topic_ids)
                        cursor.execute(f"""
                            SELECT t.id, t.name FROM topics t
                            WHERE t.domain_id = ? AND t.id NOT IN ({ph})
                            ORDER BY RANDOM() LIMIT 1
                        """, tuple([interview["domain_id"]] + excluded_topic_ids))
                        topic_row = cursor.fetchone()

                    if not topic_row and curr_interview_topics:
                        ph_curr = ",".join("?" for _ in curr_interview_topics)
                        cursor.execute(f"""
                            SELECT t.id, t.name FROM topics t
                            WHERE t.domain_id = ? AND t.id NOT IN ({ph_curr})
                            ORDER BY RANDOM() LIMIT 1
                        """, tuple([interview["domain_id"]] + curr_interview_topics))
                        topic_row = cursor.fetchone()

                    if not topic_row:
                        cursor.execute("""
                            SELECT t.id, t.name, COUNT(q.id) as used_cnt
                            FROM topics t
                            LEFT JOIN questions q ON t.id = q.topic_id AND q.interview_id = ?
                            WHERE t.domain_id = ?
                            GROUP BY t.id
                            ORDER BY used_cnt ASC, RANDOM() LIMIT 1
                        """, (interview_id, interview["domain_id"]))
                        topic_row = cursor.fetchone()

                    target_topic_id = topic_row["id"]

            cursor.execute("SELECT name FROM topics WHERE id = ?", (target_topic_id,))
            topic_name = cursor.fetchone()["name"]
            cursor.execute("SELECT name FROM domains WHERE id = ?", (interview["domain_id"],))
            domain_name = cursor.fetchone()["name"]

            # Determine question type preserving 10-question distribution
            target_q_type = determine_target_question_type(
                sequence_number=next_sequence,
                total_questions=interview["total_questions"],
                domain_name=domain_name,
                interview_type=interview["interview_type"]
            )

            candidate_weaknesses = []
            perf_context = None
            try:
                from .cross_module_engine import CrossModuleEngine
                c_profile = CrossModuleEngine.get_candidate_profile(interview["user_id"])
                if c_profile:
                    candidate_weaknesses = [w.get("topic") for w in c_profile.get("weak_topics", []) if w.get("topic")]
                    perf_context = f"Candidate platform readiness: {c_profile.get('overall_readiness', 50.0)}%"
            except Exception:
                pass

            # Generation & Deduplication validation loop
            generated = None
            max_attempts = 4
            current_topic_id = target_topic_id
            current_topic_name = topic_name

            for attempt in range(max_attempts):
                cand = LLMService.generate_question(
                    domain=domain_name,
                    topic=current_topic_name,
                    difficulty=target_difficulty,
                    question_type=target_q_type,
                    sequence_number=next_sequence,
                    is_pressure=is_pressure,
                    weak_topic_context=current_topic_name if is_pressure else None,
                    previous_questions=[q["question_text"] for q in curr_session_questions],
                    candidate_weaknesses=candidate_weaknesses,
                    candidate_performance_context=perf_context,
                    exclude_questions_full=curr_session_questions + cross_session_questions[:15]
                )

                # Validate domain isolation (no Python leakage in non-Python interviews)
                cand_text = (cand.get("question_text") or "").lower()
                if domain_name.lower() != "python" and any(p in cand_text for p in ["in python", "python's", "def __init__", "def "]):
                    logger.warning(f"Domain mismatch / leakage in attempt {attempt+1}, retrying...")
                    continue

                # Hard constraint: Reject exact or semantic duplicates within the current interview session
                is_dup, reason = is_duplicate_against_history(cand, curr_session_questions)
                if is_dup:
                    logger.warning(f"Session duplicate rejected (attempt {attempt+1}): {reason}. Retrying with alternate topic...")
                    cursor.execute("""
                        SELECT id, name FROM topics 
                        WHERE domain_id = ? AND id != ?
                        ORDER BY RANDOM() LIMIT 1
                    """, (interview["domain_id"], current_topic_id))
                    alt_t = cursor.fetchone()
                    if alt_t:
                        current_topic_id = alt_t["id"]
                        current_topic_name = alt_t["name"]
                    continue

                # Soft constraint: If candidate duplicates a recent cross-session question and retries remain, try for a fresher question
                if attempt < 2 and cross_session_questions:
                    is_cross_dup, _ = is_duplicate_against_history(cand, cross_session_questions)
                    if is_cross_dup:
                        logger.info(f"Cross-session repeat avoided (attempt {attempt+1}), seeking fresher question...")
                        continue

                generated = cand
                target_topic_id = current_topic_id
                topic_name = current_topic_name
                break

            # If all attempts exhausted or failed, select guaranteed-unique domain fallback
            if not generated:
                logger.warning("All LLM generation attempts resulted in duplicates; selecting guaranteed-unique domain fallback.")
                generated = find_fallback_question(
                    domain=domain_name,
                    topic=topic_name,
                    difficulty=target_difficulty,
                    question_type=target_q_type,
                    is_pressure=is_pressure,
                    exclude_question_texts=curr_session_questions,
                    cross_session_history=cross_session_questions
                )

            expected_concepts_json = json.dumps(generated.get("expected_concepts", [topic_name]))

            cursor.execute("""
                SELECT reason FROM difficulty_transitions 
                WHERE interview_id = ? ORDER BY id DESC LIMIT 1
            """, (interview_id,))
            last_trans = cursor.fetchone()
            transition_reason = last_trans["reason"] if last_trans else (
                f"Initial starting difficulty: {target_difficulty}" if next_sequence == 1 else None
            )

            raw_gen_type = (generated.get("question_type") or "").strip().lower()
            if raw_gen_type in ("comparison", "definition"):
                actual_q_type = "conceptual"
            elif raw_gen_type in ("debugging", "design"):
                actual_q_type = "tradeoff" if target_q_type == "tradeoff" else "scenario"
            else:
                actual_q_type = target_q_type
            is_non_code = actual_q_type.lower() in ("conceptual", "scenario", "tradeoff", "design", "comparison", "definition") or domain_name.lower() in ("computer networks", "operating systems")
            if is_non_code:
                code_snip = None
                starter_cd = None
            else:
                code_snip = generated.get("code_snippet")
                starter_cd = generated.get("starter_code")

            mapped_lang = DOMAIN_CODE_LANG_MAP.get(domain_name.strip().lower(), "text")
            code_lang = generated.get("code_language") or mapped_lang

            # Compute normalized fingerprint for persistent tracking
            fp = compute_question_fingerprint(
                question_text=generated["question_text"],
                domain=domain_name,
                topic=topic_name,
                expected_concepts=generated.get("expected_concepts")
            )

            cursor.execute("""
                INSERT INTO questions (
                    interview_id, topic_id, question_text, difficulty, question_type,
                    sequence_number, expected_concepts, evaluation_criteria,
                    is_pressure_mode, difficulty_transition_reason,
                    code_snippet, code_language, starter_code, fingerprint
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interview_id, target_topic_id, generated["question_text"],
                target_difficulty, actual_q_type,
                next_sequence, expected_concepts_json, generated.get("evaluation_criteria", ""),
                1 if is_pressure else 0, transition_reason,
                code_snip, code_lang, starter_cd, fp
            ))
            new_q_id = cursor.lastrowid

            try:
                cursor.execute("""
                    INSERT INTO user_served_questions (user_id, module, question_id)
                    VALUES (?, 'interview', ?)
                """, (interview["user_id"], new_q_id))
            except Exception:
                pass

            conn.commit()
            conn.close()

            return {
                "id": new_q_id,
                "interview_id": interview_id,
                "topic_id": target_topic_id,
                "topic_name": topic_name,
                "sequence_number": next_sequence,
                "total_questions": interview["total_questions"],
                "question_text": generated["question_text"],
                "difficulty": target_difficulty,
                "question_type": actual_q_type,
                "hints_used": 0,
                "hints_available": 3,
                "is_pressure_mode": is_pressure,
                "difficulty_transition_reason": transition_reason,
                "code_snippet": code_snip,
                "code_language": code_lang,
                "starter_code": starter_cd,
                "source": generated.get("source", "gemini"),
                "fingerprint": fp
            }

    @staticmethod
    def submit_answer(question_id: int, answer_text: str, code_answer: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluates the answer, updates adaptive difficulty, tests for weakness / pressure mode,
        and records state transitions.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch question and interview details
        cursor.execute("""
            SELECT q.*, t.name as topic_name, i.domain_id, i.current_difficulty,
                   i.consecutive_weak_count, i.pressure_mode_active, i.total_questions
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN interviews i ON q.interview_id = i.id
            WHERE q.id = ?
        """, (question_id,))
        q_row = cursor.fetchone()
        if not q_row:
            conn.close()
            raise ValueError(f"Question with id {question_id} not found.")

        interview_id = q_row["interview_id"]
        expected_concepts = json.loads(q_row["expected_concepts"]) if q_row["expected_concepts"] else [q_row["topic_name"]]
        
        # Hints count for this question
        cursor.execute("SELECT COUNT(*) FROM hint_logs WHERE question_id = ?", (question_id,))
        hints_used = cursor.fetchone()[0]

        # Evaluate via LLM service
        eval_result = LLMService.evaluate_answer(
            question_text=q_row["question_text"],
            answer_text=f"{answer_text}\n[Code Solution]: {code_answer}" if code_answer else answer_text,
            expected_concepts=expected_concepts,
            topic=q_row["topic_name"],
            difficulty=q_row["difficulty"]
        )

        overall_score = eval_result["overall_score"]
        # Hint penalty: 0.5 point per hint used, min score 1.0
        if hints_used > 0:
            overall_score = max(1.0, round(overall_score - (hints_used * 0.4), 1))
            eval_result["overall_score"] = overall_score

        missing_concepts = eval_result.get("missing_concepts", [])
        weakness_detected = eval_result.get("weakness_detected", overall_score < 6.0)
        weakness_level = eval_result.get("weakness_level", "moderate" if weakness_detected else "none")

        # Save answer with code
        cursor.execute("""
            INSERT INTO answers (
                question_id, answer_text, code_answer, correctness, relevance,
                conceptual_understanding, completeness, overall_score,
                hints_used, feedback, missing_concepts, weakness_detected, weakness_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            question_id, answer_text, code_answer, eval_result["correctness"], eval_result["relevance"],
            eval_result["conceptual_understanding"], eval_result["completeness"],
            overall_score, hints_used, eval_result["feedback"],
            json.dumps(missing_concepts), 1 if weakness_detected else 0, weakness_level
        ))

        # ADAPTIVE DIFFICULTY ENGINE LOGIC
        current_diff = q_row["current_difficulty"]
        curr_idx = DIFFICULTY_LEVELS.index(current_diff) if current_diff in DIFFICULTY_LEVELS else 1
        new_diff = current_diff
        diff_changed = False
        diff_reason = None

        consecutive_weak = q_row["consecutive_weak_count"]
        pressure_activated = False
        pressure_mode_active = bool(q_row["pressure_mode_active"])

        # Check performance on this question
        if overall_score >= 7.5:
            consecutive_weak = 0
            if curr_idx < len(DIFFICULTY_LEVELS) - 1:
                new_diff = DIFFICULTY_LEVELS[curr_idx + 1]
                diff_changed = True
                diff_reason = f"Strong answer ({overall_score}/10) demonstrated conceptual mastery. Escalating difficulty to {new_diff}."
            else:
                diff_reason = f"Maintained peak difficulty ({current_diff}) following outstanding answer ({overall_score}/10)."
            # If in pressure mode and answered strongly, candidate conquered the pressure!
            if pressure_mode_active:
                pressure_mode_active = False

        elif overall_score >= 5.0:
            consecutive_weak = max(0, consecutive_weak - 1)
            diff_reason = f"Solid average response ({overall_score}/10). Maintaining {current_diff} difficulty to reinforce consistency."
            # Maintain difficulty

        else: # Weak performance: overall_score < 5.0
            consecutive_weak += 1
            if curr_idx > 0 and not pressure_mode_active:
                new_diff = DIFFICULTY_LEVELS[curr_idx - 1]
                diff_changed = True
                diff_reason = f"Detected gap in understanding ({overall_score}/10). Calibrating difficulty down to {new_diff} to rebuild foundation."
            else:
                diff_reason = f"Weak response ({overall_score}/10). Staying at {current_diff} to probe specific conceptual deficiencies."

            # Check if Pressure Mode should activate:
            # Activates if candidate scores below 5.5 consecutively or multiple times on this topic
            cursor.execute("""
                SELECT COUNT(*) FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE q.interview_id = ? AND q.topic_id = ? AND a.overall_score < 5.5
            """, (interview_id, q_row["topic_id"]))
            topic_weak_count = cursor.fetchone()[0]

            if (consecutive_weak >= 2 or topic_weak_count >= 2) and not pressure_mode_active:
                pressure_mode_active = True
                pressure_activated = True
                diff_reason = f"🔥 Repeated weakness detected on '{q_row['topic_name']}'. Activating PRESSURE MODE to rigorously isolate core concepts."

        # Record difficulty transition if changed or pressure activated
        if diff_changed or pressure_activated:
            cursor.execute("""
                INSERT INTO difficulty_transitions (
                    interview_id, from_difficulty, to_difficulty, reason, sequence_number
                ) VALUES (?, ?, ?, ?, ?)
            """, (interview_id, current_diff, new_diff, diff_reason, q_row["sequence_number"]))

        # Update interview state
        cursor.execute("""
            UPDATE interviews SET
                current_difficulty = ?,
                pressure_mode_active = ?,
                pressure_topic_id = ?,
                consecutive_weak_count = ?
            WHERE id = ?
        """, (
            new_diff, 1 if pressure_mode_active else 0,
            q_row["topic_id"] if pressure_mode_active else None,
            consecutive_weak, interview_id
        ))

        # Check if interview is finished
        cursor.execute("""
            SELECT COUNT(*) FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE q.interview_id = ?
        """, (interview_id,))
        answered_count = cursor.fetchone()[0]
        is_completed = answered_count >= q_row["total_questions"]

        if is_completed:
            InterviewEngine._finalize_interview(interview_id, conn)

        conn.commit()
        conn.close()

        return {
            "question_id": question_id,
            "correctness": eval_result["correctness"],
            "relevance": eval_result["relevance"],
            "conceptual_understanding": eval_result["conceptual_understanding"],
            "completeness": eval_result["completeness"],
            "overall_score": overall_score,
            "topic": q_row["topic_name"],
            "weakness_detected": weakness_detected,
            "weakness_level": weakness_level,
            "missing_concepts": missing_concepts,
            "feedback": eval_result["feedback"],
            "reference_code": eval_result.get("reference_code"),
            "next_difficulty": new_diff,
            "difficulty_changed": diff_changed,
            "difficulty_change_reason": diff_reason,
            "pressure_mode_activated": pressure_activated,
            "is_interview_completed": is_completed,
            "technical_mistakes": eval_result.get("technical_mistakes", []),
            "strengths": eval_result.get("strengths", []),
            "weaknesses": eval_result.get("weaknesses", []),
            "improvement_suggestions": eval_result.get("improvement_suggestions", []),
            "source": eval_result.get("source", "gemini")
        }

    @staticmethod
    def request_hint(question_id: int) -> Dict[str, Any]:
        """Provides a 3-level progressive hint for the given question."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT q.*, t.name as topic_name,
                   (SELECT COUNT(*) FROM hint_logs h WHERE h.question_id = q.id) as hints_used
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            WHERE q.id = ?
        """, (question_id,))
        q_row = cursor.fetchone()
        if not q_row:
            conn.close()
            raise ValueError(f"Question {question_id} not found.")

        current_hints_used = q_row["hints_used"]
        if current_hints_used >= 3:
            conn.close()
            return {
                "hint_level": 3,
                "hint_text": "All 3 hints have already been provided for this question. Give it your best shot!",
                "remaining_hints": 0,
                "total_hints_used": current_hints_used
            }

        next_level = current_hints_used + 1

        # Check if fallback has explicit hints for this question
        expected_concepts = json.loads(q_row["expected_concepts"]) if q_row["expected_concepts"] else [q_row["topic_name"]]
        
        # Craft progressive hint based on level
        topic = q_row["topic_name"]
        if next_level == 1:
            hint_text = f"💡 Level 1 Clue: Think about the foundational principle behind {topic}. What is the primary purpose or contract here?"
        elif next_level == 2:
            hint_text = f"💡 Level 2 Specific Guidance: Consider how {expected_concepts[0] if expected_concepts else topic} behaves under standard execution."
        else: # Level 3
            hint_text = f"💡 Level 3 Deep Hint: Focus directly on: {', '.join(expected_concepts[:2])}. Address how these interconnect to solve the problem."

        # Insert hint log
        cursor.execute("""
            INSERT INTO hint_logs (question_id, hint_level, hint_text)
            VALUES (?, ?, ?)
        """, (question_id, next_level, hint_text))

        # Update total hints on interview
        cursor.execute("""
            UPDATE interviews SET hints_used_total = hints_used_total + 1
            WHERE id = ?
        """, (q_row["interview_id"],))

        conn.commit()
        conn.close()

        return {
            "hint_level": next_level,
            "hint_text": hint_text,
            "remaining_hints": 3 - next_level,
            "total_hints_used": next_level
        }

    @staticmethod
    def _finalize_interview(interview_id: int, conn):
        """Calculates final scores, weakness profiles, and learning recommendations."""
        cursor = conn.cursor()

        # Compute aggregate scores
        cursor.execute("""
            SELECT 
                AVG(a.overall_score) as avg_overall,
                AVG(a.correctness) as avg_correctness,
                AVG(a.conceptual_understanding) as avg_conceptual,
                AVG(a.completeness) as avg_problem_solving,
                AVG(a.relevance) as avg_communication,
                COUNT(a.id) as total_answers
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE q.interview_id = ?
        """, (interview_id,))
        agg = cursor.fetchone()

        avg_overall = round((agg["avg_overall"] or 0.0) * 10, 1) # Convert 10-scale to percentage
        avg_tech = round((agg["avg_correctness"] or 0.0) * 10, 1)
        avg_concept = round((agg["avg_conceptual"] or 0.0) * 10, 1)
        avg_prob = round((agg["avg_problem_solving"] or 0.0) * 10, 1)
        avg_comm = round((agg["avg_communication"] or 0.0) * 10, 1)

        cursor.execute("""
            UPDATE interviews SET
                status = 'completed',
                overall_score = ?,
                technical_score = ?,
                conceptual_score = ?,
                problem_solving_score = ?,
                communication_score = ?,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (avg_overall, avg_tech, avg_concept, avg_prob, avg_comm, interview_id))

        # Compute Topic-Wise Scores & Weakness Identification
        cursor.execute("""
            SELECT 
                q.topic_id, t.name as topic_name,
                AVG(a.overall_score) as topic_avg,
                COUNT(a.id) as attempts
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            JOIN topics t ON q.topic_id = t.id
            WHERE q.interview_id = ?
            GROUP BY q.topic_id
        """, (interview_id,))
        topic_rows = cursor.fetchall()

        for t in topic_rows:
            t_score_pct = round(t["topic_avg"] * 10, 1)
            
            # Collect missing concepts for this topic
            cursor.execute("""
                SELECT a.missing_concepts FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE q.interview_id = ? AND q.topic_id = ?
            """, (interview_id, t["topic_id"]))
            all_missing = []
            for m_row in cursor.fetchall():
                if m_row["missing_concepts"]:
                    try:
                        all_missing.extend(json.loads(m_row["missing_concepts"]))
                    except Exception:
                        pass
            unique_missing = list(dict.fromkeys(all_missing))

            # Determine severity
            if t_score_pct < 50.0:
                severity = "High"
            elif t_score_pct < 70.0:
                severity = "Moderate"
            else:
                severity = "Low"

            # Insert into weaknesses table if severity is Moderate or High
            if severity in ["High", "Moderate"]:
                cursor.execute("""
                    INSERT INTO weaknesses (
                        interview_id, topic_id, severity, average_score,
                        attempts_count, missing_concepts
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (interview_id, t["topic_id"], severity, t_score_pct, t["attempts"], json.dumps(unique_missing)))

                # Generate and insert personalized learning recommendation
                rec_data = LLMService.generate_learning_recommendation(
                    topic_name=t["topic_name"],
                    score=t_score_pct,
                    missing_concepts=unique_missing
                )

                cursor.execute("""
                    INSERT INTO recommendations (
                        interview_id, topic_id, topic_name, performance_score,
                        why_weak, concepts_to_learn, action_plan, practice_questions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interview_id, t["topic_id"], t["topic_name"], t_score_pct,
                    json.dumps(rec_data["why_weak"]),
                    json.dumps(rec_data["concepts_to_learn"]),
                    json.dumps(rec_data["action_plan"]),
                    json.dumps(rec_data["practice_questions"])
                ))
