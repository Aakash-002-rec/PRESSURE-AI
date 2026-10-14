import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import (
    auth_routes, domain_routes, interview_routes, progress_routes,
    admin_routes, aptitude_routes, coding_routes, assessment_routes
)

# Initialize DB tables and seed data if not yet created
init_db()

app = FastAPI(
    title="PRESSURE-AI API",
    description="Adaptive AI-Powered Placement Preparation, Technical Interview & Personalized Learning Platform",
    version="2.0.0"
)

# Configure CORS for frontend access
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(auth_routes.router)
app.include_router(domain_routes.router)
app.include_router(interview_routes.router)
app.include_router(progress_routes.router)
app.include_router(admin_routes.router)
app.include_router(aptitude_routes.router)
app.include_router(coding_routes.router)
app.include_router(assessment_routes.router)

@app.get("/")
def root():
    return {
        "platform": "PRESSURE-AI",
        "tagline": "Adaptive AI-Powered Interview & Personalized Learning Platform",
        "status": "operational",
        "version": "1.0.0",
        "core_innovations": [
            "Adaptive Difficulty Engine",
            "Rule-Based Weakness Detection",
            "3-Level Progressive Hint System",
            "Pressure Mode Deep Probing",
            "Topic-Wise Performance Analytics",
            "Personalized Learning Roadmap & Recommendations",
            "Longitudinal Progress Tracking"
        ]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
