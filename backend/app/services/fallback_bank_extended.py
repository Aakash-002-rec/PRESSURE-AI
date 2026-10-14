from typing import Dict, List, Any

# Extended curated fallback questions to ensure 15+ distinct questions per domain
# and complete coverage of conceptual, scenario, coding/practical, and tradeoff questions.
EXTENDED_FALLBACK_QUESTIONS: List[Dict[str, Any]] = [
    # =========================================================================
    # PYTHON (Domain: Python)
    # =========================================================================
    {
        "domain": "Python",
        "topic": "Decorators & Wrappers",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "In Python, explain how function decorators work using first-class functions and closures. Why is functools.wraps essential when writing custom decorators?",
        "expected_concepts": ["first-class functions", "closure", "wrapper function", "functools.wraps", "metadata preservation", "__name__", "__doc__"],
        "evaluation_criteria": "Explains that decorators accept a callable and return a wrapper callable. Mentions functools.wraps preserves function docstrings and names.",
        "hints": [
            "Functions in Python can be passed as arguments, assigned to variables, and returned from other functions.",
            "A decorator wraps the original function inside a closure.",
            "Without @functools.wraps, introspection tools see the wrapper's name instead of the original function's name."
        ],
        "pressure_followups": [
            "How do you implement a decorator that accepts arbitrary arguments like @repeat(num_times=3), and how does the extra nesting layer work?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Generators & Iterators",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain how Python generators and the yield keyword work. How do they differ from standard functions and list comprehensions in terms of memory utilization and evaluation timing?",
        "expected_concepts": ["yield", "iterator protocol", "__iter__", "__next__", "lazy evaluation", "generator object", "StopIteration", "memory efficiency"],
        "evaluation_criteria": "Explains lazy evaluation, generator state suspension, and minimal memory footprint compared to eager list allocation.",
        "hints": [
            "Functions with 'yield' return a generator object rather than running immediately to completion.",
            "Each call to next() resumes execution right after the last yield statement.",
            "Generators compute items on demand without storing the full sequence in RAM."
        ],
        "pressure_followups": [
            "How does 'yield from' delegate to a subgenerator, and how does send() pass values back into an active generator?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Memory Management & Garbage Collection",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "How does CPython manage memory? Contrast reference counting with the generational cyclic garbage collector, and explain what triggers cyclic GC runs.",
        "expected_concepts": ["reference counting", "cyclic garbage collection", "gc module", "generations 0 1 2", "circular reference", "ob_refcnt", "memory deallocation"],
        "evaluation_criteria": "Differentiates immediate deallocation via reference count reaching 0 from periodic generational cycle detection for self-referencing graphs.",
        "hints": [
            "CPython tracks an internal ob_refcnt counter on every PyObject.",
            "Reference counting alone cannot free objects that reference each other in a closed loop.",
            "The cyclic GC categorizes objects into three generations based on survival duration."
        ],
        "pressure_followups": [
            "Why did __del__ methods historically cause issues for CPython's cyclic garbage collector, and how was this addressed in Python 3.4+ PEP 442?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Global Interpreter Lock (GIL)",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "What is the Global Interpreter Lock (GIL) in CPython, why was it implemented, and what are the trade-offs between threading, multiprocessing, and asyncio for CPU-bound vs I/O-bound workloads?",
        "expected_concepts": ["GIL", "CPython thread safety", "CPU-bound", "I/O-bound", "multiprocessing", "threading", "asyncio", "memory isolation"],
        "evaluation_criteria": "Explains GIL prevents simultaneous bytecode execution across threads. Compares process memory overhead with thread concurrency for I/O vs CPU tasks.",
        "hints": [
            "The GIL protects CPython memory management and C extensions from race conditions.",
            "Threads release the GIL during I/O operations but contend for it during intensive CPU calculations.",
            "Multiprocessing sidesteps the GIL by spawning isolated Python interpreter processes."
        ],
        "pressure_followups": [
            "What architectural changes are involved in the Python 3.13 free-threaded build (PEP 703) to remove the GIL?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Context Managers & Resource Cleanup",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "You are building a database client in Python that must guarantee connections are returned to a pool even if an unexpected exception occurs. How would you design a custom context manager using both class methods (__enter__/__exit__) and contextlib.contextmanager?",
        "expected_concepts": ["context manager", "__enter__", "__exit__", "contextlib.contextmanager", "resource cleanup", "exception suppression", "with statement"],
        "evaluation_criteria": "Describes __enter__ acquiring and returning resource, __exit__ handling exc_type/exc_val/exc_tb, or using try/finally in a generator with contextlib.",
        "hints": [
            "The 'with' statement guarantees execution of cleanup logic regardless of raised errors.",
            "__exit__ receives exception details and can suppress them by returning True.",
            "@contextmanager allows using yield inside a try...finally block."
        ],
        "pressure_followups": [
            "If an unhandled exception occurs inside __enter__, does __exit__ execute? How should setup failures be handled?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Dunder Methods & Object Model",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "A backend service needs an immutable Vector2D class in Python that supports addition (+), equality checks (==), hashing for set/dict keys, and readable string representations. How should this be implemented using Python dunder methods?",
        "expected_concepts": ["__init__", "__add__", "__eq__", "__hash__", "__repr__", "__str__", "immutability", "slots"],
        "evaluation_criteria": "Details __add__, __eq__, __hash__, and notes that defining __eq__ without __hash__ makes objects unhashable unless explicitly defined.",
        "hints": [
            "Operator overloading maps + to __add__ and == to __eq__.",
            "If __eq__ is overridden, Python automatically sets __hash__ = None unless defined.",
            "Using __slots__ or frozen dataclasses reinforces immutability and reduces memory."
        ],
        "pressure_followups": [
            "Why must objects that implement __hash__ ensure their hash value remains constant throughout their lifetime?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Asynchronous Programming with AsyncIO",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A microservice written with Python's asyncio experiences freezing and high latency because a third-party library performs synchronous disk file writes inside an async route. How would you diagnose and resolve this blocking call without rewriting the third-party library?",
        "expected_concepts": ["event loop blocking", "asyncio.to_thread", "run_in_executor", "ThreadPoolExecutor", "cooperative multitasking", "await"],
        "evaluation_criteria": "Identifies that synchronous blocking operations halt the entire asyncio event loop. Proposes asyncio.to_thread or run_in_executor to offload work.",
        "hints": [
            "The asyncio event loop runs on a single thread and depends on coroutines yielding control.",
            "Any synchronous time.sleep or disk I/O blocks all concurrent tasks on that thread.",
            "asyncio.to_thread delegates blocking code to an underlying thread pool."
        ],
        "pressure_followups": [
            "What happens if an exception is raised inside the thread delegated by asyncio.to_thread? How does the event loop catch it?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Rate Limiting Decorator",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a Python decorator 'rate_limit' that restricts a function to at most N calls per minute. If the limit is exceeded, it should raise a RuntimeError.",
        "expected_concepts": ["decorator", "closure", "time.time", "collections.deque", "sliding window", "functools.wraps"],
        "evaluation_criteria": "Implements parameterized decorator tracking call timestamps in a sliding window using deque or list, pruning calls older than 60 seconds.",
        "hints": [
            "The outer decorator function should accept max_calls, returning the actual decorator.",
            "Store a list or deque of invocation timestamps in the closure.",
            "Before each invocation, filter out timestamps older than current_time - 60."
        ],
        "pressure_followups": [
            "How would you make this decorator thread-safe when multiple worker threads execute the wrapped function simultaneously?"
        ],
        "code_snippet": None,
        "starter_code": "import time\nfrom functools import wraps\n\ndef rate_limit(max_per_minute: int):\n    def decorator(func):\n        # TODO: Implement sliding window rate limit\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            pass\n        return wrapper\n    return decorator",
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Log Stream Deduplication Generator",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a Python generator function 'deduplicate_stream' that takes an iterable of log messages and yields only unique messages in order of arrival, using bounded memory by retaining at most the last K seen message hashes.",
        "expected_concepts": ["generator", "yield", "hash", "collections.deque", "set lookup", "bounded memory"],
        "evaluation_criteria": "Uses a generator with yield, tracking recent seen items with an OrderedDict or combination of set and deque with maxlen=K.",
        "hints": [
            "Iterate through the incoming stream one element at a time.",
            "Maintain a set of recent message hashes for O(1) lookup.",
            "Maintain a deque with maxlen=K to evict the oldest hashes when full."
        ],
        "pressure_followups": [
            "What is the time complexity of set lookup versus deque membership check, and why is combining both necessary?"
        ],
        "code_snippet": None,
        "starter_code": "from typing import Iterable, Iterator\nfrom collections import deque\n\ndef deduplicate_stream(stream: Iterable[str], window_size: int = 1000) -> Iterator[str]:\n    # TODO: Yield unique items within recent window\n    pass",
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Mutable Default Arguments",
        "difficulty": "Beginner",
        "question_type": "tradeoff",
        "question_text": "What is the common bug associated with mutable default arguments (such as def append_to(element, target=[])) in Python, why does it occur at the interpreter level, and what is the idiomatic fix?",
        "expected_concepts": ["mutable default argument", "function definition time", "persistent state", "target=None sentinel", "id()"],
        "evaluation_criteria": "Explains default arguments are evaluated once when the function definition is executed, so all invocations share the same list instance. Idiomatic fix uses None as sentinel.",
        "hints": [
            "Python evaluates default argument expressions once when the def statement is executed.",
            "The default list is bound to the function object's __defaults__ attribute.",
            "Use 'target=None' and initialize 'if target is None: target = []' inside the function."
        ],
        "pressure_followups": [
            "Can you think of a rare case where a mutable default argument is used intentionally as an optimization?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },

    # =========================================================================
    # JAVASCRIPT (Domain: JavaScript)
    # =========================================================================
    {
        "domain": "JavaScript",
        "topic": "Event Loop & Microtasks",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain how the JavaScript runtime executes asynchronous operations. Compare the Call Stack, Macrotask Queue (Callback Queue), and Microtask Queue. In what order are Promise callbacks, setTimeout callbacks, and synchronous code processed?",
        "expected_concepts": ["call stack", "event loop", "microtask queue", "macrotask queue", "Promise.then", "setTimeout", "run to completion", "execution order"],
        "evaluation_criteria": "Explains call stack runs synchronous code first. All pending microtasks (Promises, queueMicrotask) drain before the event loop picks the next macrotask (setTimeout).",
        "hints": [
            "JavaScript is single-threaded; only one piece of code executes on the Call Stack at a time.",
            "Microtasks (Promise reactions) have higher priority than macrotasks (timers, I/O).",
            "The microtask queue must be completely emptied before the engine proceeds to rendering or the next timer."
        ],
        "pressure_followups": [
            "What happens to the UI and browser responsiveness if a microtask recursively enqueues more microtasks using queueMicrotask?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Closures & Lexical Scope",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "What is a closure in JavaScript, how does lexical scoping make it possible, and how can closures be used to create private state and encapsulate variables?",
        "expected_concepts": ["closure", "lexical scope", "lexical environment", "scope chain", "outer function scope", "variable retention", "private state"],
        "evaluation_criteria": "Explains inner function retains access to outer variables even after the outer function has returned. Demonstrates factory pattern or module pattern.",
        "hints": [
            "Lexical scoping means scope is determined by the physical placement of variables and functions in source code.",
            "A closure bundles a function together with its referencing environment.",
            "Variables inside the outer function cannot be directly modified from the global scope unless exposed via methods."
        ],
        "pressure_followups": [
            "How can closures inadvertently cause memory leaks in single-page applications when holding references to large objects or DOM nodes?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Prototypes & Prototypal Inheritance",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain prototypal inheritance in JavaScript. How does the prototype chain work, what is the difference between prototype and __proto__, and how does ES6 class syntax map to it under the hood?",
        "expected_concepts": ["prototype", "__proto__", "prototype chain", "Object.create", "constructor function", "property lookup", "syntactic sugar"],
        "evaluation_criteria": "Explains property lookup traverses up __proto__ links until null. Explains 'prototype' is a property on constructor functions, while '__proto__' is the internal link on instances.",
        "hints": [
            "Every JavaScript object has an internal reference [[Prototype]] pointing to another object or null.",
            "When accessing a property, the engine searches the object itself, then its prototype, up to Object.prototype.",
            "ES6 classes are syntactic sugar over constructor functions and prototype chaining."
        ],
        "pressure_followups": [
            "What performance penalty occurs when accessing properties that do not exist anywhere on a deep prototype chain?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "'this' Keyword & Context Binding",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How is the 'this' keyword resolved in JavaScript across different invocation contexts: default, implicit, explicit (call/apply/bind), and arrow functions?",
        "expected_concepts": ["this binding", "call", "apply", "bind", "implicit binding", "arrow function lexical this", "strict mode"],
        "evaluation_criteria": "Details execution context determination at runtime. Explains arrow functions do not bind their own 'this' but inherit it lexically from the enclosing scope.",
        "hints": [
            "For regular functions, 'this' depends on how the function was called, not where it was declared.",
            "Method calls (obj.fn()) bind 'this' implicitly to obj.",
            "Arrow functions resolve 'this' lexically from their enclosing lexical context at definition time."
        ],
        "pressure_followups": [
            "Can you override the 'this' binding of an arrow function using .bind() or .call()? Why or why not?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Frontend Memory Leak Debugging",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A React single-page application exhibits climbing memory usage in Chrome DevTools that leads to browser crashes during prolonged user sessions. What are the most common causes of memory leaks in modern JavaScript frontends, and how would you use heap snapshots to diagnose them?",
        "expected_concepts": ["detached DOM nodes", "uncleared setInterval", "event listener leak", "heap snapshot", "retaining path", "closure leak", "GC roots"],
        "evaluation_criteria": "Identifies unremoved event listeners, detached DOM elements referenced in closures, and uncleared timers. Explains taking heap snapshots and checking retaining trees.",
        "hints": [
            "Garbage collection cannot free DOM elements if a JavaScript variable or closure still references them.",
            "setInterval callbacks continue running indefinitely until clearInterval is invoked.",
            "Heap snapshots compare memory allocations between user actions to find retained objects."
        ],
        "pressure_followups": [
            "How does WeakMap or WeakRef help prevent memory leaks when associating metadata with DOM elements or cache keys?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Custom Promise.all Implementation",
        "difficulty": "Advanced",
        "question_type": "coding",
        "question_text": "Implement a custom version of Promise.all named 'allSettledPolyfill' or 'customPromiseAll' that accepts an iterable of promises and returns a promise resolving to an array of results, with strict fail-fast rejection semantics.",
        "expected_concepts": ["Promise", "Promise.resolve", "fail-fast", "array ordering", "closure counter", "rejection handler"],
        "evaluation_criteria": "Maintains resolved values in original input index order regardless of resolution timing. Rejects immediately on the first promise rejection.",
        "hints": [
            "Handle non-promise values by wrapping them with Promise.resolve().",
            "Maintain an output array and a count of resolved promises.",
            "Do not check results.length to determine completion, as sparse arrays can give misleading lengths."
        ],
        "pressure_followups": [
            "What should customPromiseAll([]) return when passed an empty array?"
        ],
        "code_snippet": None,
        "starter_code": "function customPromiseAll(promises) {\n  // TODO: Return a Promise that resolves when all input promises resolve\n  return new Promise((resolve, reject) => {\n  });\n}",
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Debounce & Throttle Implementation",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a robust debounce function in JavaScript that delays invoking the supplied function until after 'wait' milliseconds have elapsed since the last invocation, preserving the original 'this' context and arguments.",
        "expected_concepts": ["debounce", "setTimeout", "clearTimeout", "closure", "this context", "arguments forwarding"],
        "evaluation_criteria": "Uses a closure timer variable, calls clearTimeout on each trigger, and forwards arguments and 'this' to the callback via apply or rest parameters.",
        "hints": [
            "Maintain a timerId variable inside the outer function's closure.",
            "Whenever the debounced function is invoked, clear any existing timer.",
            "Set a new timer to execute the original function using apply(this, args)."
        ],
        "pressure_followups": [
            "How does throttling differ from debouncing, and which is better suited for a window resize handler versus a search autocomplete box?"
        ],
        "code_snippet": None,
        "starter_code": "function debounce(func, wait) {\n  let timeoutId;\n  return function(...args) {\n    // TODO: Implement debouncing\n  };\n}",
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "CommonJS vs ES Modules",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare CommonJS (require/module.exports) and ES Modules (import/export) in modern JavaScript runtimes. What are the key differences regarding synchronous vs asynchronous loading, top-level await, and tree-shaking?",
        "expected_concepts": ["CommonJS", "ES Modules", "synchronous require", "static analysis", "tree-shaking", "live bindings", "top-level await"],
        "evaluation_criteria": "Contrasts CJS runtime synchronous evaluation and value copies with ESM static parse-time analysis and live read-only references enabling dead code elimination.",
        "hints": [
            "CommonJS is evaluated synchronously at runtime, allowing dynamic require() paths.",
            "ES Modules have static structure known at compile-time, allowing bundlers to tree-shake unused exports.",
            "Imported values in ESM are live bindings to exported memory, not independent copies."
        ],
        "pressure_followups": [
            "How does Node.js resolve circular dependencies differently in CommonJS compared to ES Modules?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },

    # =========================================================================
    # JAVA (Domain: Java)
    # =========================================================================
    {
        "domain": "Java",
        "topic": "JVM Memory Model & Garbage Collection",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Describe the Java Virtual Machine (JVM) memory architecture. What are the roles of Heap, Stack, and Metaspace, and how does generational garbage collection (Young vs Old generation) work?",
        "expected_concepts": ["JVM memory", "Heap", "Stack", "Metaspace", "Eden space", "Survivor spaces", "Tenured Old gen", "Minor GC vs Major GC"],
        "evaluation_criteria": "Contrasts per-thread Stack execution with shared Heap object storage and class metadata Metaspace. Explains Eden to Survivor to Tenured object aging.",
        "hints": [
            "Each Java thread has its own Stack holding primitive local variables and method call frames.",
            "All object instances and their fields are allocated on the Heap.",
            "New objects enter Eden; survivors of Minor GCs migrate to Survivor spaces, then Old Gen."
        ],
        "pressure_followups": [
            "How does the G1 GC divide the heap into regional blocks compared to traditional CMS or Parallel GC?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "HashMap Internal Architecture",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the internal working of Java's HashMap. How are buckets, hashCode(), and equals() used during put() and get()? What change was introduced in Java 8 when a bucket suffers from high hash collisions?",
        "expected_concepts": ["HashMap", "hashCode", "equals", "buckets", "load factor", "rehash", "treeify threshold", "Red-Black Tree"],
        "evaluation_criteria": "Explains bucket index calculation via hash bit-shifting. Notes Java 8 converts linked lists with >= 8 entries into Red-Black trees (O(log n)).",
        "hints": [
            "HashMap computes bucket index using (n - 1) & hash.",
            "If multiple keys land in the same bucket, elements are stored in a collision list.",
            "In Java 8, when a bucket exceeds TREEIFY_THRESHOLD (8), it converts to a TreeNode Red-Black tree."
        ],
        "pressure_followups": [
            "What happens if an object's hashCode changes after it has been stored as a key in a HashMap?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Concurrency & ConcurrentHashMap",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "Compare Hashtable, Collections.synchronizedMap(), and ConcurrentHashMap in Java. How does ConcurrentHashMap achieve high read/write throughput without locking the entire map?",
        "expected_concepts": ["ConcurrentHashMap", "synchronizedMap", "lock striping", "CAS operations", "synchronized on bucket node", "non-blocking reads", "volatile"],
        "evaluation_criteria": "Contrasts coarse global monitor locks with ConcurrentHashMap's bucket-level synchronized locks and CAS writes, enabling concurrent reads without locking.",
        "hints": [
            "Hashtable synchronizes every method, creating a single bottleneck for all threads.",
            "Java 8 ConcurrentHashMap uses Compare-And-Swap (CAS) for inserting into empty buckets.",
            "It synchronizes only the specific head node of a bucket during collision updates."
        ],
        "pressure_followups": [
            "How does ConcurrentHashMap maintain thread-safety during concurrent table resizing (transfer)?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Deadlock Diagnosis & Thread Synchronization",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A high-volume Java banking application experiences a complete freeze where worker threads stop processing transactions. Thread dumps indicate a BLOCKED state. How would you analyze the thread dump to identify a deadlock, and what lock acquisition ordering rules prevent it?",
        "expected_concepts": ["deadlock", "thread dump", "jstack", "BLOCKED state", "lock ordering", "circular wait", "ReentrantLock.tryLock"],
        "evaluation_criteria": "Explains searching for 'Found one Java-level deadlock' in jstack dumps. Recommends strict global ordering on resource locks or timed tryLock.",
        "hints": [
            "Deadlock occurs when Thread 1 holds Lock A and waits for Lock B, while Thread 2 holds Lock B and waits for Lock A.",
            "jstack prints thread states and explicitly detects circular lock dependencies.",
            "Acquiring locks in a consistent, predictable order breaks the circular wait condition."
        ],
        "pressure_followups": [
            "How does java.util.concurrent.locks.ReentrantLock provide an advantage over synchronized blocks for deadlock recovery?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },

    # =========================================================================
    # SQL / DBMS (Domain: SQL, DBMS)
    # =========================================================================
    {
        "domain": "SQL",
        "topic": "B-Tree Indexing & Query Execution",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain how B-Tree indexes work in relational database engines. What is the difference between a clustered index and a non-clustered (secondary) index, and why does an index scan differ from an index seek?",
        "expected_concepts": ["B-Tree", "clustered index", "non-clustered index", "index seek", "index scan", "leaf nodes", "table lookup", "I/O cost"],
        "evaluation_criteria": "Explains clustered index determines physical table row ordering on disk, whereas non-clustered index leaf nodes store pointers/primary keys. Differentiates direct B-Tree traversal (seek) from full leaf traversal (scan).",
        "hints": [
            "A table can have only one clustered index because rows can only be physically sorted once.",
            "An index seek traverses the B-Tree from root to leaf in O(log n) to locate specific keys.",
            "An index scan reads all leaf nodes of the index sequentially."
        ],
        "pressure_followups": [
            "What is a 'covering index', and why does it eliminate secondary lookup I/O completely?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Transaction Isolation Levels & Anomalies",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "What are the four ANSI SQL transaction isolation levels? Contrast Read Uncommitted, Read Committed, Repeatable Read, and Serializable in terms of the anomalies they prevent (dirty reads, non-repeatable reads, phantom reads).",
        "expected_concepts": ["isolation levels", "dirty read", "non-repeatable read", "phantom read", "Read Committed", "Repeatable Read", "Serializable", "MVCC"],
        "evaluation_criteria": "Maps each isolation level to the specific concurrency anomalies it prevents. Explains how Multi-Version Concurrency Control (MVCC) or two-phase locking enforces them.",
        "hints": [
            "Dirty read: Reading uncommitted changes made by another active transaction.",
            "Non-repeatable read: Re-reading the same row within a transaction produces modified values.",
            "Phantom read: Re-executing a range query reveals newly inserted or deleted matching rows."
        ],
        "pressure_followups": [
            "How does PostgreSQL implement Repeatable Read using snapshot isolation, and how can a write skew anomaly occur?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Slow Query Optimization Scenario",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "A reporting query taking 45 seconds does a SELECT with multiple JOINs, a WHERE clause containing 'WHERE LOWER(email) = LOWER(:email)', and an ORDER BY on a non-indexed timestamp. How would you use EXPLAIN ANALYZE to diagnose the bottleneck and optimize the query?",
        "expected_concepts": ["EXPLAIN ANALYZE", "sequential scan", "functional index", "expression index", "filesort", "composite index", "sargable query"],
        "evaluation_criteria": "Identifies function wrapping on columns (LOWER(email)) prevents standard B-Tree index usage (non-sargable). Recommends functional index, composite index matching filter and sort.",
        "hints": [
            "Wrapping an indexed column in a function like LOWER() forces the database to evaluate every row sequentially.",
            "EXPLAIN ANALYZE shows actual execution time and node costs (Seq Scan vs Index Scan).",
            "A composite index on (email, created_at) can satisfy both the filter and sort."
        ],
        "pressure_followups": [
            "What is the impact of excessive indexes on INSERT and UPDATE performance in high-throughput OLTP systems?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Window Functions & Analytical Query",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a SQL query using window functions to find the top 2 highest-paid employees within each department from an 'employees' table with columns: id, name, department_id, salary.",
        "expected_concepts": ["DENSE_RANK", "ROW_NUMBER", "OVER", "PARTITION BY", "ORDER BY", "Common Table Expression", "Subquery"],
        "evaluation_criteria": "Uses ROW_NUMBER() or DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) inside a CTE or subquery, filtering where rank <= 2.",
        "hints": [
            "Window functions compute values across sets of rows without collapsing rows like GROUP BY.",
            "Use PARTITION BY department_id to group ranking per department.",
            "Filter the resulting rank in an outer query because window functions cannot appear directly in WHERE clauses."
        ],
        "pressure_followups": [
            "What is the difference in behavior between ROW_NUMBER(), RANK(), and DENSE_RANK() when two employees have identical salaries?"
        ],
        "code_snippet": None,
        "starter_code": "-- Write query to return top 2 highest-paid employees per department\nWITH ranked_employees AS (\n  SELECT id, name, department_id, salary,\n         -- TODO: Add window function ranking\n  FROM employees\n)\nSELECT id, name, department_id, salary\nFROM ranked_employees\nWHERE ...;",
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Database Normalization (1NF to BCNF)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain relational database normalization from 1NF through Boyce-Codd Normal Form (BCNF). What are insertion, update, and deletion anomalies, and when is controlled denormalization justified?",
        "expected_concepts": ["1NF atomic values", "2NF partial dependency", "3NF transitive dependency", "BCNF", "data anomalies", "denormalization", "read performance"],
        "evaluation_criteria": "Defines each normal form based on functional dependencies. Explains how decomposition removes redundancy and contrasts with read-optimized denormalization.",
        "hints": [
            "1NF eliminates repeating groups and requires atomic column values.",
            "2NF eliminates partial dependencies where non-key attributes depend on part of a composite key.",
            "3NF eliminates transitive dependencies (non-key attribute depending on another non-key attribute)."
        ],
        "pressure_followups": [
            "Why does BCNF sometimes fail to preserve functional dependencies that were preserved in 3NF?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Write-Ahead Logging (WAL) & Crash Recovery",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "How do database management systems guarantee Durability and Atomicity during sudden power failures? Explain the Write-Ahead Logging (WAL) protocol and the ARIES recovery algorithm (Analysis, Redo, Undo).",
        "expected_concepts": ["WAL", "Write-Ahead Logging", "Durability", "Atomicity", "checkpoint", "flush log buffer", "ARIES", "Redo phase", "Undo phase"],
        "evaluation_criteria": "Explains log records must reach disk before dirty pages are flushed. Outlines ARIES Analysis (determine active tx), Redo (reconstruct state), and Undo (rollback uncommitted).",
        "hints": [
            "WAL invariant: No modified data page is written to disk until the corresponding log record is flushed.",
            "Checkpoints reduce recovery time by establishing a known consistent flush point.",
            "During crash recovery, the Redo phase repeats history and the Undo phase rolls back uncommitted transactions."
        ],
        "pressure_followups": [
            "What is group commit, and how does it prevent disk I/O bottlenecks during high-frequency transactions?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },

    # =========================================================================
    # OPERATING SYSTEMS (Domain: Operating Systems) - STRICTLY NO CODING SNIPPETS!
    # =========================================================================
    {
        "domain": "Operating Systems",
        "topic": "CPU Scheduling Algorithms",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "In modern operating systems, compare Round Robin, Shortest Job First (SJF), and Multilevel Feedback Queue (MLFQ) scheduling. How does the kernel balance CPU-bound and interactive I/O-bound processes?",
        "expected_concepts": ["CPU scheduling", "Round Robin", "time quantum", "SJF", "MLFQ", "context switch", "preemptive", "I/O bound priority"],
        "evaluation_criteria": "Contrasts time-sliced Round Robin with optimal-burst SJF. Explains MLFQ dynamically adjusts process priority based on whether it exhausts its CPU quantum or blocks on I/O.",
        "hints": [
            "SJF minimizes average waiting time but requires predicting future CPU burst durations.",
            "Round Robin prevents starvation through fixed time slices, but short quantums increase context switch overhead.",
            "MLFQ lowers priority for processes consuming full quantums while boosting priority for interactive I/O tasks."
        ],
        "pressure_followups": [
            "What is CPU starvation, and how does priority aging prevent low-priority processes from waiting indefinitely in an MLFQ system?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Deadlock Detection & Prevention",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "What are the four Coffman conditions necessary for a system deadlock to occur? How does Banker's Algorithm ensure safe state allocation, and how can an OS prevent deadlocks by breaking circular wait?",
        "expected_concepts": ["mutual exclusion", "hold and wait", "no preemption", "circular wait", "safe state", "Banker's Algorithm", "resource ordering"],
        "evaluation_criteria": "Lists all four Coffman conditions. Explains Banker's Algorithm tests if allocating resources leaves at least one execution sequence to completion. Shows linear resource ordering breaks circular wait.",
        "hints": [
            "Deadlock requires mutual exclusion, hold and wait, no preemption, and circular wait.",
            "If any single condition is systematically prevented, deadlock cannot happen.",
            "Assigning unique numerical IDs to resources and enforcing ascending acquisition order breaks circular wait."
        ],
        "pressure_followups": [
            "Why is Banker's Algorithm rarely used in general-purpose desktop or server OS kernels like Linux or Windows?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Virtual Memory & Page Replacement",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Explain how virtual memory is implemented using paging, page tables, and the Translation Lookaside Buffer (TLB). What happens during a Page Fault, and what causes thrashing?",
        "expected_concepts": ["virtual memory", "paging", "page table", "TLB", "page fault", "demand paging", "thrashing", "working set"],
        "evaluation_criteria": "Traces address translation from virtual address to physical frame via TLB hit/miss and multi-level page tables. Details page fault trap, disk fetch, and page replacement when RAM is oversubscribed.",
        "hints": [
            "The TLB is a high-speed hardware cache inside the CPU Memory Management Unit (MMU).",
            "A page fault triggers an interrupt when a requested virtual page is not currently resident in physical RAM.",
            "Thrashing occurs when the system spends more time paging data to and from disk than executing instructions."
        ],
        "pressure_followups": [
            "How does an inverted page table differ from a multi-level hierarchical page table in terms of memory overhead on 64-bit architectures?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Process vs Thread Architecture",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare processes and threads in an operating system. What resources are shared between threads within the same process versus kept isolated, and what are the performance trade-offs of context switching between processes versus threads?",
        "expected_concepts": ["process vs thread", "address space", "PCB", "TCB", "context switch", "shared heap", "private stack", "TLB invalidation"],
        "evaluation_criteria": "Details threads share heap, code, data, and open file descriptors, but maintain private stack, registers, and program counters. Explains process context switch requires flushing TLB and MMU page directory.",
        "hints": [
            "Processes have separate virtual address spaces and communicate via IPC (pipes, sockets, shared memory).",
            "Threads share the same virtual address space, making communication fast but vulnerable to race conditions.",
            "Switching between processes requires reloading memory management registers and invalidating TLB entries."
        ],
        "pressure_followups": [
            "What is a zombie process in Unix, what is an orphan process, and how does the init/systemd process adopt orphans?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Kernel Synchronization & Race Conditions",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A multi-threaded server application suffers from intermittent corrupted state in a shared queue when running on a multi-core machine under heavy load. Contrast using Mutexes, Counting Semaphores, and Spinlocks to protect this critical section.",
        "expected_concepts": ["critical section", "mutex", "counting semaphore", "spinlock", "busy waiting", "thread sleep", "priority inversion"],
        "evaluation_criteria": "Compares sleeping mutex locks (suitable for long holds) with CPU-spinning spinlocks (suitable for short holds in kernel/multi-core). Explains counting semaphores for resource pools.",
        "hints": [
            "A mutex allows only one holder; waiting threads enter sleep state until awakened by the kernel.",
            "A spinlock loops in user/kernel space polling an atomic variable without relinquishing the CPU.",
            "Spinlocks on single-core systems cause deadlocks if the lock holder cannot run."
        ],
        "pressure_followups": [
            "What is Priority Inversion in real-time operating systems, and how does Priority Inheritance solve it?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },

    # =========================================================================
    # COMPUTER NETWORKS (Domain: Computer Networks) - STRICTLY NO CODING SNIPPETS!
    # =========================================================================
    {
        "domain": "Computer Networks",
        "topic": "TCP Three-Way Handshake & Termination",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the TCP Three-Way Handshake and Four-Way Teardown protocols. What flags (SYN, ACK, FIN) are exchanged, how are sequence numbers initialized, and why is the TIME_WAIT state necessary on the client?",
        "expected_concepts": ["TCP handshake", "SYN", "SYN-ACK", "ACK", "FIN", "sequence numbers", "TIME_WAIT", "2MSL", "connection teardown"],
        "evaluation_criteria": "Traces SYN -> SYN+ACK -> ACK sequence. Explains TIME_WAIT (typically 2*MSL) ensures delayed packets in transit drain before a new socket with the same tuple can open.",
        "hints": [
            "Client sends SYN with Initial Sequence Number (ISN); Server responds with SYN+ACK acknowledging ISN+1.",
            "Connection termination requires both directions to close independently with FIN and ACK.",
            "TIME_WAIT prevents duplicate delayed segments from a previous connection corrupting a newly established connection."
        ],
        "pressure_followups": [
            "What is a SYN Flood attack, and how do SYN Cookies allow a server to defend against it without exhausting state memory?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "TCP vs UDP & Flow/Congestion Control",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare TCP and UDP at the Transport layer. Explain how TCP achieves reliable delivery, flow control, and congestion control using Sliding Window, Slow Start, and Congestion Avoidance algorithms.",
        "expected_concepts": ["TCP vs UDP", "sliding window", "flow control", "receive window", "congestion window", "Slow Start", "AIMD", "retransmission"],
        "evaluation_criteria": "Contrasts connection-oriented reliable byte-stream TCP with connectionless datagram UDP. Distinguishes Flow Control (protecting receiver) from Congestion Control (protecting network path).",
        "hints": [
            "TCP guarantees in-order delivery and retransmits lost packets; UDP offers best-effort delivery with minimal latency.",
            "Flow control uses the receiver's Advertised Window to prevent buffer overflow.",
            "Congestion control dynamically sizes cwnd (Congestion Window) based on network packet drop signals."
        ],
        "pressure_followups": [
            "Why do modern real-time streaming protocols like HTTP/3 (QUIC) build upon UDP rather than TCP?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "DNS Resolution Hierarchy",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Walk through the complete end-to-end DNS resolution process when a user navigates to a new website. What roles do the Local Resolver, Root Nameserver, TLD Nameserver, and Authoritative Nameserver play, and how does caching with TTL work?",
        "expected_concepts": ["DNS resolution", "recursive resolver", "root nameserver", "TLD nameserver", "authoritative nameserver", "A record", "CNAME", "TTL"],
        "evaluation_criteria": "Traces client -> recursive resolver -> Root ('.') -> TLD ('.com') -> Authoritative nameserver. Explains caching at each tier based on Time-To-Live.",
        "hints": [
            "The client's OS queries the recursive DNS resolver provided by the ISP or network config.",
            "If uncached, the resolver queries one of the global Root servers to find the TLD server for that extension.",
            "The authoritative nameserver holds the actual DNS zone file with records (A, AAAA, CNAME, MX)."
        ],
        "pressure_followups": [
            "What is DNS Amplification in DDoS attacks, and how does UDP's lack of source IP verification facilitate IP spoofing?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "HTTP Protocol Evolution (HTTP/1.1 vs HTTP/2 vs HTTP/3)",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "Explain the architectural evolution from HTTP/1.1 to HTTP/2 to HTTP/3. How did HTTP/2 solve Head-of-Line (HoL) blocking at the application layer using binary framing and multiplexing, and why did HTTP/3 shift to QUIC over UDP to solve transport-layer HoL blocking?",
        "expected_concepts": ["HTTP/1.1", "HTTP/2", "HTTP/3", "QUIC", "Head-of-Line blocking", "multiplexing", "binary framing", "HPACK", "UDP"],
        "evaluation_criteria": "Explains HTTP/1.1 pipelining limitations. Details HTTP/2 streams over single TCP connection, but notes single TCP packet drop halts all streams. Shows HTTP/3 uses independent QUIC streams over UDP.",
        "hints": [
            "HTTP/1.1 required multiple parallel TCP connections to fetch assets concurrently.",
            "HTTP/2 multiplexes multiple bidirectional request streams over a single TCP connection.",
            "When a packet drops in HTTP/2, TCP stalls all streams; HTTP/3 isolates packet loss to individual QUIC streams."
        ],
        "pressure_followups": [
            "How does TLS 1.3 0-RTT connection resumption work in QUIC, and what security trade-off does it introduce regarding replay attacks?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "Subnetting & IP Routing Architecture",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "An engineering organization is allocated the IP block 192.168.10.0/24 and needs to split it into 4 separate departmental subnets of equal size. What is the new subnet mask, what is the usable host IP range for the first subnet, and what are the network and broadcast addresses?",
        "expected_concepts": ["CIDR", "subnet mask", "/26", "255.255.255.192", "usable hosts", "network address", "broadcast address", "routing"],
        "evaluation_criteria": "Calculates borrowing 2 bits creates /26 (mask 255.255.255.192). Identifies first subnet: network 192.168.10.0, broadcast 192.168.10.63, usable range 192.168.10.1 to 192.168.10.62 (62 hosts).",
        "hints": [
            "Splitting into 4 subnets requires 2 bits (2^2 = 4), increasing prefix from /24 to /26.",
            "Each /26 subnet contains 64 total addresses (2^6 = 64).",
            "The first address is the Network ID and the last is the Broadcast address; both cannot be assigned to hosts."
        ],
        "pressure_followups": [
            "How does NAT (Network Address Translation) allow hundreds of hosts within private subnets to share a single public IPv4 address simultaneously?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },

    # =========================================================================
    # C (Domain: C)
    # =========================================================================
    {
        "domain": "C",
        "topic": "Pointer Arithmetic & Memory Addresses",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "In C, explain how pointer arithmetic computes memory addresses. Why does incrementing an 'int *' advance the address by 4 bytes while a 'char *' advances by 1 byte, and what is the danger of pointer arithmetic on a 'void *'?",
        "expected_concepts": ["pointer arithmetic", "sizeof", "type scale offset", "void pointer", "undefined behavior", "dereference"],
        "evaluation_criteria": "Explains pointer arithmetic multiplies offset by sizeof(dereferenced type). Explains void* has no defined size in ANSI C.",
        "hints": [
            "Pointers in C represent hexadecimal memory addresses in RAM.",
            "Adding 1 to ptr actually adds 1 * sizeof(*ptr) bytes.",
            "In strict ANSI C, void* has an incomplete type and cannot undergo arithmetic."
        ],
        "pressure_followups": ["What is a dangling pointer, and why is setting a pointer to NULL after free() standard practice?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Struct Padding & Memory Alignment",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Why do C compilers introduce structure padding, and how does CPU memory bus alignment dictate the sizeof a struct? How can reordering struct member fields reduce memory consumption?",
        "expected_concepts": ["struct padding", "memory alignment", "word boundary", "sizeof struct", "cache line", "#pragma pack", "field reordering"],
        "evaluation_criteria": "Explains CPUs read data in 32-bit or 64-bit word chunks. Shows ordering members from largest to smallest alignment minimizes padding bytes.",
        "hints": [
            "Processors access memory more efficiently when addresses are multiples of data type sizes.",
            "Compilers insert invisible padding bytes between struct members to satisfy alignment constraints.",
            "Arranging struct members in descending order of size minimizes wasted padding."
        ],
        "pressure_followups": ["What performance penalty occurs when using #pragma pack(1) on architectures that forbid unaligned memory access?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Buffer Overflow Mitigation",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A network daemon written in C crashes under high load due to a stack buffer overflow from unbounded strcpy and sprintf calls. How would you refactor this code to use bounded functions, and what compiler safeguards (stack canaries, ASLR) mitigate exploitation?",
        "expected_concepts": ["buffer overflow", "stack smashing", "strncpy", "snprintf", "stack canary", "ASLR", "bounds checking"],
        "evaluation_criteria": "Replaces dangerous string functions with snprintf/strlcpy. Explains stack canary detection and Address Space Layout Randomization.",
        "hints": [
            "Functions like strcpy and gets write until encountering a null byte, overwriting stack return addresses.",
            "snprintf guarantees null termination when size constraints are strictly enforced.",
            "Compiler flags like -fstack-protector place canary values before return addresses to detect corruption."
        ],
        "pressure_followups": ["Why does strncpy not guarantee null-termination if the source string length equals the destination buffer size?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Circular Buffer Implementation",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a thread-safe circular ring buffer (FIFO) in C with functions to push an integer and pop an integer, maintaining head and tail indices with wrap-around using modulo arithmetic.",
        "expected_concepts": ["circular buffer", "ring buffer", "head and tail indices", "modulo arithmetic", "full buffer condition", "empty buffer condition"],
        "evaluation_criteria": "Correctly manages head and tail indices with (index + 1) % capacity. Differentiates buffer full from buffer empty conditions.",
        "hints": [
            "Use an array of fixed capacity and two indices: head (read) and tail (write).",
            "Modulo operator '%' wraps indices back to 0 when reaching capacity.",
            "Maintain an explicit count variable or reserve one slot to distinguish full from empty."
        ],
        "pressure_followups": ["How can you replace the modulo operator '%' with bitwise AND '&' if capacity is guaranteed to be a power of two?"],
        "code_snippet": None,
        "starter_code": "#include <stdbool.h>\n#define CAPACITY 8\n\ntypedef struct {\n    int data[CAPACITY];\n    int head;\n    int tail;\n    int count;\n} RingBuffer;\n\nbool push(RingBuffer *rb, int val) {\n    // TODO: Implement push\n    return false;\n}\n\nbool pop(RingBuffer *rb, int *val) {\n    // TODO: Implement pop\n    return false;\n}",
        "code_language": "c"
    },

    # =========================================================================
    # C++ (Domain: C++)
    # =========================================================================
    {
        "domain": "C++",
        "topic": "RAII & Smart Pointers",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain Resource Acquisition Is Initialization (RAII) in modern C++. How do std::unique_ptr, std::shared_ptr, and std::weak_ptr manage heap resource lifetimes, and how does std::weak_ptr resolve circular reference memory leaks?",
        "expected_concepts": ["RAII", "unique_ptr", "shared_ptr", "weak_ptr", "reference counting", "circular reference", "deterministic destruction", "make_shared"],
        "evaluation_criteria": "Explains RAII ties resource lifetime to stack object scope. Contrasts exclusive unique_ptr ownership with shared reference counting and non-owning weak_ptr.",
        "hints": [
            "RAII guarantees destructors run when objects go out of scope, preventing resource leaks.",
            "std::unique_ptr has zero runtime overhead compared to raw pointers.",
            "When two shared_ptrs reference each other, their ref counts never hit zero; weak_ptr breaks the cycle."
        ],
        "pressure_followups": ["Why is std::make_shared preferable to 'std::shared_ptr<T>(new T)' regarding memory allocations and exception safety?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Virtual Functions & Vtable Layout",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "How does C++ implement runtime polymorphism under the hood? Explain the structure of the virtual method table (vtable) and virtual table pointer (vptr), and explain why base class destructors should virtually always be declared virtual.",
        "expected_concepts": ["vtable", "vptr", "virtual function", "dynamic dispatch", "pure virtual", "virtual destructor", "object slicing"],
        "evaluation_criteria": "Explains compiler generates a table of function pointers per class and inserts an internal vptr into each object instance. Notes deleting derived object through base pointer requires virtual destructor to prevent partial destruction.",
        "hints": [
            "Every class with at least one virtual function has a hidden vtable generated by the compiler.",
            "Each object instance stores a hidden vptr pointing to its class's vtable.",
            "Non-virtual base destructors cause undefined behavior when deleting derived instances via base pointers."
        ],
        "pressure_followups": ["What is object slicing in C++, and why does passing polymorphic objects by value cause it?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Move Semantics & Rvalue References",
        "difficulty": "Advanced",
        "question_type": "tradeoff",
        "question_text": "What problem do move semantics solve in C++11? Explain the difference between lvalues and rvalues, what std::move actually does at compile time, and how move constructors prevent expensive deep memory copies.",
        "expected_concepts": ["move semantics", "rvalue reference", "std::move", "move constructor", "Rule of Five", "stealing resources", "static_cast"],
        "evaluation_criteria": "Explains lvalues have identifiable memory addresses; rvalues are temporary objects. Explains std::move unconditionally casts to rvalue reference, enabling move constructors to pilfer pointers.",
        "hints": [
            "Copying dynamic buffers requires allocating new heap memory and copying bytes.",
            "Moving transfers ownership of existing internal pointers without heap re-allocation.",
            "std::move does not move anything at runtime; it is a compile-time static_cast to an rvalue reference."
        ],
        "pressure_followups": ["What is the Rule of 5 in modern C++, and why does implementing a custom destructor inhibit compiler-generated move operations?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Thread-Safe Meyers Singleton",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement a thread-safe Singleton class in modern C++ (Meyers' Singleton) that guarantees lazy initialization, deletes copy and move constructors, and provides thread-safe access without manual mutex locks.",
        "expected_concepts": ["Meyers Singleton", "static local variable", "thread safety C++11", "deleted copy constructor", "deleted assignment operator"],
        "evaluation_criteria": "Uses a static local variable inside a static getInstance() method, leveraging C++11 standard guarantee that static local initialization is thread-safe.",
        "hints": [
            "C++11 guarantees that static local variables are initialized exactly once in a thread-safe manner.",
            "Delete the copy constructor and copy assignment operator using '= delete'.",
            "Make the constructor and destructor private."
        ],
        "pressure_followups": ["How does the compiler ensure thread-safety during static local initialization without risking deadlocks?"],
        "code_snippet": None,
        "starter_code": "class Singleton {\npublic:\n    // TODO: Prevent copying and assignment\n    // TODO: Thread-safe getInstance method\nprivate:\n    Singleton() = default;\n};",
        "code_language": "cpp"
    },

    # =========================================================================
    # DATA STRUCTURES (Domain: Data Structures)
    # =========================================================================
    {
        "domain": "Data Structures",
        "topic": "Binary Search Tree vs Self-Balancing Trees",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Compare standard Binary Search Trees (BST) with self-balancing trees like AVL and Red-Black trees. Under what conditions does an unbalanced BST degrade to O(N) complexity, and how do tree rotations restore balance?",
        "expected_concepts": ["BST", "AVL tree", "Red-Black tree", "tree rotations", "balance factor", "worst-case O(N)", "logarithmic height"],
        "evaluation_criteria": "Explains inserting sorted data into a standard BST degrades it into a linked list. Explains AVL enforces strict height balance factor <= 1 while Red-Black uses node coloring and rotations.",
        "hints": [
            "In an unbalanced BST, inserting sequential numbers 1, 2, 3... creates a skewed tree of height N.",
            "Tree rotations (left and right) restructure parent-child links while preserving the in-order BST invariant.",
            "AVL trees rotate more frequently during writes but offer faster lookups due to stricter balance."
        ],
        "pressure_followups": ["Why do standard library associative maps (like std::map or Java TreeMap) typically use Red-Black trees rather than AVL trees?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "LRU Cache Architecture",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "You are tasked with designing an in-memory Least Recently Used (LRU) Cache with fixed capacity that supports O(1) get(key) and O(1) put(key, value) operations. What combination of data structures would you select, and how do they coordinate updates?",
        "expected_concepts": ["LRU Cache", "Doubly Linked List", "Hash Map", "O(1) get", "O(1) put", "eviction policy", "node relocation"],
        "evaluation_criteria": "Combines a Hash Map (for O(1) key-to-node pointer lookup) with a Doubly Linked List (for O(1) node removal and relocation to head upon access).",
        "hints": [
            "A hash map alone provides O(1) lookups but cannot track recency order efficiently.",
            "A singly linked list cannot delete arbitrary nodes in O(1) without a previous pointer.",
            "A doubly linked list allows immediate O(1) removal of an existing node when its address is known."
        ],
        "pressure_followups": ["How would you adapt this LRU cache to be thread-safe for high concurrency with minimal lock contention?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Monotonic Stack Implementation",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Given an array of temperatures, write a function that returns an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day with a warmer temperature, keep answer[i] == 0. Must run in O(N) time.",
        "expected_concepts": ["monotonic stack", "stack", "O(N) time complexity", "index tracking", "decreasing stack"],
        "evaluation_criteria": "Uses a decreasing monotonic stack storing indices. Pops indices when current temperature exceeds stack top, computing index difference in O(N) total time.",
        "hints": [
            "Store indices on the stack rather than raw temperature values.",
            "Maintain the stack in decreasing order of temperature.",
            "When current day's temperature is warmer than the day on top of the stack, pop and calculate the day difference."
        ],
        "pressure_followups": ["Why is the time complexity strictly O(N) even though there is a while loop inside the for loop?"],
        "code_snippet": None,
        "starter_code": "from typing import List\n\ndef daily_temperatures(temperatures: List[int]) -> List[int]:\n    # TODO: Implement O(N) monotonic stack solution\n    pass",
        "code_language": "python"
    },

    # =========================================================================
    # ALGORITHMS (Domain: Algorithms)
    # =========================================================================
    {
        "domain": "Algorithms",
        "topic": "Quicksort vs Mergesort Complexity & Stability",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare Quicksort and Mergesort. Analyze their best, average, and worst-case time complexities, auxiliary space requirements, algorithm stability, and cache locality. When is Mergesort preferred over Quicksort?",
        "expected_concepts": ["Quicksort", "Mergesort", "O(N log N)", "worst case O(N^2)", "auxiliary space O(N)", "stability", "pivot selection", "cache locality"],
        "evaluation_criteria": "Details Quicksort worst case O(N^2) on bad pivot, in-place O(log N) stack, cache friendly. Mergesort guaranteed O(N log N), stable, but requires O(N) extra memory.",
        "hints": [
            "Mergesort always divides arrays in half, guaranteeing O(N log N) time regardless of input distribution.",
            "Quicksort sorts in-place, making it cache-friendly, but poor pivot choices lead to O(N^2) recursion.",
            "Mergesort is stable (preserves original order of equal keys), making it ideal for multi-criteria sorting."
        ],
        "pressure_followups": ["What pivot selection strategies (like Median-of-Three or Dual-Pivot) prevent Quicksort from degrading to O(N^2) on pre-sorted arrays?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Dynamic Programming (0/1 Knapsack)",
        "difficulty": "Advanced",
        "question_type": "conceptual",
        "question_text": "Explain the 0/1 Knapsack problem using Dynamic Programming. What are the optimal substructure and overlapping subproblems properties? How do you formulate the recurrence relation, and how can space complexity be optimized from O(N*W) to O(W)?",
        "expected_concepts": ["dynamic programming", "0/1 Knapsack", "optimal substructure", "overlapping subproblems", "recurrence relation", "space optimization", "pseudo-polynomial time"],
        "evaluation_criteria": "Derives dp[i][w] = max(dp[i-1][w], val[i-1] + dp[i-1][w - wt[i-1]]). Explains 1D array optimization requires traversing capacities in reverse order to prevent reusing the same item.",
        "hints": [
            "For each item, we decide either to include it (if capacity allows) or exclude it.",
            "dp[w] represents maximum value achievable with maximum capacity w.",
            "Traversing the 1D capacity array backwards ensures values from the current step do not overwrite earlier calculations."
        ],
        "pressure_followups": ["Why is the 0/1 Knapsack problem classified as NP-complete, and why is its dynamic programming solution considered pseudo-polynomial?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Dijkstra vs Bellman-Ford Shortest Path",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A logistics routing service must compute shortest delivery paths across a weighted road network. Contrast using Dijkstra's algorithm with a Priority Queue versus the Bellman-Ford algorithm. What happens if a road edge has a negative weight or a negative cycle exists?",
        "expected_concepts": ["Dijkstra", "Bellman-Ford", "min-heap priority queue", "negative edge weights", "negative cycles", "greedy choice", "edge relaxation"],
        "evaluation_criteria": "Explains Dijkstra greedily finalizes vertex distances and fails on negative weights. Explains Bellman-Ford relaxes all edges |V|-1 times and detects negative cycles on the |V|th pass.",
        "hints": [
            "Dijkstra runs in O((V + E) log V) using a min-heap, assuming all edge weights are non-negative.",
            "Once Dijkstra marks a node visited, it assumes the shortest distance is finalized, which fails if negative edges exist.",
            "Bellman-Ford runs in O(V * E) and can detect negative weight cycles."
        ],
        "pressure_followups": ["What is the difference between an arbitrary shortest path and the concept of an infinite negative cycle in Bellman-Ford?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },

    # =========================================================================
    # HTML/CSS (Domain: HTML/CSS)
    # =========================================================================
    {
        "domain": "HTML/CSS",
        "topic": "CSS Flexbox vs CSS Grid",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Compare CSS Flexbox and CSS Grid layout models. When is Flexbox preferred (one-dimensional) versus CSS Grid (two-dimensional), and how does 'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))' create responsive layouts without media queries?",
        "expected_concepts": ["Flexbox", "CSS Grid", "one-dimensional vs two-dimensional", "auto-fit vs auto-fill", "minmax", "fr unit", "content-driven vs layout-driven"],
        "evaluation_criteria": "Differentiates Flexbox 1D flow (rows OR columns) from Grid 2D layout (rows AND columns simultaneously). Explains auto-fit + minmax wraps columns automatically.",
        "hints": [
            "Flexbox aligns items along a single axis (main axis or cross axis).",
            "CSS Grid aligns elements in both horizontal rows and vertical columns simultaneously.",
            "minmax(250px, 1fr) ensures columns shrink no further than 250px while expanding proportionally to fill remaining space."
        ],
        "pressure_followups": ["What is the difference between auto-fit and auto-fill in CSS Grid when there are fewer items than available column slots?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "HTML/CSS",
        "topic": "CSS Specificity & The Cascade",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain how CSS Specificity and the Cascade resolve conflicting style declarations. How are specificity points calculated across inline styles, IDs, classes/attributes/pseudo-classes, and elements/pseudo-elements, and why should '!important' be avoided?",
        "expected_concepts": ["specificity", "cascade", "inline styles (1,0,0,0)", "IDs (0,1,0,0)", "classes (0,0,1,0)", "elements (0,0,0,1)", "!important", "source order"],
        "evaluation_criteria": "Explains 4-part specificity weight calculation (Inline, ID, Class/attr, Element). Explains !important overrides cascade rules, creating unmaintainable specificity wars.",
        "hints": [
            "Specificity is calculated as a 4-part vector (a, b, c, d) where higher-order numbers trump lower ones.",
            "An ID selector has higher specificity than any combination of class selectors.",
            "When specificity is identical, the rule appearing latest in source order takes precedence."
        ],
        "pressure_followups": ["How does the CSS :where() pseudo-class differ from :is() regarding specificity calculation?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "HTML/CSS",
        "topic": "Critical Rendering Path & Performance Optimization",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "A marketing landing page scores poorly on Core Web Vitals with high Cumulative Layout Shift (CLS) and slow Largest Contentful Paint (LCP). How would you optimize the Critical Rendering Path, refactor CSS delivery, and prevent layout shifts caused by web fonts and responsive images?",
        "expected_concepts": ["Critical Rendering Path", "Cumulative Layout Shift", "Largest Contentful Paint", "render-blocking CSS", "font-display: swap", "image aspect-ratio", "preload"],
        "evaluation_criteria": "Identifies render-blocking CSS in <head>. Recommends inline critical CSS, preloading hero image, setting explicit width/height or aspect-ratio on images, and font-display: swap to prevent FOIT.",
        "hints": [
            "Images without reserved dimensions cause the page layout to jump when loaded, spiking CLS.",
            "CSS is render-blocking: the browser will not render pixels until all stylesheets in head are parsed.",
            "font-display: swap ensures text remains visible immediately using fallback fonts while custom web fonts download."
        ],
        "pressure_followups": ["What is the difference between a browser Reflow (Layout) and Repaint, and which CSS properties trigger only compositing?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },

    # =========================================================================
    # OBJECT-ORIENTED PROGRAMMING (Domain: OOP)
    # =========================================================================
    {
        "domain": "OOP",
        "topic": "SOLID Principles Architecture",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the five SOLID principles of Object-Oriented Software Design. Provide a concrete example of a violation of the Single Responsibility Principle (SRP) and the Liskov Substitution Principle (LSP), and show how to fix them.",
        "expected_concepts": ["Single Responsibility", "Open/Closed", "Liskov Substitution", "Interface Segregation", "Dependency Inversion", "LSP violation", "Square-Rectangle problem"],
        "evaluation_criteria": "Defines all 5 SOLID principles. Illustrates classic LSP violation (Square inheriting Rectangle) where subclass alters pre-conditions, and refactors via composition or shared Shape interface.",
        "hints": [
            "Single Responsibility: A class should have only one reason to change.",
            "Liskov Substitution: Subtypes must be substitutable for their base types without altering program correctness.",
            "Dependency Inversion: High-level modules should depend on abstractions, not on concrete implementations."
        ],
        "pressure_followups": ["How does the Interface Segregation Principle prevent 'fat' interfaces, and how does it relate to the Single Responsibility Principle?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Composition vs Inheritance",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Explain the principle 'Favor Object Composition over Class Inheritance'. What is fragile base class syndrome, why does deep inheritance hierarchy increase coupling, and how does composition provide greater runtime flexibility?",
        "expected_concepts": ["composition over inheritance", "fragile base class", "tight coupling", "runtime flexibility", "has-a vs is-a", "code reuse", "encapsulation breach"],
        "evaluation_criteria": "Explains inheritance is compile-time static binding ('is-a') exposing parent internals (white-box reuse). Composition ('has-a') delegates behavior to interchangeable components at runtime (black-box reuse).",
        "hints": [
            "Modifying a base class can silently break subclasses in deep inheritance hierarchies.",
            "Inheritance couples derived classes to base class implementation details.",
            "Composition allows swapping underlying strategy or behavior components dynamically at runtime."
        ],
        "pressure_followups": ["When is inheritance genuinely appropriate over composition in enterprise architecture?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Strategy & Factory Design Patterns",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "An e-commerce application needs to support multiple payment gateways (Stripe, PayPal, Crypto) that can be selected at runtime, with easy addition of future payment providers without modifying existing order processing logic. Which design patterns would you combine to implement this architecture?",
        "expected_concepts": ["Strategy Pattern", "Factory Pattern", "Open/Closed Principle", "PaymentStrategy interface", "PaymentFactory", "loose coupling", "polymorphism"],
        "evaluation_criteria": "Combines Strategy Pattern (encapsulating payment algorithms behind a PaymentStrategy interface) with Factory Pattern (instantiating the concrete strategy based on user selection), satisfying Open/Closed Principle.",
        "hints": [
            "The Strategy Pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable.",
            "The Factory Pattern encapsulates object creation logic, decoupling clients from concrete classes.",
            "Adding a new payment provider requires writing a new Strategy class and updating the factory, leaving order processing untouched."
        ],
        "pressure_followups": ["How does Dependency Injection framework (like Spring or Google Guice) automate Factory instantiation in large applications?"],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    }
]
