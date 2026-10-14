import React, { useState, useEffect } from "react";
import { 
  Play, Sparkles, Sliders, Layers, Target, Compass, Flame, 
  Code2, CheckCircle2, ChevronRight, Zap, RefreshCw
} from "lucide-react";
import { api } from "../api";

export default function SetupView({ onStartInterview, user, onOpenAuth }) {
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Form selections
  const [selectedDomainId, setSelectedDomainId] = useState(null);
  const [selectedTopicId, setSelectedTopicId] = useState("");
  const [difficulty, setDifficulty] = useState("Intermediate");
  const [interviewType, setInterviewType] = useState("Mixed");
  const [totalQuestions, setTotalQuestions] = useState(10);

  useEffect(() => {
    fetchDomains();
  }, []);

  async function fetchDomains() {
    try {
      setLoading(true);
      const data = await api.domains.getAll();
      setDomains(data);
      if (data && data.length > 0) {
        // Default to Python (per Demo Scenario)
        const py = data.find((d) => d.name.toLowerCase() === "python") || data[0];
        setSelectedDomainId(py.id);
      }
    } catch (err) {
      setError("Failed to load interview domains. Please check if the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  const currentDomain = domains.find((d) => d.id === selectedDomainId);

  async function handleLaunch() {
    if (!user) {
      onOpenAuth();
      return;
    }
    if (!selectedDomainId) return;

    setSubmitting(true);
    setError(null);

    try {
      const interview = await api.interviews.create({
        domain_id: selectedDomainId,
        topic_id: selectedTopicId ? parseInt(selectedTopicId) : null,
        difficulty,
        interview_type: interviewType,
        total_questions: totalQuestions,
      });
      onStartInterview(interview);
    } catch (err) {
      setError(err.message || "Failed to initialize interview.");
      setSubmitting(false);
    }
  }

  const difficulties = [
    { id: "Beginner", label: "Beginner", desc: "Core syntax, baseline definitions & fundamental control flow" },
    { id: "Intermediate", label: "Intermediate", desc: "Standard patterns, edge cases, trade-offs & runtime behavior" },
    { id: "Advanced", label: "Advanced", desc: "Deep architectural mechanics, concurrency & system optimizations" },
  ];

  const types = [
    { id: "Mixed", label: "Mixed Adaptive", desc: "Combines conceptual, scenario, debugging, and code questions" },
    { id: "Technical", label: "Scenario & System", desc: "Applied industry scenarios, why/how architectural trade-offs" },
    { id: "Conceptual", label: "Conceptual", desc: "Theoretical depth, mechanical explanations & comparisons" },
    { id: "Coding", label: "Coding & Debugging", desc: "Direct algorithm implementations, bug isolation & trace logic" },
  ];

  const questionCounts = [5, 10, 15];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-orange-500 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Initializing Adaptive Interview Engine...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900 to-orange-950/40 border border-slate-800 p-8 md:p-10 mb-8 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-orange-600/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-semibold mb-4">
            <Flame className="w-3.5 h-3.5" />
            Next-Gen Adaptive Assessment Engine
          </div>
          <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight leading-tight mb-3">
            Master Technical Interviews with <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-amber-300 to-orange-500">PRESSURE-AI</span>
          </h1>
          <p className="text-sm md:text-base text-slate-300 leading-relaxed mb-6">
            Not a static questionnaire. Our AI interviewer analyzes your answers in real time, isolates your exact conceptual weaknesses, adapts questioning difficulty, and triggers <strong className="text-orange-400">Pressure Mode</strong> to challenge you where it counts most.
          </p>
          <div className="flex flex-wrap items-center gap-4 text-xs font-medium text-slate-400">
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-emerald-400" /> Real-Time Weakness Detection</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-orange-400" /> Dynamic Difficulty Engine</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-amber-400" /> 3-Level Progressive Hints</span>
            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-4 h-4 text-red-400" /> 🔥 Pressure Mode</span>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchDomains} className="underline text-xs ml-4">Retry</button>
        </div>
      )}

      {/* Setup Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Domain & Topic Selection */}
        <div className="lg:col-span-2 space-y-6">
          {/* Domain Selection */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-orange-400" />
                <h2 className="text-lg font-bold text-white">1. Select Technical Domain</h2>
              </div>
              <span className="text-xs text-slate-400">{domains.length} Domains Available</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
              {domains.map((dom) => {
                const isSelected = dom.id === selectedDomainId;
                return (
                  <button
                    key={dom.id}
                    onClick={() => {
                      setSelectedDomainId(dom.id);
                      setSelectedTopicId("");
                    }}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      isSelected
                        ? "bg-orange-500/15 border-orange-500 shadow-md shadow-orange-500/10 text-white"
                        : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-800/40"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs">{dom.name}</span>
                      {isSelected && <Zap className="w-3 h-3 text-orange-400 fill-orange-400" />}
                    </div>
                    <span className="text-[10px] text-slate-500 block truncate">
                      {dom.category}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Topic Filter */}
            {currentDomain && currentDomain.topics && currentDomain.topics.length > 0 && (
              <div className="mt-5 pt-5 border-t border-slate-800">
                <label className="block text-xs font-semibold text-slate-300 mb-2">
                  Target Specific Topic (Optional)
                </label>
                <div className="flex flex-wrap gap-1.5">
                  <button
                    type="button"
                    onClick={() => setSelectedTopicId("")}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      selectedTopicId === ""
                        ? "bg-slate-200 text-slate-950 font-bold"
                        : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    All Topics (Full Domain Mix)
                  </button>
                  {currentDomain.topics.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setSelectedTopicId(t.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                        selectedTopicId === t.id
                          ? "bg-orange-500 text-white font-bold shadow-sm"
                          : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {t.name}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Difficulty & Type Configuration */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
            {/* Difficulty */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Sliders className="w-5 h-5 text-orange-400" />
                <h2 className="text-lg font-bold text-white">2. Initial Starting Difficulty</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {difficulties.map((diff) => {
                  const isSel = difficulty === diff.id;
                  return (
                    <button
                      key={diff.id}
                      type="button"
                      onClick={() => setDifficulty(diff.id)}
                      className={`p-3.5 rounded-xl border text-left transition-all ${
                        isSel
                          ? "bg-orange-500/15 border-orange-500 text-white shadow-md shadow-orange-500/10"
                          : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                      }`}
                    >
                      <div className="font-bold text-xs mb-1 flex items-center justify-between">
                        <span>{diff.label}</span>
                        {isSel && <div className="w-2 h-2 rounded-full bg-orange-500"></div>}
                      </div>
                      <p className="text-[11px] text-slate-400 leading-snug">{diff.desc}</p>
                    </button>
                  );
                })}
              </div>
              <p className="text-[11px] text-slate-500 mt-2 italic">
                * Note: The adaptive engine will autonomously scale difficulty up or down based on your live answer evaluations.
              </p>
            </div>

            {/* Interview Type */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Layers className="w-5 h-5 text-orange-400" />
                <h2 className="text-lg font-bold text-white">3. Interview Type</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {types.map((t) => {
                  const isSel = interviewType === t.id;
                  return (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setInterviewType(t.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        isSel
                          ? "bg-orange-500/15 border-orange-500 text-white shadow-md shadow-orange-500/10"
                          : "bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700"
                      }`}
                    >
                      <div className="font-bold text-xs mb-0.5">{t.label}</div>
                      <div className="text-[11px] text-slate-400">{t.desc}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Summary & Launch Card */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 sticky top-24">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-orange-500" />
              Interview Session Summary
            </h3>

            <div className="space-y-3.5 mb-6 text-xs">
              <div className="flex items-center justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400 font-medium">Domain:</span>
                <span className="font-bold text-white">{currentDomain?.name || "None"}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400 font-medium">Focus Topic:</span>
                <span className="font-bold text-orange-400">
                  {selectedTopicId ? currentDomain?.topics?.find(t => t.id === selectedTopicId)?.name : "Full Domain Coverage"}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400 font-medium">Base Difficulty:</span>
                <span className="font-bold text-white">{difficulty}</span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-slate-800">
                <span className="text-slate-400 font-medium">Format:</span>
                <span className="font-bold text-white">{interviewType}</span>
              </div>

              {/* Number of Questions */}
              <div className="py-2">
                <span className="text-slate-400 font-medium block mb-2">Question Count:</span>
                <div className="grid grid-cols-3 gap-2">
                  {questionCounts.map((cnt) => (
                    <button
                      key={cnt}
                      type="button"
                      onClick={() => setTotalQuestions(cnt)}
                      className={`py-2 rounded-lg text-xs font-bold border text-center transition-all ${
                        totalQuestions === cnt
                          ? "bg-orange-500 text-white border-orange-500 shadow-md shadow-orange-500/20"
                          : "bg-slate-900 border-slate-800 text-slate-400 hover:text-white"
                      }`}
                    >
                      {cnt} Qs
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Launch Action */}
            <button
              onClick={handleLaunch}
              disabled={submitting || !selectedDomainId}
              className="w-full py-3.5 px-4 bg-gradient-to-r from-orange-500 via-red-500 to-amber-500 hover:from-orange-600 hover:via-red-600 hover:to-amber-600 text-white font-extrabold text-sm rounded-xl shadow-xl shadow-orange-500/30 flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating Session...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  Start AI Interview
                </>
              )}
            </button>

            <div className="mt-4 p-3 bg-slate-950/60 rounded-xl border border-slate-800 text-[11px] text-slate-400 leading-relaxed">
              <span className="font-bold text-slate-300 block mb-0.5">Demo Presets Ready:</span>
              Select <strong className="text-orange-300">Python</strong> + <strong className="text-orange-300">Intermediate</strong> + <strong className="text-orange-300">Mixed</strong> (10 Questions) to experience the full adaptive loop with Recursion weakness and Pressure Mode!
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
