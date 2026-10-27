import sqlite3
import os
from pathlib import Path
from datetime import datetime
import bcrypt

DB_PATH = Path(__file__).resolve().parent.parent / "pressure_ai.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'candidate', -- 'candidate' or 'admin'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Domains table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domains (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL DEFAULT 'Technical',
        description TEXT
    );
    """)

    # Topics table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (domain_id) REFERENCES domains (id) ON DELETE CASCADE,
        UNIQUE (domain_id, name)
    );
    """)

    # Interviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        domain_id INTEGER NOT NULL,
        topic_id INTEGER,
        difficulty TEXT NOT NULL, -- 'Beginner', 'Intermediate', 'Advanced'
        current_difficulty TEXT NOT NULL,
        interview_type TEXT NOT NULL, -- 'Technical', 'Conceptual', 'Coding', 'Mixed'
        total_questions INTEGER NOT NULL DEFAULT 10,
        overall_score REAL DEFAULT NULL,
        technical_score REAL DEFAULT NULL,
        conceptual_score REAL DEFAULT NULL,
        problem_solving_score REAL DEFAULT NULL,
        communication_score REAL DEFAULT NULL,
        status TEXT NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'
        pressure_mode_active INTEGER NOT NULL DEFAULT 0,
        pressure_topic_id INTEGER DEFAULT NULL,
        consecutive_weak_count INTEGER NOT NULL DEFAULT 0,
        hints_used_total INTEGER NOT NULL DEFAULT 0,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (domain_id) REFERENCES domains (id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE SET NULL,
        FOREIGN KEY (pressure_topic_id) REFERENCES topics (id) ON DELETE SET NULL
    );
    """)

    # Questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        topic_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        question_type TEXT NOT NULL, -- 'Definition', 'Conceptual', 'Example-based', 'Scenario-based', 'Debugging', 'Coding', 'Output prediction', 'Comparison', 'Why/how', 'Problem-solving'
        sequence_number INTEGER NOT NULL,
        expected_concepts TEXT, -- JSON array
        evaluation_criteria TEXT,
        is_pressure_mode INTEGER NOT NULL DEFAULT 0,
        difficulty_transition_reason TEXT,
        code_snippet TEXT, -- Provided code snippet for debugging, output prediction, or review
        code_language TEXT DEFAULT 'python', -- Programming language of snippet
        starter_code TEXT, -- Starter boilerplate code for candidate to write solution
        fingerprint TEXT, -- Normalized content fingerprint for deduplication
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (interview_id) REFERENCES interviews (id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
    );
    """)

    # Answers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER UNIQUE NOT NULL,
        answer_text TEXT NOT NULL,
        code_answer TEXT, -- Candidate written code solution
        correctness REAL NOT NULL,
        relevance REAL NOT NULL,
        conceptual_understanding REAL NOT NULL,
        completeness REAL NOT NULL,
        overall_score REAL NOT NULL,
        hints_used INTEGER NOT NULL DEFAULT 0,
        feedback TEXT,
        missing_concepts TEXT, -- JSON array
        weakness_detected INTEGER NOT NULL DEFAULT 0,
        weakness_level TEXT, -- 'mild', 'moderate', 'severe'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
    );
    """)

    # Hints table (tracking hint requests per question)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hint_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        hint_level INTEGER NOT NULL, -- 1, 2, 3
        hint_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
    );
    """)

    # Weaknesses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weaknesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        topic_id INTEGER NOT NULL,
        severity TEXT NOT NULL, -- 'Low', 'Moderate', 'High'
        average_score REAL NOT NULL,
        attempts_count INTEGER NOT NULL DEFAULT 1,
        missing_concepts TEXT, -- JSON array
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (interview_id) REFERENCES interviews (id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
    );
    """)

    # Recommendations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        topic_id INTEGER NOT NULL,
        topic_name TEXT NOT NULL,
        performance_score REAL NOT NULL,
        why_weak TEXT NOT NULL, -- JSON array of reasons
        concepts_to_learn TEXT NOT NULL, -- JSON array of concepts
        action_plan TEXT NOT NULL, -- JSON array of steps
        practice_questions TEXT NOT NULL, -- JSON array of questions with difficulty
        code_examples TEXT, -- JSON array of practical code examples and fixes
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (interview_id) REFERENCES interviews (id) ON DELETE CASCADE,
        FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
    );
    """)

    # Difficulty transitions log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS difficulty_transitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        from_difficulty TEXT NOT NULL,
        to_difficulty TEXT NOT NULL,
        reason TEXT NOT NULL,
        sequence_number INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (interview_id) REFERENCES interviews (id) ON DELETE CASCADE
    );
    """)

    # Aptitude Questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aptitude_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL, -- 'Quantitative Aptitude', 'Logical Reasoning', 'Verbal Ability', 'Data Interpretation'
        difficulty TEXT NOT NULL, -- 'Beginner', 'Intermediate', 'Advanced'
        question TEXT NOT NULL,
        options TEXT NOT NULL, -- JSON array of strings
        correct_answer INTEGER NOT NULL, -- 0-3 index
        explanation TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Aptitude Attempts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aptitude_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        total_questions INTEGER NOT NULL,
        correct_count INTEGER NOT NULL,
        incorrect_count INTEGER NOT NULL,
        score REAL NOT NULL,
        time_taken_seconds INTEGER NOT NULL,
        category_breakdown TEXT, -- JSON dict of category: percentage
        weak_categories TEXT, -- JSON array of string category names
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Aptitude Answers log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aptitude_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_option INTEGER,
        is_correct INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attempt_id) REFERENCES aptitude_attempts (id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES aptitude_questions (id) ON DELETE CASCADE
    );
    """)

    # Coding Problems table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coding_problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL, -- 'Recursion', 'Arrays', 'Strings', 'Data Structures', 'Algorithms'
        difficulty TEXT NOT NULL, -- 'Beginner', 'Intermediate', 'Advanced'
        language TEXT NOT NULL DEFAULT 'python',
        description TEXT NOT NULL,
        starter_code TEXT NOT NULL,
        test_cases TEXT NOT NULL, -- JSON array of test cases
        constraints TEXT,
        hints TEXT, -- JSON array of strings
        time_complexity TEXT,
        space_complexity TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Coding Attempts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coding_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        problem_id INTEGER NOT NULL,
        language TEXT NOT NULL DEFAULT 'python',
        submitted_code TEXT NOT NULL,
        status TEXT NOT NULL, -- 'passed', 'failed', 'error'
        passed_tests INTEGER NOT NULL,
        total_tests INTEGER NOT NULL,
        correctness REAL NOT NULL,
        time_complexity TEXT,
        space_complexity TEXT,
        weak_area TEXT,
        ai_feedback TEXT,
        hints_used INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (problem_id) REFERENCES coding_problems (id) ON DELETE CASCADE
    );
    """)

    # Practice Questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS practice_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        difficulty TEXT NOT NULL, -- 'Easy', 'Medium', 'Advanced'
        question TEXT NOT NULL,
        options TEXT NOT NULL, -- JSON array of options
        correct_answer INTEGER NOT NULL,
        explanation TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Practice Attempts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS practice_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        score REAL NOT NULL,
        total_questions INTEGER NOT NULL,
        correct_count INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Learning Roadmap Tasks table (Interactive progress)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roadmap_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        stage_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        objective TEXT,
        status TEXT NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE(user_id, topic, stage_number)
    );
    """)

    # Combined Assessments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS combined_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        aptitude_score REAL,
        coding_score REAL,
        interview_score REAL,
        overall_score REAL,
        aptitude_attempt_id INTEGER,
        coding_attempt_id INTEGER,
        interview_id INTEGER,
        major_weaknesses TEXT, -- JSON array
        skill_profile TEXT, -- JSON dict
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Coding Sessions table (Session-aware question tracking & persistent limits)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coding_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id TEXT UNIQUE NOT NULL,
        language TEXT NOT NULL DEFAULT 'python',
        domain TEXT NOT NULL DEFAULT 'Algorithms',
        difficulty TEXT NOT NULL DEFAULT 'Intermediate',
        question_ids TEXT NOT NULL, -- JSON array of 3 assigned problem IDs [id1, id2, id3]
        question_order TEXT NOT NULL, -- JSON array of order [1, 2, 3]
        current_index INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed'
        attempt_id TEXT, -- Associated assessment attempt ID
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Assessment Attempts table (Full-pipeline Attempt / Retest orchestration)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed', 'archived'
        aptitude_attempt_id INTEGER,
        coding_session_id TEXT,
        interview_id INTEGER,
        aptitude_status TEXT NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
        coding_status TEXT NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
        interview_status TEXT NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    migrate_db(conn)
    seed_initial_data(conn)
    conn.close()

