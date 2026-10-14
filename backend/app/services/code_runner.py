import sys
import subprocess
import json
import time
import os
from typing import Dict, List, Any, Optional

class CodeRunner:
    @staticmethod
    def execute_python_tests(
        code: str,
        test_cases: List[Dict[str, Any]],
        entry_function: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes candidate Python code against test cases in an isolated subprocess.
        Returns execution results, passed counts, stdout, and error details.
        """
        # Determine entry function name if not provided
        if not entry_function:
            for line in code.split("\n"):
                line_str = line.strip()
                if line_str.startswith("def ") and "(" in line_str:
                    entry_function = line_str.split("def ")[1].split("(")[0].strip()
                    break

        if not entry_function:
            entry_function = "solution"

        # Generate a test harness script that runs the candidate code against the test cases
        test_harness = f"""
import sys
import json
import traceback

# Candidate Code
{code}

# Test cases
raw_tests_json = {json.dumps(json.dumps(test_cases))}
tests = json.loads(raw_tests_json)
func_name = "{entry_function}"
results = []

target_func = globals().get(func_name)
if not callable(target_func):
    print(json.dumps({{"error": f"Function '{{func_name}}' was not defined or is not callable."}}))
    sys.exit(0)

for idx, tc in enumerate(tests):
    raw_input = tc.get("input", "")
    expected = tc.get("expected_output", "").strip()
    is_hidden = tc.get("is_hidden", False)
    desc = tc.get("description", f"Test #{{idx + 1}}")

    try:
        # Safely evaluate inputs
        # If input has comma, treat as arguments
        parsed_args = eval(f"({{raw_input}},)")
        actual_val = target_func(*parsed_args)
        actual_str = str(actual_val)

        # Normalize comparisons for boolean, list, strings
        passed = (actual_str.strip() == expected) or (repr(actual_val) == expected)
        results.append({{
            "index": idx + 1,
            "description": desc,
            "input": raw_input if not is_hidden else "[Hidden Test Input]",
            "expected": expected if not is_hidden else "[Hidden]",
            "actual": actual_str if not is_hidden else ("[Hidden]" if passed else actual_str),
            "passed": passed,
            "is_hidden": is_hidden,
            "error": None
        }})
    except ValueError as ve:
        # Check if ValueError was expected
        passed = ("ValueError" in expected)
        results.append({{
            "index": idx + 1,
            "description": desc,
            "input": raw_input if not is_hidden else "[Hidden Test Input]",
            "expected": expected if not is_hidden else "[Hidden]",
            "actual": f"ValueError: {{str(ve)}}" if not is_hidden else ("ValueError" if passed else f"ValueError: {{str(ve)}}"),
            "passed": passed,
            "is_hidden": is_hidden,
            "error": None if passed else f"ValueError: {{str(ve)}}"
        }})
    except RecursionError:
        results.append({{
            "index": idx + 1,
            "description": desc,
            "input": raw_input if not is_hidden else "[Hidden Test Input]",
            "expected": expected,
            "actual": "RecursionError: maximum recursion depth exceeded",
            "passed": False,
            "is_hidden": is_hidden,
            "error": "RecursionError: maximum recursion depth exceeded (missing or unreachable base case)."
        }})
    except Exception as e:
        results.append({{
            "index": idx + 1,
            "description": desc,
            "input": raw_input if not is_hidden else "[Hidden Test Input]",
            "expected": expected,
            "actual": f"{{type(e).__name__}}: {{str(e)}}",
            "passed": False,
            "is_hidden": is_hidden,
            "error": f"{{type(e).__name__}}: {{str(e)}}"
        }})

print("__JSON_START__")
print(json.dumps(results))
"""

        start_time = time.time()
        try:
            # Run in separate python process with strict 4 second timeout
            proc = subprocess.run(
                [sys.executable, "-c", test_harness],
                capture_output=True,
                text=True,
                timeout=4.0
            )
            duration_ms = round((time.time() - start_time) * 1000, 1)

            if proc.returncode != 0 and "__JSON_START__" not in proc.stdout:
                err_msg = proc.stderr.strip() or "SyntaxError or Compilation Failure"
                return {
                    "success": False,
                    "status": "error",
                    "error": err_msg,
                    "passed_count": 0,
                    "total_count": len(test_cases),
                    "correctness": 0.0,
                    "test_results": [],
                    "stdout": proc.stdout,
                    "duration_ms": duration_ms,
                    "weak_area": "Syntax / Compilation",
                    "time_complexity": "N/A",
                    "space_complexity": "N/A"
                }

            # Parse harness output
            out = proc.stdout
            if "__JSON_START__" in out:
                json_part = out.split("__JSON_START__")[1].strip()
                results = json.loads(json_part)
            else:
                results = []

            passed_count = sum(1 for r in results if r.get("passed"))
            total_count = len(results)
            correctness = round((passed_count / max(total_count, 1)) * 100, 1)

            # Analyze failure patterns for weak area diagnosis
            weak_area = "None (All Passed)"
            if correctness < 100:
                has_recursion_err = any("RecursionError" in str(r.get("error", "")) for r in results)
                has_negative_fail = any("negative" in r.get("description", "").lower() and not r.get("passed") for r in results)
                has_hidden_fail = any(r.get("is_hidden") and not r.get("passed") for r in results)

                if has_recursion_err:
                    weak_area = "Base case formulation / Infinite call stack"
                elif has_negative_fail or has_hidden_fail:
                    weak_area = "Edge case handling & input validation"
                else:
                    weak_area = "Algorithmic logic / Return value formulation"

            return {
                "success": True,
                "status": "passed" if correctness == 100.0 else "failed",
                "passed_count": passed_count,
                "total_count": total_count,
                "correctness": correctness,
                "test_results": results,
                "stdout": proc.stdout.split("__JSON_START__")[0].strip(),
                "duration_ms": duration_ms,
                "weak_area": weak_area,
                "time_complexity": "O(n)",
                "space_complexity": "O(n) auxiliary stack"
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "status": "error",
                "error": "TimeLimitExceeded: Execution took longer than 4.0 seconds (probable infinite loop or deep unbounded recursion).",
                "passed_count": 0,
                "total_count": len(test_cases),
                "correctness": 0.0,
                "test_results": [],
                "stdout": "",
                "duration_ms": 4000.0,
                "weak_area": "Infinite recursion / Unbounded loop",
                "time_complexity": "Exponential / Infinite",
                "space_complexity": "Stack Exhaustion"
            }
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "passed_count": 0,
                "total_count": len(test_cases),
                "correctness": 0.0,
                "test_results": [],
                "stdout": "",
                "duration_ms": 0,
                "weak_area": "Execution Error",
                "time_complexity": "N/A",
                "space_complexity": "N/A"
            }
