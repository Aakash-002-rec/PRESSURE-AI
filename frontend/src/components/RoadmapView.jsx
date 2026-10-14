import React, { useState, useEffect } from "react";
import { 
  Target, BookOpen, CheckCircle2, RotateCcw, Sparkles, 
  ArrowRight, ChevronRight, Check, Clock, AlertTriangle, 
  Layers, BrainCircuit, RefreshCw, Send, HelpCircle
} from "lucide-react";
import { api } from "../api";

export default function RoadmapView({ initialTopic = "Recursion", onRetakeInterview }) {
  const [selectedTopic, setSelectedTopic] = useState(initialTopic);
  const [roadmapTasks, setRoadmapTasks] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(true);

  // Practice state
  const [practiceQuestions, setPracticeQuestions] = useState([]);
  const [practiceDifficulty, setPracticeDifficulty] = useState("All");
  const [practiceAnswers, setPracticeAnswers] = useState({});
  const [practiceResult, setPracticeResult] = useState(null);
  const [submittingPractice, setSubmittingPractice] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(false);

  // Active view tab: 'roadmap' or 'practice'
  const [viewMode, setViewMode] = useState("roadmap");

  useEffect(() => {
    loadRoadmap(selectedTopic);
    loadPractice(selectedTopic, practiceDifficulty);
  }, [selectedTopic]);

  async function loadRoadmap(topic) {
    try {
      setLoadingTasks(true);
      const data = await api.assessment.getRoadmap(topic);
      setRoadmapTasks(data);
    } catch (err) {
      console.error("Failed to load roadmap tasks:", err);
    } finally {
      setLoadingTasks(false);
    }
  }

  async function loadPractice(topic, diff) {
    try {
      setLoadingQuestions(true);
      setPracticeResult(null);
      setPracticeAnswers({});
      const data = await api.assessment.getPractice(topic, diff === "All" ? "" : diff);
      setPracticeQuestions(data);
    } catch (err) {
      console.error("Failed to load practice questions:", err);
    } finally {
      setLoadingQuestions(false);
    }
  }

  async function handleToggleStatus(taskId, currentStatus) {
    const nextStatus = currentStatus === "not_started" ? "in_progress" : currentStatus === "in_progress" ? "completed" : "not_started";
    try {
      await api.assessment.updateRoadmap({ task_id: taskId, status: nextStatus });
      setRoadmapTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: nextStatus } : t))
      );
    } catch (err) {
      alert("Error updating task: " + err.message);
    }
  }

  async function handleSubmitPractice() {
    if (Object.keys(practiceAnswers).length === 0) {
      alert("Please answer at least one practice question before submitting.");
      return;
    }
    setSubmittingPractice(true);

    const formatted = Object.entries(practiceAnswers).map(([qId, ansIdx]) => ({
      question_id: parseInt(qId),
      selected_option: ansIdx,
    }));

    try {
      const res = await api.assessment.submitPractice({
        topic: selectedTopic,
        difficulty: practiceDifficulty,
        answers: formatted,
      });
      setPracticeResult(res);
    } catch (err) {
      alert("Submission error: " + err.message);
    } finally {
      setSubmittingPractice(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in space-y-8">
      {/* Header Banner */}
      <div className="glass-panel rounded-3xl p-8 border border-slate-800 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-red-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                Targeted Remediation & Retest
              </span>
              <span className="text-xs text-slate-400 font-mono">5-Stage Structured Curriculum</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-white">Personalized Learning Roadmap</h2>
            <p className="text-xs text-slate-300 mt-1 max-w-xl">
              Systematically eliminate conceptual deficits diagnosed during your previous coding and AI interview sessions.
            </p>
          </div>

          {/* Topic Switcher */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-400">Target Concept:</span>
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              className="p-2.5 bg-slate-950 border border-slate-700 rounded-xl text-xs font-bold text-white outline-none focus:border-red-500"
            >
              <option value="Recursion">Recursion (Primary Weakness: 42%)</option>
              <option value="Data Interpretation">Data Interpretation (Aptitude: 48%)</option>
            </select>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-2 mt-6 pt-4 border-t border-slate-800">
          <button
            onClick={() => setViewMode("roadmap")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              viewMode === "roadmap"
                ? "bg-red-500 text-white shadow-lg shadow-red-500/20"
                : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
            }`}
          >
            5-Stage Action Roadmap
          </button>
          <button
            onClick={() => setViewMode("practice")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              viewMode === "practice"
                ? "bg-red-500 text-white shadow-lg shadow-red-500/20"
                : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
            }`}
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Targeted Practice Exercises (3 Easy, 3 Med, 2 Adv)
          </button>
        </div>
      </div>

      {/* WHY YOU ARE WEAK & WHAT TO LEARN CALLOUT */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Why considered weak */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-red-400 uppercase tracking-wide">
            <AlertTriangle className="w-4 h-4" />
            Why You Are Considered Weak: {selectedTopic}
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {selectedTopic === "Recursion" ? (
              <>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 font-bold">•</span>
                  <span><strong>Missing Base Cases:</strong> Omitted termination condition in coding session, causing call stack exhaustion.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 font-bold">•</span>
                  <span><strong>Call Stack Tracing:</strong> Struggled to articulate how stack frames unwind in LIFO order during the AI interview.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 font-bold">•</span>
                  <span><strong>Boundary Handling:</strong> Failed negative integer edge cases and boundary parameters.</span>
                </li>
              </>
            ) : (
              <>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 font-bold">•</span>
                  <span><strong>Data Interpretation Speed:</strong> Slow graph derivation during timed aptitude assessment.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-400 font-bold">•</span>
                  <span><strong>Ratio & Percent Multipliers:</strong> Calculation errors on multi-year compound percentage changes.</span>
                </li>
              </>
            )}
          </ul>
        </div>

        {/* What to learn */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-orange-400 uppercase tracking-wide">
            <Sparkles className="w-4 h-4" />
            Essential Concepts to Master
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {selectedTopic === "Recursion" ? (
              <>
                <li className="flex items-center gap-2">
                  <span className="text-orange-400 font-bold">1.</span>
                  <span><strong>Base Condition Guard:</strong> Always handle terminating condition (n &lt;= 1) before recursive calls.</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-orange-400 font-bold">2.</span>
                  <span><strong>Call Stack Mechanics:</strong> Local variable allocation per stack frame and unwinding returns.</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-orange-400 font-bold">3.</span>
                  <span><strong>Memoization / Cache:</strong> Preventing O(2^n) exponential tree branching using lookup tables.</span>
                </li>
              </>
            ) : (
              <>
                <li className="flex items-center gap-2">
                  <span className="text-orange-400 font-bold">1.</span>
                  <span><strong>Quick Percentage Multipliers:</strong> Decimal fraction conversions for rapid mental estimates.</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-orange-400 font-bold">2.</span>
                  <span><strong>Bar & Pie Chart Extraction:</strong> Reading 360-degree sector allocations and dual-axis graphs.</span>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>

      {/* VIEW 1: 5-STAGE ROADMAP */}
      {viewMode === "roadmap" && (
        <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6 animate-fade-in">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-xl font-bold text-white">Your Step-by-Step Curriculum</h3>
            <span className="text-xs text-slate-500">Click status badge to toggle task state</span>
          </div>

          <div className="space-y-4">
            {roadmapTasks.map((t) => {
              const isCompleted = t.status === "completed";
              const isInProgress = t.status === "in_progress";

              return (
                <div
                  key={t.id}
                  className={`p-5 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                    isCompleted
                      ? "bg-emerald-950/20 border-emerald-500/30"
                      : isInProgress
                      ? "bg-orange-950/20 border-orange-500/30"
                      : "bg-slate-950/70 border-slate-800/80"
                  }`}
                >
                  <div className="flex items-start gap-3.5">
                    <span className={`w-8 h-8 rounded-xl font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5 ${
                      isCompleted
                        ? "bg-emerald-500 text-white"
                        : isInProgress
                        ? "bg-orange-500 text-white"
                        : "bg-slate-900 text-slate-400 border border-slate-800"
                    }`}>
                      {t.stage_number}
                    </span>
                    <div>
                      <h4 className="text-sm font-bold text-white mb-1">{t.title}</h4>
                      <p className="text-xs text-slate-400 leading-relaxed">{t.objective}</p>
                    </div>
                  </div>

                  {/* Interactive Status Toggle Badge */}
                  <button
                    type="button"
                    onClick={() => handleToggleStatus(t.id, t.status)}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 self-start sm:self-auto transition-all ${
                      isCompleted
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 hover:bg-emerald-500/30"
                        : isInProgress
                        ? "bg-orange-500/20 text-orange-400 border border-orange-500/40 hover:bg-orange-500/30"
                        : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-white"
                    }`}
                  >
                    {isCompleted ? (
                      <>
                        <Check className="w-3.5 h-3.5" /> Completed
                      </>
                    ) : isInProgress ? (
                      <>
                        <Clock className="w-3.5 h-3.5 animate-spin" /> In Progress
                      </>
                    ) : (
                      "Not Started"
                    )}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Bottom Retest Action */}
          <div className="p-4 bg-orange-950/20 border border-orange-500/30 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4 mt-6">
            <div className="text-xs text-slate-300">
              <span className="font-bold text-white block mb-0.5">Ready to validate improvement?</span>
              Launch practice drills or retake the adaptive interview to verify score increase.
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode("practice")}
                className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold border border-slate-700 transition-colors"
              >
                Solve Practice Exercises
              </button>
              <button
                onClick={onRetakeInterview}
                className="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-amber-600 text-white rounded-xl text-xs font-bold shadow-lg shadow-orange-500/25 flex items-center gap-1.5 transition-all"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Retake AI Interview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: TARGETED PRACTICE EXERCISES */}
      {viewMode === "practice" && (
        <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-slate-800">
            <div>
              <h3 className="text-xl font-bold text-white">Targeted Practice Drills: {selectedTopic}</h3>
              <p className="text-xs text-slate-400">Complete these exercises to recalculate your topic score.</p>
            </div>

            {/* Filter */}
            <div className="flex items-center gap-2">
              {["All", "Easy", "Medium", "Advanced"].map((d) => (
                <button
                  key={d}
                  onClick={() => {
                    setPracticeDifficulty(d);
                    loadPractice(selectedTopic, d);
                  }}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                    practiceDifficulty === d
                      ? "bg-red-500 text-white shadow-sm"
                      : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-white"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Practice Questions List */}
          <div className="space-y-6">
            {practiceQuestions.map((pq, idx) => {
              const userAns = practiceAnswers[pq.id];
              return (
                <div key={pq.id} className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-white">Question {idx + 1}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      pq.difficulty === "Easy" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                      pq.difficulty === "Medium" ? "bg-orange-500/10 text-orange-400 border border-orange-500/20" :
                      "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                    }`}>
                      {pq.difficulty}
                    </span>
                  </div>

                  <p className="text-xs md:text-sm text-slate-200 font-medium leading-relaxed">
                    {pq.question}
                  </p>

                  {/* Options */}
                  <div className="space-y-2 pt-1">
                    {pq.options?.map((opt, optIdx) => {
                      const isSel = userAns === optIdx;
                      return (
                        <div
                          key={optIdx}
                          onClick={() => setPracticeAnswers((prev) => ({ ...prev, [pq.id]: optIdx }))}
                          className={`p-3 rounded-xl border text-xs cursor-pointer transition-all flex items-center gap-3 ${
                            isSel
                              ? "bg-red-500/20 border-red-500 text-white shadow-sm"
                              : "bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700"
                          }`}
                        >
                          <span className={`w-5 h-5 rounded flex items-center justify-center font-bold text-[10px] ${
                            isSel ? "bg-red-500 text-white" : "bg-slate-950 text-slate-500"
                          }`}>
                            {String.fromCharCode(65 + optIdx)}
                          </span>
                          <span>{opt}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Submit practice button */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Answered: {Object.keys(practiceAnswers).length} of {practiceQuestions.length}
            </span>

            <button
              onClick={handleSubmitPractice}
              disabled={submittingPractice}
              className="px-6 py-2.5 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-red-500/25 flex items-center gap-1.5 transition-all"
            >
              {submittingPractice ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              Submit Practice Answers
            </button>
          </div>

          {/* PRACTICE RESULTS BANNER */}
          {practiceResult && (
            <div className="p-6 rounded-2xl bg-slate-900 border-2 border-emerald-500/40 space-y-4 animate-fade-in shadow-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                  <div>
                    <h4 className="text-base font-bold text-white">Practice Drills Evaluated!</h4>
                    <p className="text-xs text-emerald-400 font-semibold">{practiceResult.improvement_message}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-2xl font-black text-white">{practiceResult.score}%</span>
                  <span className="text-[10px] text-slate-400 block uppercase font-bold">Accuracy</span>
                </div>
              </div>

              <div className="p-3.5 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300">
                Updated Topic Mastery on <strong>{practiceResult.topic}</strong>:{" "}
                <span className="text-emerald-400 font-bold">{practiceResult.updated_topic_score}%</span> (reflected across your dashboard and progress charts).
              </div>

              <button
                onClick={onRetakeInterview}
                className="w-full py-3 bg-gradient-to-r from-orange-500 to-amber-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-orange-500/20 flex items-center justify-center gap-2"
              >
                Launch Retest on PRESSURE-AI Interview Arena <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
