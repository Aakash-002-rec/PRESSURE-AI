import re
import string
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple

# Domain-specific concept clusters for deep semantic duplicate detection
CONCEPT_CLUSTERS: Dict[str, Set[str]] = {
    # JavaScript
    "js_event_loop": {
        "event loop", "eventloop", "microtask", "microtasks", "macrotask", "macrotasks",
        "task queue", "call stack", "callback queue", "settimeout", "setimmediate",
        "nexttick", "scheduler", "schedules", "synchronous code", "run to completion",
        "job queue", "execution order", "event loop phases"
    },
    "js_closures": {
        "closure", "closures", "lexical scope", "lexical environment", "scope chain",
        "outer function scope", "variable retention", "private variables", "state retention"
    },
    "js_promises_async": {
        "promise", "promises", "async await", "async/await", "promise.all", "promise.race",
        "promise chaining", "then", "catch", "settled", "rejected", "pending"
    },
    "js_prototypes": {
        "prototype", "prototypes", "prototypal inheritance", "prototype chain", "__proto__",
        "object.create", "constructor function"
    },
    "js_this_binding": {
        "this keyword", "this binding", "explicit binding", "call", "apply", "bind",
        "arrow function this", "lexical this", "implicit binding"
    },
    "js_types_coercion": {
        "type coercion", "truthy", "falsy", "typeof", "instanceof", "loose equality",
        "strict equality", "double equals", "triple equals", "nan", "null vs undefined"
    },

    # Python
    "python_decorators": {
        "decorator", "decorators", "functools", "wraps", "functools.wraps", "function wrapper",
        "higher order function", "wrapper function", "syntactic sugar", "@decorator",
        "decorating", "decorate", "alters behavior", "wrap functions", "wrapper"
    },
    "python_generators": {
        "generator", "generators", "yield", "yield from", "iterator", "iterators",
        "iterable", "__iter__", "__next__", "lazy evaluation", "generator expression"
    },
    "python_memory": {
        "reference counting", "garbage collection", "cyclic reference", "cycle detector",
        "gc module", "memory management", "deallocation", "id()", "is vs ==", "interning"
    },
    "python_concurrency_gil": {
        "gil", "global interpreter lock", "multiprocessing", "threading", "cpu bound",
        "io bound", "asyncio", "thread safety", "gil contention"
    },
    "python_oop": {
        "dunder methods", "magic methods", "__init__", "__str__", "__repr__", "mro",
        "method resolution order", "super()", "multiple inheritance", "metaclass", "slots"
    },
    "python_data_structures": {
        "list comprehension", "dict comprehension", "dictionary", "hash map", "set operations",
        "mutable vs immutable", "shallow copy", "deep copy"
    },
    "python_context_managers": {
        "context manager", "with statement", "__enter__", "__exit__", "contextlib"
    },

    # Java
    "java_jvm_memory": {
        "jvm", "garbage collection", "garbage collector", "heap memory", "stack memory",
        "metaspace", "eden space", "survivor space", "tenured", "mark and sweep",
        "gc roots", "out of memory"
    },
    "java_collections": {
        "collections framework", "hashmap", "treemap", "arraylist", "linkedlist",
        "concurrenthashmap", "hashcode and equals", "comparator", "comparable"
    },
    "java_concurrency": {
        "synchronized", "volatile", "threadpool", "executorservice", "reentrantlock",
        "deadlock", "atomic variables", "atomicinteger", "thread safe"
    },
    "java_oop": {
        "polymorphism", "encapsulation", "inheritance", "abstract class", "interface",
        "default methods", "method overriding", "method overloading"
    },

    # C / C++
    "c_pointers": {
        "pointer", "pointers", "pointer arithmetic", "dereference", "address-of",
        "dangling pointer", "void pointer", "null pointer", "double pointer", "pointer offset"
    },
    "c_memory_alloc": {
        "malloc", "calloc", "realloc", "free", "dynamic memory", "heap allocation",
        "stack allocation", "memory leak", "valgrind", "buffer overflow", "segmentation fault"
    },
    "cpp_smart_pointers": {
        "unique_ptr", "shared_ptr", "weak_ptr", "smart pointer", "smart pointers", "raii",
        "reference count", "circular reference", "make_unique", "make_shared"
    },
    "cpp_virtual_functions": {
        "virtual function", "virtual functions", "vtable", "vptr", "pure virtual",
        "dynamic dispatch", "runtime polymorphism", "virtual destructor"
    },

    # SQL / DBMS
    "sql_indexing": {
        "index", "indexes", "b-tree", "b+ tree", "clustered index", "non-clustered index",
        "composite index", "index scan", "index seek", "covering index", "hash index"
    },
    "sql_normalization": {
        "normalization", "1nf", "2nf", "3nf", "bcnf", "denormalization", "normal form",
        "functional dependency", "redundancy"
    },
    "sql_acid_transactions": {
        "acid", "atomicity", "consistency", "isolation", "durability", "transaction",
        "transactions", "commit", "rollback", "two-phase commit"
    },
    "sql_isolation_concurrency": {
        "isolation level", "isolation levels", "dirty read", "non-repeatable read",
        "phantom read", "read committed", "repeatable read", "serializable", "pessimistic lock",
        "optimistic lock"
    },
    "sql_joins": {
        "inner join", "left join", "right join", "full outer join", "cross join", "self join",
        "join optimization", "nested loop join", "hash join"
    },
    "sql_query_tuning": {
        "query optimization", "explain plan", "execution plan", "table scan", "cost-based optimizer"
    },

    # Operating Systems
    "os_scheduling": {
        "cpu scheduling", "round robin", "first-come first-served", "fcfs", "priority scheduling",
        "multilevel feedback queue", "shortest job first", "sjf", "preemption", "preemptive",
        "context switch", "scheduling algorithm"
    },
    "os_deadlocks": {
        "deadlock", "deadlocks", "banker's algorithm", "mutual exclusion", "hold and wait",
        "circular wait", "deadlock prevention", "deadlock detection", "resource allocation graph"
    },
    "os_virtual_memory": {
        "virtual memory", "paging", "page table", "page fault", "tlb", "translation lookaside buffer",
        "segmentation", "thrashing", "page replacement", "lru", "mmu"
    },
    "os_processes_threads": {
        "process vs thread", "processes and threads", "fork", "exec", "zombie process",
        "orphan process", "pcb", "process control block", "context switching"
    },
    "os_synchronization": {
        "mutex", "semaphore", "counting semaphore", "binary semaphore", "critical section",
        "race condition", "spin lock", "producer-consumer"
    },

    # Computer Networks
    "net_tcp_handshake": {
        "tcp handshake", "three-way handshake", "syn ack", "three way handshake",
        "connection termination", "fin ack", "time_wait", "reliable delivery"
    },
    "net_tcp_vs_udp": {
        "tcp vs udp", "connection-oriented", "connectionless", "flow control",
        "sliding window", "congestion control", "packet loss", "retransmission"
    },
    "net_osi_layers": {
        "osi model", "osi layers", "physical layer", "data link layer", "network layer",
        "transport layer", "application layer", "packet vs frame", "encapsulation"
    },
    "net_dns": {
        "dns", "domain name system", "dns resolution", "recursive resolver", "authoritative server",
        "root nameserver", "a record", "cname", "ttl"
    },
    "net_http_web": {
        "http vs https", "http/1.1", "http/2", "http/3", "status codes", "rest api",
        "tls handshake", "ssl handshake", "http headers", "keep-alive"
    },
    "net_routing_ip": {
        "ip address", "ipv4 vs ipv6", "subnetting", "cidr", "nat", "routing table",
        "arp protocol", "icmp", "ping"
    }
}

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "to", "from", "up",
    "down", "of", "off", "over", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "s", "t", "can", "will", "just", "don", "should", "now", "what", "is", "are", "explain",
    "describe", "discuss", "what's", "write", "implement", "given", "using", "work", "works",
    "does", "under", "hood", "purpose", "concept", "concepts", "overview", "please", "detail",
    "code", "example", "examples", "different", "difference", "compare", "role", "mean",
    "define", "understand", "walk", "through", "candidate", "interviewer"
}

