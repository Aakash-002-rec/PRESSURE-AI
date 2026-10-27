import os
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Configurable assessment time limits in seconds
# Aptitude Test: 15 minutes default for 10 questions
APTITUDE_TIME_LIMIT_SECONDS = int(os.getenv("APTITUDE_TIME_LIMIT_SECONDS", "900"))

# Coding Assessment: 30 minutes default for 3 algorithmic problems
CODING_TIME_LIMIT_SECONDS = int(os.getenv("CODING_TIME_LIMIT_SECONDS", "1800"))

# AI Mock Interview: 20 minutes default overall duration
INTERVIEW_TIME_LIMIT_SECONDS = int(os.getenv("INTERVIEW_TIME_LIMIT_SECONDS", "1200"))

# Per-question time limit in AI Mock Interview (seconds)
INTERVIEW_QUESTION_TIME_LIMIT_SECONDS = int(os.getenv("INTERVIEW_QUESTION_TIME_LIMIT_SECONDS", "180"))

# Number of coding questions strictly assigned per attempt
CODING_QUESTIONS_PER_ATTEMPT = 3

# Grace period in seconds for network latency during submission
DEADLINE_GRACE_PERIOD_SECONDS = 15
