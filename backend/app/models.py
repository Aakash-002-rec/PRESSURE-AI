from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

# Authentication Models
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Optional[str] = "candidate"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Domain & Topic Models
class TopicResponse(BaseModel):
    id: int
    domain_id: int
    name: str
    description: Optional[str] = None

class DomainResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str] = None

class DomainWithTopicsResponse(DomainResponse):
    topics: List[TopicResponse] = []

class TopicCreate(BaseModel):
    domain_id: int
    name: str
    description: Optional[str] = None

# Interview Creation & Management Models
class InterviewCreate(BaseModel):
    domain_id: int
    topic_id: Optional[int] = None
    difficulty: str = Field("Intermediate", pattern="^(Beginner|Intermediate|Advanced)$")
    interview_type: str = Field("Mixed", pattern="^(Technical|Conceptual|Coding|Mixed)$")
    total_questions: int = Field(10, ge=5, le=25)

class InterviewSummary(BaseModel):
    id: int
    user_id: int
    domain_id: int
    domain_name: str
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    difficulty: str
    current_difficulty: str
    interview_type: str
    total_questions: int
    answered_questions: int
    overall_score: Optional[float] = None
    status: str
    pressure_mode_active: bool
    pressure_topic_name: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None

# Question & Answer Models
class QuestionResponse(BaseModel):
    id: int
    interview_id: int
    topic_id: int
    topic_name: str
    sequence_number: int
    total_questions: int
    question_text: str
    difficulty: str
    question_type: str
    hints_used: int
    hints_available: int
    is_pressure_mode: bool
    difficulty_transition_reason: Optional[str] = None
    code_snippet: Optional[str] = None
    code_language: Optional[str] = "python"
    starter_code: Optional[str] = None
    source: Optional[str] = None

class AnswerSubmit(BaseModel):
    answer_text: str = Field(..., min_length=1)
    code_answer: Optional[str] = None
    language: Optional[str] = "python"

class AnswerEvaluationResponse(BaseModel):
    question_id: int
    correctness: float
    relevance: float
    conceptual_understanding: float
    completeness: float
    overall_score: float
    topic: str
    weakness_detected: bool
    weakness_level: Optional[str] = None
    missing_concepts: List[str] = []
    feedback: str
    reference_code: Optional[str] = None
    next_difficulty: str
    difficulty_changed: bool
    difficulty_change_reason: Optional[str] = None
    pressure_mode_activated: bool
    is_interview_completed: bool
    technical_mistakes: Optional[List[str]] = []
    strengths: Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []
    improvement_suggestions: Optional[List[str]] = []
    source: Optional[str] = None

class HintRequest(BaseModel):
    pass

class HintResponse(BaseModel):
    hint_level: int
    hint_text: str
    remaining_hints: int
    total_hints_used: int

# Detailed Evaluation & Recommendation Models
class TopicPerformance(BaseModel):
    topic_id: int
    topic_name: str
    score: float
    attempts: int
    weakness_level: str # 'Strong', 'Average', 'Weak'
    missing_concepts: List[str] = []

class WeaknessReportItem(BaseModel):
    topic_id: int
    topic_name: str
    severity: str
    average_score: float
    attempts_count: int
    missing_concepts: List[str]

class PracticeQuestion(BaseModel):
    level: str # 'Easy', 'Medium', 'Advanced'
    question: str
    key_focus: str

class LearningRecommendation(BaseModel):
    topic_id: int
    topic_name: str
    performance_score: float
    why_weak: List[str]
    concepts_to_learn: List[str]
    action_plan: List[str]
    practice_questions: List[PracticeQuestion]

class LearningRoadmapStage(BaseModel):
    stage_number: int
    title: str
    focus_topic: str
    action_items: List[str]
    estimated_duration: str
    objective: str

class QuestionDetail(BaseModel):
    sequence_number: int
    topic_name: str
    question_text: str
    difficulty: str
    question_type: str
    is_pressure_mode: bool
    answer_text: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    missing_concepts: List[str] = []
    hints_used: int = 0

class InterviewReportResponse(BaseModel):
    interview_id: int
    candidate_name: str
    domain_name: str
    difficulty_configured: str
    final_difficulty: str
    interview_type: str
    total_questions: int
    questions_attempted: int
    started_at: str
    completed_at: Optional[str] = None
    overall_score: float
    category_scores: Dict[str, float]
    topic_performance: List[TopicPerformance]
    strong_areas: List[str]
    weak_areas: List[str]
    pressure_mode_topics: List[str]
    hints_used_total: int
    questions_detail: List[QuestionDetail]
    recommendations: List[LearningRecommendation]
    learning_roadmap: List[LearningRoadmapStage]

# Progress Models
class ProgressHistoryItem(BaseModel):
    interview_id: int
    domain_name: str
    started_at: str
    completed_at: Optional[str]
    total_questions: int
    overall_score: float
    difficulty: str
    weak_topics_count: int
    pressure_mode_triggered: bool

