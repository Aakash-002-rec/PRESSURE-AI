import React, { useState, useEffect } from "react";
import { 
  ShieldCheck, Users, BrainCircuit, BarChart3, AlertTriangle, 
  ExternalLink, RefreshCw, CheckCircle2, ChevronRight, Layers, Flame
} from "lucide-react";
import { api } from "../api";

export default function AdminView({ onViewReport }) {
  const [stats, setStats] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewTab, setViewTab] = useState("overview"); // 'overview', 'candidates'

  useEffect(() => {
    fetchAdminData();
  }, []);

  async function fetchAdminData() {
    try {
      setLoading(true);
      const [dash, cands] = await Promise.all([
        api.admin.getDashboard(),
        api.admin.getCandidates(),
      ]);
      setStats(dash);
      setCandidates(cands);
    } catch (err) {
      setError("Failed to load admin telemetry: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <RefreshCw className="w-8 h-8 text-purple-500 animate-spin" />
        <p className="text-sm text-slate-400 font-medium">Aggregating Platform Assessment Analytics...</p>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-white mb-2">Admin Dashboard Error</h3>
        <p className="text-xs text-slate-400 mb-6">{error}</p>
        <button
          onClick={fetchAdminData}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg text-xs font-bold"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
              Admin & Interview Manager Console
            </span>
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight">
            Platform Assessment Telemetry
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Global evaluation metrics, candidate weak topic aggregations, and individual attempt audits.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl">
          <button
            onClick={() => setViewTab("overview")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewTab === "overview"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Overview & Telemetry
          </button>
          <button
            onClick={() => setViewTab("candidates")}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewTab === "candidates"
                ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Candidates ({candidates.length})
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5 text-purple-400" /> Total Candidates
          </span>
          <span className="text-2xl font-black text-white">{stats.total_candidates}</span>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1 flex items-center gap-1.5">
            <BrainCircuit className="w-3.5 h-3.5 text-orange-400" /> Total Interviews
          </span>
          <span className="text-2xl font-black text-white">{stats.total_interviews}</span>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1 flex items-center gap-1.5">
            <BarChart3 className="w-3.5 h-3.5 text-emerald-400" /> Platform Avg Score
          </span>
          <span className="text-2xl font-black text-emerald-400">{stats.average_platform_score}%</span>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase block mb-1 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" /> Completed Sessions
          </span>
          <span className="text-2xl font-black text-white">{stats.completed_interviews}</span>
        </div>
      </div>

      {viewTab === "overview" && (
        <div className="space-y-8 animate-fade-in">
          {/* Section 18: Most Common Weak Topics Across Platform */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                  Most Common Weak Topics Across Candidates
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  High-frequency conceptual gaps triggering adaptive difficulty reductions or pressure mode.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {stats.top_weak_topics.length > 0 ? (
                stats.top_weak_topics.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between"
                  >
                    <div>
                      <span className="text-xs font-bold text-white block">{item.topic_name}</span>
                      <span className="text-[10px] text-slate-500">{item.domain_name}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-bold text-red-400 block">
                        {item.weakness_instances} flags
                      </span>
                      <span className="text-[10px] text-slate-500">Avg {item.avg_score}%</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-3 text-center py-6 text-xs text-slate-500">
                  No aggregated weakness data yet recorded.
                </div>
              )}
            </div>
          </div>

          {/* Recent Candidate Interviews Table */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
            <h3 className="text-base font-bold text-white">Recent Candidate Interviews</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider text-[10px]">
                    <th className="pb-3 font-semibold">Candidate</th>
                    <th className="pb-3 font-semibold">Domain</th>
                    <th className="pb-3 font-semibold">Adaptive Diff</th>
                    <th className="pb-3 font-semibold">Score</th>
                    <th className="pb-3 font-semibold">Status</th>
                    <th className="pb-3 font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {stats.recent_interviews.map((iv) => (
                    <tr key={iv.id} className="hover:bg-slate-800/20">
                      <td className="py-3 font-medium text-white">
                        <div>{iv.candidate_name}</div>
                        <div className="text-[10px] text-slate-500">{iv.candidate_email}</div>
                      </td>
                      <td className="py-3 text-slate-300">{iv.domain_name}</td>
                      <td className="py-3 text-orange-400 font-semibold">{iv.current_difficulty}</td>
                      <td className="py-3 font-bold text-white">
                        {iv.overall_score !== null ? `${iv.overall_score}%` : "In Progress"}
                      </td>
                      <td className="py-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            iv.status === "completed"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          }`}
                        >
                          {iv.status}
                        </span>
                      </td>
                      <td className="py-3">
                        {iv.status === "completed" && (
                          <button
                            onClick={() => onViewReport(iv.id)}
                            className="flex items-center gap-1 text-[11px] text-purple-400 hover:text-purple-300 font-bold"
                          >
                            <span>Inspect Report</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {viewTab === "candidates" && (
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4 animate-fade-in">
          <h3 className="text-base font-bold text-white">Candidate Registry</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 uppercase tracking-wider text-[10px]">
                  <th className="pb-3 font-semibold">Candidate</th>
                  <th className="pb-3 font-semibold">Email</th>
                  <th className="pb-3 font-semibold">Interviews Taken</th>
                  <th className="pb-3 font-semibold">Average Score</th>
                  <th className="pb-3 font-semibold">Last Active</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {candidates.map((cand) => (
                  <tr key={cand.id} className="hover:bg-slate-800/20">
                    <td className="py-3 font-bold text-white">{cand.name}</td>
                    <td className="py-3 text-slate-400">{cand.email}</td>
                    <td className="py-3 text-slate-300 font-semibold">{cand.interviews_taken}</td>
                    <td className="py-3 font-bold text-emerald-400">
                      {cand.avg_score ? `${cand.avg_score}%` : "—"}
                    </td>
                    <td className="py-3 text-slate-500">
                      {cand.last_interview_date ? new Date(cand.last_interview_date).toLocaleDateString() : "Never"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
