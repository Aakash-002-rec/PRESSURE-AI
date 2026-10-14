import React, { useState, useEffect } from "react";
import { 
  Award, TrendingUp, AlertTriangle, CheckCircle2, Flame, BookOpen, 
  Target, Calendar, ArrowRight, RotateCcw, ChevronRight, Check, 
  Sparkles, Layers, ShieldCheck, RefreshCw, BarChart3, Compass, Code2, BrainCircuit
} from "lucide-react";
import { api } from "../api";

export default function CombinedReportView({ onGoToRoadmap, onGoToPractice, onRetakeInterview }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCombinedAssessment();
  }, []);

  async function loadCombinedAssessment() {
    try {
      setLoading(true);
      const data = await api.assessment.getCombined();
      setProfile(data);
    } catch (err) {
      console.error("Failed to load combined assessment:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Synthesizing Cross-Module Assessment Profile...</p>
      </div>
    );
  }

  const p = profile || {
    overall_readiness: 74.0,
    aptitude_score: 72.0,
    coding_score: 81.0,
    interview_score: 68.0,
    strong_topics: [
      { topic: "Python Basics", score: 88.0, modules: ["Interview"] },
      { topic: "OOP & Inheritance", score: 78.0, modules: ["Interview"] },
      { topic: "Arrays", score: 82.0, modules: ["Coding"] }
    ],
    average_topics: [
      { topic: "SQL", score: 65.0, modules: ["Interview"] },
      { topic: "Quantitative Aptitude", score: 65.0, modules: ["Aptitude"] }
    ],
    weak_topics: [
      { topic: "Recursion", score: 42.0, modules: ["Coding", "Interview"] },
      { topic: "Data Interpretation", score: 48.0, modules: ["Aptitude"] }
    ],
    major_weaknesses: [
      {
        topic: "Recursion",
        score: 42.0,
        modules: ["Coding", "Interview"],
        reason: "Struggled with base conditions and stack frames in both Coding (42%) and AI Interview (45%)"
      },
      {
        topic: "Data Interpretation",
        score: 48.0,
        modules: ["Aptitude"],
        reason: "Deficit in graph analysis, growth rates, and table percentage derivations (48%)"
      }
    ],
    recommended_priority: ["Recursion", "Data Interpretation", "SQL"]
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in space-y-8">
      {/* Header Banner */}
      <div className="glass-panel rounded-3xl p-8 md:p-10 border border-slate-800 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                Official Placement Assessment Report
              </span>
              <span className="text-xs text-slate-400 font-mono">Unified Candidate Audit</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
              PRESSURE<span className="text-orange-500">-AI</span> Candidate Diagnostic
            </h1>
            <p className="text-xs md:text-sm text-slate-300 mt-1">
              End-to-end evaluation synthesizing <strong>Aptitude Testing</strong>, <strong>Algorithmic Coding</strong>, and <strong>AI Mock Interview</strong>.
            </p>
          </div>

          {/* Overall Dial */}
          <div className="flex items-center gap-4">
            <div className="w-28 h-28 rounded-3xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-purple-500 border-2 border-purple-400/40 flex flex-col items-center justify-center p-3 shadow-2xl shadow-purple-600/30">
              <span className="text-3xl font-black text-white">{p.overall_readiness}%</span>
              <span className="text-[10px] uppercase font-bold tracking-wider text-purple-200">Overall Score</span>
            </div>
          </div>
        </div>

        {/* 3 Pillars Score Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8 pt-6 border-t border-slate-800/80">
          <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 flex items-center justify-between widget-interactive">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold block">1. Aptitude Score</span>
                <span className="text-lg font-black text-white">{p.aptitude_score}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-blue-400">25% Weight</span>
          </div>

          <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 flex items-center justify-between widget-interactive">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                <Code2 className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold block">2. Coding Session</span>
                <span className="text-lg font-black text-white">{p.coding_score}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-emerald-400">35% Weight</span>
          </div>

          <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 flex items-center justify-between widget-interactive">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-orange-500/10 text-orange-400">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold block">3. AI Mock Interview</span>
                <span className="text-lg font-black text-white">{p.interview_score}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-orange-400">40% Weight</span>
          </div>
        </div>
      </div>

      {/* CROSS-MODULE MAJOR WEAKNESS DETECTION */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <h3 className="text-lg font-bold text-white">Cross-Module Major Weakness Detection</h3>
          </div>
          <span className="text-[11px] text-red-400 font-bold bg-red-500/10 px-2.5 py-1 rounded-lg border border-red-500/20">
            Automated Multi-Stage Diagnosis
          </span>
        </div>

        <p className="text-xs text-slate-400">
          The system correlates performance across Aptitude, Coding, and Technical Interviews to identify concepts where you struggle consistently.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {p.major_weaknesses?.map((mw, idx) => (
            <div key={idx} className="p-5 rounded-2xl bg-red-950/20 border-2 border-red-500/30 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
                    Weak Concept: {mw.topic}
                  </span>
                  <span className="text-xs font-mono font-bold text-red-400">
                    Score: {mw.score}% 🔴
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  {mw.reason}
                </p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-red-500/20 text-[11px]">
                <span className="text-slate-400">Failed in: <strong className="text-white">{mw.modules.join(" & ")}</strong></span>
                <button
                  onClick={() => onGoToPractice(mw.topic)}
                  className="text-red-400 font-bold hover:text-red-300 flex items-center gap-1"
                >
                  Start Drills <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* UNIFIED CANDIDATE SKILL PROFILE & TOPIC-WISE BREAKDOWN */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-white">Unified Candidate Skill Profile</h3>
            <p className="text-xs text-slate-400">Topic-wise mastery classification across all assessment components.</p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1 text-emerald-400 font-bold">🟢 Strong (≥75%)</span>
            <span className="flex items-center gap-1 text-amber-400 font-bold">🟡 Average (60-74%)</span>
            <span className="flex items-center gap-1 text-red-400 font-bold">🔴 Weak (&lt;60%)</span>
          </div>
        </div>

        {/* 3 Columns: Strong, Average, Weak */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Strong */}
          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800">
            <span className="text-xs font-bold text-emerald-400 block mb-3 uppercase tracking-wider">
              Strong Concepts ({p.strong_topics?.length || 0})
            </span>
            <div className="space-y-2.5">
              {p.strong_topics?.map((t, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-white block">{t.topic}</span>
                    <span className="text-[10px] text-slate-500">{t.modules?.join(", ")}</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-emerald-400">{t.score}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Average */}
          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800">
            <span className="text-xs font-bold text-amber-400 block mb-3 uppercase tracking-wider">
              Average Concepts ({p.average_topics?.length || 0})
            </span>
            <div className="space-y-2.5">
              {p.average_topics?.map((t, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-white block">{t.topic}</span>
                    <span className="text-[10px] text-slate-500">{t.modules?.join(", ")}</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-amber-400">{t.score}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Weak */}
          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800">
            <span className="text-xs font-bold text-red-400 block mb-3 uppercase tracking-wider">
              Critical Weaknesses ({p.weak_topics?.length || 0})
            </span>
            <div className="space-y-2.5">
              {p.weak_topics?.map((t, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-red-950/20 border border-red-500/20 flex items-center justify-between">
                  <div>
                    <span className="text-xs font-bold text-white block">{t.topic}</span>
                    <span className="text-[10px] text-red-400">{t.modules?.join(", ")}</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-red-400">{t.score}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Priority Action Recommendation */}
        <div className="p-4 bg-orange-950/20 border border-orange-500/30 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-300">
            <span className="font-bold text-white block mb-0.5">Recommended Remediation Priority:</span>
            1. <strong className="text-red-400">{p.recommended_priority?.[0]}</strong> → 2. <strong className="text-orange-400">{p.recommended_priority?.[1]}</strong> → 3. <strong className="text-amber-400">{p.recommended_priority?.[2]}</strong>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onGoToRoadmap(p.recommended_priority?.[0] || "Recursion")}
              className="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-orange-500/25 flex items-center gap-1.5 transition-all"
            >
              Open Personalized Roadmap <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
