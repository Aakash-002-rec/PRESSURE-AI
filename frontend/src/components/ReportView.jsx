import React, { useState, useEffect } from "react";
import { 
  Award, TrendingUp, AlertCircle, CheckCircle2, Flame, HelpCircle, 
  BookOpen, Target, Calendar, ArrowRight, RotateCcw, ChevronDown, 
  ChevronUp, Check, ListChecks, Sparkles, Layers, ShieldCheck, RefreshCw
} from "lucide-react";
import { api } from "../api";
import confetti from "canvas-confetti";

export default function ReportView({ interviewId, onRetakeInterview, onGoToProgress, onGoToCombined, onGoToRoadmap }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview"); // 'overview', 'recommendations', 'roadmap', 'questions'
  const [expandedQuestion, setExpandedQuestion] = useState(null);

  useEffect(() => {
    fetchReport();
  }, [interviewId]);

  async function fetchReport() {
    try {
      setLoading(true);
      const data = await api.interviews.getReport(interviewId);
      setReport(data);

      // Trigger celebratory confetti if overall score is strong!
      if (data.overall_score >= 70) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      }
    } catch (err) {
      setError("Failed to load interview report: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-orange-500 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Generating Comprehensive Performance Analysis...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-white mb-2">Report Not Found</h3>
        <p className="text-xs text-slate-400 mb-6">{error || "Could not retrieve report data."}</p>
        <button
          onClick={onRetakeInterview}
          className="px-4 py-2 bg-orange-500 text-white rounded-lg text-xs font-bold"
        >
          Return to Setup
        </button>
      </div>
    );
  }

  const scoreColor =
    report.overall_score >= 75
      ? "text-emerald-400 border-emerald-500/40 bg-emerald-500/10"
      : report.overall_score >= 60
      ? "text-orange-400 border-orange-500/40 bg-orange-500/10"
      : "text-red-400 border-red-500/40 bg-red-500/10";

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in space-y-8">
      {/* Report Header Card */}
      <div className="glass-panel rounded-3xl p-6 md:p-10 border border-slate-800 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20">
                Official Assessment Report
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Session #{report.interview_id}
              </span>
            </div>
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
              PRESSURE<span className="text-orange-500">-AI</span> Interview Evaluation
            </h1>
            <p className="text-xs md:text-sm text-slate-300 mt-1">
              Candidate: <strong className="text-white">{report.candidate_name}</strong> • Domain:{" "}
              <strong className="text-orange-400">{report.domain_name}</strong> ({report.interview_type})
            </p>
          </div>

          {/* Overall Score Dial */}
          <div className="flex items-center gap-4">
            <div className={`w-28 h-28 rounded-3xl border-2 flex flex-col items-center justify-center p-3 shadow-2xl ${scoreColor}`}>
              <span className="text-3xl font-black">{report.overall_score}%</span>
              <span className="text-[10px] uppercase font-bold tracking-wider opacity-80">Overall Score</span>
            </div>
          </div>
        </div>

        {/* Quick Stats Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-8 pt-6 border-t border-slate-800/80">
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Configured Diff</span>
            <span className="text-xs font-bold text-white">{report.difficulty_configured}</span>
          </div>
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Final Adaptive Diff</span>
            <span className="text-xs font-bold text-orange-400">{report.final_difficulty}</span>
          </div>
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Questions Attempted</span>
            <span className="text-xs font-bold text-white">{report.questions_attempted} / {report.total_questions}</span>
          </div>
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-semibold block">Hints Used</span>
            <span className="text-xs font-bold text-amber-400">{report.hints_used_total} hints</span>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "overview"
              ? "bg-orange-500 text-white shadow-lg shadow-orange-500/20"
              : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
          }`}
        >
          <Award className="w-3.5 h-3.5" />
          Performance Breakdown
        </button>

        <button
          onClick={() => setActiveTab("recommendations")}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "recommendations"
              ? "bg-orange-500 text-white shadow-lg shadow-orange-500/20"
              : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
          }`}
        >
          <BookOpen className="w-3.5 h-3.5 text-amber-400" />
          Personalized Recommendations ({report.recommendations.length})
        </button>

        <button
          onClick={() => setActiveTab("roadmap")}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "roadmap"
              ? "bg-orange-500 text-white shadow-lg shadow-orange-500/20"
              : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
          }`}
        >
          <Target className="w-3.5 h-3.5 text-emerald-400" />
          5-Stage Learning Roadmap
        </button>

        <button
          onClick={() => setActiveTab("questions")}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "questions"
              ? "bg-orange-500 text-white shadow-lg shadow-orange-500/20"
              : "text-slate-400 hover:text-white bg-slate-900 border border-slate-800"
          }`}
        >
          <ListChecks className="w-3.5 h-3.5" />
          Review Questions & Feedback
        </button>
      </div>

      {/* TAB 1: OVERVIEW & PERFORMANCE */}
      {activeTab === "overview" && (
        <div className="space-y-6 animate-fade-in">
          {/* Category Dimensions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Category Dimension Scores */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <Layers className="w-4 h-4 text-orange-400" />
                Assessment Category Dimensions
              </h3>
              <div className="space-y-4">
                {Object.entries(report.category_scores).map(([cat, score]) => (
                  <div key={cat}>
                    <div className="flex items-center justify-between text-xs mb-1.5 font-medium">
                      <span className="text-slate-300">{cat}</span>
                      <span className="text-white font-bold">{score}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                      <div
                        className="h-full bg-gradient-to-r from-orange-500 to-amber-400 rounded-full"
                        style={{ width: `${score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Strong & Weak Areas Summary */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-orange-400" />
                  Conceptual Strengths & Weaknesses
                </h3>

                {/* Strong Areas */}
                <div className="mb-4">
                  <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Strong Performance (≥ 75%)
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {report.strong_areas.length > 0 ? (
                      report.strong_areas.map((t, idx) => (
                        <span key={idx} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-xs font-semibold">
                          {t}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500 italic">No topics surpassed 75% in this session.</span>
                    )}
                  </div>
                </div>

                {/* Weak Areas */}
                <div className="mb-4">
                  <span className="text-[11px] font-bold text-red-400 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" /> Identified Weak Areas (&lt; 65%)
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {report.weak_areas.length > 0 ? (
                      report.weak_areas.map((t, idx) => (
                        <span key={idx} className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-300 border border-red-500/20 text-xs font-semibold">
                          {t}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-emerald-400 italic">No critical weak topics detected! Excellent work.</span>
                    )}
                  </div>
                </div>

                {/* Pressure Mode Topics */}
                {report.pressure_mode_topics.length > 0 && (
                  <div className="p-3 bg-red-950/20 rounded-xl border border-red-500/30 text-xs text-red-300">
                    <span className="font-bold flex items-center gap-1 mb-1">
                      <Flame className="w-3.5 h-3.5 text-red-400" /> Pressure Mode Triggered:
                    </span>
                    The interviewer escalated into Pressure Mode specifically for:{" "}
                    <strong>{report.pressure_mode_topics.join(", ")}</strong> due to repeated conceptual gaps.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Topic Performance Grid */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-4">Topic-Wise Mastery Breakdown</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {report.topic_performance.map((tp) => (
                <div
                  key={tp.topic_id}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white truncate">{tp.topic_name}</span>
                    <span
                      className={`text-xs font-black ${
                        tp.score >= 75 ? "text-emerald-400" : tp.score >= 60 ? "text-orange-400" : "text-red-400"
                      }`}
                    >
                      {tp.score}%
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        tp.score >= 75 ? "bg-emerald-500" : tp.score >= 60 ? "bg-orange-500" : "bg-red-500"
                      }`}
                      style={{ width: `${tp.score}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-500">
                    <span>{tp.attempts} attempts</span>
                    <span className="uppercase font-semibold">{tp.weakness_level}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: PERSONALIZED LEARNING RECOMMENDATIONS */}
      {activeTab === "recommendations" && (
        <div className="space-y-6 animate-fade-in">
          {report.recommendations.length === 0 ? (
            <div className="glass-panel p-8 rounded-2xl text-center">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-2" />
              <h3 className="text-base font-bold text-white">No Critical Weaknesses Flagged!</h3>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                You performed above the weakness threshold across all evaluated topics. You can proceed directly to advanced topics.
              </p>
            </div>
          ) : (
            report.recommendations.map((rec) => (
              <div
                key={rec.topic_id}
                className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6"
              >
                {/* Header */}
                <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                        Targeted Remediation Plan
                      </span>
                    </div>
                    <h3 className="text-xl font-black text-white">Weak Topic: {rec.topic_name}</h3>
                  </div>
                  <div className="px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 font-bold text-sm">
                    Performance: {rec.performance_score}%
                  </div>
                </div>

                {/* Section 14: Why Weak & Concepts to Learn */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Why considered weak */}
                  <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800">
                    <span className="text-xs font-bold text-red-400 block mb-2 uppercase tracking-wide">
                      1. Why It Is Considered Weak:
                    </span>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {rec.why_weak.map((w, wIdx) => (
                        <li key={wIdx} className="flex items-start gap-2">
                          <span className="text-red-400 font-bold">•</span>
                          <span>{w}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* What concepts to learn */}
                  <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800">
                    <span className="text-xs font-bold text-orange-400 block mb-2 uppercase tracking-wide">
                      2. Essential Concepts to Master:
                    </span>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {rec.concepts_to_learn.map((c, cIdx) => (
                        <li key={cIdx} className="flex items-start gap-2">
                          <span className="text-orange-400 font-bold">{cIdx + 1}.</span>
                          <span>{c}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* 5-Step Action Plan */}
                <div className="p-5 bg-slate-950/70 rounded-2xl border border-slate-800">
                  <span className="text-xs font-bold text-emerald-400 block mb-3 uppercase tracking-wide">
                    3. Recommended 5-Step Action Plan:
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                    {rec.action_plan.map((step, sIdx) => (
                      <div key={sIdx} className="p-3 bg-slate-900 rounded-xl border border-slate-800 flex flex-col justify-between">
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1 block">
                          Step {sIdx + 1}
                        </span>
                        <p className="text-xs text-slate-300 leading-snug">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Targeted Practice Questions */}
                <div>
                  <span className="text-xs font-bold text-white block mb-3 uppercase tracking-wide flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" /> 4. Targeted Practice Exercises:
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {rec.practice_questions.map((pq, pIdx) => (
                      <div
                        key={pIdx}
                        className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between"
                      >
                        <div>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider mb-2 inline-block ${
                              pq.level === "Easy"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : pq.level === "Medium"
                                ? "bg-orange-500/10 text-orange-400 border border-orange-500/20"
                                : "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                            }`}
                          >
                            {pq.level} Problem
                          </span>
                          <p className="text-xs text-white font-medium mb-3 leading-relaxed">
                            {pq.question}
                          </p>
                        </div>
                        <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                          Focus: <span className="text-slate-300">{pq.key_focus}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* TAB 3: AI-GENERATED LEARNING ROADMAP */}
      {activeTab === "roadmap" && (
        <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-8 animate-fade-in">
          <div>
            <span className="text-xs font-bold text-orange-400 uppercase tracking-wider block mb-1">
              Personalized Curriculum Architecture
            </span>
            <h3 className="text-2xl font-black text-white">Your Step-by-Step Learning Roadmap</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-xl">
              Follow this progression to systematically eliminate conceptual gaps and prepare for the next AI interview attempt.
            </p>
          </div>

          <div className="relative border-l-2 border-orange-500/30 ml-4 md:ml-6 space-y-8 py-2">
            {report.learning_roadmap.map((stage) => (
              <div key={stage.stage_number} className="relative pl-6 md:pl-8 group">
                {/* Node indicator */}
                <div className="absolute -left-[17px] top-1.5 w-8 h-8 rounded-full bg-slate-900 border-2 border-orange-500 flex items-center justify-center font-bold text-xs text-orange-400 shadow-md shadow-orange-500/20 group-hover:scale-110 transition-transform">
                  {stage.stage_number}
                </div>

                <div className="glass-panel p-5 rounded-2xl border border-slate-800 group-hover:border-slate-700 transition-colors">
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                    <h4 className="text-base font-bold text-white">{stage.title}</h4>
                    <span className="text-[11px] font-semibold text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                      Est. {stage.estimated_duration}
                    </span>
                  </div>

                  <p className="text-xs text-orange-300/90 font-medium mb-3">
                    Objective: {stage.objective}
                  </p>

                  <div className="space-y-1.5">
                    {stage.action_items.map((item, iIdx) => (
                      <div key={iIdx} className="flex items-center gap-2 text-xs text-slate-300">
                        <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 bg-orange-950/20 rounded-2xl border border-orange-500/30 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-slate-300">
              <span className="font-bold text-white block mb-0.5">Ready to measure improvement?</span>
              Retake the AI interview now to verify mastery and track score increase on your dashboard.
            </div>
            <button
              onClick={onRetakeInterview}
              className="py-2.5 px-5 bg-gradient-to-r from-orange-500 to-amber-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-orange-500/25 flex items-center gap-2 flex-shrink-0"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Retake AI Interview
            </button>
          </div>
        </div>
      )}

      {/* TAB 4: COMPLETE QUESTIONS & EVALUATION DETAIL */}
      {activeTab === "questions" && (
        <div className="space-y-4 animate-fade-in">
          {report.questions_detail.map((q) => {
            const isExpanded = expandedQuestion === q.sequence_number;
            return (
              <div
                key={q.sequence_number}
                className={`glass-panel rounded-2xl border transition-all ${
                  q.is_pressure_mode ? "border-red-500/40" : "border-slate-800"
                }`}
              >
                <div
                  onClick={() => setExpandedQuestion(isExpanded ? null : q.sequence_number)}
                  className="p-5 flex items-center justify-between gap-4 cursor-pointer hover:bg-slate-800/20 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-7 h-7 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-center font-bold text-xs text-slate-400">
                      #{q.sequence_number}
                    </span>
                    <div>
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-xs font-bold text-white">{q.topic_name}</span>
                        <span className="text-[10px] text-slate-500">• {q.difficulty}</span>
                        {q.is_pressure_mode && (
                          <span className="text-[10px] font-bold text-red-400 bg-red-500/10 px-1.5 py-0.2 rounded border border-red-500/20 flex items-center gap-0.5">
                            <Flame className="w-2.5 h-2.5" /> Pressure Question
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-400 max-w-2xl truncate">
                        {q.question_text}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`text-xs font-black px-2.5 py-1 rounded-lg border ${
                        q.score >= 75
                          ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                          : q.score >= 50
                          ? "bg-orange-500/10 border-orange-500/20 text-orange-400"
                          : "bg-red-500/10 border-red-500/20 text-red-400"
                      }`}
                    >
                      {q.score}%
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {isExpanded && (
                  <div className="px-5 pb-5 pt-2 border-t border-slate-800/80 space-y-3.5 text-xs animate-fade-in">
                    <div>
                      <span className="font-bold text-slate-400 block mb-1">Full Question:</span>
                      <p className="text-white leading-relaxed">{q.question_text}</p>
                    </div>

                    <div>
                      <span className="font-bold text-slate-400 block mb-1">Candidate Answer:</span>
                      <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-slate-300 font-mono text-[11px] leading-relaxed">
                        {q.answer_text || "No response recorded"}
                      </div>
                    </div>

                    <div className="p-3 bg-slate-900 rounded-xl border border-slate-800">
                      <span className="font-bold text-orange-400 block mb-1">AI Evaluator Feedback:</span>
                      <p className="text-slate-300 leading-relaxed">{q.feedback}</p>
                    </div>

                    {q.missing_concepts && q.missing_concepts.length > 0 && (
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-red-400 font-semibold">Missing concepts:</span>
                        {q.missing_concepts.map((mc, mIdx) => (
                          <span key={mIdx} className="px-2 py-0.5 bg-red-500/10 text-red-300 border border-red-500/20 rounded text-[11px]">
                            {mc}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Bottom Action Footer */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-6 border-t border-slate-800">
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={onGoToProgress}
            className="flex items-center gap-2 text-xs font-bold text-slate-300 hover:text-white px-4 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl transition-all"
          >
            <TrendingUp className="w-4 h-4 text-orange-400" />
            Progress Comparison
          </button>
          {onGoToRoadmap && (
            <button
              onClick={onGoToRoadmap}
              className="flex items-center gap-2 text-xs font-bold text-red-300 hover:text-white px-4 py-2.5 bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 rounded-xl transition-all"
            >
              <Target className="w-4 h-4 text-red-400" />
              Learning Roadmap
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {onGoToCombined && (
            <button
              onClick={onGoToCombined}
              className="flex items-center gap-2 text-xs font-bold text-purple-200 px-5 py-2.5 bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 rounded-xl shadow-lg transition-all"
            >
              <Layers className="w-4 h-4 text-purple-300" />
              Final Combined Assessment
            </button>
          )}
          <button
            onClick={onRetakeInterview}
            className="flex items-center gap-2 text-xs font-bold text-white px-6 py-2.5 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 rounded-xl shadow-lg shadow-orange-500/25 transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            Start New Practice Interview
          </button>
        </div>
      </div>
    </div>
  );
}