def migrate_db(conn: sqlite3.Connection):
    """Safely adds missing columns to existing SQLite database tables."""
    cursor = conn.cursor()
    # Check questions table
    cursor.execute("PRAGMA table_info(questions);")
    q_cols = [row["name"] for row in cursor.fetchall()]
    if "code_snippet" not in q_cols:
        cursor.execute("ALTER TABLE questions ADD COLUMN code_snippet TEXT;")
    if "code_language" not in q_cols:
        cursor.execute("ALTER TABLE questions ADD COLUMN code_language TEXT DEFAULT 'python';")
    if "starter_code" not in q_cols:
        cursor.execute("ALTER TABLE questions ADD COLUMN starter_code TEXT;")
    if "fingerprint" not in q_cols:
        cursor.execute("ALTER TABLE questions ADD COLUMN fingerprint TEXT;")

    # Check answers table
    cursor.execute("PRAGMA table_info(answers);")
    a_cols = [row["name"] for row in cursor.fetchall()]
    if "code_answer" not in a_cols:
        cursor.execute("ALTER TABLE answers ADD COLUMN code_answer TEXT;")

    # Check recommendations table
    cursor.execute("PRAGMA table_info(recommendations);")
    r_cols = [row["name"] for row in cursor.fetchall()]
    if "code_examples" not in r_cols:
        cursor.execute("ALTER TABLE recommendations ADD COLUMN code_examples TEXT;")

    # Check aptitude_questions table
    cursor.execute("PRAGMA table_info(aptitude_questions);")
    apt_cols = [row["name"] for row in cursor.fetchall()]
    if "topic" not in apt_cols:
        cursor.execute("ALTER TABLE aptitude_questions ADD COLUMN topic TEXT DEFAULT '';")

    # Check coding_problems table
    cursor.execute("PRAGMA table_info(coding_problems);")
    cp_cols = [row["name"] for row in cursor.fetchall()]
    if "input_format" not in cp_cols:
        cursor.execute("ALTER TABLE coding_problems ADD COLUMN input_format TEXT;")
    if "output_format" not in cp_cols:
        cursor.execute("ALTER TABLE coding_problems ADD COLUMN output_format TEXT;")
    if "fingerprint" not in cp_cols:
        cursor.execute("ALTER TABLE coding_problems ADD COLUMN fingerprint TEXT;")
    if "solution_code" not in cp_cols:
        cursor.execute("ALTER TABLE coding_problems ADD COLUMN solution_code TEXT;")

    # Check aptitude_attempts table
    cursor.execute("PRAGMA table_info(aptitude_attempts);")
    aat_cols = [row["name"] for row in cursor.fetchall()]
    if "ai_feedback" not in aat_cols:
        cursor.execute("ALTER TABLE aptitude_attempts ADD COLUMN ai_feedback TEXT;")

    # Ensure user_served_questions table exists for session-aware variation
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_served_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        module TEXT NOT NULL,
        question_id INTEGER NOT NULL,
        fingerprint TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    cursor.execute("PRAGMA table_info(user_served_questions);")
    usq_cols = [row["name"] for row in cursor.fetchall()]
    if "fingerprint" not in usq_cols:
        cursor.execute("ALTER TABLE user_served_questions ADD COLUMN fingerprint TEXT;")
    if "status" not in usq_cols:
        cursor.execute("ALTER TABLE user_served_questions ADD COLUMN status TEXT DEFAULT 'in_progress';")
    if "session_id" not in usq_cols:
        cursor.execute("ALTER TABLE user_served_questions ADD COLUMN session_id TEXT;")
    if "question_order" not in usq_cols:
        cursor.execute("ALTER TABLE user_served_questions ADD COLUMN question_order INTEGER DEFAULT 1;")

    # Check coding_attempts table
    cursor.execute("PRAGMA table_info(coding_attempts);")
    ca_cols = [row["name"] for row in cursor.fetchall()]
    if "session_id" not in ca_cols:
        cursor.execute("ALTER TABLE coding_attempts ADD COLUMN session_id TEXT;")
    if "attempt_id" not in ca_cols:
        cursor.execute("ALTER TABLE coding_attempts ADD COLUMN attempt_id TEXT;")

    # Ensure coding_sessions table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coding_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id TEXT UNIQUE NOT NULL,
        language TEXT NOT NULL DEFAULT 'python',
        domain TEXT NOT NULL DEFAULT 'Algorithms',
        difficulty TEXT NOT NULL DEFAULT 'Intermediate',
        question_ids TEXT NOT NULL,
        question_order TEXT NOT NULL,
        current_index INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'in_progress',
        attempt_id TEXT,
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    cursor.execute("PRAGMA table_info(coding_sessions);")
    cs_cols = [row["name"] for row in cursor.fetchall()]
    if "attempt_id" not in cs_cols:
        cursor.execute("ALTER TABLE coding_sessions ADD COLUMN attempt_id TEXT;")

    # Ensure assessment_attempts table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'in_progress',
        aptitude_attempt_id INTEGER,
        coding_session_id TEXT,
        interview_id INTEGER,
        aptitude_status TEXT NOT NULL DEFAULT 'not_started',
        coding_status TEXT NOT NULL DEFAULT 'not_started',
        interview_status TEXT NOT NULL DEFAULT 'not_started',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """)

    # Check aptitude_attempts for attempt_id
    cursor.execute("PRAGMA table_info(aptitude_attempts);")
    aat_cols2 = [row["name"] for row in cursor.fetchall()]
    if "attempt_id" not in aat_cols2:
        cursor.execute("ALTER TABLE aptitude_attempts ADD COLUMN attempt_id TEXT;")

    # Check interviews for attempt_id
    cursor.execute("PRAGMA table_info(interviews);")
    iv_cols = [row["name"] for row in cursor.fetchall()]
    if "attempt_id" not in iv_cols:
        cursor.execute("ALTER TABLE interviews ADD COLUMN attempt_id TEXT;")

    # Check user_served_questions for attempt_id
    cursor.execute("PRAGMA table_info(user_served_questions);")
    usq_cols2 = [row["name"] for row in cursor.fetchall()]
    if "attempt_id" not in usq_cols2:
        cursor.execute("ALTER TABLE user_served_questions ADD COLUMN attempt_id TEXT;")

    # Check assessment_attempts columns
    cursor.execute("PRAGMA table_info(assessment_attempts);")
    aa_cols = [row["name"] for row in cursor.fetchall()]
    aa_new_cols = [
        ("attempt_number", "INTEGER DEFAULT 1"),
        ("current_stage", "TEXT DEFAULT 'aptitude'"),
        ("completion_reason", "TEXT"),
        ("total_time_taken_seconds", "INTEGER DEFAULT 0"),
        ("aptitude_started_at", "TIMESTAMP"),
        ("aptitude_deadline", "TIMESTAMP"),
        ("aptitude_completed_at", "TIMESTAMP"),
        ("aptitude_duration_seconds", "INTEGER DEFAULT 900"),
        ("aptitude_time_taken_seconds", "INTEGER DEFAULT 0"),
        ("aptitude_timeout", "INTEGER DEFAULT 0"),
        ("aptitude_question_ids", "TEXT"),
        ("aptitude_answers_draft", "TEXT"),
        ("coding_started_at", "TIMESTAMP"),
        ("coding_deadline", "TIMESTAMP"),
        ("coding_duration_seconds", "INTEGER DEFAULT 1800"),
        ("coding_time_taken_seconds", "INTEGER DEFAULT 0"),
        ("coding_timeout", "INTEGER DEFAULT 0"),
        ("interview_started_at", "TIMESTAMP"),
        ("interview_deadline", "TIMESTAMP"),
        ("interview_duration_seconds", "INTEGER DEFAULT 1200"),
        ("interview_time_taken_seconds", "INTEGER DEFAULT 0"),
        ("interview_timeout", "INTEGER DEFAULT 0")
    ]
    for col_name, col_type in aa_new_cols:
        if col_name not in aa_cols:
            cursor.execute(f"ALTER TABLE assessment_attempts ADD COLUMN {col_name} {col_type};")

    # Check coding_sessions columns
    cursor.execute("PRAGMA table_info(coding_sessions);")
    cs_cols2 = [row["name"] for row in cursor.fetchall()]
    cs_new_cols = [
        ("started_at", "TIMESTAMP"),
        ("deadline", "TIMESTAMP"),
        ("duration_seconds", "INTEGER DEFAULT 1800"),
        ("time_taken_seconds", "INTEGER DEFAULT 0"),
        ("is_timeout", "INTEGER DEFAULT 0"),
        ("completion_reason", "TEXT"),
        ("question_times", "TEXT")
    ]
    for col_name, col_type in cs_new_cols:
        if col_name not in cs_cols2:
            cursor.execute(f"ALTER TABLE coding_sessions ADD COLUMN {col_name} {col_type};")

    # Check coding_attempts columns
    cursor.execute("PRAGMA table_info(coding_attempts);")
    ca_cols2 = [row["name"] for row in cursor.fetchall()]
    ca_new_cols = [
        ("time_spent_seconds", "INTEGER DEFAULT 0"),
        ("submission_attempt_number", "INTEGER DEFAULT 1"),
        ("error_details", "TEXT"),
        ("execution_time_ms", "REAL DEFAULT 0")
    ]
    for col_name, col_type in ca_new_cols:
        if col_name not in ca_cols2:
            cursor.execute(f"ALTER TABLE coding_attempts ADD COLUMN {col_name} {col_type};")

    # Check interviews columns
    cursor.execute("PRAGMA table_info(interviews);")
    iv_cols2 = [row["name"] for row in cursor.fetchall()]
    iv_new_cols = [
        ("deadline", "TIMESTAMP"),
        ("duration_seconds", "INTEGER DEFAULT 1200"),
        ("time_taken_seconds", "INTEGER DEFAULT 0"),
        ("is_timeout", "INTEGER DEFAULT 0"),
        ("completion_reason", "TEXT")
    ]
    for col_name, col_type in iv_new_cols:
        if col_name not in iv_cols2:
            cursor.execute(f"ALTER TABLE interviews ADD COLUMN {col_name} {col_type};")

    # Check answers columns
    cursor.execute("PRAGMA table_info(answers);")
    ans_cols = [row["name"] for row in cursor.fetchall()]
    if "time_spent_seconds" not in ans_cols:
        cursor.execute("ALTER TABLE answers ADD COLUMN time_spent_seconds INTEGER DEFAULT 0;")
    if "submitted_at" not in ans_cols:
        cursor.execute("ALTER TABLE answers ADD COLUMN submitted_at TIMESTAMP;")

    # Check aptitude_attempts columns
    cursor.execute("PRAGMA table_info(aptitude_attempts);")
    aat_cols3 = [row["name"] for row in cursor.fetchall()]
    if "is_timeout" not in aat_cols3:
        cursor.execute("ALTER TABLE aptitude_attempts ADD COLUMN is_timeout INTEGER DEFAULT 0;")
    if "completion_reason" not in aat_cols3:
        cursor.execute("ALTER TABLE aptitude_attempts ADD COLUMN completion_reason TEXT DEFAULT 'completed_normally';")
    if "started_at" not in aat_cols3:
        cursor.execute("ALTER TABLE aptitude_attempts ADD COLUMN started_at TIMESTAMP;")
    if "completed_at" not in aat_cols3:
        cursor.execute("ALTER TABLE aptitude_attempts ADD COLUMN completed_at TIMESTAMP;")


    # Check combined_assessments columns
    cursor.execute("PRAGMA table_info(combined_assessments);")
    cmb_cols = [row["name"] for row in cursor.fetchall()]
    if "attempt_id" not in cmb_cols:
        cursor.execute("ALTER TABLE combined_assessments ADD COLUMN attempt_id TEXT;")
    if "total_time_taken_seconds" not in cmb_cols:
        cursor.execute("ALTER TABLE combined_assessments ADD COLUMN total_time_taken_seconds INTEGER DEFAULT 0;")
    if "time_efficiency_metrics" not in cmb_cols:
        cursor.execute("ALTER TABLE combined_assessments ADD COLUMN time_efficiency_metrics TEXT;")
    if "recommendations" not in cmb_cols:
        cursor.execute("ALTER TABLE combined_assessments ADD COLUMN recommendations TEXT;")

    # Performance and query speed indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessment_attempts_user ON assessment_attempts(user_id, status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessment_attempts_att ON assessment_attempts(attempt_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coding_sessions_att ON coding_sessions(attempt_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_coding_attempts_att ON coding_attempts(attempt_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_interviews_att ON interviews(attempt_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_served_questions_user_mod ON user_served_questions(user_id, module, question_id);")

    # Backfill fingerprints for any coding problems missing them
    cursor.execute("SELECT id, title, description, starter_code, test_cases FROM coding_problems WHERE fingerprint IS NULL OR fingerprint = ''")
    from .services.problem_fingerprint import compute_problem_fingerprint
    for row in cursor.fetchall():
        fp = compute_problem_fingerprint(row["title"], row["description"], row["starter_code"], row["test_cases"])
        cursor.execute("UPDATE coding_problems SET fingerprint = ? WHERE id = ?", (fp, row["id"]))

    conn.commit()


def seed_initial_data(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Seed Admin and Candidate users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass = hash_password("admin123")
        candidate_pass = hash_password("candidate123")
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role) VALUES 
            ('Administrator', 'admin@pressure.ai', ?, 'admin'),
            ('Alex Candidate', 'candidate@pressure.ai', ?, 'candidate')
        """, (admin_pass, candidate_pass))

    # Seed Domains and Topics if empty
    cursor.execute("SELECT COUNT(*) FROM domains")
    if cursor.fetchone()[0] == 0:
        domain_data = [
            ("Python", "Programming", "High-level, interpreted programming language with dynamic semantics", [
                "Variables & Data Types", "Functions & Scope", "Lists & Tuples", 
                "Dictionaries & Sets", "OOP & Inheritance", "Recursion", 
                "Exception Handling", "Generators & Iterators", "Memory Management"
            ]),
            ("Java", "Programming", "Class-based, object-oriented programming language designed for portability", [
                "Classes & Objects", "Inheritance & Polymorphism", "Exception Handling", 
                "Collections Framework", "Multithreading", "Interfaces & Abstract Classes", 
                "Memory Management & Garbage Collection"
            ]),
            ("C", "Programming", "Procedural computer programming language supporting structured programming", [
                "Pointers & Memory Addresses", "Dynamic Memory Allocation", "Structs & Unions", 
                "File I/O", "Preprocessor Directives", "Arrays & Strings"
            ]),
            ("C++", "Programming", "General-purpose programming language created as an extension of the C language", [
                "Classes & Encapsulation", "Pointers & References", "STL Containers", 
                "Templates & Generic Programming", "Smart Pointers & RAII", "Polymorphism & Virtual Functions"
            ]),
            ("JavaScript", "Programming", "High-level, just-in-time compiled language conforming to ECMAScript", [
                "Closures & Lexical Scope", "Promises & Async/Await", "Event Loop & Concurrency", 
                "Prototypes & Inheritance", "DOM Manipulation", "Array Higher-Order Functions"
            ]),
            ("Data Structures", "Technical Subjects", "Fundamental formats for organizing, processing, and storing data", [
                "Arrays & Strings", "Linked Lists", "Stacks & Queues", 
                "Trees & Binary Search Trees", "Heaps & Priority Queues", "Hash Tables", "Graphs"
            ]),
            ("Algorithms", "Technical Subjects", "Step-by-step procedures for calculation, data processing, and reasoning", [
                "Sorting & Searching", "Dynamic Programming", "Greedy Algorithms", 
                "Graph Traversal (BFS & DFS)", "Divide and Conquer", "Backtracking", "Recursion Analysis"
            ]),
            ("DBMS", "Technical Subjects", "Software system for storing, managing, and retrieving database data", [
                "Relational Model & Keys", "ACID Properties", "Database Normalization (1NF-BCNF)", 
                "Indexing & B-Trees", "Transactions & Concurrency Control", "Joins & Query Optimization"
            ]),
            ("Operating Systems", "Technical Subjects", "System software that manages computer hardware and software resources", [
                "Processes & Threads", "CPU Scheduling", "Deadlocks & Prevention", 
                "Virtual Memory & Paging", "Process Synchronization & Mutexes", "File Systems"
            ]),
            ("Computer Networks", "Technical Subjects", "Communication network connecting nodes for resource and information sharing", [
                "OSI & TCP/IP Models", "TCP vs UDP Protocols", "HTTP, HTTPS & Web Sockets", 
                "DNS & IP Routing", "Congestion & Flow Control", "Network Security & Handshakes"
            ]),
            ("OOP", "Technical Subjects", "Object-Oriented Programming paradigm and architectural design principles", [
                "Encapsulation & Data Hiding", "Abstraction & Interfaces", "Inheritance & Code Reuse", 
                "Polymorphism & Method Overriding", "SOLID Principles", "Design Patterns"
            ]),
            ("SQL", "Technical Subjects", "Standard language for storing, manipulating and retrieving structured data", [
                "SELECT & Filtering Clauses", "Aggregations & GROUP BY", "Complex INNER & OUTER JOINs", 
                "Subqueries & CTEs", "Window Functions", "Schema Constraints & Indexes"
            ]),
            ("HTML/CSS", "Technical Subjects", "Standard markup and stylesheet languages for building web documents", [
                "Semantic HTML5 Elements", "CSS Flexbox Layout", "CSS Grid Architecture", 
                "Responsive Design & Media Queries", "Box Model & Positioning", "Web Accessibility (a11y)"
            ]),
        ]

        for domain_name, cat, desc, topics in domain_data:
            cursor.execute(
                "INSERT INTO domains (name, category, description) VALUES (?, ?, ?)",
                (domain_name, cat, desc)
            )
            domain_id = cursor.lastrowid
            for t_name in topics:
                cursor.execute(
                    "INSERT INTO topics (domain_id, name, description) VALUES (?, ?, ?)",
                    (domain_id, t_name, f"Core principles and applications of {t_name}")
                )

    # Seed Aptitude Questions if not already present
    import json
    from .services.aptitude_bank import APTITUDE_QUESTIONS
    for q in APTITUDE_QUESTIONS:
        cursor.execute("SELECT id FROM aptitude_questions WHERE question = ?", (q["question"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO aptitude_questions (category, difficulty, question, options, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                q["category"], q["difficulty"], q["question"],
                json.dumps(q["options"]), q["correct_answer"], q["explanation"]
            ))

    # Seed / Sync Coding Problems
    import json
    from .services.coding_bank import CODING_PROBLEMS
    from .services.problem_fingerprint import compute_problem_fingerprint
    for p in CODING_PROBLEMS:
        cursor.execute("SELECT id, solution_code, fingerprint FROM coding_problems WHERE title = ? OR id = ?", (p["title"], p["id"]))
        existing = cursor.fetchone()
        fp = compute_problem_fingerprint(p["title"], p["description"], p["starter_code"], p["test_cases"])
        sol_code = p.get("solution_code", "")
        if existing:
            if existing["solution_code"] != sol_code or existing["fingerprint"] != fp:
                cursor.execute("""
                    UPDATE coding_problems
                    SET solution_code = ?, fingerprint = COALESCE(fingerprint, ?)
                    WHERE id = ?
                """, (sol_code, fp, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO coding_problems (
                    id, title, category, difficulty, language, description,
                    starter_code, test_cases, constraints, hints, time_complexity, space_complexity, fingerprint, solution_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"], p["title"], p["category"], p["difficulty"], p.get("language", "python"),
                p["description"], p["starter_code"], json.dumps(p["test_cases"]),
                p.get("constraints", ""), json.dumps(p.get("hints", [])),
                p.get("time_complexity", ""), p.get("space_complexity", ""), fp, sol_code
            ))

    # Seed Practice Questions if empty
    cursor.execute("SELECT COUNT(*) FROM practice_questions")
    if cursor.fetchone()[0] == 0:
        import json
        from .services.practice_bank import PRACTICE_QUESTIONS_BANK
        for topic, q_list in PRACTICE_QUESTIONS_BANK.items():
            for pq in q_list:
                cursor.execute("""
                    INSERT INTO practice_questions (topic, difficulty, question, options, correct_answer, explanation)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pq["topic"], pq["difficulty"], pq["question"],
                    json.dumps(pq.get("options", [])), pq["correct_answer"], pq["explanation"]
                ))

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
