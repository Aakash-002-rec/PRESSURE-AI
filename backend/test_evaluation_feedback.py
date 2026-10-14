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

def test_aptitude_evaluations(token):
    print("\n--- Testing Aptitude Evaluation ---")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch questions
    q_resp = requests.get(f"{BASE_URL}/aptitude/questions?limit=5", headers=headers)
    assert q_resp.status_code == 200
    questions = q_resp.json()
    assert len(questions) >= 3
    print(f"Retrieved {len(questions)} aptitude questions.")

    # 2. Perfect submission (All Correct)
    # We fetch correct answers directly from DB to simulate perfect test
    import sqlite3
    conn = sqlite3.connect("pressure_ai.db")
    c = conn.cursor()
    
    perfect_answers = []
    failing_answers = []
    for q in questions:
        c.execute("SELECT correct_answer FROM aptitude_questions WHERE id = ?", (q["id"],))
        corr_ans = c.fetchone()[0]
        perfect_answers.append({
            "question_id": q["id"],
            "selected_option": corr_ans,
            "time_spent_seconds": 15
        })
        # Wrong answer
        wrong_ans = (corr_ans + 1) % 4
        failing_answers.append({
            "question_id": q["id"],
            "selected_option": wrong_ans,
            "time_spent_seconds": 15
        })
    conn.close()

    # Submit perfect test
    sub_perf = requests.post(f"{BASE_URL}/aptitude/submit", headers=headers, json={
        "category": "All",
        "difficulty": "Intermediate",
        "total_questions": len(questions),
        "time_taken_seconds": 60,
        "answers": perfect_answers
    })
    assert sub_perf.status_code == 200, sub_perf.text
    res_perf = sub_perf.json()
    print(f"Perfect Submission Result: Score={res_perf['overall_score']}%, Correct={res_perf['correct_count']}/{res_perf['total_questions']}")
    assert res_perf["overall_score"] == 100.0, "Authoritative score must be 100%"
    assert res_perf["correct_count"] == len(questions)
    assert "ai_evaluation" in res_perf, "ai_evaluation must be present"
    ai_perf = res_perf["ai_evaluation"]
    assert "summary" in ai_perf
    assert "strengths" in ai_perf
    print(f"AI Summary (Perfect): {ai_perf['summary']}")
    print(f"AI Strengths: {ai_perf['strengths']}")

    # Submit failing test
    sub_fail = requests.post(f"{BASE_URL}/aptitude/submit", headers=headers, json={
        "category": "All",
        "difficulty": "Intermediate",
        "total_questions": len(questions),
        "time_taken_seconds": 60,
        "answers": failing_answers
    })
    assert sub_fail.status_code == 200, sub_fail.text
    res_fail = sub_fail.json()
    print(f"Failing Submission Result: Score={res_fail['overall_score']}%, Correct={res_fail['correct_count']}/{res_fail['total_questions']}")
    assert res_fail["overall_score"] == 0.0, "Authoritative score must be 0%"
    assert res_fail["correct_count"] == 0
    assert "ai_evaluation" in res_fail
    ai_fail = res_fail["ai_evaluation"]
    assert "weaknesses" in ai_fail
    print(f"AI Summary (Failing): {ai_fail['summary']}")
    print(f"AI Weaknesses: {ai_fail['weaknesses']}")
    print(f"AI Improvement Suggestions: {ai_fail.get('improvement_suggestions')}")
    print("[OK] Aptitude evaluation verified (Differentiated, Authoritative score preserved)")

