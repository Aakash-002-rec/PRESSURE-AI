import React, { useState, useEffect } from "react";
import { 
  TrendingUp, Award, Calendar, Flame, AlertCircle, ArrowUpRight, 
  CheckCircle2, RefreshCw, BarChart2, BookOpen, Clock, ChevronRight
} from "lucide-react";
import { api } from "../api";

export default function ProgressView({ onViewReport, onStartNew }) {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProgress();
  }, []);

  async function fetchProgress() {
    try {
      setLoading(true);
      const data = await api.progress.get();
      setProgress(data);
    } catch (err) {
      setError("Failed to fetch progress history: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-orange-500 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Loading Progress & Topic Deltas...</p>
      </div>
    );
  }

  if (!progress || progress.total_interviews_completed === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center animate-fade-in">
        <div className="w-16 h-16 rounded-3xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto mb-4">
          <TrendingUp className="w-8 h-8 text-orange-500" />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">No Completed Interviews Yet</h3>
        <p className="text-xs text-slate-400 mb-6 max-w-md mx-auto">
          Complete your first adaptive interview session to unlock longitudinal skill tracking, topic progression deltas, and weakness recovery graphs.
        </p>
        <button
          onClick={onStartNew}
          className="px-6 py-2.5 bg-gradient-to-r from-orange-500 to-amber-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-orange-500/20"
        >
          Launch First Interview
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-bold text-orange-400 uppercase tracking-wider">
            Longitudinal Skill Analytics
          </span>
        </div>
        <h1 className="text-3xl font-black text-white tracking-tight">
          Performance & Topic Improvement Tracking
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Monitor your score trajectory across attempts and verify conceptual weakness remediation.
        </p>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Interviews Completed</span>
          <span className="text-2xl font-black text-white">{progress.total_interviews_completed}</span>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Average Score</span>
          <span className="text-2xl font-black text-orange-400">{progress.average_score}%</span>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Best Score</span>
          <span className="text-2xl font-black text-emerald-400">{progress.best_score}%</span>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1">Mastered Topics</span>
          <span className="text-2xl font-black text-white">{progress.strongest_topics.length}</span>
        </div>
      </div>

      {/* Section 16 Highlight: Topic Improvement Deltas */}
      {progress.topic_improvements && progress.topic_improvements.length > 0 && (
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-400" />
              Topic-Wise Improvement Trajectory
            </h3>
            <span className="text-xs text-slate-400 font-medium">Compared across attempts</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {progress.topic_improvements.map((delta, dIdx) => (
              <div
                key={dIdx}
                className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 flex items-start gap-3.5"
              >
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    delta.delta >= 0
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "bg-red-500/10 text-red-400 border border-red-500/20"
                  }`}
                >
                  <ArrowUpRight
                    className={`w-5 h-5 ${delta.delta < 0 ? "rotate-90 text-red-400" : ""}`}
                  />
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white">{delta.topic_name}</span>
                    <span
                      className={`text-xs font-black ${
                        delta.delta >= 0 ? "text-emerald-400" : "text-red-400"
                      }`}
                    >
                      {delta.delta >= 0 ? `+${delta.delta}%` : `${delta.delta}%`}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-snug font-medium mb-2">
                    {delta.message}
                  </p>
                  <div className="flex items-center gap-2 text-[10px] text-slate-500">
                    <span>Initial: {delta.first_score}%</span>
                    <span>→</span>
                    <span className="text-white font-semibold">Latest: {delta.latest_score}%</span>
                    <span>• {delta.attempts_count} evals</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Historical Interviews Log */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-orange-400" />
          Completed Interview History
        </h3>

        <div className="space-y-3">
          {progress.history.map((iv) => (
            <div
              key={iv.interview_id}
              className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 flex flex-wrap items-center justify-between gap-4 transition-all"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold text-xs ${
                    iv.overall_score >= 75
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                      : iv.overall_score >= 60
                      ? "bg-orange-500/20 text-orange-400 border border-orange-500/30"
                      : "bg-red-500/20 text-red-400 border border-red-500/30"
                  }`}
                >
                  {iv.overall_score}%
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white">{iv.domain_name}</span>
                    <span className="text-[10px] text-slate-500">• {iv.difficulty}</span>
                    {iv.pressure_mode_triggered && (
                      <span className="text-[10px] font-bold text-red-400 bg-red-500/10 px-1.5 py-0.2 rounded border border-red-500/20 flex items-center gap-0.5">
                        <Flame className="w-2.5 h-2.5" /> Pressure Mode
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {new Date(iv.started_at).toLocaleDateString()} at{" "}
                    {new Date(iv.started_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} •{" "}
                    {iv.total_questions} Questions
                  </div>
                </div>
              </div>

              <button
                onClick={() => onViewReport(iv.interview_id)}
                className="flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-bold text-white rounded-lg transition-colors"
              >
                <span>View Report</span>
                <ChevronRight className="w-3.5 h-3.5 text-orange-400" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
