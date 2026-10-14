import React from "react";
import { Flame, BrainCircuit, BarChart3, ShieldCheck, User, LogOut, Info, Sparkles, PlusCircle } from "lucide-react";

export default function Navbar({ user, onLogout, activeTab, setActiveTab, onOpenAuth, onOpenHowItWorks }) {
  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-slate-800 px-4 lg:px-8 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => setActiveTab("setup")}
          className="flex items-center gap-2.5 cursor-pointer group"
        >
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-tr from-orange-600 via-red-600 to-amber-500 flex items-center justify-center shadow-lg shadow-orange-600/30 group-hover:scale-105 transition-transform">
            <Flame className="w-6 h-6 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-xl tracking-tight text-white">
                PRESSURE<span className="text-orange-500 font-black">-AI</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/20">
                Adaptive
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Intelligent Technical Interview Platform</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        {user && (
          <div className="hidden lg:flex items-center gap-1 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "dashboard"
                  ? "bg-orange-500 text-white shadow-md shadow-orange-500/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              Dashboard
            </button>

            <button
              onClick={() => setActiveTab("aptitude")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "aptitude"
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              Aptitude
            </button>

            <button
              onClick={() => setActiveTab("coding")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "coding"
                  ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              Coding
            </button>

            <button
              onClick={() => setActiveTab("setup")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "setup" || activeTab === "interview"
                  ? "bg-orange-500 text-white shadow-md shadow-orange-500/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              <BrainCircuit className="w-3.5 h-3.5" />
              AI Interview
            </button>

            <button
              onClick={() => setActiveTab("combined_report")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "combined_report"
                  ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              Assessment
            </button>

            <button
              onClick={() => setActiveTab("roadmap")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "roadmap"
                  ? "bg-red-600 text-white shadow-md shadow-red-600/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              Roadmap
            </button>

            <button
              onClick={() => setActiveTab("progress")}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "progress"
                  ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              Progress
            </button>

            {user.role === "admin" && (
              <button
                onClick={() => setActiveTab("admin")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === "admin"
                    ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                Admin
              </button>
            )}
          </div>
        )}

        {/* Actions & User State */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenHowItWorks}
            className="flex items-center gap-1 px-3 py-1.5 text-xs text-slate-300 hover:text-white bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 rounded-lg transition-colors"
          >
            <Info className="w-3.5 h-3.5 text-orange-400" />
            <span className="hidden sm:inline">How It Works</span>
          </button>

          {user ? (
            <div className="flex items-center gap-3 pl-2 border-l border-slate-800">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-semibold text-white">{user.name}</div>
                <div className="flex items-center justify-end gap-1">
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded uppercase ${
                    user.role === "admin" 
                      ? "bg-purple-500/20 text-purple-400 border border-purple-500/30" 
                      : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  }`}>
                    {user.role}
                  </span>
                </div>
              </div>

              <button
                onClick={onLogout}
                title="Log Out"
                className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg border border-slate-800 hover:border-red-500/30 transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white text-xs font-bold rounded-lg shadow-lg shadow-orange-500/25 transition-all"
            >
              <User className="w-3.5 h-3.5" />
              Sign In / Demo
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