class TopicProgressDelta(BaseModel):
    topic_name: str
    first_score: float
    latest_score: float
    delta: float
    trend: str # 'improved', 'declined', 'stable'
    attempts_count: int
    message: str

class ProgressOverview(BaseModel):
    total_interviews_completed: int
    average_score: float
    best_score: float
    strongest_topics: List[str]
    persistent_weak_topics: List[str]
    topic_improvements: List[TopicProgressDelta]
    history: List[ProgressHistoryItem]

# Admin Dashboard Models
class AdminDashboardStats(BaseModel):
    total_candidates: int
    total_interviews: int
    average_platform_score: float
    completed_interviews: int
    top_weak_topics: List[Dict[str, Any]]
    recent_interviews: List[Dict[str, Any]]
    domain_distribution: List[Dict[str, Any]]
    total_aptitude_attempts: Optional[int] = 0
    total_coding_attempts: Optional[int] = 0
    average_aptitude_score: Optional[float] = 0.0
    average_coding_score: Optional[float] = 0.0

# Aptitude Models
class AptitudeQuestionResponse(BaseModel):
    id: int
    category: str
    difficulty: str
    question: str
    options: List[str]
    topic: Optional[str] = None

class AptitudeAnswerSubmission(BaseModel):
    question_id: int
    selected_option: Optional[int] = None

class AptitudeTestSubmit(BaseModel):
    category: str
    difficulty: str
    total_questions: int
    time_taken_seconds: int
    answers: List[AptitudeAnswerSubmission]

class AptitudeResultResponse(BaseModel):
    attempt_id: int
    overall_score: float
    total_questions: int
    correct_count: int
    incorrect_count: int
    accuracy: float
    time_taken_seconds: int
    category_performance: Dict[str, float]
    weak_categories: List[str]
    recommendation: str
    ai_evaluation: Optional[Dict[str, Any]] = None

# Coding Models
class CodingProblemSummary(BaseModel):
    id: int
    title: str
    category: str
    difficulty: str
    language: str
    description: str
    starter_code: str
    constraints: Optional[str] = None
    hints: List[str] = []
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    status: Optional[str] = "unseen" # 'unseen', 'in_progress', 'completed'
    question_number: Optional[int] = 1
    total_questions: Optional[int] = 3

class CodingStatusResponse(BaseModel):
    completed_count: int
    in_progress_count: int
    remaining_unseen_count: int
    total_problems_count: int
    has_unseen: bool
    has_incomplete: bool
    all_completed: bool
    session_limit: Optional[int] = 3
    current_question_number: Optional[int] = 1

class CodingRunRequest(BaseModel):
    problem_id: int
    code: str
    language: str = "python"

class CodingSubmitRequest(BaseModel):
    problem_id: int
    code: str
    language: str = "python"

class CodingResultResponse(BaseModel):
    attempt_id: Optional[int] = None
    status: str
    passed_count: int
    total_count: int
    correctness: float
    time_complexity: Optional[str] = "O(n)"
    space_complexity: Optional[str] = "O(n)"
    weak_area: Optional[str] = None
    ai_feedback: str
    hints: List[str] = []
    test_results: List[Dict[str, Any]] = []
    stdout: Optional[str] = ""
    error: Optional[str] = None
    ai_evaluation: Optional[Dict[str, Any]] = None

# Practice & Roadmap Models
class PracticeQuestionResponse(BaseModel):
    id: int
    topic: str
    difficulty: str
    question: str
    options: List[str]

class PracticeAnswerItem(BaseModel):
    question_id: int
    selected_option: int

class PracticeSubmitRequest(BaseModel):
    topic: str
    difficulty: str
    answers: List[PracticeAnswerItem]

class PracticeResultResponse(BaseModel):
    topic: str
    difficulty: str
    score: float
    total_questions: int
    correct_count: int
    updated_topic_score: float
    improvement_message: str
    details: List[Dict[str, Any]]

class RoadmapTaskItem(BaseModel):
    id: int
    topic: str
    stage_number: int
    title: str
    objective: Optional[str] = None
    status: str # 'not_started', 'in_progress', 'completed'
    completed_at: Optional[str] = None

class RoadmapTaskUpdate(BaseModel):
    task_id: int
    status: str

# Combined Assessment Models
class MajorWeaknessItem(BaseModel):
    topic: str
    score: float
    modules: List[str]
    reason: str

class CombinedAssessmentResponse(BaseModel):
    user_id: int
    overall_readiness: float
    aptitude_score: float
    coding_score: float
    interview_score: float
    aptitude_categories: Dict[str, float]
    coding_topics: Dict[str, float]
    interview_topics: Dict[str, float]
    strong_topics: List[Dict[str, Any]]
    average_topics: List[Dict[str, Any]]
    weak_topics: List[Dict[str, Any]]
    major_weaknesses: List[MajorWeaknessItem]
    recommended_priority: List[str]
