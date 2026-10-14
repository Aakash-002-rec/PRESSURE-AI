import React, { useState, useEffect } from "react";
import { 
  Code2, Play, Send, RefreshCw, Sparkles, CheckCircle2, 
  AlertTriangle, Clock, Zap, Cpu, Terminal, ArrowRight, 
  ChevronRight, BookOpen, Layers, Check, X, RotateCcw
} from "lucide-react";
import { api } from "../api";

export default function CodingView({ user, onGoToInterview, onOpenAuth }) {
  const [problems, setProblems] = useState([]);
  const [selectedProblemId, setSelectedProblemId] = useState(null);
  const [loadingProblems, setLoadingProblems] = useState(true);

  // Editor state
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Execution & feedback results
  const [executionResult, setExecutionResult] = useState(null);
  const [activeTab, setActiveTab] = useState("description"); // 'description', 'testcases', 'result'
  const [revealedHintLevel, setRevealedHintLevel] = useState(0);
  const [autoFillingCode, setAutoFillingCode] = useState(false);
  const [codingNotification, setCodingNotification] = useState("");
  const [codingStatus, setCodingStatus] = useState(null);
  const [loadingNewProblem, setLoadingNewProblem] = useState(false);

  useEffect(() => {
    loadProblems();
  }, []);

  async function loadProblems(mode = null) {
    try {
      setLoadingProblems(true);
      const statusData = await api.coding.getStatus().catch(() => null);
      if (statusData) setCodingStatus(statusData);

      if (statusData?.all_completed) {
        setProblems([]);
        setSelectedProblemId(null);
        return;
      }

      let targetMode = mode;
      // Auto-resume if candidate has in-progress problems and no explicit mode was passed
      // Prevents page refresh/navigation from consuming another unseen question
      if (!targetMode && statusData?.in_progress_count > 0) {
        targetMode = "resume";
      }

      const params = targetMode ? { mode: targetMode, limit: 1 } : { limit: 1 };
      const problemsData = await api.coding.getProblems(params);
      setProblems(problemsData || []);
      if (problemsData && problemsData.length > 0) {
        selectProblem(problemsData[0]);
      } else {
        setSelectedProblemId(null);
      }
    } catch (err) {
      console.error("Failed to load coding problems:", err);
    } finally {
      setLoadingProblems(false);
    }
  }

  async function handleNextProblem() {
    try {
      setLoadingProblems(true);
      const statusData = await api.coding.getStatus().catch(() => null);
      if (statusData) setCodingStatus(statusData);

      // If all 3 are completed:
      if (statusData?.all_completed || statusData?.completed_count >= 3) {
        setProblems([]);
        setSelectedProblemId(null);
        return;
      }

      // If all 3 have been seen (remaining_unseen_count <= 0), do not fetch unseen questions
      if (statusData && statusData.remaining_unseen_count <= 0) {
        if (statusData.has_incomplete) {
          const resumedProbs = await api.coding.getProblems({ mode: "resume", limit: 1 });
          if (resumedProbs && resumedProbs.length > 0) {
            setProblems(resumedProbs);
            selectProblem(resumedProbs[0]);
            setCodingNotification(`Resuming Question ${resumedProbs[0].question_number || 3} of 3: "${resumedProbs[0].title}"`);
            setTimeout(() => setCodingNotification(""), 4000);
            return;
          }
        }
        setProblems([]);
        setSelectedProblemId(null);
        return;
      }

      const nextProbs = await api.coding.getProblems({ mode: "next", limit: 1 });
      const updatedStatus = await api.coding.getStatus().catch(() => null);
      if (updatedStatus) setCodingStatus(updatedStatus);

      if (nextProbs && nextProbs.length > 0) {
        setProblems(nextProbs);
        selectProblem(nextProbs[0]);
        const qNum = nextProbs[0].question_number || (updatedStatus ? updatedStatus.completed_count + 1 : 1);
        setCodingNotification(`✨ Question ${qNum} of 3: "${nextProbs[0].title}"`);
        setTimeout(() => setCodingNotification(""), 4000);
      } else {
        // If pool is exhausted but candidate has remaining slots, try generating
        if (updatedStatus && updatedStatus.remaining_unseen_count > 0 && updatedStatus.completed_count < 3) {
          const genRes = await api.coding.generateProblem().catch(() => null);
          if (genRes) {
            setProblems([genRes]);
            selectProblem(genRes);
            setCodingNotification(`✨ Question ${genRes.question_number || (updatedStatus.completed_count + 1)} of 3: "${genRes.title}"`);
            setTimeout(() => setCodingNotification(""), 4000);
            return;
          }
        }
        setProblems([]);
        setSelectedProblemId(null);
      }
    } catch (err) {
      console.error("Error loading next problem:", err);
    } finally {
      setLoadingProblems(false);
    }
  }

  async function refreshStatus() {
    try {
      const statusData = await api.coding.getStatus();
      if (statusData) setCodingStatus(statusData);
    } catch (err) {
      console.error("Failed to refresh coding status:", err);
    }
  }

  async function handleCheckOrGenerateNew() {
    try {
      setLoadingNewProblem(true);
      await loadProblems();
    } catch (err) {
      await loadProblems();
    } finally {
      setLoadingNewProblem(false);
    }
  }

  function selectProblem(prob) {
    if (!prob) return;
    setSelectedProblemId(prob.id);
    setCode(prob.starter_code || "");
    setExecutionResult(null);
    setRevealedHintLevel(0);
    setActiveTab("description");
  }

  const currentProblem = problems.find((p) => p.id === selectedProblemId);

  // Run code against sample tests
  async function handleRunSample() {
    if (!currentProblem || running) return;
    setRunning(true);
    setActiveTab("result");

    try {
      const res = await api.coding.run({
        problem_id: currentProblem.id,
        code,
        language,
      });
      setExecutionResult(res);
    } catch (err) {
      alert("Execution error: " + err.message);
    } finally {
      setRunning(false);
    }
  }

  // Submit code against all test cases
  async function handleSubmitCode() {
    if (!currentProblem || submitting) return;
    if (!user) {
      if (onOpenAuth) onOpenAuth();
      else alert("Please sign in or click 'Sign In / Demo' at the top right.");
      return;
    }
    setSubmitting(true);
    setActiveTab("result");

    try {
      const res = await api.coding.submit({
        problem_id: currentProblem.id,
        code,
        language,
      });
      setExecutionResult(res);
      refreshStatus();
    } catch (err) {
      alert("Submission error: " + err.message);
    } finally {
      setSubmitting(false);
    }
  }

  // Handle Tab key in textarea for clean 4-space indentation
  function handleKeyDown(e) {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newCode = code.substring(0, start) + "    " + code.substring(end);
      setCode(newCode);
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 4;
      }, 0);
    }
  }

  const VERIFIED_SOLUTIONS = {
    1: `def factorial(n: int) -> int:
    # Proper recursive implementation with boundary and edge validation
    if n < 0:
        raise ValueError('n must be non-negative')
    if n <= 1:
        return 1
    return n * factorial(n - 1)
`,
    2: `def fibonacci(n: int) -> int:
    # Optimal implementation handling edge cases and negative input
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
`,
    3: `from typing import List

def two_sum(nums: List[int], target: int) -> List[int]:
    # Single-pass hash map for optimal O(n) pair discovery
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
`,
    4: `def is_palindrome(s: str) -> bool:
    # Filters alphanumeric characters and performs two-way symmetry check
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]
`,
    5: `def is_valid_parentheses(s: str) -> bool:
    # LIFO stack ensuring correct closing brackets and nesting order
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for char in s:
        if char in mapping.values():
            stack.append(char)
        elif char in mapping:
            if not stack or stack.pop() != mapping[char]:
                return False
        else:
            return False
    return len(stack) == 0
`,
    6: `def count_zeros(nums: list) -> int:
    # Proper recursive count of zeros in list
    if not nums:
        return 0
    return (1 if nums[0] == 0 else 0) + count_zeros(nums[1:])
`,
    7: `def reverse_string(s: str) -> str:
    # Recursive string reversal
    if len(s) <= 1:
        return s
    return reverse_string(s[1:]) + s[0]
`,
    8: `def binary_search(nums: list, target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
`,
    9: `def max_subarray(nums: list) -> int:
    # Kadane's algorithm
    if not nums:
        return 0
    max_so_far = nums[0]
    curr_max = nums[0]
    for x in nums[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)
    return max_so_far
`,
    10: `def climb_stairs(n: int) -> int:
    if n <= 0:
        return 0
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b
`,
    11: `def is_anagram(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)
`,
    12: `def first_uniq_char(s: str) -> int:
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1
`,
    13: `def power(base: int, exp: int) -> int:
    if exp < 0:
        raise ValueError('exp must be non-negative')
    if exp == 0:
        return 1
    return base * power(base, exp - 1)
`
  };

  function getVerifiedSolution(prob) {
    if (!prob) return "";
    if (VERIFIED_SOLUTIONS[prob.id]) return VERIFIED_SOLUTIONS[prob.id];
    const titleLower = (prob.title || "").toLowerCase();
    if (titleLower.includes("zero") || titleLower.includes("count_zeros")) return VERIFIED_SOLUTIONS[6];
    if (titleLower.includes("revers")) return VERIFIED_SOLUTIONS[7];
    if (titleLower.includes("binary") || titleLower.includes("search")) return VERIFIED_SOLUTIONS[8];
    if (titleLower.includes("subarray") || titleLower.includes("kadane")) return VERIFIED_SOLUTIONS[9];
    if (titleLower.includes("stair") || titleLower.includes("climb")) return VERIFIED_SOLUTIONS[10];
    if (titleLower.includes("anagram")) return VERIFIED_SOLUTIONS[11];
    if (titleLower.includes("uniq") || titleLower.includes("non-repeating")) return VERIFIED_SOLUTIONS[12];
    if (titleLower.includes("power")) return VERIFIED_SOLUTIONS[13];
    if (titleLower.includes("factorial")) return VERIFIED_SOLUTIONS[1];
    if (titleLower.includes("fibonacci")) return VERIFIED_SOLUTIONS[2];
    if (titleLower.includes("two sum") || titleLower.includes("target pair")) return VERIFIED_SOLUTIONS[3];
    if (titleLower.includes("palindrome")) return VERIFIED_SOLUTIONS[4];
    if (titleLower.includes("parenthes") || titleLower.includes("bracket")) return VERIFIED_SOLUTIONS[5];
    return "";
  }

  // Quick Demo Answer Helpers for presentation
  async function fillDemoCode(type) {
    if (!currentProblem) return;

    if (type === "weak") {
      if (currentProblem.title.toLowerCase().includes("factorial")) {
        setCode(
          "def factorial(n: int) -> int:\n" +
          "    # Incomplete recursion: misses n <= 1 base case & negative input check\n" +
          "    if n == 1:\n" +
          "        return 1\n" +
          "    return n * factorial(n - 1)\n"
        );
      } else if (currentProblem.title.toLowerCase().includes("fibonacci")) {
        setCode(
          "def fibonacci(n: int) -> int:\n" +
          "    # Missing negative input guard and base zero handling\n" +
          "    return fibonacci(n - 1) + fibonacci(n - 2)\n"
        );
      } else {
        setCode(
          currentProblem.starter_code || "def solution():\n    pass\n"
        );
      }
      setCodingNotification("⚠️ Loaded weak demo solution (triggers adaptive weakness detection)");
      setTimeout(() => setCodingNotification(""), 4000);
      return;
    }

    // 100% optimal strong solution
    setAutoFillingCode(true);
    try {
      let optimalCode = "";
      try {
        const res = await api.coding.getSolution(currentProblem.id);
        if (res && res.solution_code) {
          optimalCode = res.solution_code;
        }
      } catch (e) {
        console.warn("Backend solution fetch error:", e);
      }

      if (!optimalCode) {
        optimalCode = getVerifiedSolution(currentProblem);
      }

      if (optimalCode) {
        setCode(optimalCode);
        setLanguage("python");
        setCodingNotification(`⚡ Auto-filled 100% optimal passing solution for "${currentProblem.title}"!`);
        setTimeout(() => setCodingNotification(""), 4500);
      }
    } catch (err) {
      console.error("Error auto-filling coding solution:", err);
    } finally {
      setAutoFillingCode(false);
    }
  }

  // Authoritative 100% Auto-Solve & Auto-Submit
  async function handleAutoSubmit() {
    if (!currentProblem || submitting || running) return;
    if (!user) {
      if (onOpenAuth) onOpenAuth();
      else alert("Please sign in or select 'Alex Candidate' at the top right.");
      return;
    }

    setSubmitting(true);
    setAutoFillingCode(true);
    setActiveTab("result");

    try {
      let optimalCode = "";
      try {
        const res = await api.coding.getSolution(currentProblem.id);
        if (res && res.solution_code) {
          optimalCode = res.solution_code;
        }
      } catch (e) {
        console.warn("Backend solution fetch error:", e);
      }

      if (!optimalCode) {
        optimalCode = getVerifiedSolution(currentProblem);
      }

      if (!optimalCode) {
        optimalCode = currentProblem.starter_code || "";
      }

      // 1. Populate the code editor with the 100% optimal passing code
      setCode(optimalCode);
      setLanguage("python");

      // 2. Submit directly to sandbox runner
      const res = await api.coding.submit({
        problem_id: currentProblem.id,
        code: optimalCode,
        language: "python"
      });

      setExecutionResult(res);
      await refreshStatus();

      if (res.correctness === 100) {
        setCodingNotification(`⚡ 100% Optimal Solution Auto-Submitted & Accepted (${res.passed_count}/${res.total_count} Passed)!`);
      } else {
        setCodingNotification(`Auto-submitted: ${res.passed_count}/${res.total_count} test cases passed.`);
      }
      setTimeout(() => setCodingNotification(""), 5000);
    } catch (err) {
      alert("Auto-Submit error: " + err.message);
    } finally {
      setSubmitting(false);
      setAutoFillingCode(false);
    }
  }

  if (loadingProblems) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Loading Coding Arena...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-fade-in space-y-6">
      {/* Top Banner */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Placement Stage 2
            </span>
            <span className="text-xs text-slate-400 font-mono">Isolated Python Runner</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-black text-white">Coding Assessment Session</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Implement algorithms with real-time test execution. Weaknesses diagnosed here (e.g. Recursion) automatically feed into your <strong>AI Mock Interview</strong>!
          </p>
        </div>

        {/* Active Problem Chip & Navigation Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {codingStatus && (
            <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-[11px] font-mono">
              <span className="text-indigo-400 font-bold">
                Question {codingStatus.all_completed ? 3 : (currentProblem?.question_number || (codingStatus.completed_count ? Math.min(3, codingStatus.completed_count + 1) : 1))} of 3
              </span>
              <span className="text-slate-600">•</span>
              <span className="text-emerald-400 font-bold">✓ {codingStatus.completed_count}/3 Solved</span>
              <span className="text-slate-600">•</span>
              <span className="text-amber-400 font-bold">⏳ {codingStatus.in_progress_count} In Progress</span>
            </div>
          )}

          {currentProblem && (
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-bold text-white shadow-inner">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-400 text-[11px]">Question {currentProblem.question_number || (codingStatus?.completed_count ? Math.min(3, codingStatus.completed_count + 1) : 1)} of 3:</span>
              <span className="text-emerald-300 font-mono">[{currentProblem.category}] {currentProblem.title}</span>
            </div>
          )}

          <button
            onClick={handleNextProblem}
            disabled={loadingProblems || (codingStatus && codingStatus.remaining_unseen_count <= 0 && !codingStatus.has_incomplete)}
            title={codingStatus && codingStatus.remaining_unseen_count <= 0 ? "3-question session limit reached" : "Move to next problem"}
            className="px-3.5 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            {loadingProblems ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ChevronRight className="w-3.5 h-3.5 text-emerald-400" />}
            {codingStatus?.completed_count >= 3 ? "View Completion" : "Next Problem"}
          </button>

          <button
            onClick={onGoToInterview}
            className="px-4 py-2.5 bg-orange-500/15 hover:bg-orange-500/25 border border-orange-500/30 text-orange-400 font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors"
          >
            Proceed to AI Interview <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Warning Banner when viewing incomplete problems after 3-question limit reached */}
      {problems.length > 0 && !codingStatus?.has_unseen && codingStatus?.has_incomplete && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-amber-300">
                You've received all 3 session questions, but some are still incomplete.
              </h4>
              <p className="text-xs text-slate-300 mt-0.5">
                Solved: <strong className="text-emerald-400">{codingStatus?.completed_count || 0} of 3</strong> • 
                In Progress: <strong className="text-amber-400">{codingStatus?.in_progress_count || 0}</strong> • 
                Remaining to Solve: <strong className="text-slate-400">{Math.max(0, 3 - (codingStatus?.completed_count || 0))}</strong>
              </p>
            </div>
          </div>
          <button
            onClick={() => loadProblems("resume")}
            className="px-3.5 py-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 font-bold text-xs rounded-xl flex items-center justify-center gap-1.5 transition-colors shrink-0"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Resume Incomplete Problems
          </button>
        </div>
      )}

      {problems.length === 0 && !loadingProblems ? (
        codingStatus?.all_completed ? (
          /* State 1: Genuine Completion Screen */
          <div className="glass-panel rounded-3xl p-10 border border-emerald-500/30 text-center space-y-4 my-8 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/10">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h3 className="text-2xl font-bold text-white">Coding Assessment Completed — You have successfully completed all 3 questions.</h3>
            <p className="text-sm text-slate-300 max-w-lg mx-auto">
              Persistent verification confirms you have successfully passed all 3 required coding challenges in this assessment session!
            </p>
            <div className="flex items-center justify-center gap-6 py-2">
              <div className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-center min-w-[120px]">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Questions Completed</span>
                <span className="text-lg font-extrabold text-emerald-400">3 of 3</span>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-center min-w-[120px]">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">In Progress</span>
                <span className="text-lg font-extrabold text-slate-400">0</span>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-center min-w-[120px]">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Remaining</span>
                <span className="text-lg font-extrabold text-slate-400">0</span>
              </div>
            </div>
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={onGoToInterview}
                className="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-orange-500/25"
              >
                Proceed to AI Interview <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        ) : codingStatus?.has_incomplete ? (
          /* State 2: Seen All 3 Problems But Incomplete */
          <div className="glass-panel rounded-3xl p-10 border border-amber-500/30 text-center space-y-4 my-8 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto shadow-lg shadow-amber-500/10">
              <AlertTriangle className="w-8 h-8" />
            </div>
            <h3 className="text-2xl font-bold text-white">Coding Assessment Incomplete — {codingStatus?.completed_count || 0} of 3 Questions Solved</h3>
            <p className="text-sm text-slate-300 max-w-lg mx-auto">
              You have received all 3 coding assessment challenges for this session, but you have not yet passed all of them. Resume your incomplete challenges to finish the assessment.
            </p>
            <div className="flex items-center justify-center gap-6 py-2">
              <div className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-center min-w-[120px]">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Questions Completed</span>
                <span className="text-lg font-extrabold text-emerald-400">{codingStatus?.completed_count || 0} of 3</span>
              </div>
              <div className="px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-center min-w-[120px]">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">Remaining to Solve</span>
                <span className="text-lg font-extrabold text-amber-400">{Math.max(0, 3 - (codingStatus?.completed_count || 0))}</span>
              </div>
            </div>
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={() => loadProblems("resume")}
                className="px-5 py-2.5 bg-orange-500 hover:bg-orange-600 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-orange-500/25"
              >
                <RotateCcw className="w-4 h-4" /> Resume Incomplete Problems
              </button>
            </div>
          </div>
        ) : (
          /* State 3: Start / Empty Pool */
          <div className="glass-panel rounded-3xl p-10 border border-slate-800 text-center space-y-4 my-8 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-slate-800/50 border border-slate-700 text-slate-400 flex items-center justify-center mx-auto">
              <Layers className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white">Coding Assessment Session</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              Solve exactly 3 algorithm questions to complete your technical coding evaluation.
            </p>
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={() => loadProblems()}
                className="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-emerald-500/25"
              >
                <RefreshCw className="w-4 h-4" /> Start Coding Assessment
              </button>
            </div>
          </div>
        )
      ) : (
      /* Main Coding IDE Split View */
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Problem Details & Feedback (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Sub-tab Navigation */}
          <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
            <button
              onClick={() => setActiveTab("description")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === "description"
                  ? "bg-emerald-500 text-white shadow-md shadow-emerald-500/20"
                  : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
              }`}
            >
              Problem Statement
            </button>

            <button
              onClick={() => setActiveTab("result")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                activeTab === "result"
                  ? "bg-emerald-500 text-white shadow-md shadow-emerald-500/20"
                  : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              Test Results {executionResult && `(${executionResult.passed_count}/${executionResult.total_count})`}
            </button>
          </div>

          {/* TAB 1: PROBLEM DESCRIPTION */}
          {activeTab === "description" && currentProblem && (
            <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4 animate-fade-in">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-extrabold px-2.5 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono">
                    Question {currentProblem.question_number || (codingStatus?.completed_count ? Math.min(3, codingStatus.completed_count + 1) : 1)} of 3
                  </span>
                  <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {currentProblem.category}
                  </span>
                </div>
                <span className="text-xs font-semibold text-slate-500">
                  Difficulty: {currentProblem.difficulty}
                </span>
              </div>

              <h3 className="text-xl font-bold text-white">{currentProblem.title}</h3>

              <div className="text-xs md:text-sm text-slate-300 whitespace-pre-line leading-relaxed font-normal">
                {currentProblem.description}
              </div>

              {currentProblem.constraints && (
                <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-xs text-slate-400">
                  <span className="font-bold text-slate-300 block mb-0.5">Constraints:</span>
                  {currentProblem.constraints}
                </div>
              )}

              {/* Progressive Hints Section */}
              <div className="pt-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    AI Progressive Hints
                  </span>
                  {revealedHintLevel < (currentProblem.hints?.length || 0) && (
                    <button
                      onClick={() => setRevealedHintLevel((prev) => prev + 1)}
                      className="text-[11px] px-2.5 py-1 bg-amber-500/15 text-amber-300 border border-amber-500/30 rounded-lg font-semibold hover:bg-amber-500/25 transition-colors"
                    >
                      Unlock Hint {revealedHintLevel + 1}
                    </button>
                  )}
                </div>

                {revealedHintLevel > 0 ? (
                  <div className="space-y-2">
                    {currentProblem.hints.slice(0, revealedHintLevel).map((h, hIdx) => (
                      <div key={hIdx} className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs text-amber-200 leading-relaxed">
                        <span className="font-bold text-amber-400 block mb-0.5">Hint {hIdx + 1}:</span>
                        {h}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[11px] text-slate-500 italic">
                    Stuck? Click "Unlock Hint" to get progressive conceptual guidance without giving away the full answer.
                  </p>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: EXECUTION RESULT & AI FEEDBACK */}
          {activeTab === "result" && (
            <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-5 animate-fade-in">
              {!executionResult ? (
                <div className="text-center py-12 text-slate-500 text-xs">
                  <Terminal className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                  Click "Run Code" or "Submit Solution" to inspect compilation and test case execution.
                </div>
              ) : (
                <>
                  {/* SECTION 1: OBJECTIVE EXECUTION RESULT (AUTHORITATIVE) */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="text-[10px] uppercase font-bold text-slate-400 block">
                            Objective Sandbox Result
                          </span>
                          <span className="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                            Authoritative
                          </span>
                        </div>
                        <h4 className={`text-xl font-black mt-0.5 ${
                          executionResult.correctness === 100.0 ? "text-emerald-400" :
                          executionResult.correctness >= 50.0 ? "text-orange-400" : "text-red-400"
                        }`}>
                          {executionResult.status === "passed" ? "Accepted (100%)" : `Failed (${executionResult.correctness}%)`}
                        </h4>
                      </div>

                      <div className="text-right">
                        <span className="text-xs font-mono font-bold text-white block">
                          {executionResult.passed_count} / {executionResult.total_count} Passed
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {executionResult.duration_ms ? `${executionResult.duration_ms} ms` : "Sandbox verified"}
                        </span>
                      </div>
                    </div>

                    {/* Test Cases Checklist */}
                    <div>
                      <span className="text-xs font-bold text-white block mb-2">Test Case Results:</span>
                      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                        {executionResult.test_results?.map((t, idx) => (
                          <div
                            key={idx}
                            className={`p-2.5 rounded-xl border text-xs flex items-center justify-between gap-2 ${
                              t.passed
                                ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300"
                                : "bg-red-500/10 border-red-500/20 text-red-300"
                            }`}
                          >
                            <div className="flex items-center gap-2">
                              {t.passed ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <X className="w-3.5 h-3.5 text-red-400" />}
                              <span className="font-semibold">{t.description}</span>
                            </div>
                            <span className="font-mono text-[11px] opacity-80">
                              {t.passed ? "Passed" : "Failed"}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* 100% Accepted Success Action Banner */}
                    {executionResult.correctness === 100.0 && (
                      <div className="p-3.5 rounded-2xl bg-gradient-to-r from-emerald-500/20 to-teal-500/10 border border-emerald-500/40 flex items-center justify-between gap-3 animate-fade-in shadow-lg shadow-emerald-500/10">
                        <div className="flex items-center gap-2.5">
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
                          <div>
                            <span className="text-xs font-bold text-white block">100% Optimal Solution Accepted!</span>
                            <span className="text-[11px] text-emerald-300">All test cases passed. Ready for the next challenge.</span>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={handleNextProblem}
                          className="px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs rounded-xl flex items-center gap-1 shadow-md shadow-emerald-500/30 transition-all shrink-0"
                        >
                          {(codingStatus?.completed_count >= 3 || (codingStatus?.completed_count === 2 && executionResult?.correctness === 100) || currentProblem?.question_number === 3)
                            ? "Finish Coding Assessment"
                            : "Next Challenge"} <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>

                  {/* SECTION 2: AI EVALUATION (GEMINI) */}
                  <div className="pt-4 border-t border-slate-800 space-y-3.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                          <Sparkles className="w-3.5 h-3.5" />
                        </div>
                        <span className="text-xs font-bold text-indigo-300 uppercase tracking-wide">
                          AI Evaluator Analysis
                        </span>
                      </div>
                      {executionResult.ai_evaluation?.source === "gemini" && (
                        <span className="text-[10px] uppercase font-bold text-indigo-400">
                          Powered by Gemini
                        </span>
                      )}
                    </div>

                    {/* Safe Fallback Notice if Gemini was temporarily rate-limited */}
                    {executionResult.ai_evaluation?.fallback_notice && (
                      <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-300 flex items-center gap-2">
                        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                        <span>{executionResult.ai_evaluation.fallback_notice}</span>
                      </div>
                    )}

                    {/* Overall Assessment */}
                    {executionResult.ai_evaluation?.overall_assessment && (
                      <div className="p-3 bg-indigo-950/20 rounded-xl border border-indigo-500/20 text-xs text-slate-200 leading-relaxed">
                        <span className="font-bold text-indigo-300 block mb-0.5">Overall Assessment:</span>
                        {executionResult.ai_evaluation.overall_assessment}
                      </div>
                    )}

                    {/* Explanation */}
                    {executionResult.ai_evaluation?.explanation && (
                      <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed">
                        <span className="font-bold text-slate-200 block mb-0.5">Why Solution Passed / Failed:</span>
                        {executionResult.ai_evaluation.explanation}
                      </div>
                    )}

                    {/* Complexity Strip */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2.5 bg-slate-950 rounded-xl border border-slate-800">
                        <span className="text-[10px] text-slate-500 uppercase block font-semibold">Time Complexity</span>
                        <span className="font-mono font-bold text-slate-200">
                          {executionResult.ai_evaluation?.time_complexity || executionResult.time_complexity || "O(n)"}
                        </span>
                      </div>
                      <div className="p-2.5 bg-slate-950 rounded-xl border border-slate-800">
                        <span className="text-[10px] text-slate-500 uppercase block font-semibold">Space Complexity</span>
                        <span className="font-mono font-bold text-slate-200">
                          {executionResult.ai_evaluation?.space_complexity || executionResult.space_complexity || "O(1)"}
                        </span>
                      </div>
                    </div>

                    {/* Conceptual Mistakes */}
                    {executionResult.ai_evaluation?.conceptual_mistakes && executionResult.ai_evaluation.conceptual_mistakes.length > 0 && (
                      <div className="p-3 bg-red-950/20 border border-red-500/20 rounded-xl text-xs space-y-1">
                        <span className="font-bold text-red-400 block">Conceptual Mistakes:</span>
                        {executionResult.ai_evaluation.conceptual_mistakes.map((m, idx) => (
                          <div key={idx} className="text-slate-300 flex items-start gap-1.5">
                            <span className="text-red-400 font-bold">•</span>
                            <span>{m}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Edge Cases Missed */}
                    {executionResult.ai_evaluation?.edge_cases_missed && executionResult.ai_evaluation.edge_cases_missed.length > 0 && (
                      <div className="p-3 bg-amber-950/20 border border-amber-500/20 rounded-xl text-xs space-y-1">
                        <span className="font-bold text-amber-400 block">Edge Cases & Invariants:</span>
                        {executionResult.ai_evaluation.edge_cases_missed.map((e, idx) => (
                          <div key={idx} className="text-slate-300 flex items-start gap-1.5">
                            <span className="text-amber-400 font-bold">•</span>
                            <span>{e}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Algorithmic Improvements */}
                    {executionResult.ai_evaluation?.algorithmic_improvements && executionResult.ai_evaluation.algorithmic_improvements.length > 0 && (
                      <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-1">
                        <span className="font-bold text-emerald-400 block">Algorithmic Improvement Suggestions:</span>
                        {executionResult.ai_evaluation.algorithmic_improvements.map((a, idx) => (
                          <div key={idx} className="text-slate-300 flex items-start gap-1.5">
                            <span className="text-emerald-400 font-bold">✓</span>
                            <span>{a}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Recommended Topic to Practice */}
                    {executionResult.ai_evaluation?.recommended_topic && (
                      <div className="p-2.5 bg-indigo-950/30 border border-indigo-500/20 rounded-xl text-xs flex items-center justify-between">
                        <span className="text-slate-400">Recommended Topic to Practice:</span>
                        <span className="font-bold text-indigo-300 font-mono">{executionResult.ai_evaluation.recommended_topic}</span>
                      </div>
                    )}

                    {/* Personalized Feedback (or default ai_feedback) */}
                    {(executionResult.ai_evaluation?.personalized_feedback || (!executionResult.ai_evaluation && executionResult.ai_feedback)) && (
                      <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300 leading-relaxed">
                        <span className="font-bold text-emerald-400 block mb-1">Personalized Feedback:</span>
                        {executionResult.ai_evaluation?.personalized_feedback || executionResult.ai_feedback}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Code Editor & Controls (7 cols) */}
        <div className="lg:col-span-7 space-y-3">
          {/* Editor Header Bar */}
          <div className="glass-panel p-3.5 rounded-2xl border border-slate-800 flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-bold text-white">Solution Editor</span>
              <span className="text-[10px] text-slate-500 font-mono">(Tab = 4 spaces)</span>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-2.5 py-1 bg-slate-950 border border-slate-800 rounded-lg text-xs font-bold text-emerald-400 outline-none"
              >
                <option value="python">Python 3</option>
                <option value="javascript">JavaScript (ES6)</option>
                <option value="cpp">C++ 20</option>
                <option value="java">Java 17</option>
              </select>

              <button
                type="button"
                onClick={() => setCode(currentProblem?.starter_code || "")}
                title="Reset Starter Code"
                className="px-2.5 py-1 text-[11px] text-slate-400 hover:text-white bg-slate-900 border border-slate-800 rounded-lg transition-colors flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" /> Reset
              </button>
            </div>
          </div>

          {/* Notification banner */}
          {codingNotification && (
            <div className="p-3 bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 rounded-xl text-xs font-semibold flex items-center gap-2 animate-fade-in shadow-md">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{codingNotification}</span>
            </div>
          )}

          {/* Code Textarea Editor */}
          <div className="relative rounded-2xl overflow-hidden border border-slate-800 bg-slate-950 shadow-2xl">
            <textarea
              rows={16}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onKeyDown={handleKeyDown}
              spellCheck={false}
              className="w-full p-4 bg-slate-950 text-slate-100 font-mono text-xs md:text-sm outline-none resize-y leading-relaxed border-none focus:ring-1 focus:ring-emerald-500/50"
              placeholder="Write your solution here..."
            />
          </div>

          {/* Quick Demo Helpers & Action Controls */}
          <div className="p-3 bg-slate-950/70 rounded-2xl border border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
            {/* Demo Pre-fill helpers */}
            <div className="flex flex-wrap items-center gap-2 text-[11px]">
              <span className="text-slate-500 font-semibold">⚡ Solution Helpers:</span>
              <button
                type="button"
                onClick={() => fillDemoCode("weak")}
                className="px-2.5 py-1 rounded bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 font-semibold transition-colors"
              >
                Fill Weak (42%)
              </button>
              <button
                type="button"
                onClick={() => fillDemoCode("strong")}
                disabled={autoFillingCode}
                className="px-2.5 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 font-semibold transition-all flex items-center gap-1 disabled:opacity-50"
              >
                <Sparkles className="w-3 h-3 text-amber-300" />
                {autoFillingCode ? "Fetching..." : "Auto-Fill 100%"}
              </button>
              <button
                type="button"
                onClick={handleAutoSubmit}
                disabled={autoFillingCode || submitting || running}
                title="Automatically fetch 100% optimal passing solution and submit to sandbox"
                className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-emerald-500 hover:from-amber-600 hover:to-emerald-600 text-white font-black text-xs transition-all shadow-md shadow-orange-500/20 flex items-center gap-1.5 disabled:opacity-50"
              >
                <Zap className="w-3.5 h-3.5 fill-white text-white" />
                {submitting && autoFillingCode ? "Auto-Submitting..." : "⚡ Auto-Submit (100% Passing)"}
              </button>
            </div>

            {/* Run & Submit buttons */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleRunSample}
                disabled={running || submitting}
                className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors disabled:opacity-50"
              >
                {running ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
                Run Code
              </button>

              <button
                type="button"
                onClick={handleSubmitCode}
                disabled={running || submitting}
                className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-xl text-xs font-extrabold shadow-lg shadow-emerald-600/25 flex items-center gap-1.5 transition-all disabled:opacity-50"
              >
                {submitting && !autoFillingCode ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                Submit Code
              </button>

              {executionResult?.correctness === 100 && (
                <button
                  type="button"
                  onClick={handleNextProblem}
                  className="px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-slate-950 font-black rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-md shadow-emerald-500/20"
                >
                  {(codingStatus?.completed_count >= 3 || (codingStatus?.completed_count === 2 && executionResult?.correctness === 100) || currentProblem?.question_number === 3)
                    ? "Finish Coding Assessment"
                    : "Next Problem"} <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
      )}
    </div>
  );
}
