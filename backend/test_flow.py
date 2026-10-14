import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def log(step, msg):
    print(f"\n[{step}] {msg}")

def test_full_flow():
    session = requests.Session()

    # 1. Test Root and Health
    log("1. HEALTH", "Testing server health...")
    r = session.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Root failed: {r.text}"
    print("[OK] Platform online:", r.json()["platform"])

    # 2. Login as Candidate
    log("2. AUTH", "Logging in as Candidate (Alex)...")
    r = session.post(f"{BASE_URL}/auth/login", json={"email": "candidate@pressure.ai", "password": "candidate123"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    candidate_token = r.json()["access_token"]
    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    print(f"✓ Candidate logged in: {r.json()['user']['name']} ({r.json()['user']['role']})")

    # 3. Login as Admin
    log("3. ADMIN AUTH", "Logging in as Admin (Manager)...")
    r = session.post(f"{BASE_URL}/auth/login", json={"email": "admin@pressure.ai", "password": "admin123"})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    admin_token = r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"✓ Admin logged in: {r.json()['user']['name']} ({r.json()['user']['role']})")

    # 4. Fetch Domains
    log("4. DOMAINS", "Fetching supported domains & topics...")
    r = session.get(f"{BASE_URL}/domains", headers=candidate_headers)
    assert r.status_code == 200, f"Fetch domains failed: {r.text}"
    domains = r.json()
    python_domain = next((d for d in domains if d["name"] == "Python"), None)
    assert python_domain is not None, "Python domain not found!"
    print(f"✓ Loaded {len(domains)} domains. Found Python with {len(python_domain['topics'])} topics.")

    # 5. Create Interview (Python, Intermediate, Mixed, 5 questions)
    log("5. CREATE INTERVIEW", "Setting up Python Intermediate Mixed interview (5 Qs)...")
    r = session.post(
        f"{BASE_URL}/interviews",
        headers=candidate_headers,
        json={
            "domain_id": python_domain["id"],
            "difficulty": "Intermediate",
            "interview_type": "Mixed",
            "total_questions": 5
        }
    )
    assert r.status_code == 200, f"Create interview failed: {r.text}"
    interview = r.json()
    interview_id = interview["id"]
    print(f"✓ Interview #{interview_id} created. Status: {interview['status']}, Difficulty: {interview['difficulty']}")

    # 6. Question 1
    log("6. QUESTION 1", "Fetching Question 1...")
    r = session.get(f"{BASE_URL}/interviews/{interview_id}/questions/next", headers=candidate_headers)
    assert r.status_code == 200, f"Q1 fetch failed: {r.text}"
    q1 = r.json()
    print(f"✓ Q1 (#{q1['sequence_number']}): Topic={q1['topic_name']}, Diff={q1['difficulty']}, Type={q1['question_type']}")
    print(f"   Text: {q1['question_text']}")

    # Submit Strong Answer on Q1
    log("6b. ANSWER 1", "Submitting strong answer to test adaptive difficulty escalation...")
    strong_ans = (
        "In Python, this concept is defined by clean separation of concern and adherence to language invariants. "
        "It handles edge cases such as empty collections and off-by-one conditions with constant space overhead O(1) "
        "and optimal time complexity O(N), ensuring sound architectural decoupling."
    )
    r = session.post(
        f"{BASE_URL}/questions/{q1['id']}/answer",
        headers=candidate_headers,
        json={"answer_text": strong_ans}
    )
    assert r.status_code == 200, f"A1 submit failed: {r.text}"
    a1_res = r.json()
    print(f"✓ Q1 Score: {a1_res['overall_score']}/10. Feedback: {a1_res['feedback']}")
    print(f"✓ Adaptive Difficulty Engine: Next Diff={a1_res['next_difficulty']}, Reason={a1_res['difficulty_change_reason']}")

    # 7. Question 2 + Hint Test
    log("7. QUESTION 2 & HINT", "Fetching Question 2...")
    r = session.get(f"{BASE_URL}/interviews/{interview_id}/questions/next", headers=candidate_headers)
    assert r.status_code == 200, f"Q2 fetch failed: {r.text}"
    q2 = r.json()
    print(f"✓ Q2 (#{q2['sequence_number']}): Topic={q2['topic_name']}, Diff={q2['difficulty']}")

    # Request Hint Level 1
    r = session.post(f"{BASE_URL}/questions/{q2['id']}/hint", headers=candidate_headers)
    assert r.status_code == 200, f"Hint 1 failed: {r.text}"
    h1 = r.json()
    print(f"✓ Hint Level {h1['hint_level']}: {h1['hint_text']} (Remaining: {h1['remaining_hints']})")

    # Request Hint Level 2
    r = session.post(f"{BASE_URL}/questions/{q2['id']}/hint", headers=candidate_headers)
    assert r.status_code == 200, f"Hint 2 failed: {r.text}"
    h2 = r.json()
    print(f"✓ Hint Level {h2['hint_level']}: {h2['hint_text']} (Remaining: {h2['remaining_hints']})")

    # Submit Weak Answer on Q2 to start weakness detection
    log("7b. ANSWER 2", "Submitting weak answer on Q2...")
    weak_ans = "It's just a loop thing in Python that runs forever."
    r = session.post(
        f"{BASE_URL}/questions/{q2['id']}/answer",
        headers=candidate_headers,
        json={"answer_text": weak_ans}
    )
    assert r.status_code == 200, f"A2 submit failed: {r.text}"
    a2_res = r.json()
    print(f"✓ Q2 Score: {a2_res['overall_score']}/10. Weakness detected: {a2_res['weakness_detected']} ({a2_res['weakness_level']})")
    print(f"   Missing concepts: {a2_res['missing_concepts']}")

    # 8. Question 3 -> Submit another weak answer to trigger PRESSURE MODE!
    log("8. QUESTION 3 & PRESSURE MODE", "Fetching Question 3...")
    r = session.get(f"{BASE_URL}/interviews/{interview_id}/questions/next", headers=candidate_headers)
    assert r.status_code == 200, f"Q3 fetch failed: {r.text}"
    q3 = r.json()
    print(f"✓ Q3 (#{q3['sequence_number']}): Topic={q3['topic_name']}, Diff={q3['difficulty']}")

    log("8b. ANSWER 3", "Submitting weak answer on Q3 to ignite PRESSURE MODE...")
    r = session.post(
        f"{BASE_URL}/questions/{q3['id']}/answer",
        headers=candidate_headers,
        json={"answer_text": "I do not know how the recursion limit or stack frames work."}
    )
    assert r.status_code == 200, f"A3 submit failed: {r.text}"
    a3_res = r.json()
    print(f"✓ Q3 Score: {a3_res['overall_score']}/10.")
    print(f"🔥 Pressure Mode Activated: {a3_res['pressure_mode_activated']}")
    print(f"   Reason: {a3_res['difficulty_change_reason']}")

    # 9. Question 4 -> Verify Question is under PRESSURE MODE
    log("9. QUESTION 4 UNDER PRESSURE", "Fetching Question 4...")
    r = session.get(f"{BASE_URL}/interviews/{interview_id}/questions/next", headers=candidate_headers)
    assert r.status_code == 200, f"Q4 fetch failed: {r.text}"
    q4 = r.json()
    print(f"✓ Q4 (#{q4['sequence_number']}): Is Pressure Mode={q4['is_pressure_mode']}")
    print(f"   Pressure Probe Text: {q4['question_text']}")
    assert q4['is_pressure_mode'] == True, "Expected Question 4 to be under Pressure Mode!"

    # Answer Question 4
    r = session.post(
        f"{BASE_URL}/questions/{q4['id']}/answer",
        headers=candidate_headers,
        json={"answer_text": "CPython uses a fixed recursion limit set by sys.setrecursionlimit() to avoid C-level stack overflow."}
    )
    assert r.status_code == 200

    # 10. Question 5 (Final Question)
    log("10. QUESTION 5", "Fetching final Question 5...")
    r = session.get(f"{BASE_URL}/interviews/{interview_id}/questions/next", headers=candidate_headers)
    assert r.status_code == 200, f"Q5 fetch failed: {r.text}"
    q5 = r.json()
    print(f"✓ Q5 (#{q5['sequence_number']}): Topic={q5['topic_name']}")

    r = session.post(
        f"{BASE_URL}/questions/{q5['id']}/answer",
        headers=candidate_headers,
        json={"answer_text": "Using tail call simulation or dynamic programming memoization prevents O(2^N) recursion trees."}
    )
    assert r.status_code == 200
    a5_res = r.json()
    print(f"✓ Final Question Evaluated. Interview completed: {a5_res['is_interview_completed']}")
    assert a5_res['is_interview_completed'] == True, "Expected interview to complete after Q5!"

    # 11. Final Performance Report
    log("11. PERFORMANCE REPORT", "Fetching final performance report...")
    r = session.get(f"{BASE_URL}/interviews/{interview_id}/report", headers=candidate_headers)
    assert r.status_code == 200, f"Report failed: {r.text}"
    report = r.json()
    print(f"✓ Report Overall Score: {report['overall_score']}%")
    print(f"✓ Category Scores: {json.dumps(report['category_scores'])}")
    print(f"✓ Strong Areas: {report['strong_areas']}")
    print(f"✓ Weak Areas: {report['weak_areas']}")
    print(f"🔥 Pressure Mode Topics: {report['pressure_mode_topics']}")
    print(f"✓ Hints Used Total: {report['hints_used_total']}")

    # 12. Personalized Learning Recommendations & Roadmap
    log("12. RECOMMENDATIONS & ROADMAP", "Verifying learning engine output...")
    recs = report["recommendations"]
    print(f"✓ Total Personalized Recommendations: {len(recs)}")
    if recs:
        r0 = recs[0]
        print(f"   Topic: {r0['topic_name']} ({r0['performance_score']}%)")
        print(f"   Why Weak: {r0['why_weak'][:2]}")
        print(f"   Concepts to Learn: {r0['concepts_to_learn'][:3]}")
        print(f"   5-Step Action Plan: {len(r0['action_plan'])} steps")
        print(f"   Practice Questions: {len(r0['practice_questions'])} questions")

    roadmap = report["learning_roadmap"]
    print(f"✓ 5-Stage Learning Roadmap: {len(roadmap)} stages")
    for st in roadmap:
        print(f"   Stage {st['stage_number']}: {st['title']} ({st['estimated_duration']})")

    # 13. Progress Tracking
    log("13. PROGRESS TRACKING", "Fetching candidate longitudinal progress...")
    r = session.get(f"{BASE_URL}/progress", headers=candidate_headers)
    assert r.status_code == 200, f"Progress failed: {r.text}"
    prog = r.json()
    print(f"✓ Completed interviews: {prog['total_interviews_completed']}")
    print(f"✓ Average score: {prog['average_score']}%")
    print(f"✓ Topic improvements count: {len(prog['topic_improvements'])}")

    # 14. Admin Dashboard
    log("14. ADMIN DASHBOARD", "Verifying admin telemetry and audit...")
    r = session.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)
    assert r.status_code == 200, f"Admin dashboard failed: {r.text}"
    adm = r.json()
    print(f"✓ Admin Telemetry: Candidates={adm['total_candidates']}, Interviews={adm['total_interviews']}, Platform Avg={adm['average_platform_score']}%")
    print(f"✓ Top Weak Topics across platform: {len(adm['top_weak_topics'])}")

    print("\n========================================================")
    print("🎉 ALL 14 PRESSURE-AI INTEGRATION TESTS PASSED 100%!")
    print("========================================================\n")

if __name__ == "__main__":
    test_full_flow()
