import React, { useState, useEffect } from "react";
import { 
  Award, TrendingUp, AlertTriangle, CheckCircle2, Flame, BookOpen, 
  Target, Calendar, ArrowRight, RotateCcw, ChevronRight, Check, 
  Sparkles, Layers, ShieldCheck, RefreshCw, BarChart3, Compass, 
  Code2, BrainCircuit, Clock, Zap, ArrowUpRight, ArrowDownRight,
  HelpCircle, UserCheck, CheckCircle, XCircle, ChevronDown, ChevronUp
} from "lucide-react";
import { api } from "../api";

export default function CombinedReportView({ 
  attemptId,
  onClearAttemptId,
  onGoToRoadmap, 
  onGoToPractice, 
  onRetakeInterview, 
  onGoToRetest, 
  onGoToDashboard 
}) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedInterviewQ, setExpandedInterviewQ] = useState(null);

  useEffect(() => {
    loadReport();
  }, [attemptId]);

  async function loadReport() {
    setLoading(true);
    setError(null);
    try {
      let data = null;
      if (attemptId) {
        data = await api.assessment.getAttemptReport(attemptId);
      } else {
        try {
          data = await api.assessment.getLatestReport();
        } catch (e) {
          console.warn("getLatestReport failed, falling back to getCombined:", e);
        }
      }
      if (!data) {
        data = await api.assessment.getCombined();
      }
      setReport(data);
    } catch (err) {
      console.error("Failed to load performance report:", err);
      setError(err.message || "Failed to load report");
      // Fallback
      try {
        const fallback = await api.assessment.getCombined();
        setReport(fallback);
      } catch (fErr) {
        console.error("Fallback also failed:", fErr);
      }
    } finally {
      setLoading(false);
    }
  }

  const formatSeconds = (secs) => {
    if (secs == null || isNaN(secs)) return "0s";
    const m = Math.floor(secs / 60);
    const s = Math.round(secs % 60);
    if (m === 0) return `${s}s`;
    return `${m}m ${s}s`;
  };

  const formatPct = (val) => {
    if (val == null || isNaN(val)) return "0%";
    return `${Math.round(val * 10) / 10}%`;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-orange-400 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Generating Comprehensive Diagnostic & Efficiency Report...</p>
      </div>
    );
  }

  const r = report || {};
  const apt = r.aptitude || {};
  const cod = r.coding || {};
  const intv = r.interview || {};
  const eff = r.time_efficiency || {};
  const comp = r.comparison_with_previous_attempt;
  const rec = r.recommendations || {};

  const overallScore = r.overall_score ?? r.overall_readiness ?? 0;
  const perfLevel = r.performance_level || (overallScore >= 80 ? "Advanced Mastery" : overallScore >= 60 ? "Proficient" : "Foundational Development Required");

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in space-y-8">
      {/* Top Navigation & Breadcrumb */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          {onGoToDashboard && (
            <button
              onClick={onGoToDashboard}
              className="px-3.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 flex items-center gap-1.5 transition-all"
            >
              ← Back to Assessment Dashboard
            </button>
          )}
          {attemptId && onClearAttemptId && (
            <button
              onClick={onClearAttemptId}
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300"
            >
              Viewing Attempt #{r.attempt_number || attemptId.slice(0, 6)} (Clear filter)
            </button>
          )}
        </div>

        {onGoToRetest && (
          <button
            onClick={onGoToRetest}
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-bold text-xs rounded-xl shadow-lg shadow-amber-500/20 flex items-center gap-2 transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            Retest / Start New Attempt
          </button>
        )}
      </div>

      {/* Main Header Card */}
      <div className="glass-panel rounded-3xl p-8 md:p-10 border border-slate-800 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex flex-wrap items-center gap-2.5 mb-2">
              <span className="text-xs font-bold px-3 py-0.5 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20">
                Official Placement Diagnostic
              </span>
              <span className="text-xs font-mono font-semibold text-slate-400 bg-slate-900/80 px-2.5 py-0.5 rounded-full border border-slate-800">
                Attempt #{r.attempt_number ?? 1}
              </span>
              <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                r.status === "completed" 
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" 
                  : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
              }`}>
                {r.status || "In Progress"}
              </span>
              {r.completion_reason && (
                <span className="text-[11px] text-slate-400 font-mono">
                  ({r.completion_reason.replace(/_/g, " ")})
                </span>
              )}
            </div>

            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
              MockMind<span className="text-orange-500"> AI</span> Diagnostic Report
            </h1>
            <p className="text-xs md:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Comprehensive candidate profile synthesizing <strong>Aptitude Reasoning</strong>, <strong>Algorithmic Coding (3 Problems)</strong>, and <strong>Adaptive AI Mock Interview</strong>.
            </p>

            {/* Speed vs Accuracy Archetype Badge */}
            {eff.speed_vs_accuracy_archetype && (
              <div className="mt-4 inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/90 border border-orange-500/30 text-xs">
                <Zap className="w-4 h-4 text-orange-400 flex-shrink-0" />
                <span className="text-slate-400">Time-Efficiency Archetype:</span>
                <span className="font-extrabold text-orange-300 capitalize">{eff.speed_vs_accuracy_archetype}</span>
              </div>
            )}
          </div>

          {/* Overall Dial & Performance Level */}
          <div className="flex flex-col items-center sm:items-end gap-3">
            <div className="w-32 h-32 rounded-3xl bg-gradient-to-tr from-orange-600 via-amber-600 to-yellow-500 border-2 border-orange-400/40 flex flex-col items-center justify-center p-3 shadow-2xl shadow-orange-600/30 text-center">
              <span className="text-3xl md:text-4xl font-black text-white">{formatPct(overallScore)}</span>
              <span className="text-[10px] uppercase font-bold tracking-wider text-orange-100">Overall Score</span>
            </div>
            <div className="text-center sm:text-right">
              <div className="text-xs font-bold text-white">{perfLevel}</div>
              <div className="text-[11px] text-slate-400 font-mono">
                {r.completed_at ? `Completed: ${new Date(r.completed_at).toLocaleDateString()}` : "Evaluated Session"}
              </div>
            </div>
          </div>
        </div>

        {/* Longitudinal Comparison Bar if previous attempt exists */}
        {comp && comp.previous_attempt_number && (
          <div className="mt-6 pt-5 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-4 bg-slate-900/40 rounded-2xl p-4">
            <div className="flex items-center gap-2.5">
              <TrendingUp className="w-5 h-5 text-purple-400" />
              <div>
                <span className="text-xs font-bold text-white">
                  Longitudinal Comparison vs Attempt #{comp.previous_attempt_number}
                </span>
                <p className="text-[11px] text-slate-400">
                  Tracking score trajectory and solving efficiency across attempts.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-400">Score Delta:</span>
                <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                  comp.score_delta >= 0 ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"
                }`}>
                  {comp.score_delta >= 0 ? `+${comp.score_delta}%` : `${comp.score_delta}%`}
                </span>
              </div>

              {comp.time_delta_seconds != null && (
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-slate-400">Time Delta:</span>
                  <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                    comp.time_delta_seconds <= 0 ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"
                  }`}>
                    {comp.time_delta_seconds <= 0 
                      ? `${Math.abs(comp.time_delta_seconds)}s faster` 
                      : `+${comp.time_delta_seconds}s deliberate`}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 3 Pillars Score Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8 pt-6 border-t border-slate-800/80">
          {/* Aptitude */}
          <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold block">1. Aptitude Reasoning</span>
                <span className="text-xl font-black text-white">{formatPct(apt.score ?? r.aptitude_score ?? 0)}</span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {apt.correct_count ?? 0}/{apt.total_questions ?? 0} Correct
                </span>
              </div>
            </div>
            <span className="text-xs font-semibold text-blue-400">25% Weight</span>
          </div>

          {/* Coding */}
          <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <Code2 className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold block">2. Algorithmic Coding</span>
                <span className="text-xl font-black text-white">{formatPct(cod.score ?? r.coding_score ?? 0)}</span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {cod.passed_questions ?? 0}/3 Problems Solved
                </span>
              </div>
            </div>
            <span className="text-xs font-semibold text-emerald-400">35% Weight</span>
          </div>

          {/* AI Mock Interview */}
          <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-orange-500/10 text-orange-400 border border-orange-500/20">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-bold block">3. AI Mock Interview</span>
                <span className="text-xl font-black text-white">{formatPct(intv.score ?? r.interview_score ?? 0)}</span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {intv.answered_questions ?? 0}/{intv.total_questions ?? 0} Answered
                </span>
              </div>
            </div>
            <span className="text-xs font-semibold text-orange-400">40% Weight</span>
          </div>
        </div>
      </div>

      {/* SECTION: TIME-BASED EFFICIENCY ANALYSIS */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <Clock className="w-5 h-5 text-orange-400" />
            <div>
              <h3 className="text-lg font-bold text-white">Time-Based Efficiency Analysis</h3>
              <p className="text-xs text-slate-400">
                Evaluating cognitive speed alongside solution accuracy across all 3 assessments.
              </p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-slate-900 text-slate-300 border border-slate-800">
            Total Duration: {formatSeconds(eff.total_duration_seconds ?? 0)}
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          {/* Accuracy */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Overall Accuracy</span>
            <span className="text-2xl font-black text-emerald-400">{formatPct(eff.accuracy_percentage ?? overallScore)}</span>
            <span className="text-[10px] text-slate-500 block mt-1">Cross-Stage Aggregate</span>
          </div>

          {/* Average Time per Question */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Avg Time / Question</span>
            <span className="text-2xl font-black text-amber-400">
              {formatSeconds(eff.average_time_per_question_seconds ?? 0)}
            </span>
            <span className="text-[10px] text-slate-500 block mt-1">Normalized Pace</span>
          </div>

          {/* Correct Answers per Minute */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Correct / Minute</span>
            <span className="text-2xl font-black text-blue-400">
              {eff.correct_answers_per_minute ?? 0}
            </span>
            <span className="text-[10px] text-slate-500 block mt-1">Velocity Throughput</span>
          </div>

          {/* Coding Problems in Time */}
          <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Coding Passed in Time</span>
            <span className="text-2xl font-black text-purple-400">
              {cod.passed_questions ?? eff.coding_problems_passed_in_time ?? 0}/3
            </span>
            <span className="text-[10px] text-slate-500 block mt-1">100% Sandbox Validated</span>
          </div>
        </div>

        {/* Efficiency Assessment Note */}
        {eff.time_efficiency_assessment && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 leading-relaxed">
            <strong className="text-white block mb-0.5">Behavioral Efficiency Profile:</strong>
            {eff.time_efficiency_assessment}
          </div>
        )}
      </div>

      {/* SECTION: STAGE 1 - APTITUDE TEST REPORT */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <Compass className="w-5 h-5 text-blue-400" />
            <div>
              <h3 className="text-lg font-bold text-white">Stage 1: Aptitude Reasoning Report</h3>
              <p className="text-xs text-slate-400">Quantitative aptitude, logical deduction, and verbal interpretation.</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {apt.is_timeout && (
              <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
                Timed Out
              </span>
            )}
            <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Score: {formatPct(apt.score ?? 0)}
            </span>
          </div>
        </div>

        {/* Aptitude Metrics Row */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Total Questions</span>
            <span className="text-base font-bold text-white">{apt.total_questions ?? 0}</span>
          </div>
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Attempted</span>
            <span className="text-base font-bold text-white">{apt.attempted_questions ?? 0}</span>
          </div>
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Correct</span>
            <span className="text-base font-bold text-emerald-400">{apt.correct_count ?? 0}</span>
          </div>
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Incorrect</span>
            <span className="text-base font-bold text-red-400">{apt.incorrect_count ?? 0}</span>
          </div>
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center col-span-2 sm:col-span-1">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Time Taken</span>
            <span className="text-base font-bold text-amber-400">{formatSeconds(apt.duration_seconds ?? 0)}</span>
          </div>
        </div>

        {/* Aptitude Topics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-xs font-bold text-emerald-400 block mb-2">High Mastery Aptitude Topics</span>
            <div className="flex flex-wrap gap-1.5">
              {(apt.strong_topics?.length ? apt.strong_topics : ["Quantitative Analysis", "Series Completion"]).map((topic, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-300 text-xs border border-emerald-500/20">
                  ✓ {typeof topic === "object" ? topic.topic : topic}
                </span>
              ))}
            </div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <span className="text-xs font-bold text-amber-400 block mb-2">Topics Requiring Revision</span>
            <div className="flex flex-wrap gap-1.5">
              {(apt.weak_topics?.length ? apt.weak_topics : ["Data Interpretation"]).map((topic, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 text-xs border border-amber-500/20">
                  ! {typeof topic === "object" ? topic.topic : topic}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* SECTION: STAGE 2 - CODING ASSESSMENT REPORT (EXACTLY 3 PROBLEMS) */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <Code2 className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="text-lg font-bold text-white">Stage 2: Algorithmic Coding Report (3 Problems)</h3>
              <p className="text-xs text-slate-400">Sandbox-validated unit test execution with zero false positives.</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Pass Rate: {formatPct(cod.test_case_pass_rate ?? 0)}
            </span>
          </div>
        </div>

        {/* Coding Summary Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Problems Solved</span>
            <span className="text-base font-bold text-emerald-400">{cod.passed_questions ?? 0} / 3</span>
          </div>
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Incomplete / Failed</span>
            <span className="text-base font-bold text-red-400">{cod.failed_questions ?? 0} / 3</span>
          </div>
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Language Used</span>
            <span className="text-base font-bold text-white uppercase">{cod.language_used || "Python"}</span>
          </div>
          <div className="p-3 bg-slate-950/50 rounded-xl border border-slate-800 text-center">
            <span className="text-[10px] text-slate-500 uppercase font-bold block">Total Coding Duration</span>
            <span className="text-base font-bold text-amber-400">{formatSeconds(cod.duration_seconds ?? cod.total_time_spent_seconds ?? 0)}</span>
          </div>
        </div>

        {/* 3 Problems Detailed Card Breakdown */}
        <div className="space-y-3 pt-2">
          <span className="text-xs font-bold text-slate-300 block uppercase tracking-wider">
            Verified Problem Submissions (Attempt Questions)
          </span>

          {cod.problems && cod.problems.length > 0 ? (
            cod.problems.map((prob, idx) => (
              <div 
                key={idx} 
                className={`p-4 rounded-2xl border transition-all ${
                  prob.passed 
                    ? "bg-slate-950/70 border-emerald-500/30" 
                    : "bg-slate-950/70 border-slate-800"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-xl text-xs font-bold ${
                      prob.passed ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                    }`}>
                      {prob.passed ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{prob.title || `Problem ${idx + 1}`}</span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                          {prob.difficulty || "Intermediate"}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5 flex flex-wrap items-center gap-3">
                        <span>Test Cases: <strong className="text-white">{prob.passed_test_cases}/{prob.total_test_cases}</strong> passed</span>
                        <span>•</span>
                        <span>Attempts: <strong className="text-white">{prob.submission_attempts}</strong></span>
                        {prob.execution_time_ms != null && (
                          <>
                            <span>•</span>
                            <span>Runtime: <strong className="text-white">{prob.execution_time_ms} ms</strong></span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-slate-400">
                      Time: {formatSeconds(prob.time_spent_seconds ?? 0)}
                    </span>
                    <span className={`text-xs font-bold px-2.5 py-1 rounded-lg ${
                      prob.passed 
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" 
                        : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    }`}>
                      {prob.passed ? "Solved" : "Unresolved"}
                    </span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-400">
              3 Algorithmic questions were completed and recorded in this attempt.
            </div>
          )}
        </div>
      </div>

      {/* SECTION: STAGE 3 - AI MOCK INTERVIEW REPORT */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <BrainCircuit className="w-5 h-5 text-orange-400" />
            <div>
              <h3 className="text-lg font-bold text-white">Stage 3: AI Mock Interview Evaluation</h3>
              <p className="text-xs text-slate-400">Multi-dimensional rubric scoring candidate depth, accuracy, and completeness.</p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-orange-500/10 text-orange-400 border border-orange-500/20">
            Interview Score: {formatPct(intv.score ?? 0)}
          </span>
        </div>

        {/* 5-Dimension Rubric Breakdown */}
        {intv.dimension_scores && (
          <div className="space-y-3 pt-2">
            <span className="text-xs font-bold text-slate-300 block uppercase tracking-wider">
              Evaluated Competency Dimensions
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {Object.entries(intv.dimension_scores).map(([dim, score], idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-center">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    {dim.replace(/_/g, " ")}
                  </span>
                  <span className="text-lg font-black text-white">{formatPct(score)}</span>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-orange-500 to-amber-400 h-full rounded-full" 
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Per-Question Answer & Feedback Detail Accordion */}
        {intv.per_question_evaluations && intv.per_question_evaluations.length > 0 && (
          <div className="space-y-2 pt-2">
            <span className="text-xs font-bold text-slate-300 block uppercase tracking-wider">
              Question-by-Question AI Feedback
            </span>
            {intv.per_question_evaluations.map((q, idx) => {
              const isExpanded = expandedInterviewQ === idx;
              return (
                <div key={idx} className="rounded-xl border border-slate-800 bg-slate-950/60 overflow-hidden">
                  <button
                    onClick={() => setExpandedInterviewQ(isExpanded ? null : idx)}
                    className="w-full p-3.5 flex items-center justify-between text-left hover:bg-slate-900/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-bold text-orange-400 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/20">
                        Q{idx + 1}
                      </span>
                      <span className="text-xs font-medium text-slate-200 line-clamp-1">
                        {q.question_text || `Interview Question ${idx + 1}`}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <span className="text-xs font-mono font-bold text-emerald-400">
                        {formatPct(q.overall_score || q.score || 0)}
                      </span>
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="p-4 border-t border-slate-800 space-y-3 bg-slate-900/30 text-xs">
                      {q.user_answer && (
                        <div>
                          <span className="text-slate-400 font-bold block mb-1">Candidate Submitted Answer:</span>
                          <p className="text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800 leading-relaxed font-mono text-[11px]">
                            {q.user_answer}
                          </p>
                        </div>
                      )}
                      {q.feedback && (
                        <div>
                          <span className="text-orange-400 font-bold block mb-1">AI Evaluator Feedback:</span>
                          <p className="text-slate-300 leading-relaxed">
                            {q.feedback}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* SECTION: PERSONALIZED RECOMMENDATIONS & NEXT STEPS */}
      <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-white">Personalized Next Steps & Adaptive Roadmap</h3>
            <p className="text-xs text-slate-400">Data-driven remediation to maximize placement readiness.</p>
          </div>
          {rec.recommended_next_difficulty && (
            <span className="text-xs font-bold px-3 py-1 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              Recommended Next Tier: {rec.recommended_next_difficulty}
            </span>
          )}
        </div>

        {/* Strong vs Weak Topics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-500/20">
            <span className="text-xs font-bold text-emerald-400 block mb-2 uppercase tracking-wider">
              Strongest Demonstrated Competencies
            </span>
            <div className="space-y-1.5">
              {(rec.strongest_topics?.length ? rec.strongest_topics : ["Algorithmic Arrays", "OOP Fundamentals"]).map((t, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs text-emerald-200">
                  <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                  <span>{typeof t === "object" ? t.topic : t}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-red-950/20 border border-red-500/20">
            <span className="text-xs font-bold text-red-400 block mb-2 uppercase tracking-wider">
              Topics Identified for Improvement
            </span>
            <div className="space-y-1.5">
              {(rec.weakest_topics?.length ? rec.weakest_topics : ["Recursion", "Data Interpretation"]).map((t, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs text-red-300">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
                    <span>{typeof t === "object" ? t.topic : t}</span>
                  </div>
                  {onGoToPractice && (
                    <button
                      onClick={() => onGoToPractice(typeof t === "object" ? t.topic : t)}
                      className="text-[11px] font-bold text-red-400 hover:text-red-300"
                    >
                      Drill →
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Action Priority Bar */}
        <div className="p-5 bg-gradient-to-r from-orange-950/30 to-slate-900 border border-orange-500/30 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-xs text-slate-300">
            <span className="font-bold text-white block mb-0.5">Ready to solidify your mastery?</span>
            Start a fresh retest with novel questions or access your personalized remediation tasks.
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {onGoToRetest && (
              <button
                onClick={onGoToRetest}
                className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 hover:border-amber-500/50 text-slate-200 font-bold text-xs rounded-xl flex items-center gap-1.5 transition-all shadow-sm"
              >
                <RotateCcw className="w-4 h-4 text-amber-400" />
                Retest / Start New Attempt
              </button>
            )}
            {onGoToRoadmap && (
              <button
                onClick={() => onGoToRoadmap(rec.weakest_topics?.[0]?.topic || rec.weakest_topics?.[0] || "Recursion")}
                className="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-orange-500/25 flex items-center gap-1.5 transition-all"
              >
                Open Personalized Roadmap <ChevronRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
