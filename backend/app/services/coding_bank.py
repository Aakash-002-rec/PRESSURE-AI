# Curated Coding Problems Bank for PRESSURE-AI
# Languages supported: Python (primary runner), Java, C, C++, JavaScript
# Problem Types: Recursion, Arrays, Strings, Functions, OOP, Searching, Sorting, Data Structures, Algorithms

CODING_PROBLEMS = [
    {
        "id": 1,
        "title": "Recursive Factorial with Boundary Guard",
        "category": "Recursion",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Write a recursive function `factorial(n)` that returns the factorial of a non-negative integer `n`.\n\n"
            "Requirements:\n"
            "- Must use recursion (a function calling itself).\n"
            "- Must define a correct base case: `0! = 1` and `1! = 1`.\n"
            "- Must raise a `ValueError` for negative inputs (`n < 0`)."
        ),
        "starter_code": (
            "def factorial(n: int) -> int:\n"
            "    # Your recursive code here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def factorial(n: int) -> int:\n"
            "    # Proper recursive implementation with boundary and edge validation\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be non-negative')\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
        ),
        "test_cases": [
            {"input": "0", "expected_output": "1", "is_hidden": False, "description": "Base case n=0"},
            {"input": "1", "expected_output": "1", "is_hidden": False, "description": "Base case n=1"},
            {"input": "5", "expected_output": "120", "is_hidden": False, "description": "Normal calculation n=5"},
            {"input": "7", "expected_output": "5040", "is_hidden": True, "description": "Hidden test n=7"},
            {"input": "-1", "expected_output": "ValueError", "is_hidden": True, "description": "Edge case negative input"}
        ],
        "constraints": "0 <= n <= 20. Must be recursive.",
        "hints": [
            "Every recursive function requires a base case to terminate execution without a stack overflow.",
            "For n <= 1, return 1 immediately.",
            "For n > 1, return n * factorial(n - 1)."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(n) auxiliary call stack"
    },
    {
        "id": 2,
        "title": "Recursive Fibonacci with Base Criteria",
        "category": "Recursion",
        "difficulty": "Intermediate",
        "language": "python",
        "description": (
            "Write a function `fibonacci(n)` that returns the n-th Fibonacci number where `fib(0) = 0`, `fib(1) = 1`, and `fib(n) = fib(n-1) + fib(n-2)`.\n\n"
            "Handle edge cases cleanly. Negative inputs should return 0."
        ),
        "starter_code": (
            "def fibonacci(n: int) -> int:\n"
            "    # Handle base cases and recursive steps\n"
            "    pass\n"
        ),
        "solution_code": (
            "def fibonacci(n: int) -> int:\n"
            "    # Optimal implementation handling edge cases and negative input\n"
            "    if n <= 0:\n"
            "        return 0\n"
            "    if n == 1:\n"
            "        return 1\n"
            "    a, b = 0, 1\n"
            "    for _ in range(2, n + 1):\n"
            "        a, b = b, a + b\n"
            "    return b\n"
        ),
        "test_cases": [
            {"input": "0", "expected_output": "0", "is_hidden": False, "description": "fib(0)"},
            {"input": "1", "expected_output": "1", "is_hidden": False, "description": "fib(1)"},
            {"input": "6", "expected_output": "8", "is_hidden": False, "description": "fib(6) = 8"},
            {"input": "10", "expected_output": "55", "is_hidden": True, "description": "fib(10) = 55"},
            {"input": "-3", "expected_output": "0", "is_hidden": True, "description": "Negative input"}
        ],
        "constraints": "n <= 30.",
        "hints": [
            "Check if n <= 0 first and return 0.",
            "If n == 1, return 1.",
            "Otherwise, decompose into fibonacci(n - 1) + fibonacci(n - 2)."
        ],
        "time_complexity": "O(2^n) or O(n) memoized",
        "space_complexity": "O(n) call stack"
    },
    {
        "id": 3,
        "title": "Two Sum / Target Pair Finder",
        "category": "Arrays",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Given a list of integers `nums` and an integer `target`, return the indices `[i, j]` of the two numbers such that they add up to `target` (with i < j).\n\n"
            "Assume each input has exactly one valid solution, and you may not use the same element twice."
        ),
        "starter_code": (
            "from typing import List\n\n"
            "def two_sum(nums: List[int], target: int) -> List[int]:\n"
            "    # Your implementation here\n"
            "    pass\n"
        ),
        "solution_code": (
            "from typing import List\n\n"
            "def two_sum(nums: List[int], target: int) -> List[int]:\n"
            "    # Single-pass hash map for optimal O(n) pair discovery\n"
            "    seen = {}\n"
            "    for i, num in enumerate(nums):\n"
            "        diff = target - num\n"
            "        if diff in seen:\n"
            "            return [seen[diff], i]\n"
            "        seen[num] = i\n"
            "    return []\n"
        ),
        "test_cases": [
            {"input": "[2, 7, 11, 15], 9", "expected_output": "[0, 1]", "is_hidden": False, "description": "Standard positive target"},
            {"input": "[3, 2, 4], 6", "expected_output": "[1, 2]", "is_hidden": False, "description": "Non-zero index match"},
            {"input": "[3, 3], 6", "expected_output": "[0, 1]", "is_hidden": False, "description": "Duplicate values"},
            {"input": "[-1, -2, -3, -4, -5], -8", "expected_output": "[2, 4]", "is_hidden": True, "description": "Negative numbers"},
            {"input": "[1, 5, 8, 3, 9, 2], 10", "expected_output": "[0, 4]", "is_hidden": True, "description": "Scattered array"}
        ],
        "constraints": "2 <= nums.length <= 10^4. Target can be positive or negative.",
        "hints": [
            "A brute force nested loop takes O(n^2) time.",
            "You can achieve O(n) time using a hash map to store seen values and their indices.",
            "For each number, check if (target - num) is already in your lookup map."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(n)"
    },
    {
        "id": 4,
        "title": "Valid Palindrome with Alphanumeric Filter",
        "category": "Strings",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.\n\n"
            "Write `is_palindrome(s: str) -> bool` that returns `True` if it is a palindrome, or `False` otherwise."
        ),
        "starter_code": (
            "def is_palindrome(s: str) -> bool:\n"
            "    # Your implementation here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def is_palindrome(s: str) -> bool:\n"
            "    # Filters alphanumeric characters and performs two-way symmetry check\n"
            "    cleaned = [c.lower() for c in s if c.isalnum()]\n"
            "    return cleaned == cleaned[::-1]\n"
        ),
        "test_cases": [
            {"input": "'A man, a plan, a canal: Panama'", "expected_output": "True", "is_hidden": False, "description": "Standard classic palindrome with punctuation"},
            {"input": "'race a car'", "expected_output": "False", "is_hidden": False, "description": "Near palindrome"},
            {"input": "' '", "expected_output": "True", "is_hidden": False, "description": "Empty / spaces only"},
            {"input": "'0P'", "expected_output": "False", "is_hidden": True, "description": "Alphanumeric mismatch"},
            {"input": "'Madam, I’m Adam'", "expected_output": "True", "is_hidden": True, "description": "Apostrophe case"}
        ],
        "constraints": "1 <= s.length <= 2 * 10^5.",
        "hints": [
            "Use Python's char.isalnum() to filter characters and .lower() to normalize.",
            "Compare the cleaned string with its reverse (cleaned[::-1]) or use two pointers."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(n)"
    },
    {
        "id": 5,
        "title": "Valid Parentheses via Stack",
        "category": "Data Structures",
        "difficulty": "Intermediate",
        "language": "python",
        "description": (
            "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type."
        ),
        "starter_code": (
            "def is_valid_parentheses(s: str) -> bool:\n"
            "    # Use a stack to track open brackets\n"
            "    pass\n"
        ),
        "solution_code": (
            "def is_valid_parentheses(s: str) -> bool:\n"
            "    # LIFO stack ensuring correct closing brackets and nesting order\n"
            "    stack = []\n"
            "    mapping = {')': '(', '}': '{', ']': '['}\n"
            "    for char in s:\n"
            "        if char in mapping.values():\n"
            "            stack.append(char)\n"
            "        elif char in mapping:\n"
            "            if not stack or stack.pop() != mapping[char]:\n"
            "                return False\n"
            "        else:\n"
            "            return False\n"
            "    return len(stack) == 0\n"
        ),
        "test_cases": [
            {"input": "'()'", "expected_output": "True", "is_hidden": False, "description": "Simple match"},
            {"input": "'()[]{}'", "expected_output": "True", "is_hidden": False, "description": "Multiple types"},
            {"input": "'(]'", "expected_output": "False", "is_hidden": False, "description": "Mismatched closing"},
            {"input": "'([)]'", "expected_output": "False", "is_hidden": True, "description": "Interleaved improper order"},
            {"input": "'{[]}'", "expected_output": "True", "is_hidden": True, "description": "Nested brackets"}
        ],
        "constraints": "1 <= s.length <= 10^4.",
        "hints": [
            "Use a list as a LIFO stack.",
            "Push opening brackets onto the stack.",
            "When encountering a closing bracket, check if it matches the top of the stack and pop it."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(n)"
    },
    {
        "id": 6,
        "title": "Recursive Count Zeros in List",
        "category": "Recursion",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Write a recursive function `count_zeros(nums)` that returns the count of 0s in nums.\n\n"
            "Requirements:\n"
            "- Must use recursion (calling itself on a smaller subproblem).\n"
            "- Must handle empty lists gracefully."
        ),
        "starter_code": (
            "def count_zeros(nums: list) -> int:\n"
            "    # recursive code\n"
            "    pass\n"
        ),
        "solution_code": (
            "def count_zeros(nums: list) -> int:\n"
            "    # Base case: empty list contains 0 zeros\n"
            "    if not nums:\n"
            "        return 0\n"
            "    # Recursive case: 1 if first element is 0 else 0, plus count in remainder of list\n"
            "    return (1 if nums[0] == 0 else 0) + count_zeros(nums[1:])\n"
        ),
        "test_cases": [
            {"input": "[0, 1, 0, 3]", "expected_output": "2", "is_hidden": False, "description": "Sample test 1"},
            {"input": "[1, 2, 3]", "expected_output": "0", "is_hidden": False, "description": "No zeros"},
            {"input": "[]", "expected_output": "0", "is_hidden": True, "description": "Empty list"},
            {"input": "[0, 0, 0]", "expected_output": "3", "is_hidden": True, "description": "All zeros"}
        ],
        "constraints": "0 <= len(nums) <= 100",
        "hints": [
            "Every recursive function requires a base case to terminate: check if not nums.",
            "If nums[0] == 0, count 1 + recursive call on nums[1:], otherwise 0 + recursive call on nums[1:]."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(n) auxiliary call stack"
    },
    {
        "id": 7,
        "title": "Recursive String Reversal",
        "category": "Recursion",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Write a recursive function `reverse_string(s: str) -> str` that reverses a given string.\n\n"
            "Requirements:\n"
            "- Must use recursion without built-in [::-1] or reversed().\n"
            "- Base case: empty string or single-character string returns itself."
        ),
        "starter_code": (
            "def reverse_string(s: str) -> str:\n"
            "    # Your recursive code here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def reverse_string(s: str) -> str:\n"
            "    # Base case: strings of length 0 or 1 are already reversed\n"
            "    if len(s) <= 1:\n"
            "        return s\n"
            "    # Recursive step: reverse the tail and append the head character\n"
            "    return reverse_string(s[1:]) + s[0]\n"
        ),
        "test_cases": [
            {"input": "'hello'", "expected_output": "olleh", "is_hidden": False, "description": "Standard word"},
            {"input": "''", "expected_output": "", "is_hidden": False, "description": "Empty string"},
            {"input": "'a'", "expected_output": "a", "is_hidden": False, "description": "Single character"},
            {"input": "'racecar'", "expected_output": "racecar", "is_hidden": True, "description": "Palindrome word"},
            {"input": "'Python'", "expected_output": "nohtyP", "is_hidden": True, "description": "Mixed case"}
        ],
        "constraints": "0 <= len(s) <= 1000",
        "hints": [
            "Base case: if len(s) <= 1, return s.",
            "Recursive step: reverse_string(s[1:]) + s[0]."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(n) call stack"
    },
    {
        "id": 8,
        "title": "Binary Search in Sorted Array",
        "category": "Algorithms",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Given an array of integers `nums` sorted in ascending order, and an integer `target`, "
            "write `binary_search(nums, target)` to search `target` in `nums`. If `target` exists, return its index. Otherwise, return -1.\n\n"
            "Must execute with O(log n) runtime complexity."
        ),
        "starter_code": (
            "def binary_search(nums: list, target: int) -> int:\n"
            "    # Implement binary search\n"
            "    pass\n"
        ),
        "solution_code": (
            "def binary_search(nums: list, target: int) -> int:\n"
            "    left, right = 0, len(nums) - 1\n"
            "    while left <= right:\n"
            "        mid = (left + right) // 2\n"
            "        if nums[mid] == target:\n"
            "            return mid\n"
            "        elif nums[mid] < target:\n"
            "            left = mid + 1\n"
            "        else:\n"
            "            right = mid - 1\n"
            "    return -1\n"
        ),
        "test_cases": [
            {"input": "[-1, 0, 3, 5, 9, 12], 9", "expected_output": "4", "is_hidden": False, "description": "Target exists"},
            {"input": "[-1, 0, 3, 5, 9, 12], 2", "expected_output": "-1", "is_hidden": False, "description": "Target missing"},
            {"input": "[5], 5", "expected_output": "0", "is_hidden": True, "description": "Single element found"},
            {"input": "[], 1", "expected_output": "-1", "is_hidden": True, "description": "Empty list"}
        ],
        "constraints": "1 <= nums.length <= 10^4. All integers are unique.",
        "hints": [
            "Maintain two pointers: left and right.",
            "Compute mid = (left + right) // 2 and narrow the range by half each iteration."
        ],
        "time_complexity": "O(log n)",
        "space_complexity": "O(1)"
    },
    {
        "id": 9,
        "title": "Maximum Subarray Sum (Kadane's Algorithm)",
        "category": "Algorithms",
        "difficulty": "Intermediate",
        "language": "python",
        "description": (
            "Given an integer array `nums`, find the subarray with the largest sum, and return its sum.\n\n"
            "A subarray is a contiguous non-empty sequence of elements within an array."
        ),
        "starter_code": (
            "def max_subarray(nums: list) -> int:\n"
            "    # Your implementation here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def max_subarray(nums: list) -> int:\n"
            "    # Kadane's algorithm for linear maximum contiguous sum\n"
            "    if not nums:\n"
            "        return 0\n"
            "    max_so_far = nums[0]\n"
            "    curr_max = nums[0]\n"
            "    for x in nums[1:]:\n"
            "        curr_max = max(x, curr_max + x)\n"
            "        max_so_far = max(max_so_far, curr_max)\n"
            "    return max_so_far\n"
        ),
        "test_cases": [
            {"input": "[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "expected_output": "6", "is_hidden": False, "description": "Standard array"},
            {"input": "[1]", "expected_output": "1", "is_hidden": False, "description": "Single element"},
            {"input": "[5, 4, -1, 7, 8]", "expected_output": "23", "is_hidden": True, "description": "Mostly positive"},
            {"input": "[-1, -2, -3]", "expected_output": "-1", "is_hidden": True, "description": "All negative"}
        ],
        "constraints": "1 <= nums.length <= 10^5",
        "hints": [
            "At each element, choose whether to extend the current subarray or start a new one.",
            "Track the global maximum seen so far."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(1)"
    },
    {
        "id": 10,
        "title": "Climbing Stairs Combinations",
        "category": "Recursion",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "You are climbing a staircase. It takes `n` steps to reach the top.\n\n"
            "Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?\n"
            "Write `climb_stairs(n: int) -> int`."
        ),
        "starter_code": (
            "def climb_stairs(n: int) -> int:\n"
            "    # Your implementation here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def climb_stairs(n: int) -> int:\n"
            "    if n <= 0:\n"
            "        return 0\n"
            "    if n <= 2:\n"
            "        return n\n"
            "    a, b = 1, 2\n"
            "    for _ in range(3, n + 1):\n"
            "        a, b = b, a + b\n"
            "    return b\n"
        ),
        "test_cases": [
            {"input": "2", "expected_output": "2", "is_hidden": False, "description": "2 steps"},
            {"input": "3", "expected_output": "3", "is_hidden": False, "description": "3 steps"},
            {"input": "5", "expected_output": "8", "is_hidden": True, "description": "5 steps"},
            {"input": "1", "expected_output": "1", "is_hidden": True, "description": "1 step"}
        ],
        "constraints": "1 <= n <= 45",
        "hints": [
            "To reach step n, you must arrive from step n-1 or step n-2.",
            "This mirrors the Fibonacci sequence where ways(n) = ways(n-1) + ways(n-2)."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(1)"
    },
    {
        "id": 11,
        "title": "Valid Anagram String",
        "category": "Strings",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, and `False` otherwise.\n\n"
            "An anagram is a word or phrase formed by rearranging the letters of a different word or phrase."
        ),
        "starter_code": (
            "def is_anagram(s: str, t: str) -> bool:\n"
            "    # Your implementation here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def is_anagram(s: str, t: str) -> bool:\n"
            "    return sorted(s) == sorted(t)\n"
        ),
        "test_cases": [
            {"input": "'anagram', 'nagaram'", "expected_output": "True", "is_hidden": False, "description": "Valid anagram"},
            {"input": "'rat', 'car'", "expected_output": "False", "is_hidden": False, "description": "Different letters"},
            {"input": "'a', 'a'", "expected_output": "True", "is_hidden": True, "description": "Single match"},
            {"input": "'a', 'ab'", "expected_output": "False", "is_hidden": True, "description": "Different lengths"}
        ],
        "constraints": "1 <= s.length, t.length <= 5 * 10^4",
        "hints": [
            "Count character frequencies or compare sorted representations of both strings."
        ],
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)"
    },
    {
        "id": 12,
        "title": "First Non-Repeating Character Index",
        "category": "Strings",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Given a string `s`, find the first non-repeating character in it and return its index. If it does not exist, return -1.\n\n"
            "Write `first_uniq_char(s: str) -> int`."
        ),
        "starter_code": (
            "def first_uniq_char(s: str) -> int:\n"
            "    # Your implementation here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def first_uniq_char(s: str) -> int:\n"
            "    counts = {}\n"
            "    for ch in s:\n"
            "        counts[ch] = counts.get(ch, 0) + 1\n"
            "    for i, ch in enumerate(s):\n"
            "        if counts[ch] == 1:\n"
            "            return i\n"
            "    return -1\n"
        ),
        "test_cases": [
            {"input": "'leetcode'", "expected_output": "0", "is_hidden": False, "description": "First char unique"},
            {"input": "'loveleetcode'", "expected_output": "2", "is_hidden": False, "description": "Middle char unique"},
            {"input": "'aabb'", "expected_output": "-1", "is_hidden": True, "description": "No unique char"}
        ],
        "constraints": "1 <= s.length <= 10^5",
        "hints": [
            "First pass: build a hash map counting occurrences of each character.",
            "Second pass: find the first character with a count of 1."
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(1) limited to alphabet"
    },
    {
        "id": 13,
        "title": "Recursive Power of Number",
        "category": "Recursion",
        "difficulty": "Beginner",
        "language": "python",
        "description": (
            "Write a recursive function `power(base: int, exp: int) -> int` that calculates `base` raised to the power `exp`.\n\n"
            "Requirements:\n"
            "- Must be recursive.\n"
            "- Base cases: `exp == 0` returns 1.\n"
            "- Raise `ValueError` if `exp < 0`."
        ),
        "starter_code": (
            "def power(base: int, exp: int) -> int:\n"
            "    # Your recursive code here\n"
            "    pass\n"
        ),
        "solution_code": (
            "def power(base: int, exp: int) -> int:\n"
            "    if exp < 0:\n"
            "        raise ValueError('exp must be non-negative')\n"
            "    if exp == 0:\n"
            "        return 1\n"
            "    return base * power(base, exp - 1)\n"
        ),
        "test_cases": [
            {"input": "2, 3", "expected_output": "8", "is_hidden": False, "description": "2^3 = 8"},
            {"input": "5, 0", "expected_output": "1", "is_hidden": False, "description": "5^0 = 1"},
            {"input": "3, 4", "expected_output": "81", "is_hidden": True, "description": "3^4 = 81"},
            {"input": "2, -1", "expected_output": "ValueError", "is_hidden": True, "description": "Negative exponent"}
        ],
        "constraints": "base <= 20, 0 <= exp <= 10",
        "hints": [
            "If exp == 0, return 1.",
            "Otherwise, return base * power(base, exp - 1)."
        ],
        "time_complexity": "O(exp)",
        "space_complexity": "O(exp) call stack"
    }
]
