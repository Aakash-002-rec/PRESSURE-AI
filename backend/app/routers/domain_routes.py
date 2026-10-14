from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..database import get_db_connection
from ..models import DomainResponse, TopicResponse, DomainWithTopicsResponse, TopicCreate
from ..auth import get_current_user, require_admin

router = APIRouter(tags=["Domains & Topics"])

@router.get("/domains", response_model=List[DomainWithTopicsResponse])
def get_domains():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM domains ORDER BY category ASC, name ASC")
    domains = cursor.fetchall()

    result = []
    for d in domains:
        cursor.execute("SELECT * FROM topics WHERE domain_id = ? ORDER BY name ASC", (d["id"],))
        topics = cursor.fetchall()
        result.append({
            "id": d["id"],
            "name": d["name"],
            "category": d["category"],
            "description": d["description"],
            "topics": [dict(t) for t in topics]
        })

    conn.close()
    return result

@router.get("/domains/{domain_id}/topics", response_model=List[TopicResponse])
def get_domain_topics(domain_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics WHERE domain_id = ? ORDER BY name ASC", (domain_id,))
    topics = cursor.fetchall()
    conn.close()
    return [dict(t) for t in topics]

@router.post("/topics", response_model=TopicResponse)
def create_topic(topic_data: TopicCreate, admin_user: dict = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO topics (domain_id, name, description)
            VALUES (?, ?, ?)
        """, (topic_data.domain_id, topic_data.name, topic_data.description))
        topic_id = cursor.lastrowid
        conn.commit()
        cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
        new_topic = dict(cursor.fetchone())
        conn.close()
        return new_topic
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
