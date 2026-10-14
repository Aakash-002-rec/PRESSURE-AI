# Curated Practice Questions for Weak Topics
# Levels: 3 Easy, 3 Medium, 2 Advanced per topic

PRACTICE_QUESTIONS_BANK = {
    "Recursion": [
        # 3 Easy
        {
            "id": 101,
            "topic": "Recursion",
            "difficulty": "Easy",
            "question": "What is the primary role of a 'base case' in a recursive function?",
            "options": [
                "To optimize the space complexity by clearing cache",
                "To provide a terminating condition that stops recursive calls and prevents stack overflow",
                "To define the function signature and argument types",
                "To dynamically increase Python's recursion limit"
            ],
            "correct_answer": 1,
            "explanation": "A base case provides the immediate solution for the smallest input, unwinding the call stack and preventing infinite recursion."
        },
        {
            "id": 102,
            "topic": "Recursion",
            "difficulty": "Easy",
            "question": "In the standard recursive factorial function `def fact(n): return 1 if n <= 1 else n * fact(n-1)`, what is the return value of `fact(3)`?",
            "options": ["3", "6", "9", "12"],
            "correct_answer": 1,
            "explanation": "fact(3) = 3 * fact(2) = 3 * (2 * fact(1)) = 3 * 2 * 1 = 6."
        },
        {
            "id": 103,
            "topic": "Recursion",
            "difficulty": "Easy",
            "question": "What data structure does the runtime environment use internally to keep track of recursive function calls?",
            "options": ["Queue (FIFO)", "Call Stack (LIFO)", "Binary Search Tree", "Hash Map"],
            "correct_answer": 1,
            "explanation": "Each recursive call pushes a new stack frame onto the Call Stack in LIFO (Last-In-First-Out) order."
        },
        # 3 Medium
        {
            "id": 104,
            "topic": "Recursion",
            "difficulty": "Medium",
            "question": "Suppose a recursive function calls itself twice for each step (e.g. `f(n) = f(n-1) + f(n-1)`). Without memoization, what is the asymptotic time complexity?",
            "options": ["O(n)", "O(n log n)", "O(2^n)", "O(n^2)"],
            "correct_answer": 2,
            "explanation": "Branching factor of 2 at each depth level creates a full binary recursion tree of depth n, leading to 2^n calls, or O(2^n) exponential time."
        },
        {
            "id": 105,
            "topic": "Recursion",
            "difficulty": "Medium",
            "question": "What specific exception does standard CPython raise when recursion exceeds the maximum configured depth limit?",
            "options": ["MemoryError", "RecursionError", "StackOverflowException", "SystemError"],
            "correct_answer": 1,
            "explanation": "In Python 3.5+, Python raises a `RecursionError` (a subclass of `RuntimeError`) when recursion depth limit (default ~1000) is reached."
        },
        {
            "id": 106,
            "topic": "Recursion",
            "difficulty": "Medium",
            "question": "Which of the following is true regarding Tail Recursion in Python?",
            "options": [
                "CPython automatically optimizes tail-recursive functions to O(1) space",
                "CPython does NOT optimize tail calls; each call allocates a stack frame regardless",
                "Tail recursion causes an immediate syntax error in Python",
                "Tail recursion requires using the 'nonlocal' keyword"
            ],
            "correct_answer": 1,
            "explanation": "Guido van Rossum explicitly chose not to implement tail-call optimization (TCO) in CPython to preserve full stack traces for debugging."
        },
        # 2 Advanced
        {
            "id": 107,
            "topic": "Recursion",
            "difficulty": "Advanced",
            "question": "How does memoization transform a naive recursive algorithm (like Fibonacci) from O(2^n) to O(n) time complexity?",
            "options": [
                "By converting the recursive stack frames into multi-threading",
                "By caching the return values of subproblems in a hash map to avoid redundant recalculation",
                "By running the recursion on GPU registers",
                "By eliminating all base cases"
            ],
            "correct_answer": 1,
            "explanation": "Memoization caches results keyed by input parameters; subsequent calls with identical arguments return in O(1) time instead of recomputing."
        },
        {
            "id": 108,
            "topic": "Recursion",
            "difficulty": "Advanced",
            "question": "When reversing a singly linked list recursively, in which phase of recursion does the actual pointer reversal `node.next.next = node` occur?",
            "options": [
                "During the descending phase before reaching the base case",
                "During the unwinding (post-order) phase after the base case returns the new head",
                "In parallel while traversing the middle node",
                "Inside the initial function parameter declaration"
            ],
            "correct_answer": 1,
            "explanation": "In recursive reversal, execution descends to the tail (new head), and pointer rewiring occurs on the unwinding phase from tail back to root."
        }
    ],

    "Data Interpretation": [
        # 3 Easy
        {
            "id": 201,
            "topic": "Data Interpretation",
            "difficulty": "Easy",
            "question": "If a bar graph indicates sales of $120k in 2021 and $150k in 2022, what is the percentage increase in sales?",
            "options": ["20%", "25%", "30%", "33.3%"],
            "correct_answer": 1,
            "explanation": "Increase = 150 - 120 = 30k. Percentage = (30 / 120) * 100 = 25%."
        },
        {
            "id": 202,
            "topic": "Data Interpretation",
            "difficulty": "Easy",
            "question": "In a pie chart, if the slice for 'Marketing Expenditure' has an angle of 72 degrees, what percentage of the total budget is spent on Marketing?",
            "options": ["15%", "20%", "25%", "30%"],
            "correct_answer": 1,
            "explanation": "Percentage = (72 / 360) * 100 = 20%."
        },
        {
            "id": 203,
            "topic": "Data Interpretation",
            "difficulty": "Easy",
            "question": "A table shows student scores: 85, 90, 75, 70, 80. What is the average (arithmetic mean) score?",
            "options": ["78", "80", "82", "84"],
            "correct_answer": 1,
            "explanation": "Sum = 85 + 90 + 75 + 70 + 80 = 400. Average = 400 / 5 = 80."
        },
        # 3 Medium
        {
            "id": 204,
            "topic": "Data Interpretation",
            "difficulty": "Medium",
            "question": "A chart shows Revenue and Expenditure. In 2022, Revenue was $500,000 and Profit Margin was 20% of Revenue. What were the total Expenses?",
            "options": ["$380,000", "$400,000", "$420,000", "$450,000"],
            "correct_answer": 1,
            "explanation": "Profit = 20% of 500k = $100k. Expenses = Revenue - Profit = 500k - 100k = $400k."
        },
        {
            "id": 205,
            "topic": "Data Interpretation",
            "difficulty": "Medium",
            "question": "A table gives the ratio of male to female employees across 3 departments: Eng (3:2, total 250), Sales (1:1, total 200), HR (1:3, total 80). What is the total number of female employees across all three departments?",
            "options": ["240", "260", "280", "300"],
            "correct_answer": 1,
            "explanation": "Eng females = 2/5 * 250 = 100. Sales females = 1/2 * 200 = 100. HR females = 3/4 * 80 = 60. Total = 100 + 100 + 60 = 260."
        },
        {
            "id": 206,
            "topic": "Data Interpretation",
            "difficulty": "Medium",
            "question": "If index value went from 100 in Base Year to 132 in Year 1, then decreased by 25% in Year 2, what is the index value at the end of Year 2?",
            "options": ["97", "99", "101", "107"],
            "correct_answer": 1,
            "explanation": "132 * (1 - 0.25) = 132 * 0.75 = 99."
        },
        # 2 Advanced
        {
            "id": 207,
            "topic": "Data Interpretation",
            "difficulty": "Advanced",
            "question": "A company produces Widgets A, B, and C in ratio 2:3:5. The unit cost is $10 for A, $15 for B, and $20 for C. What is the weighted average unit cost per widget?",
            "options": ["$15.50", "$16.50", "$17.00", "$17.50"],
            "correct_answer": 1,
            "explanation": "Weighted sum = (2*10 + 3*15 + 5*20) = (20 + 45 + 100) = 165. Total parts = 2 + 3 + 5 = 10. Weighted average = 165 / 10 = $16.50."
        },
        {
            "id": 208,
            "topic": "Data Interpretation",
            "difficulty": "Advanced",
            "question": "A compound annual growth problem: If web traffic grew by 20% in 2021, 25% in 2022, and declined by 10% in 2023, what is the net overall percentage growth from initial value?",
            "options": ["32%", "35%", "38%", "41%"],
            "correct_answer": 1,
            "explanation": "Net multiplier = 1.20 * 1.25 * 0.90 = 1.50 * 0.90 = 1.35. That represents exactly a 35% net increase."
        }
    ]
}
