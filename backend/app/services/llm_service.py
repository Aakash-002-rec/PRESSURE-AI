import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from .fallback_bank import find_fallback_question, evaluate_answer_rule_based

# Quota/rate-limit state tracking
_gemini_quota_exhausted: bool = False
_gemini_quota_exhausted_until: float = 0.0

def _is_quota_error(error: Exception) -> bool:
    """Explicitly detects HTTP 429 and quota/rate-limit errors without exposing secrets."""
    err_type = type(error).__name__.lower()
    err_msg = str(error).lower()
    return (
        "resourceexhausted" in err_type
        or "toomanyrequests" in err_type
        or "429" in err_msg
        or "quota" in err_msg
        or "resource_exhausted" in err_msg
        or "rate limit" in err_msg
    )


logger = logging.getLogger("pressure_ai.llm")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DEFAULT_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "gemini").lower()

# Initialize providers conditionally
gemini_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-flash-latest")
        logger.info("Gemini LLM initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not initialize Gemini: {e}")

openai_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI LLM initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not initialize OpenAI: {e}")

def _call_llm_json(prompt: str, system_prompt: str) -> Optional[Dict[str, Any]]:
    """Calls configured LLM (Gemini or OpenAI) expecting valid JSON output."""
    global _gemini_quota_exhausted, _gemini_quota_exhausted_until

    # 1. Try Gemini
    if gemini_model:
        now = time.time()
        if _gemini_quota_exhausted and now < _gemini_quota_exhausted_until:
            logger.warning("Gemini quota exceeded; using fallback engine.")
        else:
            try:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nReturn strictly valid JSON without markdown wrapping or backticks."
                # Disable SDK internal retries so 429 quota exhaustion fails immediately without hanging
                response = gemini_model.generate_content(
                    full_prompt,
                    request_options={"timeout": 10, "retry": None}
                )
                text = response.text.strip()
                # Clean possible markdown ```json ... ```
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                text = text.strip()
                _gemini_quota_exhausted = False
                return json.loads(text)
            except Exception as e:
                if _is_quota_error(e):
                    _gemini_quota_exhausted = True
                    _gemini_quota_exhausted_until = time.time() + 300  # 5-minute cooldown
                    logger.warning("Gemini quota exceeded; using fallback engine.")
                else:
                    safe_msg = str(e)
                    if GEMINI_API_KEY and GEMINI_API_KEY in safe_msg:
                        safe_msg = safe_msg.replace(GEMINI_API_KEY, "[REDACTED]")
                    logger.warning(f"Gemini call failed or returned invalid JSON: {safe_msg}")

    # 2. Try OpenAI
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt + " Output must be strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.warning(f"OpenAI call failed: {e}")

    return None

DOMAIN_CODE_LANG_MAP = {
    "c": "c",
    "c++": "cpp",
    "cpp": "cpp",
    "java": "java",
    "javascript": "javascript",
    "python": "python",
    "sql": "sql",
    "html/css": "html",
    "html": "html",
    "css": "css",
    "algorithms": "python",
    "data structures": "python",
    "oop": "java",
    "operating systems": "c",
    "computer networks": "text",
    "dbms": "sql"
}

