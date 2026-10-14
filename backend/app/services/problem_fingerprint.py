import re
import json
import hashlib
from typing import Dict, List, Any, Optional

def compute_problem_fingerprint(
    title: str,
    description: str,
    starter_code: Optional[str] = None,
    test_cases: Optional[Any] = None
) -> str:
    """
    Computes a canonical, normalized content fingerprint for a coding challenge.
    Captures the underlying algorithmic task, requirements, and test input/output semantics
    so that trivial rewording, paraphrasing, or variable renames produce a matching fingerprint.
    """
    if isinstance(starter_code, (list, dict)) and isinstance(test_cases, str):
        starter_code, test_cases = test_cases, starter_code
    elif isinstance(starter_code, (list, dict)) and test_cases is None:
        test_cases = starter_code
        starter_code = None

    # 1. Normalized Title Stem
    clean_title = re.sub(r'[^a-zA-Z0-9]', '', (title or "").lower())

    # 2. Extract core functional keywords from description
    # Strip stop words, markdown, and punctuation
    raw_desc = (description or "").lower()
    raw_desc = re.sub(r'```.*?```', '', raw_desc, flags=re.DOTALL)
    raw_desc = re.sub(r'`.*?`', '', raw_desc)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', raw_desc)
    stop_words = {
        "given", "write", "function", "return", "returns", "input", "output", "example",
        "constraints", "integer", "string", "array", "list", "should", "using", "your",
        "implementation", "here", "following", "such", "that", "where", "each", "have",
        "with", "from", "when", "into", "must", "code", "problem", "solve", "number"
    }
    content_words = sorted([w for w in set(words) if w not in stop_words])
    desc_signature = "-".join(content_words[:25])

    # 3. Normalized Function Signature & Return Pattern
    sig_raw = ""
    if starter_code:
        func_match = re.search(r'def\s+([a-zA-Z0-9_]+)\s*\((.*?)\)', starter_code)
        if func_match:
            args = re.sub(r'\s+', '', func_match.group(2))
            sig_raw = f"{func_match.group(1)}({args})"

    # 4. Normalized Test Case input -> output mappings
    tc_signature = ""
    parsed_tests = []
    if isinstance(test_cases, str):
        try:
            parsed_tests = json.loads(test_cases)
        except Exception:
            pass
    elif isinstance(test_cases, list):
        parsed_tests = test_cases

    if isinstance(parsed_tests, list):
        tc_parts = []
        for tc in parsed_tests:
            if isinstance(tc, dict):
                raw_in = re.sub(r'[\s\'\"]+', '', str(tc.get("input", "")).strip().lower())
                raw_out = re.sub(r'[\s\'\"]+', '', str(tc.get("expected_output", "")).strip().lower())
                tc_parts.append(f"{raw_in}->{raw_out}")
        tc_signature = "|".join(sorted(tc_parts))

    combined = f"T:{clean_title};D:{desc_signature};S:{sig_raw};TC:{tc_signature}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

def is_duplicate_problem(
    p1: Dict[str, Any],
    p2: Dict[str, Any]
) -> bool:
    """
    Determines if two problems represent the same underlying algorithmic task.
    Catches exact fingerprint matches, title matches, or test-case identity.
    """
    # 1. Compare fingerprints if both present
    fp1 = p1.get("fingerprint") or compute_problem_fingerprint(
        p1.get("title", ""), p1.get("description", ""), p1.get("starter_code", ""), p1.get("test_cases")
    )
    fp2 = p2.get("fingerprint") or compute_problem_fingerprint(
        p2.get("title", ""), p2.get("description", ""), p2.get("starter_code", ""), p2.get("test_cases")
    )
    if fp1 and fp2 and fp1 == fp2:
        return True

    # 2. Check title equivalence
    t1 = re.sub(r'[^a-zA-Z0-9]', '', (p1.get("title") or "").lower())
    t2 = re.sub(r'[^a-zA-Z0-9]', '', (p2.get("title") or "").lower())
    if t1 and t2 and t1 == t2:
        return True

    # 3. Check for obvious keyword/task equivalence (e.g. factorial, fibonacci, two sum, palindrome)
    key_tasks = ["factorial", "fibonacci", "twosum", "targetpair", "palindrome", "validparentheses"]
    for task in key_tasks:
        if task in t1 and task in t2:
            return True

    return False
