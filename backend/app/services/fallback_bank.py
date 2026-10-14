import re
import random
from typing import Dict, List, Any, Optional

# Canonical mapping of technical domains to primary programming/markup languages
DOMAIN_CODE_LANG_MAP: Dict[str, str] = {
    "c": "c",
    "c++": "cpp",
    "cpp": "cpp",
    "java": "java",
    "javascript": "javascript",
    "js": "javascript",
    "python": "python",
    "sql": "sql",
    "html/css": "html",
    "html": "html",
    "css": "css",
    "dbms": "sql",
    "operating systems": "c",
    "computer networks": "text",
    "data structures": "python",
    "algorithms": "python",
    "oop": "java"
}

def get_domain_code_language(domain: str) -> str:
    """Returns canonical programming/syntax language for a technical domain."""
    return DOMAIN_CODE_LANG_MAP.get((domain or "").strip().lower(), "python")

# Authoritative curated fallback question bank covering ALL 13 supported domains
FALLBACK_QUESTIONS: List[Dict[str, Any]] = [
    {
        "domain": "C",
        "topic": "Pointers & Pointer Arithmetic",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "In C, explain what a pointer is, how the address-of operator (&) and dereference operator (*) work, and what pointer arithmetic computes under the hood.",
        "expected_concepts": [
            "memory address",
            "address-of operator",
            "dereference",
            "pointer arithmetic",
            "type size offset"
        ],
        "evaluation_criteria": "Must clearly define pointer as a variable storing a memory address, explain & and * semantics, and explain that pointer arithmetic scales by sizeof(type).",
        "hints": [
            "Pointers in C store the hexadecimal memory address of another variable in RAM.",
            "The '&' operator extracts an address, whereas '*' accesses the value stored at that address.",
            "Adding 1 to a pointer advances it by sizeof(type) bytes, not a single byte."
        ],
        "pressure_followups": [
            "What is a dangling pointer in C, how does it differ from a void pointer (void*), and how does the compiler handle pointer arithmetic on void*?",
            "Explain the difference between 'const int *p', 'int * const p', and 'const int * const p' in C."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Stack vs Heap Memory",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "What is the difference between stack and heap memory in C? How are variable lifetimes managed in each, and what causes a stack overflow?",
        "expected_concepts": [
            "stack memory",
            "heap memory",
            "automatic allocation",
            "manual allocation",
            "stack frame",
            "stack overflow"
        ],
        "evaluation_criteria": "Contrasts automatic, fast, LIFO stack allocation with manual dynamic heap allocation. Explains deep recursion or large local arrays causing stack overflow.",
        "hints": [
            "Stack memory is automatically managed by function call frames and the CPU stack pointer.",
            "Heap memory requires explicit allocation and deallocation by the programmer.",
            "Excessive stack usage beyond the thread limit triggers a stack overflow crash."
        ],
        "pressure_followups": [
            "How does the OS set stack size limits per thread, and how does alloca() allocate variable-length buffers on the stack?",
            "What happens if a function returns a pointer to a local stack variable?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Dynamic Memory Allocation",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain dynamic memory allocation in C. Compare malloc(), calloc(), realloc(), and free(). What is a memory leak and how do you detect it?",
        "expected_concepts": [
            "malloc",
            "calloc",
            "realloc",
            "free",
            "heap memory",
            "memory leak",
            "valgrind"
        ],
        "evaluation_criteria": "Must explain that malloc leaves memory uninitialized, calloc zero-initializes memory, realloc resizes existing allocations, and free releases heap blocks.",
        "hints": [
            "malloc returns raw uninitialized bytes, whereas calloc calculates total bytes and zeroes them.",
            "realloc can resize in place or allocate a new memory block and copy existing data.",
            "Failing to call free() before losing the pointer reference leaks heap memory."
        ],
        "pressure_followups": [
            "What happens if realloc() fails to allocate memory? Why is 'ptr = realloc(ptr, new_size)' an anti-pattern that leads to leaks?",
            "Explain double-free errors and how modern heap allocators detect heap corruption."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Segmentation Faults",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "What causes a segmentation fault (SIGSEGV) in C? Describe the operating system mechanism that triggers it and how core dumps can be inspected.",
        "expected_concepts": [
            "segmentation fault",
            "SIGSEGV",
            "virtual memory page",
            "memory protection",
            "None pointer dereference",
            "out-of-bounds",
            "core dump"
        ],
        "evaluation_criteria": "Explains MMU memory protection violations when accessing unmapped pages, writing to read-only text segment, or dereferencing NULL/wild pointers.",
        "hints": [
            "A segfault occurs when a process attempts to access a memory address that the MMU has not mapped or permits.",
            "Dereferencing a NULL pointer accesses address 0x0, which is intentionally unmapped.",
            "Buffer overruns can corrupt the return address on the stack frame, triggering segfault on return."
        ],
        "pressure_followups": [
            "How do AddressSanitizer (-fsanitize=address) and GDB help pinpoint the exact line where a memory violation occurred?",
            "Explain the difference between a segmentation fault and a bus error (SIGBUS)."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "C",
        "topic": "Dynamic Strings",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement a custom version of strdup() in C called my_strdup(const char *s). It must dynamically allocate exact memory on the heap, copy the None-terminated string, and handle allocation failure safely.",
        "expected_concepts": [
            "strlen",
            "malloc",
            "None terminator",
            "strcpy",
            "heap allocation"
        ],
        "evaluation_criteria": "Allocates strlen(s) + 1 bytes on heap, checks for NULL return, copies characters including '\\0', and returns the new pointer.",
        "hints": [
            "Remember to allocate one extra byte for the None terminator '\\0'.",
            "Always check if the pointer returned by malloc() is NULL before writing.",
            "Copy characters manually or using memcpy/strcpy."
        ],
        "pressure_followups": [
            "How would you implement a safe string concatenation function that prevents buffer overflow vulnerabilities?"
        ],
        "code_snippet": "char *my_strdup(const char *s);\n// Write the implementation in C",
        "starter_code": "char *my_strdup(const char *s) {\n    if (!s) return NULL;\n    // Your code here\n    return NULL;\n}",
        "code_language": "c"
    },
    {
        "domain": "C++",
        "topic": "Virtual Functions & Runtime Polymorphism",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain virtual functions and runtime polymorphism in C++. How do the virtual method table (vtable) and virtual pointer (vptr) achieve dynamic dispatch?",
        "expected_concepts": [
            "virtual functions",
            "runtime polymorphism",
            "vtable",
            "vptr",
            "dynamic dispatch",
            "virtual destructor"
        ],
        "evaluation_criteria": "Explains dynamic dispatch through compiler-generated function pointer array (vtable) and per-object vptr. Explains why base class destructors must be declared virtual.",
        "hints": [
            "Classes with virtual functions contain a hidden pointer member (vptr) pointing to the class vtable.",
            "When calling a virtual function via a base pointer, C++ looks up the target function at runtime via the vtable.",
            "Without a virtual destructor in the base class, deleting derived objects through a base pointer causes undefined behavior."
        ],
        "pressure_followups": [
            "Can a constructor or destructor execute dynamic dispatch in C++? Why does C++ disable virtual dispatch during object construction?",
            "What is a pure virtual function and what makes an abstract class uninstantiable?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "RAII Resource Management",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the RAII (Resource Acquisition Is Initialization) idiom in modern C++. How does RAII guarantee deterministic resource cleanup even in the presence of exceptions?",
        "expected_concepts": [
            "RAII",
            "deterministic destruction",
            "stack unwinding",
            "exception safety",
            "destructors"
        ],
        "evaluation_criteria": "Explains binding resource lifetime to local object stack lifetime so destructors automatically release resources during normal exit and exception stack unwinding.",
        "hints": [
            "In RAII, acquiring a resource occurs in the constructor, and releasing it occurs in the destructor.",
            "When an exception is thrown, the runtime unwinds the call stack and calls destructors for all fully constructed local objects.",
            "Standard library types like std::unique_ptr, std::lock_guard, and std::fstream follow RAII."
        ],
        "pressure_followups": [
            "What are the three levels of exception safety guarantees (basic, strong, no-throw)?",
            "What happens if a destructor throws an exception while another exception is already active during stack unwinding?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Stack vs Heap Allocation",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "Compare stack and heap memory allocation in C++. When should you allocate objects on the stack versus dynamically allocating them on the heap?",
        "expected_concepts": [
            "stack vs heap",
            "object lifetime",
            "cache locality",
            "new/delete",
            "stack unwinding"
        ],
        "evaluation_criteria": "Contrasts stack allocation speed and automatic scope-bound lifetime with heap flexibility and unbounded lifetime. Recommends stack by default.",
        "hints": [
            "Stack allocation is nearly instantaneous, requiring only an adjustment to the CPU stack pointer.",
            "Heap allocation involves finding an available block and is significantly slower.",
            "Prefer stack allocation unless object size is too large or object lifetime must outlive the creating scope."
        ],
        "pressure_followups": [
            "Explain move semantics (rvalue references, std::move) and how it enables transferring heap resources without copying."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Smart Pointers",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain smart pointers in C++. Compare std::unique_ptr, std::shared_ptr, and std::weak_ptr, and describe how std::weak_ptr prevents circular reference memory leaks.",
        "expected_concepts": [
            "unique_ptr",
            "shared_ptr",
            "weak_ptr",
            "reference counting",
            "circular reference",
            "std::make_shared"
        ],
        "evaluation_criteria": "Contrasts exclusive ownership (unique_ptr, non-copyable) with shared ownership (shared_ptr, atomic ref count) and non-owning observer (weak_ptr) breaking cycles.",
        "hints": [
            "std::unique_ptr cannot be copied, only moved via std::move.",
            "std::shared_ptr maintains an atomic reference count in a heap control block.",
            "std::weak_ptr observes a shared object without incrementing its strong reference count."
        ],
        "pressure_followups": [
            "Why is std::make_shared preferred over directly calling 'std::shared_ptr<T>(new T())' regarding cache locality and heap allocations?",
            "Explain how std::weak_ptr::lock() provides safe, thread-safe promotion to std::shared_ptr."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "cpp"
    },
    {
        "domain": "C++",
        "topic": "Scoped RAII Pointer",
        "difficulty": "Advanced",
        "question_type": "coding",
        "question_text": "Implement a simplified RAII scoped pointer class template ScopedPtr<T> in C++ that owns a raw pointer, prevents copy construction and copy assignment, and cleans up the resource in its destructor.",
        "expected_concepts": [
            "template",
            "destructor",
            "deleted copy constructor",
            "operator*",
            "operator->"
        ],
        "evaluation_criteria": "Correct template syntax, destructor calling delete, delete copy constructor and copy assignment (= delete), dereference operators.",
        "hints": [
            "Use '= delete' to disable copy constructor and copy assignment operator.",
            "Implement operator* returning T& and operator-> returning T*.",
            "Destructor must call 'delete ptr;'."
        ],
        "pressure_followups": [
            "Add a move constructor and move assignment operator to convert ScopedPtr into a move-only unique_ptr."
        ],
        "code_snippet": "template <typename T>\nclass ScopedPtr {\n    // Implement RAII pointer\n};",
        "starter_code": "template <typename T>\nclass ScopedPtr {\nprivate:\n    T* ptr;\npublic:\n    explicit ScopedPtr(T* p = Noneptr) : ptr(p) {}\n    ~ScopedPtr() { delete ptr; }\n    // Disable copying\n    ScopedPtr(const ScopedPtr&) = delete;\n    ScopedPtr& operator=(const ScopedPtr&) = delete;\n    T& operator*() const { return *ptr; }\n    T* operator->() const { return ptr; }\n};",
        "code_language": "cpp"
    },
    {
        "domain": "Java",
        "topic": "JVM, JRE, and JDK Architecture",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain the JVM, JRE, and JDK in Java. Describe how bytecode runs across platforms and explain the primary memory regions (Heap, Stack, Metaspace).",
        "expected_concepts": [
            "JVM",
            "JRE",
            "JDK",
            "bytecode",
            "heap memory",
            "stack memory",
            "Metaspace",
            "JIT compiler"
        ],
        "evaluation_criteria": "Clarifies JDK (development tools + compiler + JRE), JRE (JVM + libraries for running), JVM (execution engine interpreting/JIT compiling bytecode). Describes Heap (objects) and Stack (frames).",
        "hints": [
            "JDK contains javac compiler and debugging utilities; JRE is the runtime environment.",
            "The JVM executes compiled .class bytecode on host hardware.",
            "Heap memory stores all instantiated objects; thread stacks store primitive local variables and object references."
        ],
        "pressure_followups": [
            "Explain how the Just-In-Time (JIT) compiler optimizes frequently executed 'hot spot' bytecode into native machine instructions at runtime.",
            "What was PermGen in Java 7, and why was it replaced by Metaspace in native memory in Java 8?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Exception Handling Mechanics",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How does exception handling work in Java? Compare checked exceptions, unchecked exceptions (RuntimeException), and Errors. How does try-with-resources prevent resource leaks?",
        "expected_concepts": [
            "checked vs unchecked",
            "RuntimeException",
            "Error",
            "try-catch-finally",
            "try-with-resources",
            "AutoCloseable"
        ],
        "evaluation_criteria": "Explains checked exceptions enforced at compile-time (IOException, SQLException) vs unchecked runtime exceptions (NullPointerException) vs fatal Errors (OutOfMemoryError). Explains try-with-resources closing AutoCloseable.",
        "hints": [
            "Checked exceptions inherit from Exception (excluding RuntimeException) and must be caught or declared in 'throws'.",
            "Unchecked exceptions inherit from RuntimeException and represent programming bugs or unexpected logic errors.",
            "try-with-resources automatically invokes close() on any object implementing AutoCloseable."
        ],
        "pressure_followups": [
            "What happens if an exception is thrown in the try block AND another exception is thrown in the close() method? How are suppressed exceptions handled?",
            "Why is catching 'Throwable' or 'Exception' considered a poor practice in enterprise Java services?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Collections Framework & HashMap",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Java Collections Framework (List, Set, Map). How does HashMap work internally, and why must hashCode() and equals() be overridden together?",
        "expected_concepts": [
            "List vs Set vs Map",
            "HashMap internals",
            "buckets",
            "hash collisions",
            "hashCode and equals contract",
            "treeification"
        ],
        "evaluation_criteria": "Explains bucket hashing, linked-list and Red-Black tree collision resolution in Java 8, and the strict contract that equal objects must have identical hash codes.",
        "hints": [
            "List preserves order and allows duplicates; Set enforces uniqueness; Map stores key-value associations.",
            "HashMap calculates a bucket index using hash(key) & (n-1).",
            "If equals() is True, hashCode() MUST produce the same integer; otherwise, HashMap lookups fail unpredictably."
        ],
        "pressure_followups": [
            "Compare HashMap with ConcurrentHashMap: how does ConcurrentHashMap achieve thread safety without locking the entire map?",
            "What is the TREEIFY_THRESHOLD in Java 8 HashMap, and what criteria cause a bucket to convert back into a linked list?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Interface vs Abstract Class",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "What is the difference between an interface and an abstract class in Java? When should you use an abstract class instead of an interface, especially considering default methods introduced in Java 8?",
        "expected_concepts": [
            "interface vs abstract class",
            "multiple inheritance",
            "default methods",
            "state vs behavior",
            "abstract methods"
        ],
        "evaluation_criteria": "Contrasts abstract classes providing shared instance state/constructors and single inheritance with interfaces defining behavioral contracts and multiple implementation.",
        "hints": [
            "A class can extend only one abstract class, but can implement multiple interfaces.",
            "Abstract classes can have instance variables and constructors; interfaces cannot hold instance state.",
            "Java 8 default methods allow interfaces to provide default method implementations without breaking existing implementers."
        ],
        "pressure_followups": [
            "How does Java resolve the 'Diamond Problem' when a class implements two interfaces that provide conflicting default methods with identical signatures?",
            "What is a functional interface in Java, and how does the @FunctionalInterface annotation support lambda expressions?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "Java",
        "topic": "Custom Generic Stack",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement a generic Stack class in Java with push, pop, and peek operations. It must handle empty stack scenarios cleanly by throwing an EmptyStackException or returning None.",
        "expected_concepts": [
            "generics",
            "Node or array",
            "EmptyStackException",
            "push",
            "pop",
            "peek"
        ],
        "evaluation_criteria": "Proper Java generic syntax <T>, correctly manages top pointer, throws exception or returns None on empty pop/peek, O(1) time complexity.",
        "hints": [
            "Use a singly linked Node<T> structure or a dynamic resizing Object[] array.",
            "Ensure pop() returns and removes the top element, while peek() inspects without removing.",
            "Handle empty stack boundary conditions."
        ],
        "pressure_followups": [
            "How would you make this Stack thread-safe using synchronized methods or ReentrantReadWriteLock?"
        ],
        "code_snippet": "public class CustomStack<T> {\n    // Implement generic stack\n}",
        "starter_code": "public class CustomStack<T> {\n    private static class Node<T> {\n        T data;\n        Node<T> next;\n        Node(T data) { this.data = data; }\n    }\n    private Node<T> top;\n    public void push(T item) { /* Code */ }\n    public T pop() { return None; }\n    public T peek() { return None; }\n}",
        "code_language": "java"
    },
    {
        "domain": "JavaScript",
        "topic": "Event Loop (Microtasks vs Macrotasks)",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the JavaScript Event Loop and the difference between microtasks and macrotasks. In what exact order do Promise callbacks and setTimeout callbacks execute?",
        "expected_concepts": [
            "event loop",
            "call stack",
            "microtask queue",
            "macrotask queue",
            "Promises vs setTimeout",
            "run-to-completion"
        ],
        "evaluation_criteria": "Explains call stack execution, complete draining of microtask queue (Promises, queueMicrotask) before processing the next macrotask (setTimeout, setInterval, I/O).",
        "hints": [
            "JavaScript is single-threaded and executes synchronous code on the call stack.",
            "Promise callbacks (.then, .catch) go into the high-priority microtask queue.",
            "The event loop processes all queued microtasks after each macrotask and before rendering."
        ],
        "pressure_followups": [
            "Given: console.log(1); setTimeout(() => console.log(2), 0); Promise.resolve().then(() => console.log(3)); console.log(4); What is the exact output sequence?",
            "How does process.nextTick in Node.js interact with the microtask queue relative to Promise.then callbacks?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Closures & Scope",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "What is a closure in JavaScript, and when would you use it? Explain how lexical scoping enables inner functions to retain access to variables in outer functions.",
        "expected_concepts": [
            "closure",
            "lexical scope",
            "outer function scope",
            "persistent state",
            "data encapsulation",
            "private variables"
        ],
        "evaluation_criteria": "Defines closure as a function bundled with references to its surrounding lexical environment. Identifies use cases like private state, function factories, and memoization.",
        "hints": [
            "A closure is formed when an inner function remembers variables from its outer function even after the outer function has returned.",
            "Lexical scoping means scope is defined by the physical location of variables in source code.",
            "Closures prevent pollution of the global namespace by encapsulating state."
        ],
        "pressure_followups": [
            "Explain the classic loop bug with 'var' and setTimeout: why does var print the loop limit repeatedly, and how does 'let' fix this?",
            "Can closures cause memory leaks in JavaScript? How does the V8 garbage collector handle unreferenced closed-over variables?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Promises and Async/Await",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain promises and async/await in JavaScript. How does async/await simplify asynchronous code, and how does error handling differ between .catch() and try/catch?",
        "expected_concepts": [
            "Promise states (pending, fulfilled, rejected)",
            "async/await syntactic sugar",
            "try/catch",
            "microtask resolution",
            "unhandled rejection"
        ],
        "evaluation_criteria": "Explains Promise lifecycle states, async/await as syntactic sugar over Promises yielding synchronous-looking code, and error catching using try/catch.",
        "hints": [
            "An async function always returns a Promise.",
            "The await keyword pauses execution of the async function until the Promise settles.",
            "Errors inside async functions can be caught using standard try/catch blocks."
        ],
        "pressure_followups": [
            "Compare Promise.all(), Promise.allSettled(), Promise.race(), and Promise.any(). Which fail fast on rejection?",
            "What happens if an async function throws an error inside an Array.prototype.forEach loop? Why is for...of necessary?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "let, const, and var",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "What is the difference between let, const, and var in JavaScript? Explain scope (function vs block), hoisting, and the Temporal Dead Zone (TDZ).",
        "expected_concepts": [
            "var vs let vs const",
            "function scope",
            "block scope",
            "hoisting",
            "Temporal Dead Zone",
            "re-assignment vs mutability"
        ],
        "evaluation_criteria": "Contrasts function-scoped var (hoisted with undefined) with block-scoped let/const (hoisted into TDZ). Clarifies const protects binding, not internal object mutation.",
        "hints": [
            "var is function-scoped and hoisted to the top of the function initialized to undefined.",
            "let and const are block-scoped and cannot be accessed before their declaration line (TDZ).",
            "const prevents reassignment of the variable identifier, but object properties can still be modified."
        ],
        "pressure_followups": [
            "Why does accessing a let variable before its declaration throw a ReferenceError instead of returning undefined?",
            "How can you freeze an object in JavaScript so that its properties cannot be mutated when declared with const?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "javascript"
    },
    {
        "domain": "JavaScript",
        "topic": "Debounce Function",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement a debounce function in JavaScript: debounce(fn, delay). It must delay execution until after 'delay' milliseconds have elapsed since the last invocation, passing the correct 'this' context and arguments.",
        "expected_concepts": [
            "debounce",
            "setTimeout",
            "clearTimeout",
            "closure",
            "this context",
            "arguments"
        ],
        "evaluation_criteria": "Maintains timerId in closure, clears previous timeout on new invocation, calls target function with correct arguments after delay.",
        "hints": [
            "Use a closure variable to store the timer ID returned by setTimeout.",
            "Every time the debounced function is invoked, call clearTimeout(timerId).",
            "Use fn.apply(this, args) or arrow function spread to preserve context."
        ],
        "pressure_followups": [
            "How does debounce differ from throttle? When would you use throttle over debounce for scroll events?"
        ],
        "code_snippet": "function debounce(fn, delay) {\n    // Implement debounce\n}",
        "starter_code": "function debounce(fn, delay) {\n    let timer = None;\n    return function(...args) {\n        // Your code here\n    };\n}",
        "code_language": "javascript"
    },
    {
        "domain": "Python",
        "topic": "List vs Tuple",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "Explain the difference between a list and a tuple in Python. How do they differ in mutability, memory allocation overhead, and use cases as dictionary keys?",
        "expected_concepts": [
            "list vs tuple",
            "mutability vs immutability",
            "memory overhead",
            "hashability",
            "dictionary keys"
        ],
        "evaluation_criteria": "Explains lists are mutable with dynamic resizing over-allocation, while tuples are immutable, memory-compact, faster, and hashable (usable as dict keys if contents hashable).",
        "hints": [
            "Lists are mutable and defined with brackets []; tuples are immutable and defined with parentheses ().",
            "Tuples are fixed size and allocate exact memory, avoiding dynamic list resize overhead.",
            "Only immutable, hashable objects can be used as keys in Python dictionaries or elements in sets."
        ],
        "pressure_followups": [
            "Can a tuple containing a list (e.g. (1, [2, 3])) be used as a dictionary key in Python? What happens and why?",
            "What is namedtuple or dataclass in Python, and how do they improve code readability over standard tuples?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Memory Management & Garbage Collection",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How does Python manage memory? Explain reference counting, cyclic garbage collection (gc module), and the role of the Global Interpreter Lock (GIL).",
        "expected_concepts": [
            "reference counting",
            "cyclic garbage collector",
            "generations (0, 1, 2)",
            "GIL",
            "PyMalloc small object allocator"
        ],
        "evaluation_criteria": "Explains immediate deallocation when reference count reaches 0, cyclic garbage collector detecting self-referencing reference cycles, and the GIL preventing multi-threaded bytecode execution.",
        "hints": [
            "Every Python object contains an ob_refcnt counter in its C struct header.",
            "Reference counting alone cannot reclaim circular references (e.g., a.b = b; b.a = a).",
            "The GIL ensures thread-safe access to CPython internal memory structures, making CPU-bound threads single-threaded."
        ],
        "pressure_followups": [
            "Why does multiprocessing bypass the GIL while standard threading does not in Python?",
            "How does __slots__ optimize memory consumption when creating millions of small class instances?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Decorators and Generators",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "What are decorators and generators in Python? Explain how higher-order functions enable decorators (@syntax) and how the 'yield' keyword achieves lazy evaluation.",
        "expected_concepts": [
            "decorator",
            "higher-order function",
            "wrapper function",
            "generator",
            "yield",
            "lazy evaluation",
            "memory efficiency"
        ],
        "evaluation_criteria": "Explains decorators wrap functions to augment behavior using closures. Explains generators pause execution with yield to produce values on-demand with O(1) memory.",
        "hints": [
            "A decorator is a callable that takes another function as an argument and returns a replacement function.",
            "The '@' syntax is syntactic sugar for func = decorator(func).",
            "Generators maintain function stack frames and local variables across successive next() calls."
        ],
        "pressure_followups": [
            "Why is functools.wraps important when writing custom decorators?",
            "Explain how 'yield from' delegates generator execution to a sub-generator in streaming pipelines."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Exception Handling and Context Managers",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain exception handling and context managers in Python. How does the 'with' statement guarantee cleanup via __enter__ and __exit__ methods?",
        "expected_concepts": [
            "try-except-finally",
            "context manager",
            "with statement",
            "__enter__",
            "__exit__",
            "resource cleanup"
        ],
        "evaluation_criteria": "Explains structured exception handling with try/except/else/finally. Explains context manager protocol (__enter__ setups, __exit__ cleans up even on exception).",
        "hints": [
            "The 'else' block executes only if no exception was raised in the try block.",
            "The 'finally' block always executes, making it suitable for cleanup.",
            "The 'with' statement invokes __enter__ upon entry and __exit__ upon exit, ensuring file or lock release."
        ],
        "pressure_followups": [
            "How do you suppress an exception inside a context manager's __exit__ method? What boolean value must it return?",
            "How does the contextlib.contextmanager decorator use generators to create context managers easily?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Python",
        "topic": "Retry Decorator Implementation",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement a retry decorator in Python: @retry(max_attempts=3). If the decorated function raises an exception, it should catch it and retry up to max_attempts times before re-raising the exception.",
        "expected_concepts": [
            "decorator with arguments",
            "functools.wraps",
            "nested wrapper",
            "try/except",
            "re-raise"
        ],
        "evaluation_criteria": "Correct three-level function nesting for decorator arguments, preserves metadata with functools.wraps, retries up to max_attempts, re-raises final exception.",
        "hints": [
            "A decorator taking arguments requires an outer factory function that returns the actual decorator.",
            "Use functools.wraps(func) on the inner wrapper to preserve docstrings and function names.",
            "Catch Exception in a loop up to max_attempts."
        ],
        "pressure_followups": [
            "How would you add exponential backoff delay with time.sleep() between consecutive retry attempts?"
        ],
        "code_snippet": "def retry(max_attempts=3):\n    # Implement retry decorator\n    pass",
        "starter_code": "import functools\n\ndef retry(max_attempts=3):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            # Your implementation here\n            pass\n        return wrapper\n    return decorator",
        "code_language": "python"
    },
    {
        "domain": "SQL",
        "topic": "Database Normalization",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain database normalization and its purpose. Walk through 1NF, 2NF, 3NF, and BCNF, explaining what anomalies normalization eliminates.",
        "expected_concepts": [
            "normalization",
            "1NF (atomic values)",
            "2NF (no partial dependency)",
            "3NF (no transitive dependency)",
            "BCNF",
            "insertion/update/deletion anomalies"
        ],
        "evaluation_criteria": "Clearly outlines atomic attributes for 1NF, removing partial dependencies on composite keys for 2NF, removing transitive dependencies for 3NF, and strict candidate key determinants for BCNF.",
        "hints": [
            "Normalization reduces redundant data and prevents insertion, update, and deletion anomalies.",
            "2NF only matters when candidate keys are composite (multiple columns).",
            "3NF requires that non-key attributes depend only on the primary key, directly."
        ],
        "pressure_followups": [
            "When is denormalization intentionally chosen in real-world read-heavy database architectures?",
            "Given R(A, B, C) with FDs A->B and B->C, identify the normal form and demonstrate 3NF decomposition."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "ACID Properties",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "What are the ACID properties in database management systems? Explain Atomicity, Consistency, Isolation, and Durability, and describe how Write-Ahead Logging (WAL) ensures durability.",
        "expected_concepts": [
            "Atomicity",
            "Consistency",
            "Isolation",
            "Durability",
            "transactions",
            "WAL (Write-Ahead Logging)",
            "commit",
            "rollback"
        ],
        "evaluation_criteria": "Accurately defines all 4 properties: Atomicity (all or nothing), Consistency (schema validation), Isolation (concurrency control), Durability (persisted changes survive crashes via WAL).",
        "hints": [
            "A transaction is an atomic unit of execution that either completely succeeds or rolls back.",
            "Isolation ensures concurrent transactions execute without interfering with one another.",
            "Write-Ahead Logging writes transaction log changes to disk before modifying actual table data pages."
        ],
        "pressure_followups": [
            "Explain the four SQL isolation levels (Read Uncommitted, Read Committed, Repeatable Read, Serializable) and the anomalies they prevent.",
            "What is a dirty read versus a phantom read?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "INNER JOIN vs LEFT JOIN",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "Explain the difference between INNER JOIN and LEFT JOIN in SQL. What happens to unmatched rows, and how do NULL values represent missing data?",
        "expected_concepts": [
            "INNER JOIN",
            "LEFT JOIN",
            "NULL values",
            "matching rows",
            "unmatched rows",
            "cartesian product"
        ],
        "evaluation_criteria": "Contrasts inner matching rows with outer joins preserving unmatched rows padded with NULLs from the non-matching side.",
        "hints": [
            "INNER JOIN retains only rows that satisfy the join predicate in both tables.",
            "LEFT JOIN returns all rows from the left table, with NULLs for unmatched right-table columns.",
            "FULL OUTER JOIN combines the results of both left and right outer joins."
        ],
        "pressure_followups": [
            "How does filtering in the ON clause differ from filtering in the WHERE clause when executing a LEFT JOIN?",
            "What is a CROSS JOIN, and what causes an accidental cartesian product explosion?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Indexes & Query Performance",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "How do indexes affect query performance in SQL databases? Explain B-Tree indexing, clustered versus non-clustered indexes, and the performance trade-offs on read vs write operations.",
        "expected_concepts": [
            "B-Tree index",
            "clustered index",
            "non-clustered index",
            "index seek vs scan",
            "write overhead",
            "covering index"
        ],
        "evaluation_criteria": "Explains logarithmic lookup with B-Tree indexes, clustered index dictating physical row order, and the write amplification penalty on INSERT/UPDATE/DELETE.",
        "hints": [
            "Indexes speed up SELECT queries by replacing full table scans with logarithmic B-Tree seeks.",
            "A table can have only one clustered index because rows can only be physically sorted once.",
            "Every index added slows down write operations because all index trees must be updated."
        ],
        "pressure_followups": [
            "What is index cardinality, and why might a query planner ignore an index on a low-cardinality boolean column?",
            "What is a covering index and how does it eliminate table lookups?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "SQL",
        "topic": "Window Functions & Ranking",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Write a SQL query to find the second highest salary in each department using window functions (e.g. DENSE_RANK()). Given an 'employees' table with columns (id, name, department_id, salary).",
        "expected_concepts": [
            "DENSE_RANK()",
            "OVER clause",
            "PARTITION BY",
            "subquery or CTE",
            "WHERE rank = 2"
        ],
        "evaluation_criteria": "Uses CTE or subquery with DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC), filters WHERE rnk = 2.",
        "hints": [
            "Use DENSE_RANK() instead of RANK() so duplicate salaries do not skip ranks.",
            "Partition by department_id and order by salary descending.",
            "Filter the ranked results in an outer query because window functions cannot be used directly in WHERE clauses."
        ],
        "pressure_followups": [
            "How would you solve this query using a correlated subquery without window functions?"
        ],
        "code_snippet": "-- Write query using DENSE_RANK()",
        "starter_code": "WITH RankedSalaries AS (\n    SELECT id, name, department_id, salary,\n           DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rnk\n    FROM employees\n)\nSELECT department_id, salary\nFROM RankedSalaries\nWHERE rnk = 2;",
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Database Normalization",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain database normalization and its purpose. Walk through 1NF, 2NF, 3NF, and BCNF, explaining what anomalies normalization eliminates.",
        "expected_concepts": [
            "normalization",
            "1NF (atomic values)",
            "2NF (no partial dependency)",
            "3NF (no transitive dependency)",
            "BCNF",
            "insertion/update/deletion anomalies"
        ],
        "evaluation_criteria": "Clearly outlines atomic attributes for 1NF, removing partial dependencies on composite keys for 2NF, removing transitive dependencies for 3NF, and strict candidate key determinants for BCNF.",
        "hints": [
            "Normalization reduces redundant data and prevents insertion, update, and deletion anomalies.",
            "2NF only matters when candidate keys are composite (multiple columns).",
            "3NF requires that non-key attributes depend only on the primary key, directly."
        ],
        "pressure_followups": [
            "When is denormalization intentionally chosen in real-world read-heavy database architectures?",
            "Given R(A, B, C) with FDs A->B and B->C, identify the normal form and demonstrate 3NF decomposition."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "ACID Properties",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "What are the ACID properties in database management systems? Explain Atomicity, Consistency, Isolation, and Durability, and describe how Write-Ahead Logging (WAL) ensures durability.",
        "expected_concepts": [
            "Atomicity",
            "Consistency",
            "Isolation",
            "Durability",
            "transactions",
            "WAL (Write-Ahead Logging)",
            "commit",
            "rollback"
        ],
        "evaluation_criteria": "Accurately defines all 4 properties: Atomicity (all or nothing), Consistency (schema validation), Isolation (concurrency control), Durability (persisted changes survive crashes via WAL).",
        "hints": [
            "A transaction is an atomic unit of execution that either completely succeeds or rolls back.",
            "Isolation ensures concurrent transactions execute without interfering with one another.",
            "Write-Ahead Logging writes transaction log changes to disk before modifying actual table data pages."
        ],
        "pressure_followups": [
            "Explain the four SQL isolation levels (Read Uncommitted, Read Committed, Repeatable Read, Serializable) and the anomalies they prevent.",
            "What is a dirty read versus a phantom read?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "DBMS",
        "topic": "Transactions & Concurrency Control",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "Explain Multi-Version Concurrency Control (MVCC) in modern databases (like PostgreSQL or MySQL InnoDB). How does MVCC achieve non-blocking reads and avoid lock contention?",
        "expected_concepts": [
            "MVCC",
            "snapshot isolation",
            "read view",
            "row versioning",
            "transaction ID",
            "undo log",
            "vacuum / garbage collection"
        ],
        "evaluation_criteria": "Explains storing multiple versions of rows stamped with transaction IDs (xmin/xmax or undo logs), allowing readers to view consistent snapshots without acquiring shared read locks that block writers.",
        "hints": [
            "In MVCC, 'readers do not block writers, and writers do not block readers.'",
            "Every UPDATE statement physically inserts a new row version rather than overwriting in place.",
            "Old row versions no longer visible to any active transaction are cleaned up asynchronously."
        ],
        "pressure_followups": [
            "Compare pessimistic concurrency control (Two-Phase Locking / 2PL) with optimistic concurrency control (OCC). Under what workload profiles does OCC outperform 2PL?",
            "What is a write skew anomaly under Snapshot Isolation?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "sql"
    },
    {
        "domain": "Computer Networks",
        "topic": "TCP versus UDP",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "Explain the differences between TCP and UDP at the Transport layer. Why is TCP considered reliable and connection-oriented while UDP is connectionless, and what are their respective use cases?",
        "expected_concepts": [
            "TCP vs UDP",
            "connection-oriented",
            "reliability",
            "packet ordering",
            "three-way handshake",
            "flow control",
            "low latency"
        ],
        "evaluation_criteria": "Contrasts TCP connection setup, sequencing, acknowledgments, and congestion control with lightweight UDP datagrams suitable for streaming, VoIP, and gaming.",
        "hints": [
            "TCP guarantees delivery and ordering via sequence numbers and ACKs.",
            "UDP has minimal header overhead (8 bytes vs 20 bytes) and does not retransmit lost packets.",
            "DNS queries and real-time multiplayer gaming favor UDP to avoid latency caused by head-of-line blocking."
        ],
        "pressure_followups": [
            "Walk through the TCP 3-way handshake (SYN, SYN-ACK, ACK) and explain how sequence numbers prevent spoofing.",
            "What is the TCP TIME_WAIT state, and why is it necessary before closing a socket?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "Opening a Website Lifecycle",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "What happens when a user types a URL into a web browser and opens a website? Trace the complete journey from local cache and DNS resolution to TCP handshake, TLS negotiation, and HTTP response rendering.",
        "expected_concepts": [
            "browser cache",
            "DNS lookup",
            "TCP handshake",
            "TLS handshake",
            "HTTP GET request",
            "server response",
            "DOM parsing"
        ],
        "evaluation_criteria": "Comprehensive trace: Browser cache check -> DNS resolution -> TCP 3-way handshake -> TLS encryption negotiation -> HTTP GET transmission -> Server response -> Browser rendering (DOM, CSSOM).",
        "hints": [
            "The browser first checks its internal DNS cache and OS resolver.",
            "Once the IP is resolved, a TCP socket is opened via SYN, SYN-ACK, ACK.",
            "TLS negotiation exchanges certificates and agrees on a symmetric session key before sending encrypted HTTP."
        ],
        "pressure_followups": [
            "How does HTTP/2 multiplexing eliminate head-of-line blocking present in HTTP/1.1?",
            "What is HTTP/3 and why does it use QUIC over UDP to solve transport head-of-line blocking?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "DNS Resolution and TCP Handshake",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain DNS resolution and the TCP 3-way handshake. How do recursive resolvers query Root, TLD, and Authoritative nameservers, and how does the TCP handshake establish sequence numbers?",
        "expected_concepts": [
            "recursive resolver",
            "root nameserver",
            "TLD nameserver",
            "authoritative nameserver",
            "SYN",
            "SYN-ACK",
            "ACK",
            "ISN (Initial Sequence Number)"
        ],
        "evaluation_criteria": "Details hierarchical DNS resolution path and steps of TCP handshake: client sends SYN with ISN, server replies SYN-ACK with its own ISN and ACK, client responds with ACK.",
        "hints": [
            "Root servers direct resolvers to Top-Level Domain (TLD) servers (.com, .org).",
            "Authoritative servers hold the official DNS zone records for the domain.",
            "The 3-way handshake synchronizes starting sequence numbers for bidirectional byte streams."
        ],
        "pressure_followups": [
            "What is DNS cache poisoning, and how does DNSSEC use public key cryptography to protect records?",
            "What is SYN Flood attack and how do SYN cookies mitigate it?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Computer Networks",
        "topic": "HTTP Status Codes",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "What is the purpose of HTTP status codes? Explain the five main classes (1xx, 2xx, 3xx, 4xx, 5xx) and describe the difference between 401 Unauthorized and 403 Forbidden.",
        "expected_concepts": [
            "1xx informational",
            "2xx success (200, 201)",
            "3xx redirection (301, 302)",
            "4xx client error (400, 401, 403, 404)",
            "5xx server error (500, 502, 503)"
        ],
        "evaluation_criteria": "Explains standardized response categorization: 1xx info, 2xx success, 3xx redirection, 4xx client errors, 5xx server errors, giving precise meanings of 401 vs 403 and 500 vs 502/503.",
        "hints": [
            "Status codes communicate the outcome of the client's request to the browser or API consumer.",
            "401 Unauthorized means unauthenticated, while 403 Forbidden means authenticated but lacking permissions.",
            "502 Bad Gateway indicates an upstream proxy server received an invalid response from the backend application."
        ],
        "pressure_followups": [
            "What is the difference between a 301 Moved Permanently and a 302 Found redirect in terms of browser caching and SEO?",
            "What is the idempotent property in HTTP methods, and which methods (GET, PUT, DELETE) are idempotent?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "text"
    },
    {
        "domain": "Operating Systems",
        "topic": "Processes versus Threads",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "Explain processes versus threads. How do their memory address spaces differ in terms of code, data, heap, and stack, and how does context switching overhead compare?",
        "expected_concepts": [
            "process vs thread",
            "address space",
            "isolated memory",
            "shared heap",
            "independent stack and registers",
            "PCB vs TCB",
            "context switch overhead"
        ],
        "evaluation_criteria": "Explains processes possess isolated virtual memory spaces managed via PCB, while threads within a process share heap, code, and data but maintain their own stack and registers.",
        "hints": [
            "A process is an executing program instance with independent virtual address space.",
            "Threads are lightweight execution units that share the same process heap and open files.",
            "Process context switches require flushing CPU TLB caches, making them heavier than thread context switches."
        ],
        "pressure_followups": [
            "Explain user-level threads versus kernel-level threads. What happens if a user thread performs a blocking I/O call in a 1:N model?",
            "What is a zombie process versus an orphan process in Unix?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Deadlock Conditions",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "What are the four necessary conditions for deadlock in an operating system? How can breaking just one of these conditions guarantee deadlock prevention?",
        "expected_concepts": [
            "Mutual Exclusion",
            "Hold and Wait",
            "No Preemption",
            "Circular Wait",
            "Coffman conditions",
            "resource ordering",
            "Banker's algorithm"
        ],
        "evaluation_criteria": "Names all 4 conditions correctly (Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait) and demonstrates how imposing global resource ordering eliminates Circular Wait.",
        "hints": [
            "All four conditions must hold simultaneously for a deadlock to occur.",
            "Circular Wait can be eliminated by numbering all resources and requiring processes to request resources in strictly ascending order.",
            "Hold and Wait can be broken by requiring processes to acquire all resources at once before executing."
        ],
        "pressure_followups": [
            "Explain Dijkstra's Banker's Algorithm for deadlock avoidance: how does it differentiate between safe states and unsafe states?",
            "What is the difference between deadlock prevention and deadlock detection/recovery?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Virtual Memory and Paging",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain virtual memory and paging in modern operating systems. What is a page fault, what is the role of the Translation Lookaside Buffer (TLB), and how do multi-level page tables manage memory?",
        "expected_concepts": [
            "virtual memory",
            "paging",
            "page table",
            "page fault",
            "TLB",
            "multi-level paging",
            "frame",
            "MMU"
        ],
        "evaluation_criteria": "Explains MMU translating virtual addresses to physical frames using page tables, TLB caching translations, page fault interrupts bringing pages from disk, and multi-level tables saving space.",
        "hints": [
            "Virtual memory gives each process the illusion of a large, contiguous address space.",
            "The TLB is a fast hardware cache on the CPU that stores recent virtual-to-physical address mappings.",
            "A page fault occurs when a process accesses a valid page that is not currently resident in physical RAM."
        ],
        "pressure_followups": [
            "What is thrashing in virtual memory, and how does the Working Set Model prevent severe thrashing?",
            "Compare LRU, FIFO, and Clock (Second Chance) page replacement algorithms."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Operating Systems",
        "topic": "Context Switching",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "What is context switching in an operating system? Walk through the step-by-step mechanism of saving CPU registers, switching memory mappings, and the performance overhead involved.",
        "expected_concepts": [
            "context switch",
            "CPU registers",
            "program counter",
            "PCB",
            "TLB flush",
            "scheduler",
            "interrupt handler",
            "cache pollution"
        ],
        "evaluation_criteria": "Details saving CPU register state to PCB, updating scheduler queues, switching memory address space pointers (CR3 in x86), invalidating TLB, and restoring new process state.",
        "hints": [
            "A context switch occurs when the OS scheduler preempts the currently running process to run another.",
            "The OS saves the hardware state (registers, stack pointer, program counter) into the Process Control Block (PCB).",
            "Switching address spaces causes cold CPU caches and TLB invalidation, introducing noticeable overhead."
        ],
        "pressure_followups": [
            "What is the difference between a cooperative multitasking scheduler and a preemptive multitasking scheduler?",
            "How do hardware interrupts (e.g. timer interrupt) trigger preemptive context switches?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "c"
    },
    {
        "domain": "Data Structures",
        "topic": "Hash-Table Collision Handling",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain hash-table collision handling. Compare Separate Chaining with Open Addressing (Linear Probing, Quadratic Probing, Double Hashing), and discuss the effect of load factor.",
        "expected_concepts": [
            "hash table",
            "hash collision",
            "Separate Chaining",
            "Open Addressing",
            "Linear Probing",
            "load factor",
            "O(1) average vs O(N) worst case"
        ],
        "evaluation_criteria": "Contrasts separate chaining (linked list / tree per bucket) with open addressing (probing for open slots within the array). Explains load factor triggering rehashing.",
        "hints": [
            "A collision occurs when two distinct keys produce the same bucket index from the hash function.",
            "Separate chaining stores colliding elements in a secondary data structure at that index.",
            "Open addressing stores all elements inside the table itself and probes subsequent indices when collisions occur."
        ],
        "pressure_followups": [
            "What is primary clustering in linear probing, and how does double hashing mitigate it?",
            "Why is deleting an element in an open-addressed hash table complex, requiring 'tombstone' markers?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Heap vs Sorted Array",
        "difficulty": "Intermediate",
        "question_type": "comparison",
        "question_text": "When would you choose a heap over a sorted array? Compare their time complexities for insertion, deletion of the extremum (min/max), and arbitrary element lookup.",
        "expected_concepts": [
            "Heap vs Sorted Array",
            "Min-Heap",
            "O(1) peek",
            "O(log N) insertion",
            "O(N) search",
            "Priority Queue"
        ],
        "evaluation_criteria": "Shows Heap offers O(log N) insertion and O(log N) extract-min with O(1) peek, whereas Sorted Array requires O(N) insertion to maintain order despite O(1) extract and O(log N) binary search.",
        "hints": [
            "A Binary Heap satisfies the heap property: parent is always smaller/larger than children.",
            "Inserting into a sorted array requires shifting elements, which takes O(N) time.",
            "Heaps are optimal for priority queues where only the extremum (min or max) is needed, not full sorted order."
        ],
        "pressure_followups": [
            "Why can a binary heap be efficiently represented as a flat array without pointer nodes? Give the formula for child and parent indices.",
            "What is the time complexity of build_heap from an unsorted array of N elements? Why is it O(N) and not O(N log N)?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "Time and Space Complexity",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain time and space complexity in algorithmic analysis. Define Big-O, Big-Omega, and Big-Theta notations, and explain why worst-case Big-O is standard in industry evaluations.",
        "expected_concepts": [
            "Big-O (upper bound)",
            "Big-Omega (lower bound)",
            "Big-Theta (tight bound)",
            "worst case",
            "asymptotic analysis",
            "space complexity"
        ],
        "evaluation_criteria": "Defines asymptotic bounds: Big-O (upper bound), Omega (lower bound), Theta (tight bound). Explains analyzing execution steps and auxiliary memory as input size N grows.",
        "hints": [
            "Big-O notation describes the upper bound limiting growth rate as N approaches infinity.",
            "Space complexity accounts for auxiliary memory allocated on the heap or recursion call stack, excluding input.",
            "Industry standard prioritizes worst-case Big-O to guarantee upper performance limits."
        ],
        "pressure_followups": [
            "What is amortized analysis? Explain why dynamic array append is O(1) amortized despite occasional O(N) reallocations.",
            "Compare O(log N), O(N), O(N log N), O(N^2), and O(2^N) complexity curves for N = 1,000,000."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "BFS vs DFS",
        "difficulty": "Intermediate",
        "question_type": "comparison",
        "question_text": "Compare BFS and DFS on directed and undirected graphs. When is BFS preferred over DFS, and why does BFS guarantee finding the shortest path in an unweighted graph?",
        "expected_concepts": [
            "BFS vs DFS",
            "queue vs stack/recursion",
            "shortest path in unweighted graphs",
            "visited set",
            "level-order traversal"
        ],
        "evaluation_criteria": "Explains BFS uses a FIFO queue exploring nodes level-by-level, guaranteeing shortest path in unweighted graphs. Explains DFS uses stack/recursion exploring as deep as possible before backtracking.",
        "hints": [
            "BFS explores nodes in order of increasing distance from the starting vertex.",
            "Because edge weights are uniform (1), the first time BFS reaches a target node is guaranteed to be the shortest path.",
            "DFS is preferred for topological sorting, cycle detection, and maze/backtracking problems."
        ],
        "pressure_followups": [
            "How does Dijkstra's algorithm adapt BFS for graphs with non-negative edge weights using a Priority Queue?",
            "What is the space complexity of BFS vs DFS on a balanced binary tree with depth D?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Algorithms",
        "topic": "BFS Shortest Path Implementation",
        "difficulty": "Intermediate",
        "question_type": "coding",
        "question_text": "Implement Breadth-First Search (BFS) to find the shortest path length (in number of edges) between a start node and target node in an unweighted graph represented as an adjacency list.",
        "expected_concepts": [
            "collections.deque",
            "visited set",
            "queue with distance tuple",
            "level traversal",
            "return distance"
        ],
        "evaluation_criteria": "Uses deque for O(1) popleft, tracks visited nodes to prevent cycles, tracks distance correctly, returns distance when target is reached or -1 if unreachable.",
        "hints": [
            "Store tuples of (current_node, distance) in the queue.",
            "Mark nodes visited immediately when pushing to the queue to avoid redundant visits.",
            "Return distance as soon as current_node == target."
        ],
        "pressure_followups": [
            "How would you reconstruct the actual sequence of vertices along the shortest path rather than just returning the length?"
        ],
        "code_snippet": "from collections import deque\n\ndef shortest_path(graph, start, target):\n    # Implement BFS shortest path\n    pass",
        "starter_code": "from collections import deque\n\ndef shortest_path(graph, start, target):\n    if start == target: return 0\n    queue = deque([(start, 0)])\n    visited = {start}\n    while queue:\n        node, dist = queue.popleft()\n        if node == target:\n            return dist\n        for neighbor in graph.get(node, []):\n            if neighbor not in visited:\n                visited.add(neighbor)\n                queue.append((neighbor, dist + 1))\n    return -1",
        "code_language": "python"
    },
    {
        "domain": "HTML/CSS",
        "topic": "Semantic HTML5 Elements",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Explain why semantic HTML5 elements (<header>, <nav>, <main>, <article>, <section>, <aside>, <footer>) are preferred over generic <div> tags for accessibility (a11y) and SEO.",
        "expected_concepts": [
            "semantic HTML",
            "accessibility",
            "screen readers",
            "SEO",
            "landmarks",
            "document outline"
        ],
        "evaluation_criteria": "Explains that semantic tags convey meaning to search engine crawlers and assistive screen readers by defining landmark roles, contrasting with unsemantic div soup.",
        "hints": [
            "Semantic HTML tags clearly describe their role to both the browser and developer.",
            "Screen readers allow visually impaired users to jump directly to landmarks like <nav> or <main>.",
            "Search engine crawlers give higher weight and contextual understanding to semantic content."
        ],
        "pressure_followups": [
            "What is the difference between <section> and <article>? When should each be used according to W3C specifications?",
            "Explain ARIA (Accessible Rich Internet Applications) attributes: when should aria-label or role be used instead of standard HTML5 elements?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "html"
    },
    {
        "domain": "HTML/CSS",
        "topic": "CSS Flexbox Layout",
        "difficulty": "Intermediate",
        "question_type": "comparison",
        "question_text": "Explain how CSS Flexbox handles one-dimensional layouts. Describe the relationship between the main axis and cross axis, and explain justify-content vs align-items.",
        "expected_concepts": [
            "Flexbox",
            "main axis",
            "cross axis",
            "flex-direction",
            "justify-content",
            "align-items",
            "flex-grow",
            "flex-shrink"
        ],
        "evaluation_criteria": "Explains main axis orientation dictated by flex-direction (row vs column), justify-content aligning along main axis, and align-items aligning along the perpendicular cross axis.",
        "hints": [
            "Flexbox is designed for one-dimensional layouts (either a row or a column).",
            "justify-content controls distribution of free space along the main axis.",
            "align-items aligns items along the cross axis across a single line."
        ],
        "pressure_followups": [
            "Compare CSS Flexbox with CSS Grid. When is a 1D flex container preferred over a 2D grid container?",
            "Explain how 'flex: 1 1 auto' differs from 'flex: 0 0 auto' and 'flex: 1'."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "OOP",
        "topic": "Four Pillars of OOP",
        "difficulty": "Beginner",
        "question_type": "conceptual",
        "question_text": "Define the four fundamental pillars of Object-Oriented Programming (Encapsulation, Abstraction, Inheritance, Polymorphism) with practical examples.",
        "expected_concepts": [
            "Encapsulation",
            "Abstraction",
            "Inheritance",
            "Polymorphism",
            "data hiding",
            "interfaces"
        ],
        "evaluation_criteria": "Must accurately articulate all 4 pillars: Encapsulation (bundling data and methods, hiding internals), Abstraction (hiding implementation complexity), Inheritance (subclass code reuse), Polymorphism (multiple forms, interface adherence).",
        "hints": [
            "Encapsulation bundles data with the methods that operate on that data and restricts direct external access.",
            "Abstraction displays only essential features of an entity while hiding internal implementation mechanics.",
            "Polymorphism allows objects of different classes to respond to the same message or method call in their own specific way."
        ],
        "pressure_followups": [
            "Explain composition over inheritance: why is preferring object composition ('has-a') over deep inheritance hierarchies ('is-a') considered a foundational software engineering best practice?",
            "What is the Liskov Substitution Principle (LSP) in SOLID, and how does improper subclassing violate LSP?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "SOLID Principles",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Walk through each of the SOLID principles in Object-Oriented Design (SRP, OCP, LSP, ISP, DIP). Explain how Dependency Inversion (DIP) decouples high-level modules from low-level implementations.",
        "expected_concepts": [
            "Single Responsibility",
            "Open/Closed",
            "Liskov Substitution",
            "Interface Segregation",
            "Dependency Inversion",
            "dependency injection"
        ],
        "evaluation_criteria": "Thorough breakdown of all 5 principles with focus on Dependency Inversion: high-level modules must depend on abstractions/interfaces rather than concrete low-level implementations.",
        "hints": [
            "SRP: A class should have one, and only one, reason to change.",
            "OCP: Classes should be open for extension, but closed for modification.",
            "DIP: Depend on abstractions (interfaces) rather than concrete details."
        ],
        "pressure_followups": [
            "How does the Open/Closed Principle relate to design patterns like the Strategy Pattern or Factory Pattern?",
            "Describe the Interface Segregation Principle: why is having multiple small, client-specific interfaces better than a single bloated interface?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Composition over Inheritance",
        "difficulty": "Intermediate",
        "question_type": "tradeoff",
        "question_text": "Explain the principle of 'Composition over Inheritance' in Object-Oriented Design. Why can deep inheritance hierarchies create fragile base classes, and how does object composition improve maintainability?",
        "expected_concepts": [
            "composition over inheritance",
            "has-a vs is-a",
            "fragile base class",
            "loose coupling",
            "code reuse"
        ],
        "evaluation_criteria": "Explains that subclassing binds derived classes tightly to base class implementations, while composition allows dynamic runtime swapping of behaviors and avoids rigid hierarchies.",
        "hints": [
            "Inheritance creates an 'is-a' relationship, whereas composition creates a 'has-a' relationship.",
            "Changing a method in a deeply inherited base class can unintentionally break subclasses.",
            "Composition delegates responsibilities to enclosed component objects via interfaces."
        ],
        "pressure_followups": [
            "How does the Strategy Design Pattern exemplify composition over inheritance?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "OOP",
        "topic": "Design Patterns",
        "difficulty": "Advanced",
        "question_type": "scenario",
        "question_text": "Compare the Factory Method, Observer, and Strategy design patterns. When would you apply the Strategy Pattern to eliminate deeply nested switch/if statements in production code?",
        "expected_concepts": [
            "Design Patterns",
            "Factory Pattern",
            "Observer Pattern",
            "Strategy Pattern",
            "behavioral vs creational",
            "loose coupling"
        ],
        "evaluation_criteria": "Explains Strategy pattern encapsulating interchangeable algorithms behind an interface, enabling runtime algorithm switching without altering client context.",
        "hints": [
            "The Factory Method is creational: it delegates object instantiation to subclasses.",
            "The Observer pattern is behavioral: it establishes a 1-to-many dependency where subjects notify observers of state changes.",
            "The Strategy pattern encapsulates interchangeable behaviors behind a common interface."
        ],
        "pressure_followups": [
            "Explain the Thread-Safe Singleton pattern in Java/C++ using Double-Checked Locking. Why is the 'volatile' keyword required in Java?",
            "How does the Decorator Pattern enable dynamic extension of object behavior without subclass explosion?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "java"
    },
    {
        "domain": "HTML/CSS",
        "topic": "CSS Specificity & Cascade",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the CSS Cascade and specificity calculation hierarchy (Inline styles, IDs, Classes/attributes/pseudo-classes, Elements/pseudo-elements). How do CSS Cascade Layers (@layer) resolve specificity conflicts?",
        "expected_concepts": [
            "CSS Cascade",
            "specificity weight (0,0,0,0)",
            "inline styles",
            "ID selector",
            "class selector",
            "@layer (Cascade Layers)",
            "!important"
        ],
        "evaluation_criteria": "Breaks down 4-part specificity vector, explains source order resolving ties, and explains how @layer allows authoring styles with explicit priority irrespective of selector weight.",
        "hints": [
            "Specificity is calculated as a vector: (inline, ID, class, element).",
            "An ID selector always overrides any number of chained class selectors in standard specificity.",
            "@layer groups styles into ordered tiers where later layers take precedence over earlier layers."
        ],
        "pressure_followups": [
            "What causes layout reflow and repaint in browser rendering engines, and how can CSS transform/opacity optimize animations?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "HTML/CSS",
        "topic": "Responsive Layouts (clamp & fluid design)",
        "difficulty": "Intermediate",
        "question_type": "scenario",
        "question_text": "Explain fluid responsive design in modern CSS using clamp(), min(), max(), and relative viewport units. How does fluid typography eliminate jagged breakpoint jumps?",
        "expected_concepts": [
            "clamp(min, preferred, max)",
            "fluid typography",
            "viewport units (vw, vh)",
            "rem units",
            "breakpoint jumps"
        ],
        "evaluation_criteria": "Explains clamp() defining minimum bound, fluid scaling middle value using viewport units, and maximum bound, smoothly scaling fonts and layouts across any screen width.",
        "hints": [
            "clamp(1rem, 2.5vw, 2rem) keeps font size between 1rem and 2rem while scaling smoothly with viewport width.",
            "Fluid layouts scale continuously rather than stepping abruptly at media query breakpoints.",
            "Combining rem with vw inside clamp ensures user accessibility zooming remains functional."
        ],
        "pressure_followups": [
            "Compare CSS Grid and Flexbox for responsive card layouts: when is 'grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))' superior to Flexbox?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "css"
    },
    {
        "domain": "Data Structures",
        "topic": "Linked Lists vs Arrays",
        "difficulty": "Beginner",
        "question_type": "comparison",
        "question_text": "Compare contiguous arrays with singly linked lists in terms of memory layout, CPU cache locality, insertion/deletion time complexity, and random access performance.",
        "expected_concepts": [
            "array vs linked list",
            "contiguous memory",
            "pointer nodes",
            "O(1) vs O(N) access",
            "cache locality",
            "heap allocation"
        ],
        "evaluation_criteria": "Contrasts arrays having contiguous memory with O(1) index access but O(n) arbitrary insertions, versus linked lists with scattered nodes, pointer overhead, poor cache locality, but O(1) head insertion.",
        "hints": [
            "Arrays are stored in contiguous memory blocks, allowing instant pointer arithmetic offset access.",
            "Linked lists store value and next-pointer nodes scattered across heap memory.",
            "CPU cache prefetching dramatically speeds up contiguous array iteration compared to linked list pointer-chasing."
        ],
        "pressure_followups": [
            "How does Floyd's Cycle-Finding Algorithm (Tortoise and Hare) detect cycles in a linked list in O(N) time and O(1) auxiliary space?",
            "Explain how to reverse a singly linked list in-place both iteratively and recursively."
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    },
    {
        "domain": "Data Structures",
        "topic": "Binary Search Trees & Self-Balancing",
        "difficulty": "Intermediate",
        "question_type": "conceptual",
        "question_text": "Explain the Binary Search Tree (BST) invariant. What causes an unbalanced BST to degrade to O(N) time complexity, and how do self-balancing trees (AVL and Red-Black Trees) guarantee O(log N) operations?",
        "expected_concepts": [
            "BST property",
            "left < root < right",
            "unbalanced tree degradation",
            "AVL tree",
            "Red-Black tree",
            "tree rotations"
        ],
        "evaluation_criteria": "Details BST property, skew degradation on sorted inputs, and self-balancing mechanics: AVL strict height balance (|balance factor| <= 1) via single/double rotations vs Red-Black node coloring rules.",
        "hints": [
            "In a valid BST, all keys in the left subtree are smaller than the node, and all keys in the right subtree are larger.",
            "Inserting pre-sorted numbers (1, 2, 3, 4, 5) turns an ordinary BST into a linked list with O(n) search.",
            "Self-balancing trees perform O(1) pointer rotations during insertions and deletions to bound maximum tree height to O(log n)."
        ],
        "pressure_followups": [
            "Trace an AVL Left-Right (LR) double rotation. What node balance factors trigger it?",
            "Explain the difference between In-order, Pre-order, and Post-order DFS tree traversals. Why does in-order traversal of a BST yield sorted output?"
        ],
        "code_snippet": None,
        "starter_code": None,
        "code_language": "python"
    }
]

# Merge extended curated question bank
try:
    from .fallback_bank_extended import EXTENDED_FALLBACK_QUESTIONS
    FALLBACK_QUESTIONS.extend(EXTENDED_FALLBACK_QUESTIONS)
except Exception:
    pass

try:
    from .fallback_bank_part2 import FALLBACK_QUESTIONS_PART2
    FALLBACK_QUESTIONS.extend(FALLBACK_QUESTIONS_PART2)
except Exception:
    pass

from .question_deduplicator import is_duplicate_against_history, compute_question_fingerprint

# Extended domain subtopics for fallback synthesis when curated pools are exhausted
DOMAIN_SYNTHESIS_TOPICS: Dict[str, List[str]] = {
    "python": [
        "AsyncIO Event Loop Internals & Task Scheduling", "Memory Profiling with Tracemalloc & GC Tuning",
        "Attribute Descriptors (__get__, __set__) & Metaclass Protocols", "Custom Serialization, Pickle Security & Marshaling",
        "Threading vs Multiprocessing IPC Queues & Pipe Latency", "Abstract Base Classes & Structural Subtyping (typing.Protocol)",
        "Weak References & Memory Optimization in Caching", "Socket Programming & Non-blocking I/O Selectors",
        "Dynamic Bytecode Inspection with dis Module", "Context Variables (contextvars) in Async Python",
        "Generator Pipelines for Terabyte Stream Processing", "Custom Exception Hierarchies & Traceback Chaining (from e)",
        "Dataclasses vs NamedTuples vs Pydantic Memory Footprint", "Import System Internals (sys.meta_path & importlib)"
    ],
    "javascript": [
        "Event Loop Microtask Queues vs Node.js process.nextTick", "Memory Leak Diagnosis with Chrome Heap Snapshots & Retaining Trees",
        "V8 Hidden Classes, Inline Caching & JIT Deoptimizations", "Custom Promise Combinators (Promise.any, Promise.allSettled Polyfill)",
        "Proxy and Reflect API for Reactive State Management", "Web Workers & SharedArrayBuffer Concurrency with Atomics",
        "AbortController & Async Request Cancellation Architecture", "DOM Event Delegation, Bubbling, and Capturing Phases",
        "ES Modules Dynamic Import, Live Bindings & Tree-Shaking", "WeakMap and WeakSet for Ephemeral Object Metadata",
        "Streams API (ReadableStream, TransformStream) for Network Transfers", "Service Workers Cache API & Offline Strategy Patterns"
    ],
    "java": [
        "JVM Garbage Collection Algorithms (ZGC vs Shenandoah vs G1)", "ConcurrentHashMap Memory Architecture & CAS Operations",
        "Java Memory Model: volatile, happens-before & memory barriers", "ClassLoader Hierarchy & Dynamic Class Loading Mechanics",
        "CompletableFuture Asynchronous Reactive Pipelines", "Generics Type Erasure & Bridge Methods Under the Hood",
        "JVM Thread Dumps Analysis & Lock Contention Profiling", "ForkJoinPool & Work-Stealing Algorithm Internals",
        "Custom Annotations & Java Reflection Performance Trade-offs", "ThreadLocal Memory Leak Vulnerabilities in Servlet Containers"
    ],
    "c": [
        "Pointer Arithmetic Scaling & Void Pointer Type Constraints", "Struct Memory Alignment, Padding & Cache Line Packing",
        "Dynamic Memory Allocator Architecture (Custom malloc/free)", "Setjmp/Longjmp Non-local Jumps & Coroutine Emulation",
        "Volatile Keyword, Compiler Memory Barriers & Hardware Registers", "Bitwise Bitmasking, Endianness & Network Byte Ordering",
        "Function Pointers for Object-Oriented Virtual Tables in C", "Stack Smashing Protection, ASLR & Secure String Buffers"
    ],
    "c++": [
        "Move Semantics, Rvalue References & Universal References (Forwarding)", "Virtual Method Tables (vtable) & Dynamic Dispatch Internals",
        "RAII Smart Pointer Circular Dependency Resolution with weak_ptr", "Template Metaprogramming, SFINAE & C++20 Concepts",
        "Memory Model, std::atomic & std::memory_order Semantics", "Exception Safety Guarantees (Strong, Basic, No-throw)",
        "Rule of Five & Copy-and-Swap Idiom Architecture", "Cache Locality & std::vector Capacity Doubling Strategies"
    ],
    "sql": [
        "B-Tree Clustered vs Non-Clustered Index Seek Mechanics", "Transaction Isolation Levels & Multi-Version Concurrency Control (MVCC)",
        "Recursive Common Table Expressions (CTEs) for Graph Traversal", "Query Cost-Based Optimizer & EXPLAIN ANALYZE Execution Plans",
        "Database Sharding, Horizontal Partitioning & Consistent Hashing", "Deadlock Detection in Relational Transactions & Two-Phase Locking",
        "Window Functions (DENSE_RANK, NTILE, LAG/LEAD) for Time-Series Analysis", "Write-Ahead Logging (WAL) & ARIES Crash Recovery Protocol"
    ],
    "dbms": [
        "Write-Ahead Logging (WAL) & Buffer Pool Dirty Page Flushing", "Database Normalization (1NF to BCNF) & Dependency Preservation",
        "Two-Phase Commit (2PC) Protocol in Distributed Transactions", "Storage Engine Architecture (InnoDB Buffer Pool vs Log-Structured Merge)",
        "Lock Escalation, Lock Modes (S, X, IS, IX) & Granularity", "Crash Recovery ARIES Algorithm (Analysis, Redo, Undo Phases)"
    ],
    "operating systems": [
        "CPU Multilevel Feedback Queue Scheduling & Starvation Aging", "Virtual Memory Paging, Page Fault Handling & TLB Misses",
        "Deadlock Prevention, Banker's Algorithm & Circular Wait Breaking", "Inter-Process Communication: Pipes, Shared Memory & Unix Sockets",
        "Thread Synchronization: Mutex vs Semaphore vs Spinlock Trade-offs", "File System Architecture: Inodes, Superblocks & Journaling Ext4",
        "Memory Thrashing, Working Set Model & Page Replacement Algorithms", "Kernel Space vs User Space Context Switch Overhead"
    ],
    "computer networks": [
        "TCP 3-Way Handshake, Sequence Synchronization & TIME_WAIT State", "TCP Congestion Control (Slow Start, Congestion Avoidance, AIMD)",
        "HTTP/1.1 vs HTTP/2 Multiplexing vs HTTP/3 QUIC UDP Evolution", "DNS Resolution Hierarchy & Recursive Resolver Caching TTL",
        "Subnetting, CIDR Notation & Longest Prefix Match Routing", "TLS 1.3 Cryptographic Handshake & Forward Secrecy Architecture",
        "OSI Model Encapsulation, Packet vs Frame Headers & MTU Fragmentation", "Network Address Translation (NAT) & Port Address Translation (PAT)"
    ],
    "data structures": [
        "Balanced Search Trees: Red-Black vs AVL Tree Rotations", "Hash Table Collision Resolution: Chaining vs Open Addressing Probing",
        "Monotonic Stack & Queue for Sliding Window Problems", "Trie (Prefix Tree) Implementation for Substring Lookups",
        "Min/Max Binary Heap Operations & Priority Queue Internals", "LRU Cache Combination: Doubly Linked List with Hash Map",
        "Disjoint Set Union (Union-Find) with Path Compression & Rank"
    ],
    "algorithms": [
        "Quicksort vs Mergesort: Stability, Cache Locality & Stack Overhead", "Dynamic Programming: Optimal Substructure & 1D Array Space Compression",
        "Dijkstra's Algorithm with Min-Heap vs Bellman-Ford Negative Cycles", "Binary Search on Answer Space & Boundary Invariants",
        "Topological Sort with Kahn's In-Degree Queue for Task Scheduling", "Backtracking Pruning & Branch-and-Bound State-Space Search"
    ],
    "html/css": [
        "CSS Flexbox 1D Flow vs CSS Grid 2D Matrix Layout Systems", "CSS Specificity Vectors, Cascade Layering & Inheritance Rules",
        "Critical Rendering Path: DOM/CSSOM Construction & Layout Shifts (CLS)", "Semantic HTML Architecture & WAI-ARIA Accessibility Standards",
        "CSS Stacking Context, z-index Stacking Orders & Compositing Layers"
    ],
    "oop": [
        "SOLID Principles: Liskov Substitution & Interface Segregation", "Composition over Inheritance & Fragile Base Class Syndrome",
        "Strategy and Factory Patterns for Decoupled Microservice Clients", "Observer Pattern & Event-Driven Architecture Decoupling",
        "Encapsulation Invariants & Domain-Driven Design Value Objects"
    ]
}

def find_fallback_question(
    domain: str,
    topic: Optional[str] = None,
    difficulty: str = "Intermediate",
    question_type: Optional[str] = None,
    is_pressure: bool = False,
    exclude_question_texts: Optional[List[Any]] = None,
    exclude_ids: Optional[List[Any]] = None,
    question_history: Optional[List[Any]] = None,
    cross_session_history: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """
    Finds a strictly domain-compliant question from the curated fallback question bank.
    Guarantees strict deduplication (no exact or semantic duplicates of excluded questions).
    Preserves question type distribution and domain isolation.
    If the curated pool for the domain is exhausted, dynamically synthesizes a guaranteed
    novel, distinct question for that domain.
    """
    norm_domain = (domain or "").strip().lower()

    # Build normalized session history list of dicts for semantic comparison
    history: List[Dict[str, Any]] = []
    all_exclusions = []
    if exclude_question_texts:
        all_exclusions.extend(exclude_question_texts)
    if question_history:
        all_exclusions.extend(question_history)

    for item in all_exclusions:
        if isinstance(item, dict):
            history.append(item)
        elif isinstance(item, str) and item.strip():
            history.append({
                "question_text": item.strip(),
                "domain": domain,
                "topic": topic or ""
            })

    # Normalized cross-session history
    cross_history: List[Dict[str, Any]] = []
    if cross_session_history:
        for item in cross_session_history:
            if isinstance(item, dict):
                cross_history.append(item)
            elif isinstance(item, str) and item.strip():
                cross_history.append({
                    "question_text": item.strip(),
                    "domain": domain,
                    "topic": topic or ""
                })

    # Filter candidate pool strictly by domain
    pool = [q for q in FALLBACK_QUESTIONS if q["domain"].strip().lower() == norm_domain]

    # Handle domain aliases if direct match fails
    if not pool:
        if norm_domain in ["cpp", "c plus plus"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == "c++"]
        elif norm_domain in ["js"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == "javascript"]
        elif norm_domain in ["py"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == "python"]
        elif norm_domain in ["os"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == "operating systems"]
        elif norm_domain in ["networks", "network", "cn"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == "computer networks"]
        elif norm_domain in ["database", "databases"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() in ("dbms", "sql")]
        elif norm_domain in ["dsa"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() in ("data structures", "algorithms")]
        elif norm_domain in ["algo"]:
            pool = [q for q in FALLBACK_QUESTIONS if q["domain"].lower() == "algorithms"]

    # Filter out any questions that match current session history (hard deduplication)
    unasked_pool = []
    for q in pool:
        is_dup, _ = is_duplicate_against_history(q, history)
        if not is_dup:
            unasked_pool.append(q)

    # Soft preference: If questions exist that are also fresh across sessions, prefer them
    if unasked_pool and cross_history:
        fresh_cross = []
        for q in unasked_pool:
            is_cross_dup, _ = is_duplicate_against_history(q, cross_history)
            if not is_cross_dup:
                fresh_cross.append(q)
        if fresh_cross:
            unasked_pool = fresh_cross

    # If unasked questions exist in curated bank
    if unasked_pool:
        candidate_pool = list(unasked_pool)

        # 1. Filter by question_type if possible
        if question_type:
            norm_type = question_type.strip().lower()
            type_matches = [
                q for q in candidate_pool
                if q.get("question_type", "").strip().lower() == norm_type
            ]
            if type_matches:
                candidate_pool = type_matches

        # 2. Filter by topic if possible, WITHOUT sacrificing unasked status
        if topic:
            norm_topic = topic.strip().lower()
            topic_matches = [
                q for q in candidate_pool
                if norm_topic in q["topic"].lower() or q["topic"].lower() in norm_topic
            ]
            if topic_matches:
                candidate_pool = topic_matches

        # 3. Match difficulty if possible
        diff_matches = [q for q in candidate_pool if q["difficulty"].lower() == difficulty.lower()]
        final_pool = diff_matches if diff_matches else candidate_pool

        selected = dict(random.choice(final_pool))

        # Handle pressure mode transformation safely
        if is_pressure and selected.get("pressure_followups"):
            for followup_text in selected["pressure_followups"]:
                cand_pressure = dict(selected)
                cand_pressure["question_text"] = followup_text
                cand_pressure["difficulty"] = "Advanced"
                cand_pressure["question_type"] = "scenario"
                is_p_dup, _ = is_duplicate_against_history(cand_pressure, history)
                if not is_p_dup:
                    selected = cand_pressure
                    selected["expected_concepts"] = selected.get("expected_concepts", []) + ["edge cases", "runtime invariants"]
                    selected["evaluation_criteria"] = f"Rigorous evaluation of {selected['topic']} under pressure: " + selected.get("evaluation_criteria", "")
                    break

        if not selected.get("code_language"):
            selected["code_language"] = get_domain_code_language(selected["domain"])

        # Enforce non-code constraints
        sel_type = str(selected.get("question_type") or "").strip().lower()
        is_non_code = sel_type in ("conceptual", "scenario", "tradeoff", "design", "comparison", "definition") or selected["domain"].lower() in ("computer networks", "operating systems")
        if is_non_code:
            selected["code_snippet"] = None
            selected["starter_code"] = None

        return selected

    # If curated pool is exhausted, dynamically synthesize a guaranteed-unique question
    # using unused domain subtopic seeds with diverse structural prompts
    domain_key = norm_domain
    if domain_key in ["cpp", "c plus plus"]:
        domain_key = "c++"
    elif domain_key in ["js"]:
        domain_key = "javascript"
    elif domain_key in ["py"]:
        domain_key = "python"
    elif domain_key in ["os"]:
        domain_key = "operating systems"
    elif domain_key in ["networks", "network", "cn"]:
        domain_key = "computer networks"
    elif domain_key in ["database", "databases"]:
        domain_key = "sql"

    subtopic_seeds = DOMAIN_SYNTHESIS_TOPICS.get(domain_key, [
        f"{domain} Architectural Foundations", f"{domain} Memory Mechanics",
        f"{domain} Concurrency Invariants", f"{domain} High-Throughput Design",
        f"{domain} Reliability Engineering", f"{domain} Latency Optimization"
    ])

    lang = get_domain_code_language(domain)
    synth_q_type = question_type or "conceptual"

    TEMPLATES = [
        "In {domain}, explain the internal implementation details and execution guarantees of {seed}. How does {domain} enforce state consistency and memory safety in this area?",
        "A critical {domain} service experiences degraded performance and subtle anomalies tied to {seed}. How would you systematically diagnose and resolve this issue?",
        "Compare the architectural advantages and trade-offs of {seed} in {domain} versus traditional alternatives. In what production scenarios is this design optimal?",
        "Examine the boundary conditions and failure modes of {seed} in {domain}. What mechanisms prevent data corruption or deadlocks under high load?",
        "Walk through the memory layout, resource allocation lifecycle, and runtime invariants of {seed} in {domain}.",
        "Discuss modern best practices and concurrency considerations when designing high-throughput systems around {seed} in {domain}."
    ]

    for idx, seed in enumerate(subtopic_seeds):
        q_format = TEMPLATES[idx % len(TEMPLATES)]
        candidate_synth = {
            "domain": domain,
            "topic": seed,
            "difficulty": difficulty,
            "question_type": synth_q_type,
            "question_text": q_format.format(domain=domain, seed=seed),
            "expected_concepts": [f"{domain} runtime", f"{seed} mechanics", "boundary conditions", "performance trade-offs"],
            "evaluation_criteria": f"Evaluates mastery of {seed} specifically within the {domain} technical domain.",
            "hints": [
                f"Analyze the underlying data structures and execution flow of {seed} in {domain}.",
                f"Identify typical production failure modes and memory/throughput bottlenecks.",
                f"Explain standard idioms or architectural patterns in {domain} to mitigate these issues."
            ],
            "pressure_followups": [
                f"Under high load or memory constraints in {domain}, how does {seed} fail, and what invariants prevent catastrophic degradation?"
            ],
            "code_language": lang,
            "code_snippet": None,
            "starter_code": None
        }
        is_s_dup, _ = is_duplicate_against_history(candidate_synth, history)
        if not is_s_dup:
            return candidate_synth

    # Final fallback if all seeds touched
    unique_salt = len(history) + 1
    seed_topic = f"{topic or 'Architecture'} Deep-Dive {unique_salt}"
    return {
        "domain": domain,
        "topic": seed_topic,
        "difficulty": difficulty,
        "question_type": synth_q_type,
        "question_text": f"Analyze the runtime invariants and failure recovery mechanisms for {seed_topic} in {domain}. How should engineers architect fault-tolerant safeguards for this component?",
        "expected_concepts": [f"{domain} syntax", "runtime invariants", "concurrency safety"],
        "evaluation_criteria": f"Evaluates specific domain execution guarantees in {domain}.",
        "hints": [f"Focus on {domain} language guarantees and standard runtime patterns."],
        "pressure_followups": [],
        "code_language": lang,
        "code_snippet": None,
        "starter_code": None
    }

def evaluate_answer_rule_based(
    question_text: str,
    answer_text: str,
    expected_concepts: List[str],
    topic: str
) -> Dict[str, Any]:
    """Deterministic fallback evaluator comparing answer against expected concepts."""
    clean_ans = answer_text.strip().lower()
    
    # Check coverage of expected concepts
    matched_concepts = []
    missing_concepts = []

    for concept in expected_concepts:
        concept_terms = [t.strip().lower() for t in concept.split()]
        if any(term in clean_ans for term in concept_terms if len(term) > 3):
            matched_concepts.append(concept)
        else:
            missing_concepts.append(concept)

    concept_ratio = len(matched_concepts) / max(len(expected_concepts), 1)
    word_count = len(clean_ans.split())

    # Assess length & depth
    if word_count < 8:
        correctness = min(3.0, concept_ratio * 4.0)
        relevance = 4.0 if word_count >= 3 else 1.5
        conceptual = 2.5
        completeness = 2.0
    elif word_count < 25:
        correctness = 3.5 + (concept_ratio * 3.5)
        relevance = 6.0
        conceptual = 4.0 + (concept_ratio * 3.0)
        completeness = 4.0 + (concept_ratio * 3.0)
    else:
        correctness = 4.5 + (concept_ratio * 5.0)
        relevance = 7.5 + (concept_ratio * 2.0)
        conceptual = 5.0 + (concept_ratio * 4.5)
        completeness = 5.0 + (concept_ratio * 4.5)

    correctness = round(min(max(correctness, 1.0), 9.8), 1)
    relevance = round(min(max(relevance, 1.0), 10.0), 1)
    conceptual = round(min(max(conceptual, 1.0), 9.8), 1)
    completeness = round(min(max(completeness, 1.0), 9.8), 1)

    overall_score = round((correctness * 0.40) + (conceptual * 0.30) + (completeness * 0.20) + (relevance * 0.10), 1)

    weakness_detected = overall_score < 6.0
    if overall_score < 4.5:
        weakness_level = "severe"
    elif overall_score < 6.5:
        weakness_level = "moderate"
    elif overall_score < 8.0:
        weakness_level = "mild"
    else:
        weakness_level = None

    if matched_concepts and not missing_concepts:
        feedback = f"Excellent response! You clearly addressed key principles of {topic}, demonstrating sound understanding of {', '.join(matched_concepts[:3])}."
    elif matched_concepts and missing_concepts:
        feedback = f"Good start covering {', '.join(matched_concepts[:2])}. However, your answer lacked detail regarding {', '.join(missing_concepts[:2])}."
    else:
        feedback = f"Your answer requires significant refinement on {topic}. Key missing elements include: {', '.join(missing_concepts[:3]) if missing_concepts else 'fundamental definitions'}."

    return {
        "correctness": correctness,
        "relevance": relevance,
        "conceptual_understanding": conceptual,
        "completeness": completeness,
        "overall_score": overall_score,
        "topic": topic,
        "subtopics": matched_concepts if matched_concepts else ["fundamentals"],
        "weakness_detected": weakness_detected,
        "weakness_level": weakness_level,
        "missing_concepts": missing_concepts,
        "feedback": feedback
    }