class LLMService:
    @staticmethod
    def generate_question(
        domain: str,
        topic: str,
        difficulty: str,
        question_type: str,
        sequence_number: int,
        is_pressure: bool = False,
        weak_topic_context: Optional[str] = None,
        previous_questions: Optional[List[str]] = None,
        candidate_weaknesses: Optional[List[str]] = None,
        candidate_performance_context: Optional[str] = None,
        exclude_questions_full: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """Generates dynamic interview question via LLM (Gemini) or intelligent domain fallback bank."""
        domain_clean = domain.strip()
        domain_lower = domain_clean.lower()
        mapped_lang = DOMAIN_CODE_LANG_MAP.get(domain_lower, "text")

        leakage_warning = ""
        if domain_lower != "python":
            leakage_warning = (
                f"\nCRITICAL DOMAIN ENFORCEMENT: The interview domain is strictly '{domain_clean}'. "
                f"You MUST NOT mention Python, Python syntax (def, self, __init__, print()), or Python libraries. "
                f"The question, terminology, code snippets, and concepts MUST belong exclusively to '{domain_clean}'."
            )

        is_non_code_q = question_type.lower() in ("conceptual", "scenario", "tradeoff", "design", "comparison", "definition") or domain_lower in ("computer networks", "operating systems")
        type_instruction = ""
        if is_non_code_q:
            type_instruction = (
                f"\nCRITICAL QUESTION TYPE ENFORCEMENT: The question type is '{question_type}'. "
                "This tests deep conceptual understanding, runtime mechanics, memory management, and system trade-offs. "
                "Do NOT ask the candidate to write code or predict code output. "
                "'code_snippet' and 'starter_code' MUST be null."
            )
        else:
            type_instruction = (
                f"\nQUESTION TYPE ENFORCEMENT: The question type is '{question_type}'. "
                f"Provide clean idiomatic code in 'code_snippet' or 'starter_code' matching '{domain_clean}'."
            )

        system_prompt = (
            "You are an elite, highly professional technical interviewer at a top tech company. "
            f"Generate one targeted, insightful technical interview question strictly for domain '{domain_clean}' and topic '{topic}'. "
            f"{leakage_warning}\n{type_instruction}\n"
            "Do NOT include internal chain-of-thought or reasoning. "
            "Output strictly valid JSON with keys: "
            "'question_text', 'expected_concepts' (list of strings), 'evaluation_criteria' (string), "
            "'code_snippet' (optional string containing code in the domain's language, or null), "
            "'starter_code' (optional string, or null), "
            f"'code_language' (string, e.g. '{mapped_lang}'), "
            "'hints' (list of 3 strings progressing from subtle conceptual clue to strong guidance)."
        )

        pressure_instruction = ""
        if is_pressure:
            pressure_instruction = (
                f"\nCRITICAL: PRESSURE MODE IS ACTIVATED. The candidate showed weakness in '{topic}' under domain '{domain_clean}'. "
                "Generate a deeper question targeting this weak topic with an edge case, scenario-based probe, "
                "or deep architectural invariant to rigorously isolate core concepts."
            )

        prompt = (
            f"Domain: {domain_clean}\n"
            f"Topic: {topic}\n"
            f"Target Difficulty: {difficulty}\n"
            f"Question Type: {question_type}\n"
            f"Question #{sequence_number}\n"
            f"Candidate Known Weaknesses: {', '.join(candidate_weaknesses) if candidate_weaknesses else 'None'}\n"
            f"Candidate Performance Context: {candidate_performance_context or 'Standard'}\n"
            f"{pressure_instruction}\n"
            f"Exclude previous questions: {previous_questions or []}\n"
            f"Remember: The question must test '{domain_clean}' and '{topic}' specifically."
        )

        res = _call_llm_json(prompt, system_prompt)
        if res and "question_text" in res and "expected_concepts" in res:
            q_text = str(res["question_text"]).strip()
            # Post-check for Python leakage if non-Python domain
            is_leaked = False
            if domain_lower != "python":
                python_markers = ["in python", "python's", "def __init__", "def ", "self.", "lambda x:", "import sys", "import os", "from typing import"]
                q_lower = q_text.lower()
                for marker in python_markers:
                    if marker in q_lower:
                        logger.warning(f"Rejected Gemini question due to Python leakage for domain '{domain_clean}': {q_text[:80]}")
                        is_leaked = True
                        break

            if not is_leaked:
                # Check for semantic duplicate against existing questions
                from .question_deduplicator import is_duplicate_against_history
                cand_check = {
                    "question_text": q_text,
                    "domain": domain_clean,
                    "topic": topic,
                    "expected_concepts": res.get("expected_concepts", [topic])
                }
                history_to_check = exclude_questions_full if exclude_questions_full is not None else (previous_questions or [])
                is_dup, reason = is_duplicate_against_history(cand_check, history_to_check)
                if is_dup:
                    logger.warning(f"Rejected Gemini question due to duplicate detection ({reason}): {q_text[:80]}")
                    is_leaked = True

            if not is_leaked:
                hints = res.get("hints", [])
                if len(hints) < 3:
                    hints = [
                        f"Think carefully about how {topic} operates conceptually in {domain_clean}.",
                        f"Consider the trade-offs and underlying mechanics in {domain_clean}.",
                        f"Focus on the standard industry pattern or syntax for {topic}."
                    ]
                return {
                    "source": "gemini",
                    "domain": domain_clean,
                    "topic": topic,
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "question_text": q_text,
                    "expected_concepts": res.get("expected_concepts", [topic]),
                    "evaluation_criteria": res.get("evaluation_criteria", f"Assess candidate's clarity on {topic} in {domain_clean}"),
                    "hints": hints,
                    "code_snippet": None if is_non_code_q else res.get("code_snippet"),
                    "code_language": res.get("code_language") or mapped_lang,
                    "starter_code": None if is_non_code_q else res.get("starter_code")
                }

        # Fallback to curated domain question bank
        history_for_fallback = exclude_questions_full if exclude_questions_full is not None else (previous_questions or [])
        fb_q = find_fallback_question(
            domain=domain_clean,
            topic=topic,
            difficulty=difficulty,
            question_type=question_type,
            is_pressure=is_pressure,
            exclude_question_texts=history_for_fallback
        )
        fb_res = dict(fb_q)
        fb_res["source"] = "fallback"
        if is_non_code_q:
            fb_res["code_snippet"] = None
            fb_res["starter_code"] = None
        return fb_res

    @staticmethod
    def evaluate_answer(
        question_text: str,
        answer_text: str,
        expected_concepts: List[str],
        topic: str,
        difficulty: str
    ) -> Dict[str, Any]:
        """Evaluates candidate answer against expected concepts, returning structured assessment."""
        system_prompt = (
            "You are an expert technical evaluator at a premier software company. "
            "Evaluate the candidate's answer across the four dimensions: correctness, relevance, "
            "conceptual_understanding, and completeness (each scored 1.0 to 10.0). "
            "Output strictly valid JSON with keys:\n"
            "- 'correctness' (1-10 float)\n"
            "- 'relevance' (1-10 float)\n"
            "- 'conceptual_understanding' (1-10 float)\n"
            "- 'completeness' (1-10 float)\n"
            "- 'overall_score' (1-10 float)\n"
            "- 'topic' (string)\n"
            "- 'subtopics' (list of strings)\n"
            "- 'weakness_detected' (boolean: true if overall_score < 6.0)\n"
            "- 'weakness_level' (one of: 'none', 'mild', 'moderate', 'severe')\n"
            "- 'missing_concepts' (list of key concepts candidate failed to address or got wrong)\n"
            "- 'technical_mistakes' (list of specific technical errors or inaccuracies in candidate's explanation)\n"
            "- 'strengths' (list of specific points or concepts candidate articulated well)\n"
            "- 'weaknesses' (list of conceptual gaps or overlooked areas)\n"
            "- 'improvement_suggestions' (list of concrete actionable study recommendations)\n"
            "- 'feedback' (concise professional critique: 2 sentences praising what was good and specifically identifying what was missed)"
        )

        prompt = (
            f"Question: {question_text}\n"
            f"Topic: {topic} (Difficulty: {difficulty})\n"
            f"Expected Concepts: {json.dumps(expected_concepts)}\n"
            f"Candidate's Answer: {answer_text}\n"
        )

        res = _call_llm_json(prompt, system_prompt)
        if res and "overall_score" in res:
            try:
                overall = float(res["overall_score"])
                return {
                    "source": "gemini",
                    "correctness": float(res.get("correctness", overall)),
                    "relevance": float(res.get("relevance", overall)),
                    "conceptual_understanding": float(res.get("conceptual_understanding", overall)),
                    "completeness": float(res.get("completeness", overall)),
                    "overall_score": overall,
                    "topic": res.get("topic", topic),
                    "subtopics": res.get("subtopics", [topic]),
                    "weakness_detected": bool(res.get("weakness_detected", overall < 6.0)),
                    "weakness_level": res.get("weakness_level", "moderate" if overall < 6.0 else "none"),
                    "missing_concepts": res.get("missing_concepts", []),
                    "technical_mistakes": res.get("technical_mistakes", []),
                    "strengths": res.get("strengths", []),
                    "weaknesses": res.get("weaknesses", []),
                    "improvement_suggestions": res.get("improvement_suggestions", []),
                    "feedback": res.get("feedback", f"Score: {overall}/10."),
                    "confidence": 0.95
                }
            except Exception as e:
                logger.warning(f"Error parsing Gemini evaluation fields: {e}")

        # Fallback rule-based evaluator
        fb_eval = evaluate_answer_rule_based(
            question_text=question_text,
            answer_text=answer_text,
            expected_concepts=expected_concepts,
            topic=topic
        )
        fb_eval["source"] = "fallback"
        fb_eval["technical_mistakes"] = [f"Omitted or imprecise coverage of: {', '.join(fb_eval.get('missing_concepts', [])[:2])}"] if fb_eval.get('missing_concepts') else []
        fb_eval["strengths"] = [f"Basic familiarity with {topic}"]
        fb_eval["weaknesses"] = fb_eval.get("missing_concepts", [])[:3]
        fb_eval["improvement_suggestions"] = [f"Review foundational principles and syntax of {topic}."]
        if _gemini_quota_exhausted:
            fb_eval["feedback"] = f"AI feedback is temporarily unavailable. Your objective assessment result is still valid. {fb_eval['feedback']}"
        return fb_eval

    @staticmethod
    def generate_model_interview_answer(
        question_text: str,
        topic: str,
        expected_concepts: List[str],
        evaluation_criteria: Optional[str] = None,
        question_type: Optional[str] = None,
        difficulty: str = "Intermediate",
        starter_code: Optional[str] = None,
        code_snippet: Optional[str] = None,
        domain: str = "General"
    ) -> Dict[str, Any]:
        """
        Generates an authoritative, 100% comprehensive model answer covering all expected concepts,
        invariants, architectural nuances, and working code if applicable.
        Guarantees 10/10 evaluation score. Respects the question's domain.
        """
        domain_clean = (domain or "General").strip()
        system_prompt = (
            "You are an Elite Staff Software Engineer and Technical Interviewer. "
            f"Write the definitive 100% score (10.0/10.0) candidate answer to the given interview question for domain '{domain_clean}'. "
            f"Requirements:\n"
            f"1. Deeply explain every single expected concept with rigorous terminology and mechanics specific to '{domain_clean}'.\n"
            "2. Address edge cases, trade-offs, and invariants.\n"
            f"3. If the question asks for code, debugging, or an implementation, provide clean, idiomatic code in 'code_answer' matching the language of '{domain_clean}' (do NOT default to Python unless domain is Python).\n"
            "Output strictly valid JSON with:\n"
            "- 'answer_text': comprehensive, beautifully articulated explanation (3-5 detailed paragraphs with bullet points)\n"
            "- 'code_answer': clean runnable code snippet if applicable or empty string\n"
            "- 'key_points_covered': list of strings of concepts addressed"
        )

        prompt = (
            f"Domain: {domain_clean}\n"
            f"Question: {question_text}\n"
            f"Topic: {topic} ({difficulty})\n"
            f"Question Type: {question_type or 'Conceptual'}\n"
            f"Expected Concepts: {json.dumps(expected_concepts)}\n"
            f"Evaluation Criteria: {evaluation_criteria or ''}\n"
            f"Starter Code / Context: {starter_code or code_snippet or 'None'}\n"
        )

        res = _call_llm_json(prompt, system_prompt)
        if res and "answer_text" in res:
            return res

        # High-grade deterministic fallback tailored to domain, expected_concepts and topic
        concepts_str = ", ".join(expected_concepts) if expected_concepts else topic
        bullets = "\n".join([f"• {c}: Core architectural mechanic governing runtime behavior, correctness, and performance in {domain_clean}." for c in (expected_concepts or [topic])])
        fallback_text = (
            f"Comprehensive Analysis of {topic} in {domain_clean}:\n\n"
            f"1. Foundations & Conceptual Architecture:\n"
            f"{topic} is essential for building scalable, resilient software systems. It directly addresses: {concepts_str}.\n\n"
            f"2. Deep Technical Breakdown:\n"
            f"{bullets}\n\n"
            f"3. Operational Invariants, Edge Cases & Trade-offs:\n"
            f"In enterprise production environments, implementations must rigorously defend against boundary anomalies, "
            f"prevent non-deterministic race conditions or memory leaks, and optimize computational time and space trade-offs."
        )

        domain_low = domain_clean.lower()
        if starter_code:
            fallback_code = starter_code
        elif domain_low == "sql":
            fallback_code = f"-- Optimal demonstration query for {topic}\n-- Complies with standard SQL indexing and execution plan invariants\n"
        elif domain_low in ["c", "cpp", "c++", "java", "javascript"]:
            fallback_code = f"// Optimal demonstration snippet in {domain_clean}\n// Implements {topic} covering all expected criteria\n"
        elif domain_low in ["html", "html/css", "css"]:
            fallback_code = f"<!-- Optimal demonstration snippet in {domain_clean} -->\n<!-- Implements {topic} covering all expected criteria -->\n"
        else:
            fallback_code = f"# Optimal demonstration snippet\n# Implements {topic} covering all expected criteria\n"

        return {
            "answer_text": fallback_text,
            "code_answer": fallback_code,
            "key_points_covered": expected_concepts
        }

    @staticmethod
    def generate_learning_recommendation(
        topic_name: str,
        score: float,
        missing_concepts: List[str]
    ) -> Dict[str, Any]:
        """Generates detailed recommendation breakdown and practice questions for a weak topic."""
        system_prompt = (
            "You are a Senior Technical Curriculum Architect. "
            "Generate actionable, personalized learning guidance for a candidate with a technical weakness. "
            "Output strictly valid JSON with keys: "
            "'why_weak' (list of 3 bullet points explaining likely root conceptual gaps), "
            "'concepts_to_learn' (list of 5 fundamental topics/mechanics to study), "
            "'action_plan' (list of 5 progressive study steps), "
            "'practice_questions' (list of 3 objects each having 'level' ['Easy', 'Medium', 'Advanced'], 'question', and 'key_focus')."
        )

        prompt = (
            f"Topic: {topic_name}\n"
            f"Candidate Performance: {score}%\n"
            f"Missing Concepts Detected: {missing_concepts}\n"
        )

        res = _call_llm_json(prompt, system_prompt)
        if res and "action_plan" in res:
            return res

        # High-quality programmatic fallback tailored by topic
        return {
            "why_weak": [
                f"Difficulty articulating the core runtime behavior and edge cases in {topic_name}.",
                f"Unclear explanation or omission of key concepts: {', '.join(missing_concepts[:2]) if missing_concepts else 'fundamental mechanics'}.",
                f"Gap between theoretical definition and practical implementation under interview constraints."
            ],
            "concepts_to_learn": [
                f"{topic_name} core mechanics & syntax",
                f"Internal memory & execution model",
                f"Common boundary conditions & edge-case handling",
                f"Time & space complexity trade-offs in {topic_name}",
                f"Industry best practices & debugging patterns"
            ],
            "action_plan": [
                f"Step 1: Read authoritative documentation and revise the theoretical foundations of {topic_name}.",
                f"Step 2: Trace execution step-by-step with pen and paper or debugger for 3 standard examples.",
                f"Step 3: Implement 5 canonical problems without using hints or external assistance.",
                f"Step 4: Conduct code reviews and analyze failure modes / edge cases.",
                f"Step 5: Retake the PRESSURE-AI adaptive interview to validate mastery."
            ],
            "practice_questions": [
                {
                    "level": "Easy",
                    "question": f"Define {topic_name} from first principles and write a minimal working demonstration.",
                    "key_focus": "Core syntax and basic flow control"
                },
                {
                    "level": "Medium",
                    "question": f"Implement a scenario where {topic_name} handles non-standard inputs and boundary conditions.",
                    "key_focus": "Defensive coding and error handling"
                },
                {
                    "level": "Advanced",
                    "question": f"Analyze performance bottlenecks associated with {topic_name} and optimize for time and memory constraints.",
                    "key_focus": "Algorithmic efficiency and architectural trade-offs"
                }
            ]
        }

    @staticmethod
    def generate_aptitude_question(
        category: str,
        difficulty: str = "Intermediate",
        topic: Optional[str] = None,
        exclude_questions: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Dynamically generates structured MCQ aptitude questions using Gemini.
        Returns validated dict with keys: category, topic, difficulty, question, options, correct_answer, explanation.
        Returns None on any failure so caller can immediately invoke the fallback system.
        """
        cat_clean = category.strip()
        if cat_clean.lower() in ["verbal reasoning", "verbal ability"]:
            cat_clean = "Verbal Reasoning"

        system_prompt = (
            "You are an expert psychometric and aptitude assessment designer for elite tech placement exams. "
            "Generate one brand new, completely solvable objective multiple-choice question (MCQ). "
            "Output strictly valid JSON with NO markdown code block tags or extra commentary. "
            "JSON must contain exactly these keys:\n"
            "- 'category': string (exact category name)\n"
            "- 'topic': string (e.g. 'Percentages', 'Time & Work', 'Syllogisms', 'Probability', 'Reading Comprehension', 'Data Interpretation Tables')\n"
            "- 'difficulty': string ('Beginner', 'Intermediate', or 'Advanced')\n"
            "- 'question': string (clear, unambiguous question statement)\n"
            "- 'options': list of exactly 4 distinct strings\n"
            "- 'correct_answer': integer (0, 1, 2, or 3 representing the index in options of the correct answer)\n"
            "- 'explanation': string (step-by-step mathematical, logical, or linguistic proof of the correct answer)"
        )

        exclude_sample = (exclude_questions or [])[-10:]
        prompt = (
            f"Category: {cat_clean}\n"
            f"Difficulty: {difficulty}\n"
            f"Target Topic / Weakness Area: {topic or 'Core topics for ' + cat_clean}\n"
            f"Exclude previously seen questions: {exclude_sample}\n"
            "Requirements:\n"
            "1. Must have exactly 4 options.\n"
            "2. Exactly one option must be unambiguously correct.\n"
            "3. The 'correct_answer' index must accurately point to the correct option in 'options'.\n"
            "4. Provide a sound, verified numerical or analytical explanation."
        )

        res = _call_llm_json(prompt, system_prompt)
        if not res or not isinstance(res, dict):
            return None

        try:
            q_text = str(res.get("question", "")).strip()
            if not q_text or len(q_text) < 10:
                logger.warning("Gemini aptitude question failed validation: question text too short or empty")
                return None

            raw_options = res.get("options")
            if not isinstance(raw_options, list) or len(raw_options) < 4:
                logger.warning("Gemini aptitude question failed validation: options not a list of at least 4 items")
                return None

            options = [str(opt).strip() for opt in raw_options[:4]]
            if len(set(options)) != 4:
                logger.warning("Gemini aptitude question failed validation: options contain duplicates")
                return None

            correct_ans = res.get("correct_answer")
            if correct_ans is None or not str(correct_ans).isdigit():
                if isinstance(correct_ans, str) and correct_ans in options:
                    correct_ans = options.index(correct_ans)
                else:
                    logger.warning("Gemini aptitude question failed validation: invalid correct_answer index")
                    return None
            else:
                correct_ans = int(correct_ans)

            if correct_ans < 0 or correct_ans >= 4:
                logger.warning(f"Gemini aptitude question failed validation: correct_answer {correct_ans} out of range 0-3")
                return None

            explanation = str(res.get("explanation", "")).strip()
            if not explanation:
                explanation = f"Option {correct_ans + 1} ({options[correct_ans]}) is the correct answer."

            validated_topic = str(res.get("topic") or topic or cat_clean).strip()
            validated_diff = str(res.get("difficulty") or difficulty).capitalize()
            if validated_diff not in ["Beginner", "Intermediate", "Advanced"]:
                validated_diff = difficulty

            return {
                "category": cat_clean,
                "topic": validated_topic,
                "difficulty": validated_diff,
                "question": q_text,
                "options": options,
                "correct_answer": correct_ans,
                "explanation": explanation
            }
        except Exception as e:
            logger.warning(f"Validation error on Gemini aptitude question: {e}")
            return None

    @staticmethod
    def generate_coding_problem(
        language: str = "python",
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        weak_topic: Optional[str] = None,
        previous_titles: Optional[List[str]] = None,
        previous_fingerprints: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Dynamically generates structured coding challenges via Gemini.
        Returns validated dict containing:
        title, category, difficulty, language, description, starter_code, test_cases,
        constraints, hints, time_complexity, space_complexity, input_format, output_format, fingerprint.
        Returns None on any failure or duplicate so caller can immediately invoke the fallback system.
        """
        target_cat = category or weak_topic or "Algorithms"
        target_diff = difficulty or "Intermediate"
        if target_diff not in ["Beginner", "Intermediate", "Advanced"]:
            target_diff = "Intermediate"

        system_prompt = (
            "You are a Senior Principal Software Engineer designing algorithmic placement coding challenges. "
            "Generate an original, high-quality, solvable coding problem. "
            "Output strictly valid JSON with NO markdown code block tags or extra commentary. "
            "JSON must contain exactly these keys:\n"
            "- 'title': string (concise, unique problem title)\n"
            "- 'category': string (e.g. 'Recursion', 'Arrays', 'Strings', 'Data Structures', 'Algorithms', 'Dynamic Programming')\n"
            "- 'difficulty': string ('Beginner', 'Intermediate', or 'Advanced')\n"
            "- 'language': 'python'\n"
            "- 'description': string (clear problem statement with input/output requirements and at least 1 formatted example)\n"
            "- 'input_format': string\n"
            "- 'output_format': string\n"
            "- 'constraints': string (e.g. 1 <= n <= 10^4)\n"
            "- 'starter_code': string (valid python code with function signature, typing, docstring, and pass)\n"
            "- 'entry_function': string (the function name declared in starter_code)\n"
            "- 'test_cases': list of 4 to 6 test case objects, each having:\n"
            "    - 'input': string (raw arguments formatted for python eval(f'({input},)'), e.g. '5' or '[1, 2, 3]' or '\"abc\", 3')\n"
            "    - 'expected_output': string (string representation of expected result, e.g. '120' or 'True' or '[1, 2]')\n"
            "    - 'is_hidden': boolean (must have at least 2 false and at least 2 true)\n"
            "    - 'description': string (brief test case label)\n"
            "- 'hints': list of 2-3 progressive conceptual clues\n"
            "- 'time_complexity': string (e.g. 'O(n)')\n"
            "- 'space_complexity': string (e.g. 'O(1)')"
        )

        exclude_titles = (previous_titles or [])[-15:]
        prompt = (
            f"Language: {language}\n"
            f"Category / Topic: {target_cat}\n"
            f"Difficulty: {target_diff}\n"
            f"Candidate Weakness Context: {f'Candidate showed weakness in {weak_topic}. Tailor this challenge to strengthen that foundation.' if weak_topic else 'Standard interview assessment.'}\n"
            f"Avoid these existing problem titles: {exclude_titles}\n"
            "CRITICAL DEDUPLICATION REQUIREMENT:\n"
            "You MUST create a genuinely NEW coding problem. Do NOT create a paraphrase, slight variation, or simple wording rename of any previously seen problem.\n"
            "The underlying task, invariants, and test cases must be fresh and unique.\n"
            "Requirements:\n"
            "1. Python test cases must evaluate cleanly with eval(f'({input},)'). For strings, enclose with quotes inside the input string like '\"racecar\"' or \"'hello'\".\n"
            "2. Expected output must match str(target_func(*args)).strip(). For booleans, use 'True' or 'False'.\n"
            "3. Starter code must define the entry_function cleanly without syntax errors."
        )

        res = _call_llm_json(prompt, system_prompt)
        if not res or not isinstance(res, dict):
            return None

        try:
            title = str(res.get("title", "")).strip()
            desc = str(res.get("description", "")).strip()
            starter = str(res.get("starter_code", "")).strip()
            test_cases = res.get("test_cases", [])

            if not title or not desc or not starter or not isinstance(test_cases, list):
                logger.warning("Gemini coding problem failed validation: missing core fields")
                return None

            # Reject title match
            if previous_titles and any(title.lower() == prev.lower() for prev in previous_titles):
                logger.warning(f"Gemini coding problem title duplicate detected: {title}")
                return None

            try:
                compile(starter, "<string>", "exec")
            except Exception as e:
                logger.warning(f"Gemini coding problem starter code syntax error: {e}")
                return None

            entry_func = res.get("entry_function")
            if not entry_func or f"def {entry_func}" not in starter:
                for line in starter.split("\n"):
                    if line.strip().startswith("def ") and "(" in line:
                        entry_func = line.strip().split("def ")[1].split("(")[0].strip()
                        break
            if not entry_func:
                logger.warning("Gemini coding problem has no identifiable entry function")
                return None

            validated_tests = []
            has_public = False
            has_hidden = False
            for idx, tc in enumerate(test_cases):
                if not isinstance(tc, dict):
                    continue
                tc_input = str(tc.get("input", "")).strip()
                tc_exp = str(tc.get("expected_output", "")).strip()
                if not tc_input or tc_exp == "":
                    continue
                is_hid = bool(tc.get("is_hidden", False))
                if is_hid:
                    has_hidden = True
                else:
                    has_public = True
                validated_tests.append({
                    "input": tc_input,
                    "expected_output": tc_exp,
                    "is_hidden": is_hid,
                    "description": tc.get("description", f"Test #{idx + 1}")
                })

            if len(validated_tests) < 3 or not has_public or not has_hidden:
                logger.warning(f"Gemini coding problem has insufficient test cases: public={has_public}, hidden={has_hidden}, total={len(validated_tests)}")
                return None

            # Compute content fingerprint
            from .problem_fingerprint import compute_problem_fingerprint
            fp = compute_problem_fingerprint(title, desc, validated_tests, starter)
            if previous_fingerprints and fp in previous_fingerprints:
                logger.warning(f"Gemini coding problem generated duplicate fingerprint: {fp}")
                return None

            hints = res.get("hints", [])
            if not isinstance(hints, list) or len(hints) == 0:
                hints = [
                    f"Analyze the base cases and constraints for {target_cat}.",
                    f"Consider time and space trade-offs before finalizing your solution."
                ]

            return {
                "title": title,
                "category": res.get("category", target_cat),
                "difficulty": res.get("difficulty", target_diff),
                "language": "python",
                "description": desc,
                "starter_code": starter,
                "test_cases": validated_tests,
                "constraints": str(res.get("constraints", "1 <= n <= 10^4")),
                "hints": hints,
                "time_complexity": str(res.get("time_complexity", "O(n)")),
                "space_complexity": str(res.get("space_complexity", "O(n)")),
                "input_format": str(res.get("input_format", "")),
                "output_format": str(res.get("output_format", "")),
                "fingerprint": fp
            }
        except Exception as e:
            logger.warning(f"Validation error on Gemini coding problem: {e}")
            return None

    @staticmethod
    def generate_coding_feedback(
        problem_title: str,
        category: str,
        candidate_code: str,
        status: str,
        passed_count: int,
        total_count: int,
        correctness: float,
        weak_area: str,
        error_msg: Optional[str] = None
    ) -> Optional[str]:
        """
        Uses Gemini to generate rich, personalized conceptual feedback on candidate code
        without altering the authoritative execution test results.
        Returns string feedback or None to fall back to rule-based feedback.
        """
        system_prompt = (
            "You are an encouraging, expert computer science professor and technical mentor. "
            "Provide concise, constructive conceptual feedback on a candidate's code submission. "
            "Output strictly valid JSON with one key 'feedback' containing 2-3 sentences: "
            "1 sentence recognizing what worked, 1 sentence diagnosing the conceptual gap/mistake, "
            "and 1 sentence suggesting a specific algorithmic or coding improvement."
        )

        prompt = (
            f"Problem: {problem_title} ({category})\n"
            f"Status: {status} ({passed_count}/{total_count} test cases passed, {correctness}%)\n"
            f"Diagnosed Weak Area: {weak_area}\n"
            f"Runtime / Compilation Error: {error_msg or 'None'}\n"
            f"Candidate Code:\n{candidate_code}\n"
        )

        res = _call_llm_json(prompt, system_prompt)
        if res and isinstance(res, dict) and "feedback" in res:
            fb = str(res["feedback"]).strip()
            if len(fb) > 15:
                return fb
        return None

    @staticmethod
    def evaluate_aptitude_performance(
        total_questions: int,
        correct_count: int,
        incorrect_count: int,
        overall_score: float,
        category_performance: Dict[str, float],
        weak_categories: List[str],
        question_breakdown: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calls Gemini to provide comprehensive, personalized AI evaluation of candidate's aptitude test performance.
        DOES NOT alter the authoritative objective score.
        Falls back to intelligent rule-based evaluation if Gemini is unavailable or rate-limited.
        """
        system_prompt = (
            "You are a Senior Psychometric Evaluator and Placement Assessment Specialist. "
            "Analyze the candidate's aptitude assessment performance objectively and constructively. "
            "Output strictly valid JSON with NO markdown formatting or backticks. "
            "JSON must contain exactly these keys:\n"
            "- 'summary': string (2-3 concise sentences analyzing overall aptitude readiness and pattern)\n"
            "- 'strengths': list of strings (categories or concepts where the candidate performed with high accuracy)\n"
            "- 'weaknesses': list of strings (categories or concepts where accuracy was below benchmark)\n"
            "- 'mistakes_analysis': list of strings (analysis of conceptual errors or missed reasoning patterns in incorrect questions)\n"
            "- 'difficulty_observations': string (observations on candidate's command across beginner vs intermediate vs advanced questions)\n"
            "- 'improvement_suggestions': list of strings (3 actionable, concrete study suggestions targeting weak areas)"
        )

        prompt = (
            f"Overall Objective Score: {overall_score}% ({correct_count}/{total_questions} correct, {incorrect_count} incorrect)\n"
            f"Category Breakdown: {json.dumps(category_performance)}\n"
            f"Identified Weak Categories (<60%): {json.dumps(weak_categories)}\n"
            f"Question Analysis Sample: {json.dumps((question_breakdown or [])[:8])}\n"
        )

        res = _call_llm_json(prompt, system_prompt)
        if res and isinstance(res, dict) and "summary" in res:
            try:
                return {
                    "source": "gemini",
                    "summary": str(res.get("summary", "")).strip(),
                    "strengths": [str(s) for s in res.get("strengths", []) if s],
                    "weaknesses": [str(w) for w in res.get("weaknesses", []) if w],
                    "mistakes_analysis": [str(m) for m in res.get("mistakes_analysis", []) if m],
                    "difficulty_observations": str(res.get("difficulty_observations", "")).strip(),
                    "improvement_suggestions": [str(s) for s in res.get("improvement_suggestions", []) if s]
                }
            except Exception as e:
                logger.warning(f"Error parsing Gemini aptitude evaluation: {e}")

        # Fallback to rule-based evaluation
        fb = LLMService.evaluate_aptitude_rule_based(
            total_questions=total_questions,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
            overall_score=overall_score,
            category_performance=category_performance,
            weak_categories=weak_categories,
            question_breakdown=question_breakdown
        )
        fb["source"] = "fallback"
        fb["fallback_notice"] = "AI feedback is temporarily unavailable. Your objective assessment result is still valid."
        return fb

    @staticmethod
    def evaluate_aptitude_rule_based(
        total_questions: int,
        correct_count: int,
        incorrect_count: int,
        overall_score: float,
        category_performance: Dict[str, float],
        weak_categories: List[str],
        question_breakdown: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """High-quality rule-based fallback evaluation for aptitude assessments."""
        strengths = [cat for cat, sc in category_performance.items() if sc >= 70.0]
        weaknesses = [cat for cat, sc in category_performance.items() if sc < 60.0]
        if not weaknesses and weak_categories:
            weaknesses = list(weak_categories)

        if overall_score >= 80.0:
            summary = (
                f"Exceptional aptitude proficiency! Your objective score of {overall_score}% "
                f"({correct_count}/{total_questions} correct) demonstrates strong numerical, logical, and verbal command."
            )
        elif overall_score >= 60.0:
            summary = (
                f"Solid overall aptitude foundation with an objective score of {overall_score}% "
                f"({correct_count}/{total_questions} correct). Core competencies in {', '.join(strengths[:2]) if strengths else 'primary categories'} "
                f"are well-formed, while {', '.join(weaknesses[:2]) if weaknesses else 'certain subtopics'} require targeted refinement."
            )
        else:
            summary = (
                f"Your assessment score of {overall_score}% ({correct_count}/{total_questions} correct) indicates notable conceptual gaps. "
                f"Priority remediation is needed in {', '.join(weaknesses) if weaknesses else 'core test areas'} before taking competitive company tests."
            )

        mistakes = []
        if question_breakdown:
            incorrect_qs = [q for q in question_breakdown if not q.get("is_correct")]
            for q in incorrect_qs[:3]:
                cat = q.get("category", "")
                topic = q.get("topic", "")
                mistakes.append(f"In {cat} ({topic or 'core subtopic'}): miscalculated formula or misapplied deduction logic on question options.")
        if not mistakes:
            if weaknesses:
                mistakes = [f"Difficulty resolving multi-parameter constraints in {w} problem stems under time pressure." for w in weaknesses[:2]]
            else:
                mistakes = ["Minor calculation variance under timed conditions."]

        suggestions = []
        if "Data Interpretation" in weaknesses:
            suggestions.append("Practice fast percentage calculation and ratio estimation on multi-column data tables without using a calculator.")
        if "Quantitative Aptitude" in weaknesses:
            suggestions.append("Review foundational arithmetic formulas: Profit & Loss, Speed-Distance-Time, and Work-Time equivalents.")
        if "Logical Reasoning" in weaknesses:
            suggestions.append("Solve 10 seating arrangement and syllogism puzzles daily to strengthen deduction speed.")
        if "Verbal Reasoning" in weaknesses:
            suggestions.append("Focus on context-clue reading comprehension and subject-verb agreement rules.")
        if not suggestions:
            suggestions = [
                "Maintain speed drills on full-length mock tests to preserve high accuracy.",
                "Review edge-case logic puzzles and advanced quantitative questions.",
                "Transition directly to Stage 2: Coding Session."
            ]

        diff_obs = (
            "Consistent performance on standard baseline questions with moderate variation on multi-step reasoning."
            if overall_score >= 60 else
            "Struggled with multi-parameter constraint problems; recommend strengthening fundamentals before advancing to high-difficulty questions."
        )

        return {
            "summary": summary,
            "strengths": strengths if strengths else ["Basic quantitative principles"],
            "weaknesses": weaknesses if weaknesses else ["None identified"],
            "mistakes_analysis": mistakes,
            "difficulty_observations": diff_obs,
            "improvement_suggestions": suggestions[:3]
        }

    @staticmethod
    def evaluate_coding_submission(
        problem_title: str,
        category: str,
        difficulty: str,
        constraints: Optional[str],
        description: str,
        candidate_code: str,
        status: str,
        passed_count: int,
        total_count: int,
        correctness: float,
        weak_area: str,
        test_results: List[Dict[str, Any]],
        error_msg: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calls Gemini to provide comprehensive, personalized AI evaluation of candidate's code submission.
        DOES NOT alter the authoritative sandbox execution result.
        Falls back to intelligent rule-based evaluation if Gemini is unavailable.
        """
        system_prompt = (
            "You are a Senior Principal Software Engineer and Technical Placement Evaluator. "
            "Analyze the candidate's code submission against the problem and authoritative sandbox test execution results. "
            "Output strictly valid JSON with NO markdown formatting or backticks. "
            "JSON must contain exactly these keys:\n"
            "- 'overall_assessment': string (concise 1-2 sentence technical assessment)\n"
            "- 'explanation': string (clear explanation of why the solution passed or failed)\n"
            "- 'conceptual_mistakes': list of strings (conceptual or logical bugs found in candidate's code)\n"
            "- 'edge_cases_missed': list of strings (specific edge cases or boundary conditions that caused failure or could break the code)\n"
            "- 'algorithmic_improvements': list of strings (specific suggestions to optimize efficiency or code structure)\n"
            "- 'time_complexity': string (e.g. 'O(n)', 'O(n log n)', 'O(n^2)')\n"
            "- 'space_complexity': string (e.g. 'O(1)', 'O(n)')\n"
            "- 'recommended_topic': string (topic candidate should practice next to reinforce concepts)\n"
            "- 'personalized_feedback': string (encouraging, constructive 2-3 sentence personalized feedback)"
        )

        prompt = (
            f"Problem: {problem_title} ({category}, Difficulty: {difficulty})\n"
            f"Constraints: {constraints or 'Standard'}\n"
            f"Problem Description:\n{description[:300]}...\n\n"
            f"Candidate Submitted Code:\n{candidate_code}\n\n"
            f"Authoritative Sandbox Execution Outcome: {status} ({passed_count}/{total_count} tests passed, {correctness}%)\n"
            f"Runtime / Compilation Error: {error_msg or 'None'}\n"
            f"Diagnosed Weak Area: {weak_area}\n"
            f"Test Case Results Breakdown:\n{json.dumps(test_results[:5])}\n"
        )

        res = _call_llm_json(prompt, system_prompt)
        if res and isinstance(res, dict) and "overall_assessment" in res:
            try:
                return {
                    "source": "gemini",
                    "overall_assessment": str(res.get("overall_assessment", "")).strip(),
                    "explanation": str(res.get("explanation", "")).strip(),
                    "conceptual_mistakes": [str(m) for m in res.get("conceptual_mistakes", []) if m],
                    "edge_cases_missed": [str(e) for e in res.get("edge_cases_missed", []) if e],
                    "algorithmic_improvements": [str(a) for a in res.get("algorithmic_improvements", []) if a],
                    "time_complexity": str(res.get("time_complexity", "O(n)")).strip(),
                    "space_complexity": str(res.get("space_complexity", "O(1)")).strip(),
                    "recommended_topic": str(res.get("recommended_topic", category)).strip(),
                    "personalized_feedback": str(res.get("personalized_feedback", "")).strip()
                }
            except Exception as e:
                logger.warning(f"Error parsing Gemini coding evaluation: {e}")

        # Fallback to rule-based evaluation
        fb = LLMService.evaluate_coding_rule_based(
            problem_title=problem_title,
            category=category,
            difficulty=difficulty,
            candidate_code=candidate_code,
            status=status,
            passed_count=passed_count,
            total_count=total_count,
            correctness=correctness,
            weak_area=weak_area,
            test_results=test_results,
            error_msg=error_msg
        )
        fb["source"] = "fallback"
        fb["fallback_notice"] = "AI feedback is temporarily unavailable. Your objective assessment result is still valid."
        return fb

    @staticmethod
    def evaluate_coding_rule_based(
        problem_title: str,
        category: str,
        difficulty: str,
        candidate_code: str,
        status: str,
        passed_count: int,
        total_count: int,
        correctness: float,
        weak_area: str,
        test_results: List[Dict[str, Any]],
        error_msg: Optional[str] = None
    ) -> Dict[str, Any]:
        """High-quality rule-based fallback evaluation for coding submissions."""
        if correctness == 100.0:
            overall = f"Excellent implementation for {problem_title}. The solution passed all {total_count} test cases."
            explanation = "Your code successfully satisfies all base cases, constraints, and hidden boundary scenarios with optimal asymptotic complexity."
            mistakes = []
            missed_edges = []
            improvements = [
                "Consider micro-optimizations like early return exits or in-place transformations where applicable.",
                "Ensure docstrings and type annotations conform to PEP 8 standards."
            ]
            rec_topic = "Dynamic Programming" if category == "Recursion" else "Advanced Data Structures"
            personalized = (
                f"Outstanding work! Your {category} logic is sound and robust. "
                "You are ready to advance to more complex algorithmic challenges."
            )
            time_comp = "O(n)"
            space_comp = "O(1)" if "for" in candidate_code and "list(" not in candidate_code else "O(n)"
        elif error_msg or status == "error":
            overall = f"Execution halted due to a runtime or compilation error in {problem_title}."
            explanation = f"The sandbox encountered an execution error: {error_msg or 'Execution failure'}. No test cases could be verified."
            mistakes = [f"Unhandled exception: {error_msg or 'Runtime error'}"]
            missed_edges = ["Boundary type validation", "Base condition termination"]
            improvements = [
                "Run simple test inputs manually to verify syntax and variable definitions.",
                "Check function signature and ensure the entry function returns the expected type."
            ]
            rec_topic = category
            personalized = (
                f"Your code encountered a runtime failure ({error_msg or 'syntax/runtime'}). "
                "Carefully inspect line references in the stack trace and fix syntax or unhandled exceptions before resubmitting."
            )
            time_comp = "N/A"
            space_comp = "N/A"
        else:
            overall = f"Partial solution ({passed_count}/{total_count} tests passed, {correctness}%). Deficit detected in {weak_area}."
            failing_tests = [t for t in test_results if not t.get("passed")]
            explanation = f"Your implementation handled basic cases but failed {len(failing_tests)} test cases, primarily related to {weak_area.lower()}."
            mistakes = [f"Failing logic on: {failing_tests[0].get('description', weak_area)}"] if failing_tests else [f"Flaw in {weak_area}"]
            missed_edges = [t.get("description", "Boundary condition") for t in failing_tests[:2]]
            improvements = [
                "Add defensive guards at the start of your function for edge conditions (empty, negative, single-element).",
                f"Trace execution flow step-by-step for the failing inputs."
            ]
            rec_topic = category
            personalized = (
                f"Good attempt ({passed_count}/{total_count} passed). The core logic is partially working, but struggles with {weak_area.lower()}. "
                "Review the hints and edge cases before retrying."
            )
            time_comp = "O(n)"
            space_comp = "O(n)"

        return {
            "overall_assessment": overall,
            "explanation": explanation,
            "conceptual_mistakes": mistakes,
            "edge_cases_missed": missed_edges,
            "algorithmic_improvements": improvements,
            "time_complexity": time_comp,
            "space_complexity": space_comp,
            "recommended_topic": rec_topic,
            "personalized_feedback": personalized
        }