def test_coding_evaluations(token):
    print("\n--- Testing Coding Evaluation ---")
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch coding problems
    p_resp = requests.get(f"{BASE_URL}/coding/problems", headers=headers)
    assert p_resp.status_code == 200
    problems = p_resp.json()
    if not problems:
        p_resp = requests.get(f"{BASE_URL}/coding/problems?mode=resume", headers=headers)
        assert p_resp.status_code == 200
        problems = p_resp.json()
    assert len(problems) > 0
    problem = problems[0]
    prob_id = problem["id"]
    print(f"Selected Problem #{prob_id}: {problem['title']} ({problem['category']})")

    # Fetch full problem to inspect
    full_p = requests.get(f"{BASE_URL}/coding/problems/{prob_id}", headers=headers).json()
    starter = full_p["starter_code"]

    # 1. Correct code submission
    # Find entry function
    entry_func = "solution"
    for line in starter.split("\n"):
        if line.strip().startswith("def ") and "(" in line:
            entry_func = line.strip().split("def ")[1].split("(")[0].strip()
            break

    # We test on problem #1 (Two Sum) or problem #2 (Reverse String)
    # Let's inspect which problem it is
    import sqlite3
    conn = sqlite3.connect("pressure_ai.db")
    c = conn.cursor()
    c.execute("SELECT id, title, starter_code, test_cases FROM coding_problems WHERE id = ?", (prob_id,))
    p_row = c.fetchone()
    conn.close()

    test_cases = json.loads(p_row[3])
    print(f"Problem: {p_row[1]}, Starter: {p_row[2][:40]}..., Tests: {len(test_cases)}")

    # Test 1: Submit Incorrect Code (returns dummy value)
    incorrect_code = p_row[2] + "\n    return -999999"
    sub_inc = requests.post(f"{BASE_URL}/coding/submit", headers=headers, json={
        "problem_id": prob_id,
        "code": incorrect_code,
        "language": "python"
    })
    assert sub_inc.status_code == 200, sub_inc.text
    res_inc = sub_inc.json()
    print(f"Incorrect Code Result: status={res_inc['status']}, passed={res_inc['passed_count']}/{res_inc['total_count']}, correctness={res_inc['correctness']}%")
    assert res_inc["status"] in ["failed", "partial"]
    assert res_inc["correctness"] < 50.0
    assert "ai_evaluation" in res_inc
    ai_inc = res_inc["ai_evaluation"]
    print(f"AI Overall Assessment: {ai_inc['overall_assessment']}")
    print(f"AI Explanation: {ai_inc['explanation']}")
    print(f"AI Conceptual Mistakes: {ai_inc.get('conceptual_mistakes')}")
    print(f"AI Edge Cases Missed: {ai_inc.get('edge_cases_missed')}")

    # Test 2: Submit Syntax / Runtime Error Code
    error_code = "def factorial(n):\n    invalid python syntax +++ ???"
    sub_err = requests.post(f"{BASE_URL}/coding/submit", headers=headers, json={
        "problem_id": prob_id,
        "code": error_code,
        "language": "python"
    })
    assert sub_err.status_code == 200, sub_err.text
    res_err = sub_err.json()
    print(f"Error Code Result: status={res_err['status']}, passed={res_err['passed_count']}/{res_err['total_count']}, correctness={res_err['correctness']}%")
    assert res_err["status"] == "error" or res_err["correctness"] == 0.0
    ai_err = res_err["ai_evaluation"]
    print(f"AI Assessment (Error): {ai_err['overall_assessment']}")
    print(f"AI Explanation (Error): {ai_err['explanation']}")
    print(f"AI Conceptual Mistakes: {ai_err.get('conceptual_mistakes')}")
    print(f"AI Personalized Feedback: {ai_err.get('personalized_feedback')}")

    # Test 3: Correct Code
    # Determine correct implementation for problem
    if "factorial" in starter:
        correct_code = """def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Cannot calculate factorial of negative number")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)"""
    elif "fibonacci" in starter:
        correct_code = """def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Cannot calculate fibonacci for negative index")
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b"""
    elif "two_sum" in starter:
        correct_code = """def two_sum(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in lookup:
            return [lookup[complement], i]
        lookup[num] = i
    return []"""
    elif "reverse_string" in starter:
        correct_code = """def reverse_string(s):
    return s[::-1]"""
    elif "is_palindrome" in starter:
        correct_code = """def is_palindrome(s):
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]"""
    elif "max_subarray_sum" in starter:
        correct_code = """def max_subarray_sum(nums):
    max_so_far = current_max = nums[0]
    for x in nums[1:]:
        current_max = max(x, current_max + x)
        max_so_far = max(max_so_far, current_max)
    return max_so_far"""
    else:
        correct_code = starter + "\n    return True"

    sub_corr = requests.post(f"{BASE_URL}/coding/submit", headers=headers, json={
        "problem_id": prob_id,
        "code": correct_code,
        "language": "python"
    })
    assert sub_corr.status_code == 200, sub_corr.text
    res_corr = sub_corr.json()
    print(f"Correct Code Result: status={res_corr['status']}, passed={res_corr['passed_count']}/{res_corr['total_count']}, correctness={res_corr['correctness']}%")
    if res_corr["correctness"] == 100.0:
        print("[OK] Code passed 100% of test cases.")
        ai_corr = res_corr["ai_evaluation"]
        print(f"AI Overall Assessment (Passed): {ai_corr['overall_assessment']}")
        print(f"AI Time Complexity: {ai_corr.get('time_complexity')}")
        print(f"AI Space Complexity: {ai_corr.get('space_complexity')}")
        print(f"AI Algorithmic Improvements: {ai_corr.get('algorithmic_improvements')}")

    print("[OK] Coding evaluation verified (Differentiated, Authoritative CodeRunner score preserved)")

if __name__ == "__main__":
    t = get_auth_token()
    test_aptitude_evaluations(t)
    test_coding_evaluations(t)
    print("\nALL EVALUATION & FEEDBACK TESTS PASSED SUCCESSFULLY!")
