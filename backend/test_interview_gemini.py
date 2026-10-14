import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "demo.candidate@pressureai.internal",
        "password": "Password123!"
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]

def test_interview_flow():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch domain
    dom_resp = requests.get(f"{BASE_URL}/domains", headers=headers)
    assert dom_resp.status_code == 200
    domains = dom_resp.json()
    py_domain = next(d for d in domains if d["name"] == "Python")
    domain_id = py_domain["id"]

    print("\n--- [TEST 1] AI Mock Interview Session 1: Creation & Question Generation ---")
    int_resp = requests.post(f"{BASE_URL}/interviews", headers=headers, json={
        "domain_id": domain_id,
        "difficulty": "Intermediate",
        "interview_type": "Mixed",
        "total_questions": 5
    })
    assert int_resp.status_code == 200, int_resp.text
    session1 = int_resp.json()
    s1_id = session1["id"]
    print(f"Session 1 Created: ID={s1_id}, Domain=Python, Starting Difficulty=Intermediate")

    # Fetch Q1
    q1_resp = requests.get(f"{BASE_URL}/interviews/{s1_id}/questions/next", headers=headers)
    assert q1_resp.status_code == 200, q1_resp.text
    q1 = q1_resp.json()
    q1_text = q1["question_text"]
    q1_source = q1.get("source", "unknown")
    print(f"Session 1 Q1: Topic='{q1['topic_name']}', Diff={q1['difficulty']}, Source='{q1_source}'")
    print(f"Q1 Text: {q1_text}")
    assert len(q1_text) > 15

    # 2. Submit Strong Answer on Q1 (Test CAT Escalation)
    print("\n--- [TEST 2] Gemini Answer Evaluation (4 Dimensions + Structured Diagnostic) ---")
    import sqlite3
    conn = sqlite3.connect("pressure_ai.db")
    c = conn.cursor()
    c.execute("SELECT expected_concepts FROM questions WHERE id = ?", (q1["id"],))
    raw_exp = c.fetchone()[0]
    exp_c = json.loads(raw_exp) if raw_exp else [q1["topic_name"]]
    conn.close()

    strong_ans = (
        f"In Python, {q1['topic_name']} directly utilizes {', '.join(exp_c)}. "
        "It adheres strictly to runtime execution invariants, memory bounds, and language standards with optimal efficiency."
    )
    a1_resp = requests.post(f"{BASE_URL}/questions/{q1['id']}/answer", headers=headers, json={
        "answer_text": strong_ans
    })
    assert a1_resp.status_code == 200, a1_resp.text
    a1 = a1_resp.json()
    print(f"Answer 1 Evaluated: Source='{a1.get('source')}', Overall Score={a1['overall_score']}/10")
    print(f"  - Correctness: {a1['correctness']}")
    print(f"  - Relevance: {a1['relevance']}")
    print(f"  - Conceptual Depth: {a1['conceptual_understanding']}")
    print(f"  - Completeness: {a1['completeness']}")
    print(f"  - Missing Concepts: {a1.get('missing_concepts')}")
    print(f"  - Feedback: {a1['feedback']}")
    print(f"  - CAT Decision: Next Difficulty={a1['next_difficulty']}, Reason={a1['difficulty_change_reason']}")
    assert a1["overall_score"] >= 6.0, "Strong answer should score decently"

    # 3. Request Hint on Q2
    print("\n--- [TEST 3] Progressive Contextual Hints ---")
    q2_resp = requests.get(f"{BASE_URL}/interviews/{s1_id}/questions/next", headers=headers)
    assert q2_resp.status_code == 200
    q2 = q2_resp.json()
    print(f"Session 1 Q2: Topic='{q2['topic_name']}', Diff={q2['difficulty']}")

    h1_resp = requests.post(f"{BASE_URL}/questions/{q2['id']}/hint", headers=headers)
    assert h1_resp.status_code == 200
    h1 = h1_resp.json()
    h1_clean = h1['hint_text'].encode('ascii', 'ignore').decode('ascii')
    print(f"Hint Level 1: {h1_clean} (Remaining: {h1['remaining_hints']})")
    assert h1["hint_level"] == 1
    assert "Level 1" in h1["hint_text"]

    h2_resp = requests.post(f"{BASE_URL}/questions/{q2['id']}/hint", headers=headers)
    assert h2_resp.status_code == 200
    h2 = h2_resp.json()
    h2_clean = h2['hint_text'].encode('ascii', 'ignore').decode('ascii')
    print(f"Hint Level 2: {h2_clean} (Remaining: {h2['remaining_hints']})")
    assert h2["hint_level"] == 2

    # 4. Submit weak answers on Q2 and Q3 to trigger PRESSURE MODE
    print("\n--- [TEST 4] Weakness Detection & Pressure Mode Activation ---")
    a2_resp = requests.post(f"{BASE_URL}/questions/{q2['id']}/answer", headers=headers, json={
        "answer_text": "I do not know, it's just something."
    })
    assert a2_resp.status_code == 200
    a2 = a2_resp.json()
    print(f"Q2 Score: {a2['overall_score']}/10, Weakness Detected={a2['weakness_detected']} ({a2['weakness_level']})")

    q3_resp = requests.get(f"{BASE_URL}/interviews/{s1_id}/questions/next", headers=headers)
    assert q3_resp.status_code == 200
    q3 = q3_resp.json()
    print(f"Session 1 Q3: Topic='{q3['topic_name']}', Diff={q3['difficulty']}")

    a3_resp = requests.post(f"{BASE_URL}/questions/{q3['id']}/answer", headers=headers, json={
        "answer_text": "I have no idea about how this mechanism works."
    })
    assert a3_resp.status_code == 200
    a3 = a3_resp.json()
    print(f"Q3 Score: {a3['overall_score']}/10, Pressure Mode Activated={a3['pressure_mode_activated']}")
    reason_clean = str(a3['difficulty_change_reason']).encode('ascii', 'ignore').decode('ascii')
    print(f"Transition Reason: {reason_clean}")

    # Check Q4 is under Pressure Mode
    q4_resp = requests.get(f"{BASE_URL}/interviews/{s1_id}/questions/next", headers=headers)
    assert q4_resp.status_code == 200
    q4 = q4_resp.json()
    print(f"Session 1 Q4: Is Pressure Mode={q4['is_pressure_mode']}")
    print(f"Q4 Text: {q4['question_text']}")
    assert q4["is_pressure_mode"] == True, "Expected Question 4 to be under Pressure Mode"

    # 5. Session-to-Session Variation Test
    print("\n--- [TEST 5] Session-to-Session Question Variation ---")
    # Start Session 2
    int2_resp = requests.post(f"{BASE_URL}/interviews", headers=headers, json={
        "domain_id": domain_id,
        "difficulty": "Intermediate",
        "interview_type": "Mixed",
        "total_questions": 5
    })
    assert int2_resp.status_code == 200
    s2_id = int2_resp.json()["id"]

    q_s2_resp = requests.get(f"{BASE_URL}/interviews/{s2_id}/questions/next", headers=headers)
    assert q_s2_resp.status_code == 200
    q_s2 = q_s2_resp.json()
    print(f"Session 2 Q1: Topic='{q_s2['topic_name']}', Source='{q_s2.get('source')}'")
    print(f"Session 2 Q1 Text: {q_s2['question_text']}")

    # Start Session 3
    int3_resp = requests.post(f"{BASE_URL}/interviews", headers=headers, json={
        "domain_id": domain_id,
        "difficulty": "Intermediate",
        "interview_type": "Mixed",
        "total_questions": 5
    })
    assert int3_resp.status_code == 200
    s3_id = int3_resp.json()["id"]

    q_s3_resp = requests.get(f"{BASE_URL}/interviews/{s3_id}/questions/next", headers=headers)
    assert q_s3_resp.status_code == 200
    q_s3 = q_s3_resp.json()
    print(f"Session 3 Q1: Topic='{q_s3['topic_name']}', Source='{q_s3.get('source')}'")
    print(f"Session 3 Q1 Text: {q_s3['question_text']}")

    # Verify questions vary across sessions
    print("\n--- Verification Summary ---")
    print(f"Session 1 Question: {q1_text}")
    print(f"Session 2 Question: {q_s2['question_text']}")
    print(f"Session 3 Question: {q_s3['question_text']}")

    assert q1_text != q_s2["question_text"], "Session 1 and Session 2 must not have identical Question 1"
    assert q_s2["question_text"] != q_s3["question_text"], "Session 2 and Session 3 must not have identical Question 1"
    print("[OK] Session-to-session question variation confirmed!")

if __name__ == "__main__":
    test_interview_flow()
    print("\nALL AI MOCK INTERVIEW GEMINI FLOW TESTS PASSED SUCCESSFULLY!")