FILLER_PREFIX_REGEX = re.compile(
    r'^(in\s+[a-zA-Z\+\#\/]+\s*,\s*|explain\s+(how|what|why|the)\s+|describe\s+(how|what|why|the)\s+|'
    r'what\s+is\s+(the\s+|a\s+|an\s+)?|what\s+are\s+(the\s+|a\s+|an\s+)?|'
    r'how\s+(does|do)\s+|can\s+you\s+(explain|describe)\s+|'
    r'walk\s+us\s+through\s+|please\s+(explain|describe)\s+)',
    re.IGNORECASE
)

# Domain prefix map to filter clusters by domain
DOMAIN_CLUSTER_PREFIX: Dict[str, str] = {
    "javascript": "js_",
    "js": "js_",
    "python": "python_",
    "java": "java_",
    "c": "c_",
    "c++": "c",
    "cpp": "c",
    "sql": "sql_",
    "dbms": "sql_",
    "operating systems": "os_",
    "computer networks": "net_",
    "data structures": "ds_",
    "algorithms": "algo_",
    "html/css": "html_",
    "oop": "oop_"
}

def clean_text(text: str) -> str:
    """Removes punctuation, lowercases, and normalizes whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    return " ".join(text.split())

def normalize_question_core(text: str) -> str:
    """Strips conversational boilerplate and returns core question content tokens."""
    cleaned = clean_text(text)
    cleaned = FILLER_PREFIX_REGEX.sub('', cleaned).strip()
    words = [w for w in cleaned.split() if w not in STOP_WORDS and len(w) > 2]
    return " ".join(words)

def extract_technical_tokens(text: str) -> Set[str]:
    """Extracts distinctive technical tokens and bigrams from a question string."""
    cleaned = clean_text(text)
    words = [w for w in cleaned.split() if w not in STOP_WORDS and len(w) > 2]
    tokens = set(words)
    for i in range(len(words) - 1):
        tokens.add(f"{words[i]} {words[i+1]}")
    return tokens

def identify_concept_clusters(
    text: str,
    domain: Optional[str] = None,
    topic: Optional[str] = None,
    expected_concepts: Optional[List[str]] = None
) -> Set[str]:
    """Identifies which concept clusters a question belongs to using whole-word boundary matching."""
    matched = set()
    combined_text = (clean_text(text) + " " + clean_text(topic or "")).lower()
    if expected_concepts:
        combined_text += " " + " ".join([clean_text(c) for c in expected_concepts])

    norm_domain = (domain or "").strip().lower()
    prefix = DOMAIN_CLUSTER_PREFIX.get(norm_domain)

    for cluster_name, keywords in CONCEPT_CLUSTERS.items():
        # If domain specified, strictly isolate to clusters for this domain
        if prefix:
            if norm_domain in ("c", "c++", "cpp"):
                if not (cluster_name.startswith("c_") or cluster_name.startswith("cpp_")):
                    continue
            elif not cluster_name.startswith(prefix):
                continue
        elif not (cluster_name.startswith("c_") or cluster_name.startswith("cpp_")):
            continue

        for kw in keywords:
            ckw = clean_text(kw)
            if not ckw:
                continue
            # Match whole phrase or word with boundary and common inflectional endings
            pattern = r'\b' + re.escape(ckw) + r'(s|es|ing|ed)?\b'
            if re.search(pattern, combined_text):
                matched.add(cluster_name)
                break
    return matched

def compute_question_fingerprint(
    question_text: str,
    domain: str,
    topic: Optional[str] = None,
    expected_concepts: Optional[List[str]] = None
) -> str:
    """Computes a canonical content fingerprint capturing the domain and technical concepts."""
    clean_domain = (domain or "").strip().lower()
    clusters = sorted(list(identify_concept_clusters(question_text, clean_domain, topic, expected_concepts)))
    cluster_sig = "|".join(clusters)

    core_tokens = sorted(list(extract_technical_tokens(question_text)))[:20]
    token_sig = "-".join(core_tokens)

    concept_sig = ""
    if expected_concepts:
        clean_exp = sorted([clean_text(c) for c in expected_concepts if clean_text(c)])
        concept_sig = "|".join(clean_exp)

    raw_sig = f"DOM:{clean_domain};CLUST:{cluster_sig};TOK:{token_sig};EXP:{concept_sig}"
    return hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()

def token_jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Computes Jaccard similarity between two sets of tokens."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def is_semantic_duplicate(
    q1: Dict[str, Any],
    q2: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Determines if two questions are duplicates (exact or semantically equivalent).
    Returns (is_duplicate: bool, reason: str).
    """
    text1 = q1.get("question_text", "")
    text2 = q2.get("question_text", "")

    if not text1 or not text2:
        return False, "Empty question text"

    # 1. Exact string match (case-insensitive & whitespace trimmed)
    if text1.strip().lower() == text2.strip().lower():
        return True, "Exact text match"

    # 2. Normalized Core match (after filler phrase and stopword removal)
    norm1 = normalize_question_core(text1)
    norm2 = normalize_question_core(text2)
    if norm1 and norm2 and norm1 == norm2:
        return True, "Normalized core question text is identical"

    domain1 = (q1.get("domain") or "").strip().lower()
    domain2 = (q2.get("domain") or "").strip().lower()
    is_same_domain = domain1 and domain2 and domain1 == domain2

    # 3. Fingerprint match
    if is_same_domain:
        fp1 = q1.get("fingerprint") or compute_question_fingerprint(
            text1, domain1, q1.get("topic"), q1.get("expected_concepts")
        )
        fp2 = q2.get("fingerprint") or compute_question_fingerprint(
            text2, domain2, q2.get("topic"), q2.get("expected_concepts")
        )
        if fp1 and fp2 and fp1 == fp2:
            return True, "Canonical question fingerprint match"

    # 4. Domain concept cluster matching
    clusters1 = identify_concept_clusters(text1, domain1, q1.get("topic"), q1.get("expected_concepts"))
    clusters2 = identify_concept_clusters(text2, domain2, q2.get("topic"), q2.get("expected_concepts"))
    shared_clusters = clusters1.intersection(clusters2)

    tokens1 = extract_technical_tokens(text1)
    tokens2 = extract_technical_tokens(text2)
    jaccard = token_jaccard_similarity(tokens1, tokens2)

    if shared_clusters and is_same_domain:
        # Both questions map to the exact same specific technical concept cluster.
        # Atomic clusters flag automatically; broader clusters require minor technical token overlap (0.15).
        atomic_clusters = {
            "js_event_loop", "python_decorators", "sql_indexing",
            "python_context_managers", "sql_acid_transactions"
        }
        if shared_clusters.intersection(atomic_clusters) or jaccard >= 0.15:
            for cluster in shared_clusters:
                return True, f"Both questions test the same domain concept cluster: '{cluster}'"

    # 5. Token Jaccard threshold (high similarity on technical vocabulary)
    if is_same_domain and jaccard >= 0.50:
        return True, f"High technical token similarity ({jaccard:.2f})"

    # 6. Expected Concepts Overlap
    exp1 = set(clean_text(c) for c in (q1.get("expected_concepts") or []) if clean_text(c))
    exp2 = set(clean_text(c) for c in (q2.get("expected_concepts") or []) if clean_text(c))
    if is_same_domain and exp1 and exp2:
        exp_jaccard = token_jaccard_similarity(exp1, exp2)
        if exp_jaccard >= 0.60:
            return True, f"Substantial expected concepts overlap ({exp_jaccard:.2f})"

    # 7. Topic-level duplicate check if same topic and significant technical overlap
    topic1 = clean_text(q1.get("topic", ""))
    topic2 = clean_text(q2.get("topic", ""))
    if topic1 and topic2 and topic1 == topic2 and is_same_domain:
        if jaccard >= 0.30:
            return True, f"Same topic '{topic1}' with significant technical overlap ({jaccard:.2f})"

    return False, "Distinct concepts"

def is_duplicate_against_history(
    candidate_q: Dict[str, Any],
    history_questions: List[Dict[str, Any]]
) -> Tuple[bool, Optional[str]]:
    """Checks candidate_q against a list of previously delivered questions."""
    for past_q in history_questions:
        is_dup, reason = is_semantic_duplicate(candidate_q, past_q)
        if is_dup:
            return True, reason
    return False, None
