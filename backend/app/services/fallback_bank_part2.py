from typing import Dict, List, Any

# Part 2 of curated fallback question bank to guarantee >= 15 questions per domain
# across all 13 domains.
FALLBACK_QUESTIONS_PART2: List[Dict[str, Any]] = [
    # =========================================================================
    # C (Domain: C)
    # =========================================================================
    {
        "domain": "C",
        "topic": "Function Pointers & Callbacks",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How do function pointers work in C? What is their syntax, and how are they used to implement generic callbacks, event dispatch tables, and qsort comparison functions?",
        "expected_concepts": ["function pointer", "callback", "qsort comparator", "void*", "dispatch table", "code segment"],
        "evaluation_criteria": "Explains function pointer stores address of executable instructions in code segment. Illustrates typedef and usage in callbacks.",
        "hints": [
            "In C, function names decay into pointers to their entry address in memory.",
            "Syntax: return_type (*func_ptr_name)(param_types).",
            "qsort uses 'int (*)(const void *, const void *)' to sort arbitrary data types."
        ],
        "pressure_followups": ["What is the risk of casting between incompatible function pointer types in C?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Bitwise Manipulation & Flag Registers",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain bitwise operations in C (&, |, ^, ~, <<, >>). How do you set, clear, toggle, and check individual bits in an integer flag register using bitmasks?",
        "expected_concepts": ["bitwise operations", "bitmask", "bit shifting", "flag register", "toggle bit XOR", "clear bit AND NOT"],
        "evaluation_criteria": "Details bitwise idioms: set (val |= (1 << n)), clear (val &= ~(1 << n)), toggle (val ^= (1 << n)), test (val & (1 << n)).",
        "hints": [
            "Shifting 1 << n produces a mask with only the nth bit enabled.",
            "Use bitwise OR '|' to turn on bits, and AND with NOT '& ~' to turn off bits.",
            "XOR '^' flips bits without affecting other positions."
        ],
        "pressure_followups": ["What happens during arithmetic right shift versus logical right shift on signed integers in C?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Memory Leaks & Valgrind Profiling",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A long-running C network server steadily leaks memory over 48 hours. How would you use Valgrind Memcheck to distinguish between Definitely Lost, Indirectly Lost, and Still Reachable memory blocks?",
        "expected_concepts": ["Valgrind", "Memcheck", "definitely lost", "indirectly lost", "still reachable", "heap leak", "free"],
        "evaluation_criteria": "Explains definitely lost means no pointer to block exists. Indirectly lost means pointer was inside another lost block. Still reachable means pointers exist at exit.",
        "hints": [
            "Valgrind replaces malloc and free to track every allocated heap block and its retaining pointers.",
            "Definitely lost indicates a severe leak where the allocation address was completely overwritten.",
            "Indirectly lost occurs in tree or graph structures when the root is lost."
        ],
        "pressure_followups": ["What overhead does Valgrind impose on execution speed and memory consumption during profiling?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Dynamic 2D Array Allocation",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare two strategies for allocating a 2D matrix dynamically in C: an array of row pointers (malloc per row) versus a single contiguous 1D buffer (single malloc with row-major indexing). What are the cache locality and fragmentation trade-offs?",
        "expected_concepts": ["2D array allocation", "contiguous memory", "pointer array", "cache locality", "heap fragmentation", "stride indexing"],
        "evaluation_criteria": "Contrasts pointer-to-pointer (separate rows, poor cache locality, N+1 allocations) with contiguous block (single malloc, sequential cache prefetching, stride formula row * cols + col).",
        "hints": [
            "An array of pointers requires M allocations for rows and 1 for pointers, causing heap fragmentation.",
            "A single contiguous block can be fetched efficiently into CPU L1/L2 cache lines.",
            "Accessing contiguous memory uses index formula: matrix[r * cols + c]."
        ],
        "pressure_followups": ["How do you free each allocation structure without causing undefined behavior or leaks?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "In-Place String Tokenization",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a C function 'reverse_words' that reverses the words in a string in-place without allocating auxiliary heap memory. For example, 'the sky is blue' becomes 'blue is sky the'.",
        "expected_concepts": ["in-place reversal", "string manipulation", "pointer two-sum", "O(1) extra space", "null terminator"],
        "evaluation_criteria": "First reverses the entire string in-place, then reverses each individual word separated by spaces. O(N) time and O(1) space.",
        "hints": [
            "Reversing the entire string puts the words in reverse order, but with individual words backwards.",
            "A second pass reversing each word restores character order within words.",
            "Use two pointers (start and end) to swap characters in-place."
        ],
        "pressure_followups": ["How would you handle multiple consecutive spaces or leading/trailing whitespace?"],
        "code_snippet": None,
        "starter_code": "#include <string.h>\n\nvoid reverse_words(char *s) {\n    // TODO: Reverse words in-place in O(1) extra space\n}",
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Volatile Keyword in Embedded Systems",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "What is the purpose of the 'volatile' qualifier in C? Why does the compiler optimize away reads from memory-mapped hardware registers without it, and why does volatile NOT guarantee thread-safety or atomicity?",
        "expected_concepts": ["volatile qualifier", "memory-mapped I/O", "compiler optimization", "register caching", "thread safety", "atomicity", "memory barrier"],
        "evaluation_criteria": "Explains volatile forces compiler to re-read from memory rather than caching in CPU registers. Clarifies volatile does not generate atomic CPU instructions or memory barriers.",
        "hints": [
            "Compilers assume variable values only change if modified by the current execution thread.",
            "Hardware registers or interrupt routines can modify memory values asynchronously.",
            "Volatile prevents compiler dead-code elimination and register caching, but does not provide thread synchronization."
        ],
        "pressure_followups": ["What is the difference between 'volatile int *p', 'int * volatile p', and 'volatile int * volatile p'?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },

    # =========================================================================
    # C++ (Domain: C++)
    # =========================================================================
    {
        "domain": "C++",
        "topic": "Template Metaprogramming & SFINAE",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Explain Substitution Failure Is Not An Error (SFINAE) in C++ templates. How does std::enable_if constrain template overloads, and how do C++20 Concepts simplify template constraints?",
        "expected_concepts": ["SFINAE", "enable_if", "template specialization", "compile-time type traits", "C++20 Concepts", "overload resolution"],
        "evaluation_criteria": "Explains compiler discards invalid template substitutions during overload deduction without throwing errors. Shows how C++20 concepts replace enable_if with clean constraints.",
        "hints": [
            "When evaluating template overloads, deduction failures simply remove that candidate from consideration.",
            "std::enable_if uses SFINAE to conditionally enable function templates based on boolean type traits.",
            "C++20 concepts allow writing 'requires' clauses with readable syntax."
        ],
        "pressure_followups": ["What compiler error messages arise when a template fails with enable_if compared to C++20 concepts?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Rule of Three vs Five vs Zero",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the evolution from the Rule of Three (C++98) to the Rule of Five (C++11) and the Rule of Zero in modern C++. What five special member functions manage resources?",
        "expected_concepts": ["Rule of Three", "Rule of Five", "Rule of Zero", "destructor", "copy constructor", "copy assignment", "move constructor", "move assignment"],
        "evaluation_criteria": "Lists Destructor, Copy Constructor, Copy Assignment, Move Constructor, Move Assignment. Explains Rule of Zero advocates using RAII wrappers (vector, unique_ptr) so compiler manages all five automatically.",
        "hints": [
            "If a class manages a raw resource, it must implement all copy and move operations explicitly.",
            "Rule of 3: Destructor, Copy Constructor, Copy Assignment.",
            "Rule of Zero: Use standard smart pointers and containers so custom copy/move logic is unnecessary."
        ],
        "pressure_followups": ["What is the Copy-and-Swap idiom, and how does it guarantee strong exception safety for assignment operators?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "STL Containers Memory Layout",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare std::vector, std::list, and std::deque in C++. Analyze their internal memory layouts, iterator invalidation rules, random access complexity, and cache locality.",
        "expected_concepts": ["vector", "list", "deque", "contiguous memory", "doubly linked nodes", "chunked arrays", "cache locality", "iterator invalidation"],
        "evaluation_criteria": "Details vector's contiguous array, deque's map of fixed-size chunks, and list's heap-allocated nodes with pointers. Explains vector's superior cache locality.",
        "hints": [
            "std::vector stores elements in a single contiguous heap buffer.",
            "std::list allocates a heap node with prev/next pointers for every single element.",
            "std::deque uses a central array of pointers to fixed-size memory blocks, allowing O(1) push_front without shifting."
        ],
        "pressure_followups": ["What operations invalidate iterators and references in std::vector versus std::list?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Multithreading & Condition Variables",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "In a C++ multithreaded producer-consumer system using std::condition_variable, why must waiting on a condition variable always be enclosed within a while loop checking a predicate rather than an if statement?",
        "expected_concepts": ["condition_variable", "spurious wakeup", "unique_lock", "predicate loop", "race condition", "wait_for"],
        "evaluation_criteria": "Explains spurious wakeups occur where threads unblock without notification. Rechecking the predicate inside a while loop prevents processing unready states.",
        "hints": [
            "Operating systems can wake sleeping threads even if notify_one() was not called.",
            "Multiple consumer threads might awaken, but only one can consume the available item.",
            "Syntax: cv.wait(lock, [&]{ return !queue.empty(); }) encapsulates the while loop."
        ],
        "pressure_followups": ["Why does std::condition_variable require std::unique_lock instead of std::lock_guard?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Custom Vector Implementation",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement a minimal dynamic array template class 'SimpleVector' in C++ with push_back and size/capacity tracking, doubling capacity on exhaustion using move operations.",
        "expected_concepts": ["dynamic array", "capacity doubling", "std::move", "template class", "new[] and delete[]", "destructor"],
        "evaluation_criteria": "Correctly manages heap buffer, doubles capacity when size reaches capacity, re-allocates, moves existing elements, and deletes old buffer.",
        "hints": [
            "Maintain three members: pointer to buffer T*, size_t size, size_t capacity.",
            "When size == capacity, allocate new_capacity = capacity == 0 ? 1 : capacity * 2.",
            "Use std::move to transfer existing elements to the new buffer before freeing the old buffer."
        ],
        "pressure_followups": ["Why does capacity doubling ensure amortized O(1) push_back complexity?"],
        "code_snippet": None,
        "starter_code": "template <typename T>\nclass SimpleVector {\n    T* data_ = nullptr;\n    size_t size_ = 0;\n    size_t capacity_ = 0;\npublic:\n    // TODO: Implement push_back, size, capacity, and destructor\n};",
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Exception Safety Guarantees",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "Explain the four levels of Exception Safety in C++: No Exception Safety, Basic Guarantee, Strong Guarantee, and No-throw (noexcept) Guarantee. Why is noexcept critical for move constructors in std::vector resizing?",
        "expected_concepts": ["exception safety", "basic guarantee", "strong guarantee", "noexcept", "vector reallocation", "commit-or-rollback", "std::move_if_noexcept"],
        "evaluation_criteria": "Defines all 4 guarantees. Explains std::vector will fallback to copying elements during reallocation unless move constructors are marked noexcept to maintain strong safety.",
        "hints": [
            "Basic: Invariant holds, no memory leaks, but state may change.",
            "Strong: Operation succeeds or rolls back completely to original state.",
            "std::vector::reserve uses std::move_if_noexcept; if an exception is thrown mid-move, original data cannot be restored."
        ],
        "pressure_followups": ["What happens at runtime if an exception escapes a function marked noexcept?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },

    # =========================================================================
    # JAVA (Domain: Java)
    # =========================================================================
    {
        "domain": "Java",
        "topic": "Generics Type Erasure & Bridge Methods",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Explain Type Erasure in Java Generics. How does the compiler enforce type safety at compile-time while removing generic types in bytecode, and why are synthetic Bridge Methods generated?",
        "expected_concepts": ["type erasure", "bytecode", "bridge method", "synthetic method", "cast insertion", "unbounded wildcard", "covariance"],
        "evaluation_criteria": "Explains generic types are replaced by Object or bound type in bytecode. Explains bridge methods preserve polymorphism when overriding parameterized methods.",
        "hints": [
            "Generics were added in Java 5 with backward compatibility for pre-Java 5 JVM bytecode.",
            "List<String> and List<Integer> share the exact same raw List.class at runtime.",
            "Compilers insert synthetic bridge methods with Object parameters to satisfy method signature overriding."
        ],
        "pressure_followups": ["Why can't you write 'new T()' or 'new T[10]' directly inside a generic Java class?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Streams API vs Imperative Loops",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare Java 8 Streams API (map, filter, reduce) with traditional imperative for-loops. What are the performance and debuggability trade-offs, and how does lazy evaluation work in Stream pipelines?",
        "expected_concepts": ["Streams API", "lazy evaluation", "intermediate operations", "terminal operation", "parallelStream", "garbage collection overhead"],
        "evaluation_criteria": "Explains intermediate operations return new Stream pipelines without executing until a terminal operation is called. Contrasts loop JIT optimization with Stream lambda allocations.",
        "hints": [
            "Intermediate operations (filter, map) build an execution pipeline lazily.",
            "No elements are processed until a terminal operation (collect, forEach, findFirst) executes.",
            "Traditional loops have lower allocation overhead and easier stack-trace debugging in tight loops."
        ],
        "pressure_followups": ["Why can parallelStream() degrade performance on CPU-bound tasks if the default ForkJoinPool is saturated?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "ClassLoader Architecture",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A modular Java enterprise application needs to load and unload plugins dynamically at runtime without restarting the JVM. How does the ClassLoader hierarchy (Bootstrap, Platform/Extension, Application) work, and how does delegation prevent class duplication?",
        "expected_concepts": ["ClassLoader", "parent delegation model", "Bootstrap ClassLoader", "Application ClassLoader", "plugin isolation", "ClassCastException"],
        "evaluation_criteria": "Explains Parent Delegation Model: requests delegate to parent first before searching child paths. Custom ClassLoaders override loadClass to enable isolated plugin reloading.",
        "hints": [
            "ClassLoaders delegate upward to parents before attempting to load classes locally.",
            "A class in the JVM is uniquely identified by its fully qualified name AND its ClassLoader instance.",
            "Two classes with identical package and name loaded by different ClassLoaders are incompatible types."
        ],
        "pressure_followups": ["How can uncollected ClassLoaders cause Metaspace OutOfMemoryError during repeated plugin reloads?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "CompletableFuture Async Pipelines",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A travel aggregation service in Java must query 5 flight APIs concurrently with a 2-second timeout, combine the results, and return the cheapest option. How would you design this using CompletableFuture and thread pools?",
        "expected_concepts": ["CompletableFuture", "allOf", "thenCombine", "exceptionally", "orTimeout", "custom Executor", "non-blocking"],
        "evaluation_criteria": "Uses supplyAsync with custom Executor, CompletableFuture.allOf, exceptionally/handle for resilient partial results, and orTimeout for SLA enforcement.",
        "hints": [
            "CompletableFuture.allOf coordinates completion across multiple independent futures.",
            "Always pass a custom Executor to prevent exhausting the shared CommonForkJoinPool.",
            "Use exceptionally() to return empty or fallback data if a single external airline API fails."
        ],
        "pressure_followups": ["What is the difference between thenApply() and thenApplyAsync()?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Thread-Safe Bounded Blocking Queue",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement a generic BoundedBlockingQueue in Java with put(T) and take() methods using a ReentrantLock and two Condition variables (notFull, notEmpty).",
        "expected_concepts": ["ReentrantLock", "Condition", "notFull", "notEmpty", "bounded queue", "await", "signal"],
        "evaluation_criteria": "Correctly locks critical section, awaits notFull when queue is full, awaits notEmpty when queue is empty, and signals conditions on state transitions in finally block.",
        "hints": [
            "Use one ReentrantLock and create two conditions: lock.newCondition().",
            "Always wrap condition.await() inside a while loop checking queue capacity.",
            "Always unlock in a finally block to prevent permanent deadlocks."
        ],
        "pressure_followups": ["Why is signal() preferred over signalAll() when multiple threads wait on the same Condition?"],
        "code_snippet": None,
        "starter_code": "import java.util.concurrent.locks.*;\nimport java.util.*;\n\npublic class BoundedBlockingQueue<T> {\n    private final Queue<T> queue = new LinkedList<>();\n    private final int capacity;\n    private final ReentrantLock lock = new ReentrantLock();\n    // TODO: Add conditions and implement put/take\n    public BoundedBlockingQueue(int capacity) { this.capacity = capacity; }\n}",
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Reflection & Java Modules",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "What are the trade-offs of using Java Reflection (java.lang.reflect)? How does it affect JIT inlining, type safety, and runtime performance, and how did the Java 9 Module System (JPMS) restrict deep reflection?",
        "expected_concepts": ["reflection", "JIT inlining", "performance overhead", "type safety", "JPMS", "module-info", "opens directive"],
        "evaluation_criteria": "Explains reflection bypasses compile-time checks, impedes JIT optimizations, and incurs boxing/unboxing costs. Notes JPMS requires explicit 'opens' packages to allow deep reflection.",
        "hints": [
            "Reflective method invocations require dynamic lookup and cannot be easily inlined by the HotSpot JIT compiler.",
            "Security managers and JPMS restrict setAccessible(true) access to private fields.",
            "Modern frameworks often prefer bytecode generation (ByteBuddy, ASM) or compile-time annotation processing."
        ],
        "pressure_followups": ["What is MethodHandle, and how does it compare to standard Reflection in terms of JVM performance?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },

    # =========================================================================
    # JAVASCRIPT (Domain: JavaScript)
    # =========================================================================
    {
        "domain": "JavaScript",
        "topic": "Proxy & Reflect API",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "How do JavaScript Proxy and Reflect APIs enable metaprogramming and reactive state management (like Vue 3 reactivity)? What traps are available, and why should trap implementations forward operations via Reflect?",
        "expected_concepts": ["Proxy", "Reflect", "traps", "get and set traps", "reactivity", "receiver", "prototype forwarding"],
        "evaluation_criteria": "Explains Proxy intercepts fundamental object operations. Explains Reflect guarantees correct receiver binding for getters and prototype consistency.",
        "hints": [
            "A Proxy wraps a target object and intercepts operations like property access, assignment, and deletion.",
            "Reflect methods mirror internal object operations with identical parameters to Proxy traps.",
            "Using Reflect.get(target, prop, receiver) preserves proper 'this' binding inside getters."
        ],
        "pressure_followups": ["What are the limitations of Proxies regarding private class fields (#field)?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Web Workers & SharedArrayBuffer",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A browser-based image editor drops frames to 15 FPS when applying heavy blur filters on 4K images on the main UI thread. How would you redesign the architecture using Web Workers, OffscreenCanvas, and SharedArrayBuffer with Atomics for zero-copy concurrency?",
        "expected_concepts": ["Web Workers", "main thread blocking", "OffscreenCanvas", "SharedArrayBuffer", "Atomics", "structured clone", "transferable objects"],
        "evaluation_criteria": "Offloads pixel calculations to background Web Worker threads. Uses SharedArrayBuffer for zero-copy shared memory or Transferable ArrayBuffers, coordinated with Atomics.",
        "hints": [
            "Web Workers run scripts in background threads without blocking the browser UI event loop.",
            "Transferable objects (like ArrayBuffer) transfer ownership without copying memory.",
            "SharedArrayBuffer allows multi-threaded read/write on the same RAM, requiring Atomics to prevent race conditions."
        ],
        "pressure_followups": ["Why were SharedArrayBuffers temporarily disabled in browsers, and what HTTP headers (COOP, COEP) are required to enable them today?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Async Generators & Iteration",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement an asynchronous generator function 'paginateApi' that fetches paginated API pages sequentially using async/await and yields individual items one by one, stopping when 'hasNextPage' is false.",
        "expected_concepts": ["async generator", "for await...of", "yield", "pagination", "async iterator", "Promise"],
        "evaluation_criteria": "Uses async function* syntax with yield. Fetches pages in a while loop, iterating through items and yielding each, updating page cursor until exhaustion.",
        "hints": [
            "An async generator combines async/await with yield: async function* name().",
            "Consumers consume items using 'for await (const item of paginateApi())'.",
            "Each yield statement suspends execution until the consumer requests the next item."
        ],
        "pressure_followups": ["What is the difference between Symbol.iterator and Symbol.asyncIterator?"],
        "code_snippet": None,
        "starter_code": "async function* paginateApi(fetchPageFn) {\n  let page = 1;\n  let hasMore = true;\n  // TODO: Yield items one-by-one across pages\n}",
        "code_language": "javascript"
    },

    # =========================================================================
    # SQL (Domain: SQL)
    # =========================================================================
    {
        "domain": "SQL",
        "topic": "Recursive CTEs for Hierarchical Data",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How do Recursive Common Table Expressions (CTEs) work in SQL? Explain the anchor member, recursive member, UNION ALL termination condition, and how to query organizational management hierarchies.",
        "expected_concepts": ["recursive CTE", "anchor member", "recursive member", "UNION ALL", "termination condition", "hierarchy depth", "employee manager"],
        "evaluation_criteria": "Explains initial anchor query executes once, followed by recursive iteration joining previous result set until empty. Illustrates tracking manager_id to employee_id.",
        "hints": [
            "A recursive CTE has two parts joined by UNION ALL: the anchor query and the recursive query.",
            "The anchor query defines the base result set (e.g. CEO where manager_id IS NULL).",
            "The recursive step joins the CTE to the base table to fetch the next level of children."
        ],
        "pressure_followups": ["How do you prevent infinite loops in recursive CTEs if circular reporting relationships exist in the database?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Composite Indexes & Leftmost Prefix Rule",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Explain the Leftmost Prefix Rule for composite indexes (e.g. INDEX on (status, created_at, user_id)). Under what query conditions can the database use this index for filtering and sorting, and when does it fail to use the index?",
        "expected_concepts": ["composite index", "leftmost prefix rule", "range scan", "index skip scan", "column cardinality", "sort order"],
        "evaluation_criteria": "Explains B-Tree composite index orders keys lexicographically (col1, then col2, then col3). Queries skipping col1 cannot perform index seek on col2 or col3.",
        "hints": [
            "A composite index on (A, B, C) can satisfy queries on (A), (A, B), and (A, B, C).",
            "A query filtering only on (B) or (C) cannot seek the index because the tree is sorted primarily by A.",
            "Once a range condition (<, >) is encountered on a column, subsequent columns in the index cannot be used for filtering."
        ],
        "pressure_followups": ["Should higher-cardinality columns always appear first in a composite index?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Sharding vs Partitioning",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A financial ledger table exceeds 500 million rows and 2 Terabytes, causing queries to slow down significantly. Compare Horizontal Table Partitioning (declarative range/hash partitioning inside a single database) versus Application-Level Sharding across multiple database instances.",
        "expected_concepts": ["table partitioning", "sharding", "partition pruning", "sharding key", "cross-shard joins", "distributed transactions", "re-sharding"],
        "evaluation_criteria": "Contrasts native partitioning (transparent to app, partition pruning, single node I/O ceiling) with sharding (distributes compute/storage across nodes, but complicates cross-shard joins and transactions).",
        "hints": [
            "Declarative partitioning splits tables on disk while maintaining a single logical table view.",
            "Partition pruning skips scanning irrelevant partitions based on query WHERE clauses.",
            "Sharding splits data across completely separate database servers, requiring a sharding key."
        ],
        "pressure_followups": ["How does consistent hashing minimize data migration when adding new shard instances?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Join Algorithms Comparison",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare Nested Loop Join, Hash Join, and Merge Join in relational database query optimizers. Under what table sizes, indexing configurations, and sort orders does the optimizer select each algorithm?",
        "expected_concepts": ["Nested Loop Join", "Hash Join", "Merge Join", "cost-based optimizer", "outer table", "hash table in memory", "presorted input"],
        "evaluation_criteria": "Details Nested Loop (small outer table with indexed inner table), Hash Join (large unsorted tables with equality join), Merge Join (both inputs presorted on join key).",
        "hints": [
            "Nested loop iterates through outer rows and probes the inner table (O(M * log N) if indexed).",
            "Hash join builds an in-memory hash table of the smaller relation, then streams the larger table through it.",
            "Merge join steps through two pre-sorted datasets simultaneously in O(M + N)."
        ],
        "pressure_followups": ["What happens when the hash table in a Hash Join exceeds available work_mem buffer space?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Deduplicate Rows Query",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a SQL query or script to delete duplicate rows from a 'customers' table having duplicate 'email' values, keeping only the row with the lowest 'id'.",
        "expected_concepts": ["DELETE with JOIN", "ROW_NUMBER()", "MIN(id)", "GROUP BY", "subquery", "Common Table Expression"],
        "evaluation_criteria": "Uses a self-join DELETE c1 FROM customers c1 JOIN customers c2 ON c1.email = c2.email AND c1.id > c2.id, or CTE with ROW_NUMBER() > 1.",
        "hints": [
            "Self-join customers table to itself on matching email.",
            "Compare primary keys so c1.id > c2.id to identify duplicate rows with higher IDs.",
            "Delete from the alias corresponding to the higher IDs."
        ],
        "pressure_followups": ["How would you execute this deduplication in batches on a table with 50 million rows without locking the table?"],
        "code_snippet": None,
        "starter_code": "-- Write query to delete duplicate customers by email, keeping lowest id\nDELETE c1\nFROM customers c1\nJOIN customers c2\n  -- TODO: Join condition and filter",
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Deadlock Detection in Transactions",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "Two concurrent transactions run the following updates:\nTx1: UPDATE accounts SET balance = balance - 100 WHERE id = 1; UPDATE accounts SET balance = balance + 100 WHERE id = 2;\nTx2: UPDATE accounts SET balance = balance - 50 WHERE id = 2; UPDATE accounts SET balance = balance + 50 WHERE id = 1;\nExplain how a deadlock occurs and how the database detects and breaks it.",
        "expected_concepts": ["deadlock", "row-level lock", "exclusive lock", "wait-for graph", "deadlock victim", "transaction rollback", "lock acquisition ordering"],
        "evaluation_criteria": "Explains Tx1 holds row 1 and requests row 2; Tx2 holds row 2 and requests row 1. Database detects cycle in wait-for graph, aborts one transaction (victim), and rolls it back.",
        "hints": [
            "UPDATE statements take exclusive (X) row locks until COMMIT or ROLLBACK.",
            "Both transactions block waiting on the other's held row lock.",
            "The database background deadlock detector detects cycles in the lock graph and aborts one transaction."
        ],
        "pressure_followups": ["How can the application eliminate these deadlocks completely by sorting the account IDs prior to updating?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },

    # =========================================================================
    # DBMS (Domain: DBMS)
    # =========================================================================
    {
        "domain": "DBMS",
        "topic": "Two-Phase Locking (2PL) Concurrency",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Two-Phase Locking (2PL) protocol in DBMS transaction management. What are the Growing Phase and Shrinking Phase, and how does Strict 2PL prevent cascading aborts?",
        "expected_concepts": ["Two-Phase Locking", "growing phase", "shrinking phase", "serializability", "strict 2PL", "cascading rollback", "exclusive locks"],
        "evaluation_criteria": "Explains transactions acquire locks during growing phase and release locks during shrinking phase. Strict 2PL holds exclusive locks until commit/abort to eliminate cascading aborts.",
        "hints": [
            "In basic 2PL, once a transaction releases any lock, it cannot acquire any new locks.",
            "2PL guarantees conflict serializability of concurrent transaction schedules.",
            "Strict 2PL prevents other transactions from reading uncommitted dirty data by holding X-locks until commit."
        ],
        "pressure_followups": ["Can 2PL cause deadlocks, and how does Conservative (Static) 2PL prevent them?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Two-Phase Commit (2PC) Distributed Transactions",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Explain the Two-Phase Commit (2PC) protocol in distributed database systems. What messages are exchanged between the Coordinator and Cohorts during the Prepare and Commit phases, and what happens if the Coordinator crashes mid-commit?",
        "expected_concepts": ["Two-Phase Commit", "distributed transaction", "coordinator", "cohort participants", "prepare phase", "commit phase", "blocking protocol", "coordinator failure"],
        "evaluation_criteria": "Details Prepare phase (VOTE_COMMIT / VOTE_ABORT) and Commit phase (GLOBAL_COMMIT / GLOBAL_ABORT). Explains cohorts block holding resource locks if coordinator crashes after voting yes.",
        "hints": [
            "Phase 1 (Prepare): Coordinator asks all nodes if they are ready to commit; nodes log state and reply.",
            "Phase 2 (Commit): If all voted yes, Coordinator broadcasts GLOBAL_COMMIT; otherwise GLOBAL_ABORT.",
            "2PC is a blocking protocol: cohorts cannot unilaterally commit or abort if the coordinator fails mid-flight."
        ],
        "pressure_followups": ["How does Three-Phase Commit (3PC) or Paxos/Raft consensus overcome the blocking limitation of 2PC?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Buffer Pool Management & Replacement",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "How do database buffer pools manage in-memory cached disk pages? Contrast standard LRU with LRU-K and Clock-Sweep algorithms, and explain how the Buffer Manager flushes dirty pages.",
        "expected_concepts": ["Buffer Pool", "frame table", "pin count", "dirty page", "LRU-K", "clock sweep", "sequential scan flooding"],
        "evaluation_criteria": "Explains page pinning to prevent eviction during active use. Details how LRU-K prevents large sequential table scans from wiping out frequently accessed index pages.",
        "hints": [
            "Buffer pools read fixed-size pages from disk into memory frames.",
            "A pin count prevents a page from being evicted while an execution thread is reading or modifying it.",
            "Standard LRU is vulnerable to sequential flooding where a full table scan evicts all cached hot pages."
        ],
        "pressure_followups": ["What is the Steal/No-Force buffer management policy, and how does it relate to Write-Ahead Logging (WAL)?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "B+ Tree vs Log-Structured Merge (LSM) Trees",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "Compare traditional B+ Tree storage engines (like InnoDB) with Log-Structured Merge (LSM) Tree engines (like RocksDB, Cassandra). What are the write amplification, read amplification, and compaction trade-offs for write-heavy workloads?",
        "expected_concepts": ["B+ Tree", "LSM Tree", "write amplification", "read amplification", "SSTables", "MemTable", "compaction", "sequential vs random I/O"],
        "evaluation_criteria": "Contrasts in-place page updates in B+ Trees (random disk writes) with append-only sequential writes in LSM MemTable and SSTables. Details compaction overhead and Bloom filter read optimization.",
        "hints": [
            "B+ trees modify pages in-place on disk, incurring expensive random I/O and page splits.",
            "LSM trees write to an in-memory MemTable and flush immutable SSTables sequentially to disk.",
            "Reads in LSM trees must search multiple SSTable levels, mitigated by Bloom filters."
        ],
        "pressure_followups": ["What causes write stalls during heavy ingestion in LSM-based databases?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Multi-Version Concurrency Control (MVCC)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain Multi-Version Concurrency Control (MVCC) in modern DBMS engines. How does it allow readers to not block writers and writers to not block readers, and how are undo logs and transaction visibility snapshots used?",
        "expected_concepts": ["MVCC", "non-blocking reads", "undo logs", "xmin and xmax", "transaction snapshot", "vacuuming", "garbage collection"],
        "evaluation_criteria": "Explains modifications create new version records rather than overwriting in place. Readers view a consistent point-in-time snapshot based on active transaction IDs.",
        "hints": [
            "In MVCC, an UPDATE creates a new version of the row with new transaction metadata.",
            "A reader only sees row versions that were committed before its transaction snapshot began.",
            "Background vacuuming cleans up old row versions no longer visible to any active transaction."
        ],
        "pressure_followups": ["What is transaction ID wraparound in PostgreSQL, and why is autovacuum freezing necessary?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "CAP Theorem & PACELC Trade-offs",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Explain the CAP Theorem (Consistency, Availability, Partition Tolerance) and the PACELC extension in distributed database design. Why must a distributed database choose between Consistency and Availability during a network partition?",
        "expected_concepts": ["CAP Theorem", "PACELC", "network partition", "linearizability", "eventual consistency", "latency vs consistency"],
        "evaluation_criteria": "Explains network partitions (P) are unavoidable in distributed hardware, forcing choice between CP (refuse writes to ensure correctness) and AP (accept writes risking split-brain). Details PACELC latency trade-off during normal operations.",
        "hints": [
            "Network partitions can sever communication between data center replicas at any time.",
            "If partitioned: an AP system allows stale reads/writes; a CP system rejects requests to prevent divergence.",
            "PACELC states: If Partition (P), choose Availability (A) or Consistency (C); Else (E), choose Latency (L) or Consistency (C)."
        ],
        "pressure_followups": ["How does Cassandra achieve tunable consistency using quorum formulas (R + W > N)?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },

    # =========================================================================
    # OPERATING SYSTEMS (Domain: Operating Systems) - STRICTLY NO CODING SNIPPETS!
    # =========================================================================
    {
        "domain": "Operating Systems",
        "topic": "Inter-Process Communication (IPC) Mechanisms",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare Inter-Process Communication (IPC) mechanisms in Unix: Anonymous Pipes, Named Pipes (FIFOs), Message Queues, Shared Memory, and Unix Domain Sockets. Which provides the lowest latency and why?",
        "expected_concepts": ["IPC", "shared memory", "Unix domain socket", "anonymous pipes", "FIFOs", "message queues", "zero-copy", "synchronization"],
        "evaluation_criteria": "Details Shared Memory provides highest throughput (zero-copy between process address spaces, requiring semaphores/mutexes). Contrasts kernel-buffered pipes and stream-oriented Unix domain sockets.",
        "hints": [
            "Pipes and sockets require copying data from user space to kernel buffer, then to destination user space.",
            "Shared memory maps the same physical RAM frame into multiple process page tables.",
            "Shared memory requires external synchronization (semaphores) to prevent race conditions."
        ],
        "pressure_followups": ["Why are Unix Domain Sockets significantly faster than TCP loopback sockets (127.0.0.1) on the same host?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "File System Inodes & Directory Structure",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Inode architecture in Unix/Linux file systems (e.g. ext4). What metadata is stored inside an Inode versus a directory entry, and what is the difference between a Hard Link and a Symbolic Link?",
        "expected_concepts": ["inode", "file metadata", "directory entry", "hard link", "symbolic link", "link count", "direct and indirect blocks"],
        "evaluation_criteria": "Explains Inodes store file size, permissions, ownership, timestamps, and block pointers, but NOT file name. Directories map filenames to inode numbers. Hard links share inodes; symlinks store path strings.",
        "hints": [
            "A directory is simply a special file containing a list of (filename, inode_number) pairs.",
            "A hard link creates another directory entry pointing to an existing inode, incrementing the link count.",
            "A symbolic link is a separate file whose data block contains the string path of the target file."
        ],
        "pressure_followups": ["What happens to a file on disk when you call unlink() or rm while another process still has it open in memory?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Fork, Exec & Copy-on-Write (CoW)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How do fork() and exec() system calls spawn processes in Unix? Explain how Copy-on-Write (CoW) optimizes fork() memory allocation, and what happens when either the parent or child writes to memory.",
        "expected_concepts": ["fork()", "exec()", "Copy-on-Write", "page table duplication", "read-only page fault", "PID", "process creation"],
        "evaluation_criteria": "Explains fork() duplicates the parent's page table with pages marked read-only. When either process writes, MMU traps a page fault, duplicating only that specific 4KB page.",
        "hints": [
            "fork() creates an almost exact child clone; exec() replaces the current process image with a new binary.",
            "Without Copy-on-Write, fork() would copy entire gigabytes of RAM only for exec() to discard it immediately.",
            "CoW shares physical pages until a write triggers a hardware trap that duplicates the page on demand."
        ],
        "pressure_followups": ["How does vfork() differ from fork(), and why is executing code other than exec() or _exit() dangerous in vfork()?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Interrupts vs Polling vs Direct Memory Access",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "Compare Programmed I/O (Polling), Interrupt-Driven I/O, and Direct Memory Access (DMA) for hardware device communication. Why is DMA essential for high-throughput network cards and NVMe storage?",
        "expected_concepts": ["DMA", "interrupts", "polling", "CPU offloading", "interrupt handler", "memory bus", "bus mastering"],
        "evaluation_criteria": "Explains polling wastes CPU cycles checking status. Interrupts notify CPU upon data arrival. DMA transfers data blocks directly between device and RAM without CPU intervention per byte.",
        "hints": [
            "Polling burns CPU cycles in busy-wait loops checking device ready bits.",
            "Interrupts allow the CPU to run other threads until hardware asserts an IRQ signal.",
            "DMA controllers transfer large data blocks straight into physical RAM, interrupting the CPU only upon completion."
        ],
        "pressure_followups": ["What is an Interrupt Storm, and how do high-speed network drivers use NAPI to dynamically switch from interrupts to polling under extreme packet load?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "System Calls & Context Switch Overhead",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A high-performance web proxy server handles 100,000 requests/sec. Profiling reveals 40% of CPU time is spent in kernel context switches from small read() and write() system calls. How does sendfile() or io_uring reduce this overhead?",
        "expected_concepts": ["system calls", "context switch", "user space to kernel space", "sendfile", "zero-copy", "io_uring", "submission queue"],
        "evaluation_criteria": "Identifies context switch trap overhead and data copying between user and kernel space. Recommends zero-copy sendfile() or asynchronous kernel ring buffers (io_uring).",
        "hints": [
            "Each system call transitions the CPU from User Mode (Ring 3) to Kernel Mode (Ring 0).",
            "sendfile() transfers file data directly from page cache to socket buffer within kernel space (zero-copy).",
            "io_uring uses shared ring buffers to submit and complete I/O requests without issuing syscall traps per operation."
        ],
        "pressure_followups": ["What hardware security mitigations (like KPTI for Meltdown) increased system call context switch latency?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Memory Fragmentation & Slab Allocators",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "An operating system kernel frequently allocates and deallocates small fixed-size objects (like task_struct and file descriptors). Why does general-purpose buddy allocation suffer from internal/external fragmentation, and how does the Slab Allocator eliminate this overhead?",
        "expected_concepts": ["internal fragmentation", "external fragmentation", "Buddy Allocator", "Slab Allocator", "object caching", "pre-constructed objects"],
        "evaluation_criteria": "Explains Buddy system allocates in powers-of-two page sizes causing internal fragmentation. Slab allocator maintains contiguous caches of pre-constructed fixed-size objects for instant reuse.",
        "hints": [
            "External fragmentation: Total memory is sufficient, but no single contiguous block is large enough.",
            "Internal fragmentation: Allocated memory block is larger than requested data size.",
            "The Slab Allocator pre-allocates pools of initialized objects, bypassing page-level allocation overhead."
        ],
        "pressure_followups": ["What are SLOB and SLUB in Linux, and when is SLUB preferred over standard SLAB?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },

    # =========================================================================
    # COMPUTER NETWORKS (Domain: Computer Networks) - STRICTLY NO CODING SNIPPETS!
    # =========================================================================
    {
        "domain": "Computer Networks",
        "topic": "TLS 1.3 Cryptographic Handshake",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Explain the TLS 1.3 handshake protocol. How was latency reduced from 2 Round-Trip Times (2-RTT) in TLS 1.2 to 1-RTT in TLS 1.3, what is 0-RTT session resumption, and how does Ephemeral Diffie-Hellman guarantee Forward Secrecy?",
        "expected_concepts": ["TLS 1.3", "1-RTT handshake", "0-RTT resumption", "Ephemeral Diffie-Hellman", "Forward Secrecy", "ServerHello", "ClientHello"],
        "evaluation_criteria": "Explains client combines cipher selection with Diffie-Hellman key share in initial ClientHello (1-RTT). Forward secrecy ensures compromise of server private key cannot decrypt historical sessions.",
        "hints": [
            "TLS 1.2 required negotiating cipher suites before exchanging key material, taking 2 full round trips.",
            "TLS 1.3 clients predict the key exchange algorithm and send public key shares in the initial ClientHello.",
            "Forward Secrecy uses ephemeral session keys that are deleted immediately after session termination."
        ],
        "pressure_followups": ["What replay attack vulnerability exists in TLS 1.3 0-RTT data, and how do web applications protect against it?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "NAT, PAT & STUN/TURN Traversal",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "Two peer-to-peer WebRTC clients want to establish direct video streaming, but both reside behind symmetric NAT routers in private subnets. Explain how Port Address Translation (PAT) works, why direct P2P connections fail, and how STUN and TURN servers enable connectivity.",
        "expected_concepts": ["NAT", "PAT", "symmetric NAT", "STUN", "TURN relay", "ICE protocol", "hole punching", "public IP"],
        "evaluation_criteria": "Explains PAT maps private (IP, port) tuples to public router ports. Details STUN discovers public reflex mapping; TURN relays media traffic when symmetric NAT blocks direct hole punching.",
        "hints": [
            "PAT (NAPT) rewrites private IP and port headers to a single public IP with unique outbound port mappings.",
            "STUN allows a client to discover its own public-facing IP and port mapping.",
            "TURN acts as a fallback relay server when strict symmetric NAT firewalls forbid direct peer-to-peer UDP streams."
        ],
        "pressure_followups": ["How does the ICE (Interactive Connectivity Establishment) protocol select between host, server reflexive, and relay candidates?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "BGP Routing & Autonomous Systems",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "How does the Border Gateway Protocol (BGP) route internet traffic between Autonomous Systems (AS)? Contrast Interior Gateway Protocols (like OSPF) with BGP's Path Vector routing, and explain what causes BGP Route Hijacking.",
        "expected_concepts": ["BGP", "Autonomous System", "path vector", "OSPF", "AS-PATH", "BGP route hijacking", "RPKI", "peering vs transit"],
        "evaluation_criteria": "Contrasts link-state intra-AS routing (OSPF) with policy-based inter-AS path-vector routing (BGP). Explains BGP hijacking occurs when a malicious or misconfigured AS announces unauthorized IP prefixes.",
        "hints": [
            "The global Internet is a collection of interconnected Autonomous Systems (ISPs, tech companies, universities).",
            "BGP selects routes based on policy and shortest AS-PATH, not purely physical link speed.",
            "BGP historically trusted route announcements without cryptographic validation, allowing unauthorized prefix hijacking."
        ],
        "pressure_followups": ["How does Resource Public Key Infrastructure (RPKI) use cryptographic Route Origin Authorizations (ROAs) to prevent BGP hijacking?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "WebSockets vs SSE vs Long Polling",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare WebSockets, Server-Sent Events (SSE), and HTTP Long Polling for real-time web applications. What are the protocol overheads, bidirectional capabilities, reconnection semantics, and HTTP/2 compatibility trade-offs?",
        "expected_concepts": ["WebSockets", "Server-Sent Events", "Long Polling", "bidirectional full-duplex", "unidirectional streaming", "HTTP/2 multiplexing", "framing overhead"],
        "evaluation_criteria": "Contrasts full-duplex bidirectional TCP WebSocket framing with unidirectional text-stream SSE (native reconnection, HTTP/2 multiplexing) and wasteful Long Polling connection churn.",
        "hints": [
            "WebSockets upgrade from HTTP to a persistent, bidirectional full-duplex TCP protocol with minimal framing.",
            "SSE uses standard HTTP/1.1 or HTTP/2 to stream text data from server to client with automatic browser reconnection.",
            "Long polling repeatedly opens and closes HTTP connections, generating massive header overhead."
        ],
        "pressure_followups": ["Why can WebSockets experience issues traversing corporate enterprise proxies and firewalls that inspect standard HTTP traffic?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "MTU, Path MTU Discovery & Fragmentation",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "A VPN network tunnel drops large HTTPS packets while small ping requests succeed. Explain Maximum Transmission Unit (MTU), Path MTU Discovery (PMTUD), why IP fragmentation degrades performance, and what causes 'PMTUD Black Holes'.",
        "expected_concepts": ["MTU", "Path MTU Discovery", "IP fragmentation", "DF bit", "ICMP Fragmentation Needed", "PMTUD Black Hole", "MSS clamping"],
        "evaluation_criteria": "Explains standard Ethernet MTU is 1500 bytes; VPN encapsulation adds headers exceeding MTU. If DF (Don't Fragment) bit is set and routers block ICMP Type 3 Code 4 replies, a black hole drops packets silently.",
        "hints": [
            "Standard Ethernet MTU is 1500 bytes; packets exceeding this must be fragmented or rejected.",
            "With the Don't Fragment (DF) bit set, routers drop oversized packets and send back ICMP 'Fragmentation Needed'.",
            "If firewalls block ICMP messages, the sender never learns to reduce packet size, causing a PMTUD Black Hole."
        ],
        "pressure_followups": ["How does TCP MSS Clamping on network routers solve PMTUD black hole issues without requiring client reconfiguration?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },

    # =========================================================================
    # DATA STRUCTURES (Domain: Data Structures)
    # =========================================================================
    {
        "domain": "Data Structures",
        "topic": "Trie (Prefix Tree) Architecture",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How does a Trie (Prefix Tree) data structure work? Analyze its time complexity for insert, search, and startsWith operations with words of length L. How does it compare to a Hash Map for autocomplete search?",
        "expected_concepts": ["Trie", "prefix tree", "O(L) search time", "alphabet array vs map", "autocomplete", "space complexity", "radix tree"],
        "evaluation_criteria": "Explains tree nodes represent character branches sharing common prefixes. O(L) lookup independent of total dictionary size N. Hash maps cannot perform prefix searches in O(L).",
        "hints": [
            "Each Trie node contains an array or map of child character pointers and an isEndOfWord boolean flag.",
            "Words with common prefixes share root-to-node paths, conserving redundant character storage.",
            "Searching a prefix takes O(L) where L is prefix length, making it ideal for predictive text and autocomplete."
        ],
        "pressure_followups": ["What is a Radix Tree (Compressed Trie), and how does edge compression reduce node memory overhead?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Disjoint Set Union (Union-Find)",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Explain the Disjoint Set Union (DSU / Union-Find) data structure. How do Path Compression and Union by Rank (or Size) achieve near-constant amortized time complexity O(alpha(N)) using the Inverse Ackermann function?",
        "expected_concepts": ["Disjoint Set Union", "Union-Find", "path compression", "union by rank", "Inverse Ackermann alpha(N)", "connected components", "Kruskal's algorithm"],
        "evaluation_criteria": "Explains find() flattens tree structure pointing visited nodes directly to root (path compression). Union by rank attaches smaller tree beneath root of larger tree, yielding O(alpha(N)) amortized time.",
        "hints": [
            "DSU maintains disjoint sets with two primary operations: find(x) to identify set representative, and union(x, y) to merge sets.",
            "Path compression flattens the parent tree on each find() call.",
            "Union by rank prevents degenerate linked-list trees by attaching shorter trees to taller trees."
        ],
        "pressure_followups": ["Why is DSU well-suited for Kruskal's Minimum Spanning Tree algorithm and cycle detection in undirected graphs?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Min Stack Implementation in O(1)",
        "difficulty": "Beginner",
        "question_type": "coding",
        "question_text": "Design a Stack class that supports push, pop, top, and retrieving the minimum element in O(1) time complexity.",
        "expected_concepts": ["Min Stack", "auxiliary stack", "O(1) getMin", "paired values", "space-time trade-off"],
        "evaluation_criteria": "Maintains an auxiliary min_stack tracking current minimums, or pushes (value, current_min) tuples onto a single stack in O(1) time.",
        "hints": [
            "A standard stack cannot find its minimum in O(1) without iterating through all elements.",
            "Maintain a second stack that mirrors the first, but only records the minimum value seen up to that depth.",
            "When popping, pop from both stacks simultaneously to keep them synchronized."
        ],
        "pressure_followups": ["Can you implement Min Stack in O(1) time using only a single stack without storing tuples, by pushing 2*val - min?"],
        "code_snippet": None,
        "starter_code": "class MinStack:\n    def __init__(self):\n        # TODO: Initialize stack data structures\n        pass\n\n    def push(self, val: int) -> None:\n        pass\n\n    def pop(self) -> None:\n        pass\n\n    def top(self) -> int:\n        pass\n\n    def getMin(self) -> int:\n        pass",
        "code_language": "python"
    },

    # =========================================================================
    # ALGORITHMS (Domain: Algorithms)
    # =========================================================================
    {
        "domain": "Algorithms",
        "topic": "Binary Search on Answer Space",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the technique of 'Binary Search on the Answer Space'. Under what condition of monotonicity (predicate function f(x)) can binary search be used to find optimal values for problems like 'Koko Eating Bananas' or 'Capacity To Ship Packages Within D Days'?",
        "expected_concepts": ["binary search on answer", "monotonicity", "feasibility function", "lower bound", "search space boundaries", "O(log(Range) * N)"],
        "evaluation_criteria": "Explains if feasibility predicate f(x) produces a monotonic boolean sequence (False...False, True...True), binary search finds the boundary in logarithmic steps over candidate answer space.",
        "hints": [
            "Instead of searching a sorted array, we search across the range of possible answer values [min_ans, max_ans].",
            "A helper function can_ship(capacity) tests if a given capacity is feasible in O(N) time.",
            "If capacity C works, all capacities > C also work; if C fails, all < C fail."
        ],
        "pressure_followups": ["How do you prevent integer overflow when calculating mid = (low + high) // 2 in languages with fixed integer sizes like C++ or Java?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Topological Sort & Cycle Detection",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain Topological Sorting on Directed Acyclic Graphs (DAGs). Compare Kahn's Algorithm (in-degree BFS queue) with DFS post-order reversal. How does Kahn's algorithm detect if a directed graph contains a cycle?",
        "expected_concepts": ["topological sort", "DAG", "Kahn's algorithm", "in-degree", "cycle detection", "dependency resolution", "build order"],
        "evaluation_criteria": "Explains topological ordering lists nodes such that every directed edge u -> v has u before v. Kahn's initializes in-degree queue; if processed nodes count < V, a cycle exists.",
        "hints": [
            "Topological sorting is only valid for Directed Acyclic Graphs (DAGs).",
            "Kahn's algorithm computes in-degrees for all vertices and enqueues vertices with in-degree 0.",
            "If the queue empties before all vertices are visited, the remaining vertices form a cycle."
        ],
        "pressure_followups": ["How is topological sorting used in task scheduling, package package managers (pip/npm), and build systems (Make/Bazel)?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Kadane's Algorithm for Maximum Subarray",
        "difficulty": "Beginner",
        "question_type": "coding",
        "question_text": "Given an integer array nums, write a function that finds the contiguous subarray with the largest sum and returns its sum in O(N) time using Kadane's Algorithm.",
        "expected_concepts": ["Kadane's Algorithm", "maximum subarray", "O(N) time", "O(1) space", "dynamic programming"],
        "evaluation_criteria": "Tracks current_sum = max(num, current_sum + num) and max_sum = max(max_sum, current_sum) in a single O(N) pass with O(1) memory.",
        "hints": [
            "At each element, we decide whether to add it to the existing subarray or start a fresh subarray at this element.",
            "current_sum = max(num, current_sum + num).",
            "Keep a running global maximum of current_sum."
        ],
        "pressure_followups": ["How would you modify Kadane's algorithm to return the starting and ending indices of the maximum subarray?"],
        "code_snippet": None,
        "starter_code": "from typing import List\n\ndef max_sub_array(nums: List[int]) -> int:\n    # TODO: Implement O(N) Kadane's algorithm\n    pass",
        "code_language": "python"
    },

    # =========================================================================
    # HTML/CSS (Domain: HTML/CSS)
    # =========================================================================
    {
        "domain": "HTML/CSS",
        "topic": "CSS Box Model & Border-Box",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain the CSS Box Model (Content, Padding, Border, Margin). How does 'box-sizing: content-box' differ from 'box-sizing: border-box', and why is '* { box-sizing: border-box; }' universally adopted in modern CSS resets?",
        "expected_concepts": ["box model", "content-box", "border-box", "padding", "border", "margin", "rendered width", "CSS reset"],
        "evaluation_criteria": "Explains content-box adds padding and borders to declared width (width + padding + border). border-box includes padding and border within declared width, making layout math predictable.",
        "hints": [
            "In content-box (default), setting width: 100px and padding: 10px results in a total element width of 120px.",
            "In border-box, setting width: 100px keeps the total rendered width at 100px, absorbing padding inside.",
            "border-box prevents elements with 100% width and padding from overflowing their parent containers."
        ],
        "pressure_followups": ["What is Margin Collapsing in CSS, and under what conditions do vertical margins collapse?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "HTML/CSS",
        "topic": "CSS Stacking Context & z-index",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How is a CSS Stacking Context created, and why does setting 'z-index: 9999' sometimes fail to bring an element to the front? List three CSS properties that spawn a new stacking context.",
        "expected_concepts": ["stacking context", "z-index", "position: relative/absolute", "opacity < 1", "transform", "isolation: isolate", "layering order"],
        "evaluation_criteria": "Explains z-index is only evaluated within its local stacking context. Properties spawning stacking context: opacity < 1, transform != none, filter, isolation: isolate, position with z-index != auto.",
        "hints": [
            "z-index only compares elements within the exact same parent stacking context.",
            "If Parent A has a lower stacking order than Parent B, no child of A can ever appear in front of B regardless of z-index.",
            "Modern CSS properties like transform, filter, and opacity < 1 create new stacking contexts."
        ],
        "pressure_followups": ["How does 'isolation: isolate' prevent child elements from accidentally escaping their component boundary?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "HTML/CSS",
        "topic": "Fluid Responsive Layout with Clamp",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write clean CSS rules to implement fluid typography and responsive spacing using clamp(min, val, max), ensuring font sizes scale smoothly between mobile (320px) and desktop (1280px) viewports without media queries.",
        "expected_concepts": ["clamp()", "fluid typography", "viewport units vw", "min font size", "max font size", "media-query-less"],
        "evaluation_criteria": "Uses clamp(min_rem, preferred_vw, max_rem) to establish responsive fluid font scaling smoothly across viewports.",
        "hints": [
            "clamp() accepts three parameters: minimum value, preferred value, and maximum value.",
            "Using viewport units (vw) for the preferred value allows continuous scaling with screen width.",
            "Combining rem with vw (e.g. 1rem + 2vw) preserves user accessibility zoom settings."
        ],
        "pressure_followups": ["Why can using pure viewport units (e.g. font-size: 4vw) violate WCAG accessibility guidelines when users zoom their browser?"],
        "code_snippet": None,
        "starter_code": "/* Write fluid responsive typography rule for h1 */\nh1 {\n  /* TODO: Use clamp for font-size */\n}",
        "code_language": "css"
    },

    # =========================================================================
    # OOP (Domain: OOP)
    # =========================================================================
    {
        "domain": "OOP",
        "topic": "Interface Segregation Principle (ISP)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Interface Segregation Principle (ISP) from SOLID. Why are 'fat interfaces' problematic, and how does splitting large interfaces into role-specific client interfaces prevent tight coupling?",
        "expected_concepts": ["Interface Segregation Principle", "fat interface", "role interface", "unnecessary dependencies", "single responsibility", "interface pollution"],
        "evaluation_criteria": "Explains clients should not be forced to depend on methods they do not use. Shows breaking large monolithic interfaces into smaller, cohesive role interfaces.",
        "hints": [
            "When a class implements a massive interface, it is forced to implement dummy methods for functions it does not need.",
            "Changes to unused methods in a fat interface trigger unnecessary recompilation and testing across all clients.",
            "Small, role-focused interfaces (e.g. Printable, Serializable, Closable) are more reusable and composable."
        ],
        "pressure_followups": ["How does Interface Segregation relate to the Adapter Design Pattern?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Decorator Design Pattern",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "A coffee shop POS application models coffee orders with optional add-ons (Milk, Sugar, Caramel, OatMilk). Using class inheritance leads to an explosion of classes (CoffeeWithMilkAndSugar). How would you refactor this using the Decorator Design Pattern?",
        "expected_concepts": ["Decorator Pattern", "component interface", "concrete decorator", "dynamic composition", "class explosion", "wrapper"],
        "evaluation_criteria": "Defines Beverage interface and Coffee base class. Implements BeverageDecorator that wraps a Beverage reference and augments cost() and getDescription() dynamically at runtime.",
        "hints": [
            "Subclassing every combination of toppings creates an unmanageable class explosion.",
            "The Decorator implements the same interface as the wrapped object and delegates calls to it.",
            "Decorators can be nested arbitrarily at runtime: new Milk(new Caramel(new Coffee()))."
        ],
        "pressure_followups": ["How does Java's I/O Streams library (new BufferedReader(new FileReader())) exemplify the Decorator pattern?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Observer Design Pattern",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Observer Design Pattern. What are the roles of Subject and Observer, how does it promote loose coupling, and what memory leak issue ('Lapsed Listener problem') commonly arises if observers are not unregistered?",
        "expected_concepts": ["Observer Pattern", "Subject", "Observer", "publish-subscribe", "loose coupling", "Lapsed Listener", "weak reference", "unregister"],
        "evaluation_criteria": "Explains Subject maintains a list of Observer listeners and calls update() on state change. Explains strong references in the Subject listener list prevent Observers from being garbage collected.",
        "hints": [
            "The Subject notifies observers without knowing their concrete implementation details.",
            "If an observer registers with a long-lived subject and forgets to unregister, the subject holds a strong reference to it.",
            "This Lapsed Listener problem prevents the observer and its associated view/data from being garbage collected."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },

    # =========================================================================
    # ADDITIONAL DBMS (Domain: DBMS) - Reaching 15
    # =========================================================================
    {
        "domain": "DBMS",
        "topic": "Storage Engine Architecture (InnoDB vs MyISAM)",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare the MySQL storage engines InnoDB and MyISAM. Why does InnoDB support ACID transactions, row-level locking, and foreign keys while MyISAM only supports table-level locking?",
        "expected_concepts": ["InnoDB", "MyISAM", "row-level locking", "table-level locking", "ACID transactions", "clustered index", "crash recovery"],
        "evaluation_criteria": "Contrasts transactional crash-safe InnoDB (clustered B+ tree, redo log) with non-transactional MyISAM (table locks, separate .MYD/.MYI files).",
        "hints": ["InnoDB uses Write-Ahead Logging for crash recovery.", "MyISAM locks the entire table during write operations, causing write bottlenecks.", "InnoDB organizes rows in a primary clustered index."],
        "pressure_followups": ["Why is full-table COUNT(*) faster in MyISAM than in InnoDB under MVCC?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Lock Escalation & Granularity",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "An inventory batch update in a DBMS acquires thousands of individual row locks, causing memory exhaustion in the lock manager until Lock Escalation converts them into an exclusive table lock. How does this impact concurrent transactions?",
        "expected_concepts": ["lock escalation", "lock manager memory", "row lock to table lock", "lock contention", "batch updates", "deadlocks"],
        "evaluation_criteria": "Explains converting fine-grained row locks to coarse table lock frees lock manager memory but blocks all concurrent reads/writes to unrelated rows in the table.",
        "hints": ["Each row lock consumes internal RAM in the database lock table.", "When lock count passes a threshold, the engine escalates to page or table lock.", "Batching updates in smaller chunks avoids triggering lock escalation."],
        "pressure_followups": ["How do Intent Locks (IS, IX) allow the database to detect table-level lock conflicts in O(1)?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Database Replication Architecture",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare Synchronous vs Asynchronous database replication across primary and replica instances. What are the replication lag, data loss risk (RPO), and commit latency trade-offs during network partitions?",
        "expected_concepts": ["synchronous replication", "asynchronous replication", "replication lag", "RPO", "RTO", "failover", "binary log"],
        "evaluation_criteria": "Contrasts synchronous (zero data loss, higher commit latency waiting for replica ACK) with asynchronous (fast primary commits, risk of data loss on failover).",
        "hints": ["Asynchronous replication writes to the binlog and sends events without blocking client commit.", "Synchronous replication waits for at least one replica to write before acknowledging success.", "Semi-synchronous replication balances latency by waiting for replica memory receipt."],
        "pressure_followups": ["What causes Split-Brain in multi-primary replication setups during network splits?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Indexing Strategies (B+ Tree vs Hash Index)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Why do relational DBMS engines default to B+ Tree indexes rather than Hash Indexes for primary and secondary keys? What query operations (range scans, prefix matching, order by) fail on Hash Indexes?",
        "expected_concepts": ["B+ Tree vs Hash Index", "range scan (<, >)", "ORDER BY sorting", "prefix matching", "O(1) equality lookup", "hash collision"],
        "evaluation_criteria": "Explains Hash Indexes offer O(1) equality lookups but cannot support range queries (BETWEEN, >, <), sorted order, or partial prefix lookups because hash functions destroy key ordering.",
        "hints": ["Hash functions scatter keys pseudo-randomly across buckets.", "B+ Trees maintain keys in sorted order at leaf nodes, enabling sequential range traversal.", "Hash indexes only support equality operators (=, IN)."],
        "pressure_followups": ["What is an Adaptive Hash Index in InnoDB, and how does the engine construct it automatically?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },

    # =========================================================================
    # ADDITIONAL COMPUTER NETWORKS (Domain: Computer Networks) - Reaching 15
    # =========================================================================
    {
        "domain": "Computer Networks",
        "topic": "CDN Edge Caching & Anycast Routing",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "A global media platform uses Content Delivery Networks (CDNs) to serve video assets with low latency. Explain how BGP Anycast routes requests to the topologically nearest edge server, how Cache-Control headers (s-maxage, stale-while-revalidate) control eviction, and what causes cache stampedes.",
        "expected_concepts": ["CDN", "Anycast routing", "BGP", "edge cache", "stale-while-revalidate", "cache stampede", "origin shield"],
        "evaluation_criteria": "Explains multiple CDN points-of-presence advertise identical IP via BGP Anycast. Details stale-while-revalidate serving cached content while asynchronously refreshing origin, preventing thundering herd stampedes.",
        "hints": ["Anycast assigns the same IP address to servers in multiple geographic locations.", "BGP routes client packets to the nearest Point of Presence (PoP).", "A cache stampede occurs when an expired popular asset causes thousands of concurrent requests to hammer the origin database."],
        "pressure_followups": ["How does Origin Shielding protect central origin infrastructure from multi-PoP cache misses?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },

    # =========================================================================
    # ADDITIONAL DATA STRUCTURES (Domain: Data Structures) - Reaching 15
    # =========================================================================
    {
        "domain": "Data Structures",
        "topic": "Hash Table Collision Strategies",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare Separate Chaining with Open Addressing (Linear Probing, Quadratic Probing, Double Hashing) for hash table collision resolution. How does load factor threshold affect clustering and cache locality in each?",
        "expected_concepts": ["Separate Chaining", "Open Addressing", "Linear Probing", "primary clustering", "load factor", "cache locality", "tombstones"],
        "evaluation_criteria": "Contrasts chaining (linked lists, robust under high load factor, pointer overhead) with open addressing (contiguous array, great cache locality, primary clustering with linear probing, tombstones for deletion).",
        "hints": ["Separate chaining stores collided keys in linked lists or balanced trees at each bucket.", "Linear probing places collided keys in the next open array slot, causing primary clustering clusters.", "Open addressing degrades rapidly when load factor exceeds 0.7."],
        "pressure_followups": ["Why is Robin Hood Hashing effective at minimizing variance in probe sequence lengths?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Binary Heap Array Representation",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain how a Binary Min-Heap is represented using a 1D array. Derive the index formulas for a node's parent, left child, and right child for 0-indexed arrays, and analyze the time complexity of heapify, push, and pop.",
        "expected_concepts": ["Binary Heap", "array indexing", "parent (i-1)//2", "left child 2i+1", "right child 2i+2", "heapify O(N)", "push/pop O(log N)"],
        "evaluation_criteria": "Derives parent=(i-1)//2, left=2*i+1, right=2*i+2. Explains build-heap running in O(N) linear time using sift-down operations rather than O(N log N).",
        "hints": ["Complete binary trees can be packed densely into arrays without child pointers.", "Sift-up restores heap invariant during insertion (push).", "Sift-down restores heap invariant during extraction of root (pop)."],
        "pressure_followups": ["Why is building a heap from an unsorted array O(N) rather than O(N log N)?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Circular Queue Array Implementation",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Design a Circular Queue using a fixed-size array supporting enQueue, deQueue, Front, Rear, isEmpty, and isFull in O(1) time.",
        "expected_concepts": ["Circular Queue", "modulo arithmetic", "head and tail pointers", "isFull", "isEmpty", "O(1) operations"],
        "evaluation_criteria": "Maintains front and count or rear pointers with (index + 1) % capacity. Correctly distinguishes full from empty without allocating extra memory.",
        "hints": ["Use an array of fixed capacity k.", "Keep track of head index and current element count.", "tail = (head + count - 1) % k."],
        "pressure_followups": ["How does a circular queue prevent memory waste compared to a standard array-based queue?"],
        "code_snippet": None,
        "starter_code": "class MyCircularQueue:\n    def __init__(self, k: int):\n        # TODO: Initialize circular queue\n        pass\n\n    def enQueue(self, value: int) -> bool:\n        pass\n\n    def deQueue(self) -> bool:\n        pass\n\n    def Front(self) -> int:\n        pass\n\n    def Rear(self) -> int:\n        pass\n\n    def isEmpty(self) -> bool:\n        pass\n\n    def isFull(self) -> bool:\n        pass",
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Skip List Architecture",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "How does a Skip List achieve O(log N) average time complexity for search, insertion, and deletion using probabilistic height levels? When is a Skip List preferred over Red-Black trees in concurrent databases (like Redis sorted sets)?",
        "expected_concepts": ["Skip List", "probabilistic level", "express lanes", "O(log N)", "concurrent lock-free", "Redis zset", "pointer forward array"],
        "evaluation_criteria": "Explains multi-level linked lists where nodes have probabilistic forward pointers. Contrasts simpler lock-free concurrent updates in skip lists with complex tree rotation rebalancing locks.",
        "hints": ["A Skip List builds hierarchical linked list layers where higher layers skip over multiple elements.", "Node height is determined by a coin-toss geometric distribution.", "Lock-free skip lists only require CAS operations on node pointers, avoiding tree rotation locks."],
        "pressure_followups": ["What is the memory overhead of forward pointer arrays in a Skip List compared to a Red-Black tree?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Monotonic Queue for Sliding Window Maximum",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "You are processing real-time stock prices and must maintain the maximum price in a sliding window of size K as new prices stream in. Explain how a Monotonic Deque provides O(N) total processing time compared to an O(N log K) heap.",
        "expected_concepts": ["Monotonic Queue", "deque", "sliding window maximum", "O(N) total time", "amortized O(1)", "decreasing deque"],
        "evaluation_criteria": "Maintains deque storing indices in decreasing order of values. Pops elements smaller than incoming price from back, pops expired indices from front. Each element enters and leaves deque at most once.",
        "hints": ["A heap takes O(log K) to extract and clean up stale window elements.", "A monotonic deque preserves candidate maximums in descending order.", "Because every index is pushed and popped at most once, total time across all N elements is O(N)."],
        "pressure_followups": ["Why can't a standard queue find the maximum in O(1)?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },

    # =========================================================================
    # ADDITIONAL ALGORITHMS (Domain: Algorithms) - Reaching 15
    # =========================================================================
    {
        "domain": "Algorithms",
        "topic": "Backtracking with Pruning (N-Queens)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Backtracking paradigm. Using the N-Queens problem, how does state-space tree traversal explore candidates, and how do pruning checks (column, major diagonal, minor diagonal sets) prevent exponential dead-end exploration?",
        "expected_concepts": ["backtracking", "state-space tree", "pruning", "N-Queens", "diagonal constraint", "depth-first search", "constraint satisfaction"],
        "evaluation_criteria": "Explains recursive exploration placing one queen per row. Details O(1) pruning using sets for cols, diagonals (r - c), and anti-diagonals (r + c) to abandon invalid branches early.",
        "hints": ["Backtracking builds candidate solutions incrementally and abandons branches as soon as constraints are violated.", "Major diagonals have constant (row - col); minor diagonals have constant (row + col).", "Pruning cuts off massive subtrees of invalid placements."],
        "pressure_followups": ["How does bitmask optimization speed up N-Queens state tracking by replacing sets with integer bit operations?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Greedy Choice Property (Interval Scheduling)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "What are the two core requirements for a Greedy Algorithm: Greedy Choice Property and Optimal Substructure? Prove why sorting by earliest finish time solves the Interval Scheduling (Activity Selection) problem optimally.",
        "expected_concepts": ["greedy algorithm", "greedy choice property", "optimal substructure", "interval scheduling", "earliest finish time", "exchange argument proof"],
        "evaluation_criteria": "Explains greedy choice selects locally optimal choice leading to global optimum. Proves earliest finish time leaves maximal remaining time for subsequent non-overlapping intervals (exchange argument).",
        "hints": ["Greedy algorithms make the best local decision at each step without revisiting past choices.", "Picking the activity with earliest start time or shortest duration can fail catastrophically.", "Selecting earliest finish time preserves the maximum possible future window."],
        "pressure_followups": ["Why does the 0/1 Knapsack problem fail with a greedy approach while Fractional Knapsack succeeds?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Breadth-First Search vs Depth-First Search",
        "difficulty": "Beginner",
        "question_type": "tradeoff",
        "question_text": "Compare Breadth-First Search (BFS) and Depth-First Search (DFS) on graphs. What are their queue versus stack mechanisms, memory footprints, and suitability for finding unweighted shortest paths versus topological sorting?",
        "expected_concepts": ["BFS vs DFS", "queue vs stack", "shortest path in unweighted graphs", "space complexity O(V) vs O(depth)", "visited set", "bipartite testing"],
        "evaluation_criteria": "Details BFS explores level-by-level using a Queue (guaranteeing shortest path on unweighted graphs, memory proportional to frontier width). DFS explores branches using Stack/recursion (memory proportional to depth, ideal for cycle detection/topo sort).",
        "hints": ["BFS guarantees first visit to a node is the shortest distance in an unweighted graph.", "DFS can consume O(depth) stack space, which is O(V) in worst-case skewed trees.", "BFS can consume massive memory storing the widest layer of the graph."],
        "pressure_followups": ["What is Iterative Deepening DFS (IDDFS), and how does it combine BFS shortest-path optimality with DFS linear memory efficiency?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Quickselect Kth Largest Element",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement the Quickselect algorithm to find the Kth largest element in an unsorted array in O(N) average time complexity without sorting the entire array.",
        "expected_concepts": ["Quickselect", "partition algorithm", "pivot", "average O(N)", "worst case O(N^2)", "divide and conquer"],
        "evaluation_criteria": "Uses Lomuto or Hoare partition. Recurses only into the single partition containing index N - k, achieving recurrence T(N) = T(N/2) + O(N) = O(N) average time.",
        "hints": ["Partition the array around a pivot like Quicksort.", "If pivot index equals target, return nums[pivot].", "Unlike Quicksort, Quickselect only recurses into one half of the partition."],
        "pressure_followups": ["How does the Median-of-Medians algorithm guarantee O(N) worst-case time complexity for Quickselect?"],
        "code_snippet": None,
        "starter_code": "from typing import List\n\ndef find_kth_largest(nums: List[int], k: int) -> int:\n    # TODO: Implement O(N) average Quickselect\n    pass",
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "String Pattern Matching (KMP Algorithm)",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "Compare Naive string matching (O(N*M)) with the Knuth-Morris-Pratt (KMP) algorithm (O(N+M)). How does the Longest Prefix Suffix (LPS) table prevent backtracking the main text pointer upon a mismatch?",
        "expected_concepts": ["KMP algorithm", "LPS array", "prefix function", "no text backtracking", "O(N + M) time", "finite state automaton"],
        "evaluation_criteria": "Explains LPS table stores length of longest proper prefix that is also suffix for pattern[0..i]. On mismatch, text pointer advances while pattern pointer shifts to lps[j-1] without re-reading text characters.",
        "hints": ["Naive matching resets text pointer back to i - j + 1 on mismatch.", "KMP precomputes the pattern's self-similarity in an LPS table.", "The text pointer never moves backward in KMP."],
        "pressure_followups": ["How does the Boyer-Moore algorithm achieve sublinear search time O(N/M) in best-case scenarios by searching from right to left?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Graph Cycle Detection (3-Color DFS)",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a function 'can_finish_courses' that takes numCourses and a list of prerequisites [course, prereq] and returns True if all courses can be finished (no cyclic dependency), using 3-color DFS (WHITE, GRAY, BLACK).",
        "expected_concepts": ["cycle detection", "3-color DFS", "WHITE unvisited", "GRAY visiting", "BLACK visited", "back-edge"],
        "evaluation_criteria": "Builds adjacency list. Marks nodes GRAY during current DFS recursion stack; encountering a GRAY node indicates a back-edge cycle. Marks BLACK upon completion.",
        "hints": ["Build a directed adjacency graph where prereq -> course.", "0 = unvisited (white), 1 = visiting in current path (gray), 2 = completely visited (black).", "If DFS encounters a node currently marked 1 (gray), a cycle exists."],
        "pressure_followups": ["What is the difference between an undirected graph cycle check and a directed graph cycle check?"],
        "code_snippet": None,
        "starter_code": "from typing import List\n\ndef can_finish_courses(numCourses: int, prerequisites: List[List[int]]) -> bool:\n    # TODO: Detect directed cycle with 3-color DFS\n    pass",
        "code_language": "python"
    },

    # =========================================================================
    # ADDITIONAL HTML/CSS (Domain: HTML/CSS) - Reaching 15
    # =========================================================================
    {
        "domain": "HTML/CSS",
        "topic": "CSS Transitions vs Animations vs Web Animations API",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare CSS Transitions, CSS Keyframe Animations (@keyframes), and the Web Animations API (WAAPI). Which CSS properties animate on the GPU compositor thread without triggering layout reflows or repaints?",
        "expected_concepts": ["CSS transitions", "@keyframes", "Web Animations API", "GPU compositor thread", "transform", "opacity", "will-change", "reflow"],
        "evaluation_criteria": "Details transitions for state-change interpolation, keyframes for complex multi-step sequences, WAAPI for programmatic JS control. Explains transform and opacity run on GPU compositor without layout reflows.",
        "hints": ["Animating width, height, or top/left triggers expensive layout reflows on the CPU.", "Animating transform (translate, scale, rotate) and opacity bypasses layout and repaint.", "The will-change property prompts the browser to promote elements to dedicated GPU render layers."],
        "pressure_followups": ["What memory risk occurs when overusing 'will-change: transform' across hundreds of elements?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "HTML/CSS",
        "topic": "Semantic HTML & ARIA Accessibility",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Why is Semantic HTML preferred over generic <div> and <span> tags for web accessibility and SEO? How do ARIA roles, states (aria-expanded, aria-hidden), and live regions assist screen readers when custom interactive components are built?",
        "expected_concepts": ["Semantic HTML", "accessibility (a11y)", "screen readers", "ARIA roles", "aria-expanded", "aria-live", "keyboard focusable tabIndex"],
        "evaluation_criteria": "Explains semantic tags (<header>, <nav>, <main>, <button>) provide built-in keyboard navigation, roles, and focusability. ARIA bridges gaps for custom widgets without overriding native semantics unnecessarily.",
        "hints": ["Native <button> has keyboard Enter/Space triggers and focusability for free; a <div onclick> has neither.", "The First Rule of ARIA: Do not use ARIA if a native HTML element already exists with that behavior.", "aria-live informs screen readers when dynamic content changes asynchronously without page refresh."],
        "pressure_followups": ["What is the difference between 'aria-live=\"polite\"' and 'aria-live=\"assertive\"'?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "html"
    },
    {
        "domain": "HTML/CSS",
        "topic": "CSS Custom Properties (Variables) Scoping",
        "difficulty": "Beginner",
        "question_type": "scenario",
        "question_text": "How do CSS Custom Properties (--variable) work? Explain variable scoping, inheritance down the DOM tree, fallback values, and how custom properties enable clean Dark Mode toggling with data attributes compared to SASS/SCSS variables.",
        "expected_concepts": ["CSS custom properties", "CSS variables", "var() with fallback", ":root scope", "dark mode theming", "dynamic runtime update", "CSS vs preprocessor"],
        "evaluation_criteria": "Contrasts preprocessor variables (static compile-time substitution) with CSS variables (live runtime DOM inheritance, inspectable in DevTools, responsive to media queries and JS).",
        "hints": ["--main-color declared on :root is available globally across all elements.", "CSS variables cascade down the DOM hierarchy and can be overridden locally in child components.", "JavaScript can dynamically update variables using element.style.setProperty()."],
        "pressure_followups": ["How does @media (prefers-color-scheme: dark) automatically trigger CSS custom property theme swaps?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "HTML/CSS",
        "topic": "Shadow DOM & Web Components Encapsulation",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "Explain Web Components and the Shadow DOM. How does the Shadow Root achieve style encapsulation preventing global CSS leaks, and what are the trade-offs regarding accessibility and CSS theming with ::part() and CSS variables?",
        "expected_concepts": ["Shadow DOM", "Web Components", "custom elements", "style encapsulation", "::part() selector", "closed vs open shadow root", "slotted content"],
        "evaluation_criteria": "Explains Shadow DOM isolates component DOM tree and scoped stylesheets from global document. Global CSS cannot pierce shadow boundary unless exposed via custom properties or ::part().",
        "hints": ["Global CSS styles do not cascade into a Shadow Root.", "Styles defined inside a Shadow Root do not leak out into the host page.", "The ::part() pseudo-element allows component authors to expose specific styled sub-elements safely."],
        "pressure_followups": ["What is the difference between 'attachShadow({mode: \"open\"})' and 'attachShadow({mode: \"closed\"})'?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "HTML/CSS",
        "topic": "Responsive Card Grid Layout",
        "difficulty": "Beginner",
        "question_type": "coding",
        "question_text": "Write a clean CSS layout for a responsive product card grid that automatically wraps cards into columns of at least 280px width, fills available horizontal space, and maintains equal card heights with 24px gaps.",
        "expected_concepts": ["CSS Grid", "display: grid", "repeat()", "auto-fit", "minmax(280px, 1fr)", "gap", "equal height cards"],
        "evaluation_criteria": "Uses display: grid, grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)), gap: 24px, achieving fully responsive wrapping without media queries.",
        "hints": ["CSS Grid grid-template-columns controls column generation.", "repeat(auto-fit, minmax(280px, 1fr)) creates flexible columns that wrap as viewport resizes.", "Grid cells automatically stretch items to equal height along the cross axis."],
        "pressure_followups": ["How do you ensure card footers stick to the bottom of cards of varying content height using flexbox inside each card?"],
        "code_snippet": None,
        "starter_code": ".card-grid {\n  /* TODO: Implement responsive grid with minmax and auto-fit */\n}",
        "code_language": "css"
    },

    # =========================================================================
    # ADDITIONAL OOP (Domain: OOP) - Reaching 15
    # =========================================================================
    {
        "domain": "OOP",
        "topic": "Dependency Inversion Principle (DIP)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Dependency Inversion Principle (DIP) in SOLID. What does 'High-level modules should not depend on low-level modules; both should depend on abstractions' mean in enterprise software architecture, and how does Inversion of Control (IoC) relate to it?",
        "expected_concepts": ["Dependency Inversion Principle", "Inversion of Control", "abstractions over concretions", "loose coupling", "Dependency Injection", "testability"],
        "evaluation_criteria": "Explains DIP reverses standard dependency flow so business logic depends on interfaces rather than concrete infrastructure (database, API clients). Enables mocking and independent deployment.",
        "hints": ["Without DIP, a UserService class directly instantiates a MySQLDatabase class (tight coupling).", "With DIP, UserService depends on an abstract UserRepository interface.", "Inversion of Control (IoC) delegates object creation and lifecycle management to a container."],
        "pressure_followups": ["What is the difference between Constructor Injection, Setter Injection, and Interface Injection?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Template Method vs Strategy Pattern",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare the Template Method Pattern with the Strategy Pattern. How does Template Method rely on inheritance and the 'Hollywood Principle' (Don't call us, we'll call you) while Strategy relies on composition, and what are their runtime flexibility differences?",
        "expected_concepts": ["Template Method", "Strategy Pattern", "inheritance vs composition", "Hollywood Principle", "algorithm skeleton", "runtime swapping"],
        "evaluation_criteria": "Contrasts compile-time subclass algorithm customization (Template Method defines invariant skeleton with abstract hook steps) with runtime interchangeable object delegation (Strategy Pattern).",
        "hints": ["Template method fixes the algorithm steps in a base class and lets subclasses override specific hook methods.", "Strategy encapsulates an entire algorithm in a separate object passed via composition.", "Strategy algorithms can be swapped dynamically at runtime; Template Method is fixed at compile-time."],
        "pressure_followups": ["When does the Template Method pattern lead to fragile base class syndrome?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Immutable Value Objects vs Entities",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "In Domain-Driven Design (DDD) and object-oriented architecture, contrast an Entity with a Value Object. Why should Value Objects (like Money, Email, Address) be immutable, and how do they determine equality compared to Entities?",
        "expected_concepts": ["Entity", "Value Object", "immutability", "identity vs attribute equality", "Domain-Driven Design", "side-effect free functions"],
        "evaluation_criteria": "Explains Entities have persistent unique identity (ID) across state changes. Value Objects have no identity and are defined purely by their attributes; two Value Objects with identical attributes are equal. Immutability prevents shared mutation bugs.",
        "hints": ["A User is an Entity because two users with the same name are distinct people.", "Money($100, USD) is a Value Object because any two $100 bills are interchangeable.", "Value Objects should override equals() and hashCode() based entirely on their fields."],
        "pressure_followups": ["How do Java Records or Python frozen dataclasses simplify implementing Value Objects?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Command Pattern for Undoable Actions",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement the Command Design Pattern in Java (or Python) to model an undoable Text Editor operation with an execute() and undo() method and a CommandHistory manager.",
        "expected_concepts": ["Command Pattern", "execute", "undo", "CommandHistory stack", "Invoker", "Receiver", "decoupling"],
        "evaluation_criteria": "Defines Command interface with execute() and undo(). Concrete commands capture receiver state prior to mutation. Command history manages undo stack.",
        "hints": ["The Command encapsulates a request as a standalone object containing all information to perform and reverse the action.", "CommandHistory pushes executed commands onto an undo stack.", "Calling undo() pops the last command and invokes command.undo()."],
        "pressure_followups": ["How does the Memento Pattern differ from the Command Pattern for undo implementations?"],
        "code_snippet": None,
        "starter_code": "interface Command {\n    void execute();\n    void undo();\n}\n\n// TODO: Implement concrete command and CommandHistory manager",
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Anti-Patterns: God Object & Anemic Model",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Describe two prevalent OOP anti-patterns: The 'God Object' (Blob) and the 'Anemic Domain Model'. Why do they violate encapsulation, and how do you refactor them into cohesive, rich domain models?",
        "expected_concepts": ["God Object", "Anemic Domain Model", "cohesion", "encapsulation", "data with behavior", "feature envy", "rich domain model"],
        "evaluation_criteria": "Explains God Object aggregates too many responsibilities (low cohesion, tight coupling). Anemic model separates data (getters/setters only) from business logic (procedural service scripts), abandoning encapsulation.",
        "hints": ["A God Object knows too much and does too much, becoming an unmaintainable bottleneck.", "An Anemic Domain Model uses classes as dumb data holders while logic sits in external service classes.", "Rich domain models place business validation and state transitions directly inside the domain classes."],
        "pressure_followups": ["How does the 'Tell, Don't Ask' principle prevent anemic domain models?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    }
]
