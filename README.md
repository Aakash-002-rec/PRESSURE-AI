# PRESSURE-AI: Adaptive AI-Powered Interview & Personalized Learning Platform

[![Status: Operational](https://img.shields.io/badge/Status-Operational-brightgreen)](#)
[![Stack: FastAPI + React + Vite](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20Tailwind-blue)](#)
[![Engine: Adaptive Difficulty & Pressure Mode](https://img.shields.io/badge/Engine-Pressure%20Mode%20Active-orange)](#)

> **"PRESSURE-AI is an adaptive AI-powered interview and assessment platform that analyzes candidate responses, identifies weak concepts, dynamically adapts interview difficulty, provides targeted pressure questions, and generates a personalized learning roadmap for improvement."**

---

## 1. Problem Statement
Traditional online technical assessments and mock interview platforms rely on static question sets or generic conversational chatbots. They suffer from critical limitations:
- **Zero Real-Time Adaptation**: Questions are fixed regardless of whether a candidate finds them trivial or struggles hopelessly.
- **Surface-Level Feedback**: Chatbots offer vague polite praise or reveal solutions prematurely without diagnosing fundamental conceptual gaps.
- **Absence of Diagnostic Stress**: Live technical interviews at elite tech companies assess how engineers behave under targeted conceptual pressure when edge cases are pushed.
- **Disconnected Learning**: Candidates are left with a raw percentage score without an actionable, step-by-step curriculum to systematically eliminate root weaknesses.

---

## 2. Abstract
**PRESSURE-AI** resolves these challenges by introducing a closed-loop adaptive interview and assessment engine. Rather than simply functioning as a chatbot, the platform couples an AI interviewer persona with server-side decision modules:
1. Evaluates candidate answers across 4 strict dimensions: **Correctness, Relevance, Conceptual Depth, and Completeness**.
2. Tracks topic mastery and runs a **Rule-Based Weakness Detection Engine**.
3. Dynamically adapts subsequent question difficulty (*Beginner → Intermediate → Advanced*).
4. Provides a **3-Level Progressive Hint System** that guides candidates without revealing answers.
5. Ignites **🔥 PRESSURE MODE** when repeated deficits are detected on a concept, delivering deep scenario-based and debugging probes.
6. Compiles an exhaustive post-interview **Performance Report**, a **Personalized Remediation Plan**, and an **AI-Generated 5-Stage Learning Roadmap**.
7. Persists multi-attempt history to provide longitudinal progress comparisons (*"Your Recursion performance improved from 42% to 81%"*).

---

## 3. Objectives
- **Conduct Context-Aware AI Interviews**: Simulate realistic, professional technical interviews across 13 major computer science domains.
- **Structured Multi-Dimensional Grading**: Return rigorous numeric evaluations and diagnose missing concepts without exposed reasoning artifacts.
- **Autonomous Difficulty Calibration**: Scale difficulty up on proven competence, down to rebuild foundations, and store transition rationales.
- **Implement Pressure Mode**: Rigorously probe identified conceptual gaps from alternative angles.
- **Provide Actionable Roadmaps**: Transition candidates immediately from diagnostic failure to a structured, 5-stage learning plan.
- **Facilitate Candidate & Manager Oversight**: Provide dedicated Candidate and Admin portals for progress tracking and cohort analytics.

---

## 4. Existing System vs. Proposed System

| Dimension | Conventional Mock Platforms | PRESSURE-AI (Proposed System) |
|---|---|---|
| **Question Sequencing** | Static or random question lists | Dynamic, state-driven adaptive sequencing |
| **Evaluation Depth** | Binary pass/fail or unstructured prose | Structured 4-axis JSON scoring + missing concepts |
| **Difficulty Flow** | Fixed at session start | Live dynamic calibration (Promote, Maintain, Calibrate) |
| **Assistance System** | Direct answer reveal or no hints | 3-Level progressive clues with evaluation tracking |
| **Handling Weakness** | Skips topic or repeats same question | **🔥 Pressure Mode**: Deep targeted probes from new angles |
| **Post-Session Output** | Raw numeric score | Performance Report + Remediation Plan + 5-Stage Roadmap |
| **Progress Over Time** | Isolated attempt logs | Longitudinal topic-delta tracking (*Initial vs. Latest %*) |

---

## 5. Literature Review Placeholder
*Modern computer-adaptive testing (CAT) traces its origins to Item Response Theory (IRT), traditionally applied in standardized psychometric examinations. In technical software engineering recruitment, conventional CAT approaches fall short because coding answers are multi-faceted, open-ended, and context-dependent. Recent developments in Large Language Models (LLMs) enable real-time semantic extraction and conceptual classification. PRESSURE-AI synthesizes rule-based decision trees with LLM semantic evaluators, ensuring deterministic progression guardrails while benefiting from nuanced natural-language comprehension.*

---

## 6. System Architecture

```
                                      +-----------------------------------+
                                      |         CANDIDATE / ADMIN         |
                                      +-----------------------------------+
                                                        |
                                                        v
                                      +-----------------------------------+
                                      |     React + Vite + Tailwind UI    |
                                      +-----------------------------------+
                                                        |  HTTPS / REST / JWT
                                                        v
                                      +-----------------------------------+
                                      |        FastAPI Backend API        |
                                      +-----------------------------------+
                                                        |
                     +----------------------------------+----------------------------------+
                     |                                  |                                  |
                     v                                  v                                  v
+------------------------------------+  +-------------------------------+  +-------------------------------+
|         INTERVIEW MANAGER          |  |       AUTH & ADMIN APIS       |  |     PROGRESS TRACKING API     |
+------------------------------------+  +-------------------------------+  +-------------------------------+
  |               |                 |                   |                                  |
  |               |                 |                   +----------------+                 |
  v               v                 v                                    v                 v
+-----------+  +------------+  +-------------------+               +-------------------------------+
| AI Engine |  | Hint Engine|  | Weakness Engine   |               |         SQLite Database       |
+-----------+  +------------+  +-------------------+               +-------------------------------+
  |               |                 |                                              ^
  |               v                 |                                              |
  |      [Level 1, 2, 3 Hints]      v                                              |
  |                        +-----------------------+                               |
  +----------------------->| Dynamic Difficulty    |                               |
                           | & 🔥 PRESSURE MODE    |-------------------------------+
                           +-----------------------+
                                    |
                                    v
                           +-----------------------+
                           |  Learning Engine &    |
                           |  5-Stage Roadmap      |
                           +-----------------------+
```

---

## 7. Supported Domains & Expandability

PRESSURE-AI is designed with a database-driven domain and topic architecture. More domains can be added without code modifications.

### Initial 13 Supported Domains:
1. **Programming Languages**:
   - Python
   - Java
   - C
   - C++
   - JavaScript
2. **Core Technical Subjects**:
   - Data Structures
   - Algorithms
   - DBMS (Database Management Systems)
   - Operating Systems
   - Computer Networks
   - OOP (Object-Oriented Programming)
   - SQL
   - HTML/CSS

---

## 8. Modules & Key Innovations

### A. AI Interviewer Persona & Question Generation
- Welcoming, professional technical demeanor.
- Presents one question at a time across 10 varied formats (*Definition, Conceptual, Example-based, Scenario-based, Debugging, Coding, Output prediction, Comparison, Why/how, Problem-solving*).
- Never leaks internal reasoning or chain-of-thought to the client.

### B. Answer Evaluation Module
- Evaluates answers using structured JSON schema:
  - `correctness` (1–10)
  - `relevance` (1–10)
  - `conceptual_understanding` (1–10)
  - `completeness` (1–10)
  - `overall_score` (1–10)
  - `weakness_detected` (boolean)
  - `weakness_level` (*mild, moderate, severe*)
  - `missing_concepts` (array of strings)
  - `feedback` (professional targeted critique)

### C. Rule-Based Weakness Detection Engine
- Evaluates score distribution per topic:
  - Score $\ge 7.5$: **Strong**
  - Score $5.0 - 7.4$: **Average**
  - Score $< 5.0$: **Weak**
- Detects recurring deficits across attempts and isolates conceptual missing elements.

### D. Adaptive Difficulty Engine
- **Strong Response**: Escalates difficulty (*Beginner → Intermediate → Advanced*).
- **Average Response**: Maintains current difficulty to test consistency.
- **Weak Response**: Calibrates difficulty down or provides a targeted baseline question.
- Every transition is logged with a human-readable reason.

### E. 3-Level Progressive Hint System
- **Level 1**: Subtle conceptual orientation clue.
- **Level 2**: Specific guidance regarding mechanics or trade-offs.
- **Level 3**: Strong directional clue without revealing the complete solution.
- Hint usage is tracked and recorded in the final evaluation report.

### F. 🔥 PRESSURE MODE (Core Innovation)
- Triggers when a candidate scores poorly consecutively on the same concept or exhibits critical knowledge gaps.
- Renders an unmistakable fiery visual banner with ambient glow.
- Switches questioning strategy from general topics to intense, multi-angle probes (*debugging scenarios, runtime execution tracing, edge-case failure modes*).

### G. Final Performance Report & Analytics
- Overall score percentage gauge.
- 4-category dimensional breakdown.
- Topic-wise mastery cards.
- Explicit lists of Strong vs. Weak conceptual areas.
- Pressure Mode activation history and total hints consumed.

### H. Personalized Learning Recommendations & 5-Stage Roadmap
For every weak topic:
1. **Why It Is Considered Weak**: Exact root gaps identified.
2. **Concepts to Learn**: 5 fundamental focus areas.
3. **5-Step Action Plan**: Concrete study progression.
4. **Targeted Practice**: Easy, Medium, and Advanced practice problems.
5. **5-Stage Roadmap**: Progression timeline from review to retaking the interview.

### I. Progress Tracking & Multi-Interview Comparison
- Longitudinal tracking across sessions.
- Automatically computes topic improvement deltas (*e.g., "Your Recursion performance improved from 42% to 81% (+39%)"*).

### J. Admin & Management Dashboard
- High-level platform KPIs: Total candidates, Total sessions, Platform average score, Completed sessions.
- Most frequent weak topics across the student/candidate population.
- Candidate inspection directory with full audit access to past interview transcripts and reports.

---

## 9. Technology Stack

- **Backend**: Python 3.14+, FastAPI, Uvicorn, Pydantic v2
- **Database**: SQLite with foreign key constraints and transactional integrity
- **Security**: PyJWT, Bcrypt password hashing, Bearer Token authorization
- **AI Integration**: Google Gemini API (`google-generativeai`) / OpenAI API (`openai`), backed by a built-in intelligent fallback engine
- **Frontend**: React 19, Vite, Tailwind CSS v4, Lucide React, Recharts, Canvas-Confetti

---

## 10. Database Design

```sql
users (id, name, email, password_hash, role, created_at)
domains (id, name, category, description)
topics (id, domain_id, name, description)
interviews (id, user_id, domain_id, topic_id, difficulty, current_difficulty, 
            interview_type, total_questions, overall_score, technical_score, 
            conceptual_score, problem_solving_score, communication_score, 
            status, pressure_mode_active, pressure_topic_id, consecutive_weak_count, 
            hints_used_total, started_at, completed_at)
questions (id, interview_id, topic_id, question_text, difficulty, question_type, 
           sequence_number, expected_concepts, evaluation_criteria, is_pressure_mode, 
           difficulty_transition_reason, created_at)
answers (id, question_id, answer_text, correctness, relevance, conceptual_understanding, 
         completeness, overall_score, hints_used, feedback, missing_concepts, 
         weakness_detected, weakness_level, created_at)
hint_logs (id, question_id, hint_level, hint_text, created_at)
weaknesses (id, interview_id, topic_id, severity, average_score, attempts_count, 
            missing_concepts, created_at)
recommendations (id, interview_id, topic_id, topic_name, performance_score, why_weak, 
                 concepts_to_learn, action_plan, practice_questions, created_at)
difficulty_transitions (id, interview_id, from_difficulty, to_difficulty, reason, 
                        sequence_number, created_at)
```

---

## 11. API Documentation

### Authentication
- `POST /auth/register`: Create candidate or admin account
- `POST /auth/login`: Authenticate and obtain JWT bearer token
- `GET /auth/me`: Retrieve current user profile and role

### Domains & Topics
- `GET /domains`: List all domains with nested topics
- `GET /domains/{id}/topics`: List topics for specific domain
- `POST /topics`: Admin endpoint to register new interview topics

### Interviews & Live Arena
- `POST /interviews`: Initialize an adaptive interview session
- `GET /interviews`: List candidate's past interview sessions
- `GET /interviews/{id}`: Fetch interview status and configuration
- `GET /interviews/{id}/questions/next`: Fetch current or generate next adaptive question
- `POST /questions/{id}/answer`: Submit technical answer and receive real-time evaluation
- `POST /questions/{id}/hint`: Request next progressive hint (Levels 1–3)
- `GET /interviews/{id}/report`: Compile comprehensive performance report and roadmap
- `GET /interviews/{id}/recommendations`: Retrieve personalized learning recommendations

### Progress & Analytics
- `GET /progress`: Retrieve longitudinal progress statistics and topic improvement deltas
- `GET /admin/dashboard`: Admin overview with candidate volume and weakness metrics
- `GET /admin/candidates`: Candidate registry and audit directory

---

## 12. Installation Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Clone & Setup Workspace
```bash
cd "c:/Users/AAKASH R/Desktop/pressure ai"
```

### 2. Configure Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m pip install email-validator
python app/database.py
```

### 3. Configure Frontend
```bash
cd ../frontend
npm install
```

---

## 13. Environment Variables

Create or edit `backend/.env`:
```env
PORT=8000
HOST=0.0.0.0
JWT_SECRET=pressure_ai_super_secret_jwt_key_2026_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LLM API Configuration (Optional)
# If provided, questions and evaluations will leverage live Gemini/OpenAI models.
# If omitted or offline, the intelligent built-in fallback bank seamlessly powers the demo!
GEMINI_API_KEY=
OPENAI_API_KEY=
DEFAULT_LLM_PROVIDER=gemini
```

---

## 14. How to Run

### Start Backend API Server
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API docs available at: `http://127.0.0.1:8000/docs`*

### Start Frontend Client
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
*Web application available at: `http://127.0.0.1:5173/`*

---

## 15. Sample Demo Credentials

| Role | Email | Password | Quick Access |
|---|---|---|---|
| **Candidate** | `candidate@pressure.ai` | `candidate123` | Click **Candidate Demo** button |
| **Admin** | `admin@pressure.ai` | `admin123` | Click **Admin Demo** button |

---

## 16. Step-by-Step Demo Workflow

1. Navigate to `http://127.0.0.1:5173/` in your browser.
2. Click **Sign In / Demo** in the top navigation, then select **Candidate Demo**.
3. In the **Interview Arena Setup**:
   - Select **Python**.
   - Select **Intermediate** starting difficulty.
   - Select **Mixed** format.
   - Select **10 Questions** (or 5 for rapid demonstration).
   - Click **Start AI Interview**.
4. **Demonstrate Adaptive Difficulty Promotion**:
   - On Question 1, click the quick helper **"Fill Strong Answer (Promote Diff)"** and click **Submit Technical Answer**.
   - Observe the evaluation score ($\ge 7.5$), feedback, and the adaptive engine notification escalating difficulty toward **Advanced**.
5. **Demonstrate 3-Level Progressive Hints**:
   - On Question 2, click **Get Hint (Level 1)** to view a conceptual clue.
   - Click **Get Hint (Level 2)** to view more specific guidance.
6. **Demonstrate Weakness Detection & Pressure Mode**:
   - On a question (e.g. Recursion), click **"Fill Weak Answer (Trigger Pressure)"** and submit.
   - Observe the score $(< 5.0)$ and missing concepts.
   - On the next question, submit another weak response.
   - Watch the platform trigger **🔥 PRESSURE MODE ACTIVATED** with an intense fiery banner and sound reasoning!
   - Observe the next question generate a deep, scenario-based probe testing the exact weak concept from an architectural angle.
7. **Demonstrate Final Performance Report**:
   - Complete the session to view the score gauge, category breakdown, strong areas, weak areas, and Pressure Mode summary.
8. **Demonstrate Personalized Learning Recommendation & Roadmap**:
   - Switch to the **Personalized Recommendations** tab to see why the topic was weak, concepts to learn, a 5-step action plan, and 3 practice problems.
   - Switch to the **5-Stage Learning Roadmap** tab to inspect the structured curriculum.
9. **Demonstrate Progress Tracking**:
   - Click **My Progress** in the navbar to observe the score trajectory and the topic improvement message (*e.g. "Your Recursion performance improved from 42% to 81%"*).
10. **Demonstrate Admin Console**:
    - Sign in as Admin (`admin@pressure.ai`) and view candidate completion telemetry, cohort weak topics, and audit individual candidate reports.

---

## 17. Limitations & Future Enhancements

### Limitations
- Audio and real-time video streaming are not included in the initial release.
- Code execution is evaluated semantically and syntactically via AI rather than an isolated container sandbox (e.g. Docker/gVisor).

### Future Enhancements
- Integration with sandboxed code execution environments (e.g., Judge0 or Pyodide).
- Voice conversational mode utilizing low-latency speech-to-text (Whisper) and text-to-speech.
- Peer-comparison percentiles and institutional classroom management portals.
