import React, { useState, useEffect } from "react";
import { 
  Award, BrainCircuit, Code2, BookOpen, BarChart3, Flame, 
  ArrowRight, CheckCircle2, AlertTriangle, Sparkles, Target, 
  Compass, Clock, Play, RotateCcw, Layers, HelpCircle, ChevronRight,
  Maximize2, X, Zap, TrendingUp, ShieldCheck, Activity
} from "lucide-react";
import { api } from "../api";

export default function CandidateDashboard({ 
  user, 
  onNavigate, 
  onStartInterview, 
  onOpenAuth 
}) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeWidgetDetail, setActiveWidgetDetail] = useState(null); // stores active enlarged widget info

  useEffect(() => {
    if (user) {
      loadProfile();
    } else {
      setLoading(false);
    }
  }, [user]);

  async function loadProfile() {
    try {
      setLoading(true);
      const data = await api.assessment.getCombined();
      setProfile(data);
    } catch (err) {
      console.warn("Could not load combined profile:", err);
    } finally {
      setLoading(false);
    }
  }

  // Journey steps definition
  const journeySteps = [
    { 
      id: "aptitude", 
      title: "Aptitude Test", 
      desc: "Quantitative, Logical, Verbal & Data Interpretation", 
      icon: Compass, 
      color: "text-blue-400 bg-blue-500/10 border-blue-500/30",
      actionDesc: "Aptitude benchmarking across 4 categories. Requires 10 completed questions to advance."
    },
    { 
      id: "coding", 
      title: "Coding Session", 
      desc: "Python algorithmic execution & edge-case testing", 
      icon: Code2, 
      color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
      actionDesc: "Live Python editor with isolated execution against visible and hidden test cases."
    },
    { 
      id: "setup", 
      title: "AI Mock Interview", 
      desc: "Context-aware adaptive interview & pressure mode", 
      icon: BrainCircuit, 
      color: "text-orange-400 bg-orange-500/10 border-orange-500/30",
      actionDesc: "Interviews adapt to your prior weaknesses and activate 🔥 Pressure Mode when challenged."
    },
    { 
      id: "combined_report", 
      title: "Final Assessment", 
      desc: "Unified multi-axis performance report", 
      icon: Award, 
      color: "text-purple-400 bg-purple-500/10 border-purple-500/30",
      actionDesc: "Comprehensive audit synthesising Aptitude, Coding, and Technical Interview."
    },
    { 
      id: "roadmap", 
      title: "Weakness & Roadmap", 
      desc: "Targeted root-cause analysis & 5-stage plan", 
      icon: Target, 
      color: "text-red-400 bg-red-500/10 border-red-500/30",
      actionDesc: "Actionable 5-stage plan to eliminate your specific identified bottlenecks."
    },
    { 
      id: "practice", 
      title: "Practice & Retest", 
      desc: "Easy, Medium, Advanced drills with score updates", 
      icon: RotateCcw, 
      color: "text-amber-400 bg-amber-500/10 border-amber-500/30",
      actionDesc: "8 targeted practice problems to solidify mastery and re-benchmark your score."
    },
    { 
      id: "progress", 
      title: "Progress Tracking", 
      desc: "Longitudinal score curves & delta tracking", 
      icon: BarChart3, 
      color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
      actionDesc: "Track historical test curves and measured percentage improvement points."
    }
  ];

  const aptitudeScore = profile ? profile.aptitude_score : 72.0;
  const codingScore = profile ? profile.coding_score : 81.0;
  const interviewScore = profile ? profile.interview_score : 68.0;
  const overallProgress = profile ? profile.overall_readiness : 74.0;

  const majorWeakness = profile && profile.major_weaknesses && profile.major_weaknesses.length > 0
    ? profile.major_weaknesses[0].topic
    : "Recursion";

  // Open Enlarged Widget Inspector
  function inspectWidget(widgetType, customData = {}) {
    setActiveWidgetDetail({
      type: widgetType,
      ...customData
    });
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 animate-fade-in space-y-8">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-900 to-orange-950/40 border border-slate-800 p-8 md:p-10 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-semibold mb-3">
              <Flame className="w-3.5 h-3.5" />
              Comprehensive Placement Preparation & Assessment Platform
            </div>
            <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight mb-3">
              Welcome to PRESSURE<span className="text-orange-500">-AI</span>
            </h1>
            <p className="text-xs md:text-sm text-slate-300 leading-relaxed font-normal">
              Master technical recruitment from first principles. Progress seamlessly through diagnostic <strong>Aptitude</strong>, live <strong>Coding</strong>, and closed-loop <strong>AI Mock Interviews</strong> with targeted <strong>🔥 Pressure Mode</strong> probing.
            </p>
          </div>

          {/* Quick CTA */}
          <div className="flex flex-col sm:flex-row items-center gap-3">
            <button
              onClick={() => onNavigate("aptitude")}
              className="w-full sm:w-auto px-6 py-3.5 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-orange-500/25 flex items-center justify-center gap-2 transition-transform hover:scale-[1.03] active:scale-[0.98]"
            >
              <Compass className="w-4 h-4" />
              Start Aptitude Test
            </button>
            <button
              onClick={() => onNavigate("coding")}
              className="w-full sm:w-auto px-5 py-3.5 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-bold text-xs rounded-xl flex items-center justify-center gap-2 transition-all hover:scale-[1.03] active:scale-[0.98]"
            >
              <Code2 className="w-4 h-4 text-emerald-400" />
              Coding Arena
            </button>
          </div>
        </div>

        {/* Candidate Preparation Pipeline Journey Tracker */}
        <div className="mt-8 pt-6 border-t border-slate-800/80">
          <div className="flex items-center justify-between mb-3 text-xs font-bold text-slate-400 uppercase tracking-wider">
            <span>Placement Readiness Journey (Click any step to inspect & launch)</span>
            <span className="text-orange-400 font-mono">End-to-End Pipeline</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5">
            {journeySteps.map((step, idx) => {
              const StepIcon = step.icon;
              return (
                <button
                  key={step.id}
                  onClick={() => inspectWidget("pipeline_step", { step, stepIdx: idx + 1 })}
                  className="p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-orange-500/60 text-left transition-all group flex flex-col justify-between hover:bg-slate-900 hover:scale-[1.04] active:scale-[0.96] shadow-sm hover:shadow-orange-500/10"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="w-5 h-5 rounded-md bg-slate-900 text-[10px] font-bold text-slate-400 flex items-center justify-center border border-slate-800 group-hover:border-orange-500/50 group-hover:text-orange-400">
                      {idx + 1}
                    </span>
                    <StepIcon className="w-3.5 h-3.5 text-slate-400 group-hover:text-orange-400 transition-colors" />
                  </div>
                  <div>
                    <span className="text-xs font-bold text-white block group-hover:text-orange-400 transition-colors">
                      {step.title}
                    </span>
                    <span className="text-[10px] text-slate-400 line-clamp-1">
                      {step.desc}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* PLACEMENT READINESS METRICS CARD - CLICKABLE & EXPANDABLE */}
      <div 
        onClick={() => inspectWidget("readiness")}
        className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 relative overflow-hidden widget-interactive group"
      >
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Live Diagnostic Profile
              </span>
              <span className="text-[11px] text-slate-500 flex items-center gap-1 group-hover:text-orange-400 transition-colors">
                <Maximize2 className="w-3 h-3" /> Click to enlarge & inspect
              </span>
            </div>
            <h2 className="text-2xl font-black text-white group-hover:text-orange-400 transition-colors">
              Placement Readiness Overview
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Weighted aggregation of Aptitude (25%), Coding (35%), and Technical AI Mock Interviews (40%).
            </p>
          </div>

          {/* Overall Dial */}
          <div className="flex items-center gap-4">
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center gap-4 group-hover:border-orange-500/40 transition-colors">
              <div className="w-16 h-16 rounded-xl bg-gradient-to-tr from-orange-500 to-amber-500 flex items-center justify-center font-black text-2xl text-white shadow-lg shadow-orange-500/20 group-hover:scale-105 transition-transform">
                {overallProgress}%
              </div>
              <div>
                <span className="text-xs font-bold text-white block">Overall Readiness</span>
                <span className="text-[11px] text-emerald-400 font-semibold">Tier 1 Placement Ready</span>
              </div>
            </div>
          </div>
        </div>

        {/* 3 Core Module Progress Bars - CLICKABLE */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
          {/* Aptitude Bar */}
          <div 
            onClick={(e) => {
              e.stopPropagation();
              inspectWidget("aptitude_detail");
            }}
            className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 hover:border-blue-500/50 hover:bg-slate-900/80 transition-all cursor-pointer group/bar hover:scale-[1.02]"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Compass className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-bold text-white group-hover/bar:text-blue-300">Aptitude Test</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-mono font-bold text-blue-400">{aptitudeScore}%</span>
                <Maximize2 className="w-3 h-3 text-slate-500 group-hover/bar:text-blue-400" />
              </div>
            </div>
            <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800 mb-2">
              <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${aptitudeScore}%` }} />
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Logical: 82%</span>
              <span className="text-red-400">Data Interp: 48% 🔴</span>
            </div>
          </div>

          {/* Coding Bar */}
          <div 
            onClick={(e) => {
              e.stopPropagation();
              inspectWidget("coding_detail");
            }}
            className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 hover:border-emerald-500/50 hover:bg-slate-900/80 transition-all cursor-pointer group/bar hover:scale-[1.02]"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold text-white group-hover/bar:text-emerald-300">Coding Session</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-mono font-bold text-emerald-400">{codingScore}%</span>
                <Maximize2 className="w-3 h-3 text-slate-500 group-hover/bar:text-emerald-400" />
              </div>
            </div>
            <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800 mb-2">
              <div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${codingScore}%` }} />
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>Arrays: 82%</span>
              <span className="text-red-400">Recursion: 42% 🔴</span>
            </div>
          </div>

          {/* Technical Interview Bar */}
          <div 
            onClick={(e) => {
              e.stopPropagation();
              inspectWidget("interview_detail");
            }}
            className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 hover:border-orange-500/50 hover:bg-slate-900/80 transition-all cursor-pointer group/bar hover:scale-[1.02]"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-orange-400" />
                <span className="text-xs font-bold text-white group-hover/bar:text-orange-300">AI Mock Interview</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-mono font-bold text-orange-400">{interviewScore}%</span>
                <Maximize2 className="w-3 h-3 text-slate-500 group-hover/bar:text-orange-400" />
              </div>
            </div>
            <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800 mb-2">
              <div className="h-full bg-gradient-to-r from-orange-500 to-amber-500 rounded-full transition-all" style={{ width: `${interviewScore}%` }} />
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <span>OOP: 76%</span>
              <span className="text-red-400">Recursion Probe: 45% 🔴</span>
            </div>
          </div>
        </div>

        {/* 3 Quick Diagnostic Callouts - CLICKABLE WIDGETS */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6 pt-6 border-t border-slate-800/80">
          <div 
            onClick={(e) => {
              e.stopPropagation();
              inspectWidget("weakness_detail");
            }}
            className="p-3.5 bg-red-950/20 border border-red-500/20 rounded-xl flex items-start gap-3 hover:bg-red-950/40 hover:border-red-500/40 hover:scale-[1.02] cursor-pointer transition-all"
          >
            <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold text-red-400 block">Cross-Module Major Weakness</span>
                <Maximize2 className="w-2.5 h-2.5 text-red-400/60" />
              </div>
              <span className="text-xs font-bold text-white">{majorWeakness}</span>
              <p className="text-[11px] text-slate-400 mt-0.5">Struggled in both Coding (42%) and Interview (45%). Click to inspect.</p>
            </div>
          </div>

          <div 
            onClick={(e) => {
              e.stopPropagation();
              inspectWidget("recommendation_detail");
            }}
            className="p-3.5 bg-orange-950/20 border border-orange-500/20 rounded-xl flex items-start gap-3 hover:bg-orange-950/40 hover:border-orange-500/40 hover:scale-[1.02] cursor-pointer transition-all"
          >
            <Sparkles className="w-4 h-4 text-orange-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold text-orange-400 block">Recommended Action</span>
                <Maximize2 className="w-2.5 h-2.5 text-orange-400/60" />
              </div>
              <span className="text-xs font-bold text-white">Practice Base Cases & Stack Frames</span>
              <p className="text-[11px] text-slate-400 mt-0.5">Complete the 5-stage personalized roadmap. Click to inspect.</p>
            </div>
          </div>

          <div 
            onClick={(e) => {
              e.stopPropagation();
              inspectWidget("strength_detail");
            }}
            className="p-3.5 bg-emerald-950/20 border border-emerald-500/20 rounded-xl flex items-start gap-3 hover:bg-emerald-950/40 hover:border-emerald-500/40 hover:scale-[1.02] cursor-pointer transition-all"
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold text-emerald-400 block">Strongest Foundation</span>
                <Maximize2 className="w-2.5 h-2.5 text-emerald-400/60" />
              </div>
              <span className="text-xs font-bold text-white">Python Basics & OOP (88%)</span>
              <p className="text-[11px] text-slate-400 mt-0.5">High conceptual clarity in class structures & syntax.</p>
            </div>
          </div>
        </div>
      </div>

      {/* 6 MAIN PLATFORM CARDS - INTERACTIVE EXPANDABLE WIDGETS */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <span>Candidate Core Modules</span>
            <span className="text-xs text-slate-500 font-normal">• Click card to inspect or launch action</span>
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {/* Card 1: Aptitude Test */}
          <div 
            onClick={() => inspectWidget("aptitude_detail")}
            className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-blue-500/50 hover:shadow-2xl hover:shadow-blue-500/10 transition-all cursor-pointer group flex flex-col justify-between widget-interactive"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 group-hover:scale-110 transition-transform">
                  <Compass className="w-6 h-6" />
                </div>
                <span className="text-xs text-slate-500 group-hover:text-blue-400 flex items-center gap-1 font-semibold">
                  <Maximize2 className="w-3.5 h-3.5" /> Inspect
                </span>
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                  Stage 1
                </span>
                <span className="text-xs text-slate-500 font-mono">Timed MCQs</span>
              </div>
              <h4 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors mb-2">
                1. Aptitude Test
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Evaluate Quantitative Aptitude, Logical Reasoning, Verbal Ability, and Data Interpretation with reliable question banks.
              </p>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs">
              <span className="text-slate-400 font-medium">Difficulty: Beginner - Adv</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onNavigate("aptitude");
                }}
                className="px-3 py-1.5 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 text-blue-400 font-bold rounded-lg flex items-center gap-1 group-hover:translate-x-0.5 transition-all"
              >
                Launch Test <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Card 2: Coding Session */}
          <div 
            onClick={() => inspectWidget("coding_detail")}
            className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-emerald-500/50 hover:shadow-2xl hover:shadow-emerald-500/10 transition-all cursor-pointer group flex flex-col justify-between widget-interactive"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                  <Code2 className="w-6 h-6" />
                </div>
                <span className="text-xs text-slate-500 group-hover:text-emerald-400 flex items-center gap-1 font-semibold">
                  <Maximize2 className="w-3.5 h-3.5" /> Inspect
                </span>
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">
                  Stage 2
                </span>
                <span className="text-xs text-slate-500 font-mono">Live Runner</span>
              </div>
              <h4 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors mb-2">
                2. Coding Session
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Solve coding problems with a dedicated editor, real-time Python execution, edge-case test suites, and AI progressive hints.
              </p>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs">
              <span className="text-slate-400 font-medium">Languages: Python, JS, C++</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onNavigate("coding");
                }}
                className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 font-bold rounded-lg flex items-center gap-1 group-hover:translate-x-0.5 transition-all"
              >
                Enter Arena <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Card 3: AI Mock Interview */}
          <div 
            onClick={() => inspectWidget("interview_detail")}
            className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-orange-500/50 hover:shadow-2xl hover:shadow-orange-500/10 transition-all cursor-pointer group flex flex-col justify-between widget-interactive"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-400 group-hover:scale-110 transition-transform">
                  <Flame className="w-6 h-6" />
                </div>
                <span className="text-xs text-slate-500 group-hover:text-orange-400 flex items-center gap-1 font-semibold">
                  <Maximize2 className="w-3.5 h-3.5" /> Inspect
                </span>
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-orange-500/10 text-orange-400 border border-orange-500/20 uppercase">
                  Stage 3
                </span>
                <span className="text-xs text-slate-500 font-mono">Adaptive AI</span>
              </div>
              <h4 className="text-lg font-bold text-white group-hover:text-orange-400 transition-colors mb-2">
                3. AI Mock Interview
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Interactive oral and code interview arena. Dynamically probes weak concepts from previous sessions and triggers 🔥 Pressure Mode.
              </p>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs">
              <span className="text-slate-400 font-medium">13 Tech Domains</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onNavigate("setup");
                }}
                className="px-3 py-1.5 bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/30 text-orange-400 font-bold rounded-lg flex items-center gap-1 group-hover:translate-x-0.5 transition-all"
              >
                Launch Arena <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Card 4: Performance Report */}
          <div 
            onClick={() => inspectWidget("report_detail")}
            className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-purple-500/50 hover:shadow-2xl hover:shadow-purple-500/10 transition-all cursor-pointer group flex flex-col justify-between widget-interactive"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                  <Award className="w-6 h-6" />
                </div>
                <span className="text-xs text-slate-500 group-hover:text-purple-400 flex items-center gap-1 font-semibold">
                  <Maximize2 className="w-3.5 h-3.5" /> Inspect
                </span>
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 uppercase">
                  Diagnostic
                </span>
                <span className="text-xs text-slate-500 font-mono">Combined Audit</span>
              </div>
              <h4 className="text-lg font-bold text-white group-hover:text-purple-400 transition-colors mb-2">
                4. Performance Report
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Examine your combined assessment results across Aptitude, Coding, and Interview. View multi-axis scoring and diagnosed gaps.
              </p>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs">
              <span className="text-slate-400 font-medium">Overall Score: {overallProgress}%</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onNavigate("combined_report");
                }}
                className="px-3 py-1.5 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-400 font-bold rounded-lg flex items-center gap-1 group-hover:translate-x-0.5 transition-all"
              >
                View Report <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Card 5: Learning Recommendations & Roadmap */}
          <div 
            onClick={() => inspectWidget("roadmap_detail")}
            className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-red-500/50 hover:shadow-2xl hover:shadow-red-500/10 transition-all cursor-pointer group flex flex-col justify-between widget-interactive"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400 group-hover:scale-110 transition-transform">
                  <Target className="w-6 h-6" />
                </div>
                <span className="text-xs text-slate-500 group-hover:text-red-400 flex items-center gap-1 font-semibold">
                  <Maximize2 className="w-3.5 h-3.5" /> Inspect
                </span>
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20 uppercase">
                  Remediation
                </span>
                <span className="text-xs text-slate-500 font-mono">5-Stage Roadmap</span>
              </div>
              <h4 className="text-lg font-bold text-white group-hover:text-red-400 transition-colors mb-2">
                5. Learning Recommendations
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Discover why you struggled with weak concepts, what core mechanics to learn, and check off interactive roadmap milestones.
              </p>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs">
              <span className="text-slate-400 font-medium">Top Priority: {majorWeakness}</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onNavigate("roadmap");
                }}
                className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400 font-bold rounded-lg flex items-center gap-1 group-hover:translate-x-0.5 transition-all"
              >
                Open Roadmap <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Card 6: Progress Tracking */}
          <div 
            onClick={() => inspectWidget("progress_detail")}
            className="glass-panel p-6 rounded-3xl border border-slate-800 hover:border-cyan-500/50 hover:shadow-2xl hover:shadow-cyan-500/10 transition-all cursor-pointer group flex flex-col justify-between widget-interactive"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
                  <BarChart3 className="w-6 h-6" />
                </div>
                <span className="text-xs text-slate-500 group-hover:text-cyan-400 flex items-center gap-1 font-semibold">
                  <Maximize2 className="w-3.5 h-3.5" /> Inspect
                </span>
              </div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase">
                  Analytics
                </span>
                <span className="text-xs text-slate-500 font-mono">Longitudinal</span>
              </div>
              <h4 className="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors mb-2">
                6. Progress Tracking
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Verify measurable improvement over multi-session attempts. Track upward percentage deltas and topic mastery verification.
              </p>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs">
              <span className="text-slate-400 font-medium">Charts & Attempt History</span>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onNavigate("progress");
                }}
                className="px-3 py-1.5 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 font-bold rounded-lg flex items-center gap-1 group-hover:translate-x-0.5 transition-all"
              >
                Track Deltas <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* INTERACTIVE ENLARGED WIDGET INSPECTION MODAL ("COMING BIG" ON CLICK)     */}
      {/* ========================================================================= */}
      {activeWidgetDetail && (
        <div 
          onClick={() => setActiveWidgetDetail(null)}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in"
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-2xl animate-pop-in space-y-6 max-h-[90vh] overflow-y-auto"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-orange-500/15 border border-orange-500/30 flex items-center justify-center text-orange-400 font-bold">
                  {activeWidgetDetail.type === "readiness" && <Activity className="w-6 h-6" />}
                  {activeWidgetDetail.type === "aptitude_detail" && <Compass className="w-6 h-6 text-blue-400" />}
                  {activeWidgetDetail.type === "coding_detail" && <Code2 className="w-6 h-6 text-emerald-400" />}
                  {activeWidgetDetail.type === "interview_detail" && <Flame className="w-6 h-6 text-orange-400" />}
                  {activeWidgetDetail.type === "weakness_detail" && <AlertTriangle className="w-6 h-6 text-red-400" />}
                  {activeWidgetDetail.type === "recommendation_detail" && <Sparkles className="w-6 h-6 text-orange-400" />}
                  {activeWidgetDetail.type === "strength_detail" && <CheckCircle2 className="w-6 h-6 text-emerald-400" />}
                  {activeWidgetDetail.type === "report_detail" && <Award className="w-6 h-6 text-purple-400" />}
                  {activeWidgetDetail.type === "roadmap_detail" && <Target className="w-6 h-6 text-red-400" />}
                  {activeWidgetDetail.type === "progress_detail" && <BarChart3 className="w-6 h-6 text-cyan-400" />}
                  {activeWidgetDetail.type === "pipeline_step" && <Zap className="w-6 h-6 text-amber-400" />}
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                    Interactive Widget Inspector
                  </span>
                  <h3 className="text-xl font-black text-white mt-1">
                    {activeWidgetDetail.type === "readiness" && "Placement Readiness Diagnostic Hub"}
                    {activeWidgetDetail.type === "aptitude_detail" && "Stage 1: Aptitude Assessment Module"}
                    {activeWidgetDetail.type === "coding_detail" && "Stage 2: Algorithmic Coding Arena"}
                    {activeWidgetDetail.type === "interview_detail" && "Stage 3: Adaptive AI Mock Interview"}
                    {activeWidgetDetail.type === "weakness_detail" && `Critical Root-Cause Analysis: ${majorWeakness}`}
                    {activeWidgetDetail.type === "recommendation_detail" && "Interactive Remediation Strategy"}
                    {activeWidgetDetail.type === "strength_detail" && "Demonstrated Mastery Profile"}
                    {activeWidgetDetail.type === "report_detail" && "Comprehensive Multi-Pillar Audit"}
                    {activeWidgetDetail.type === "roadmap_detail" && "5-Stage Personalized Learning Roadmap"}
                    {activeWidgetDetail.type === "progress_detail" && "Longitudinal Progress & Delta Analytics"}
                    {activeWidgetDetail.type === "pipeline_step" && `Pipeline Step #${activeWidgetDetail.stepIdx}: ${activeWidgetDetail.step?.title}`}
                  </h3>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setActiveWidgetDetail(null)}
                className="w-9 h-9 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body with Detailed Metrics */}
            <div className="space-y-4">
              {/* Readiness View */}
              {activeWidgetDetail.type === "readiness" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                      <span className="text-[10px] text-slate-400 block uppercase font-semibold">Aptitude</span>
                      <span className="text-lg font-bold text-blue-400">{aptitudeScore}%</span>
                    </div>
                    <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                      <span className="text-[10px] text-slate-400 block uppercase font-semibold">Coding</span>
                      <span className="text-lg font-bold text-emerald-400">{codingScore}%</span>
                    </div>
                    <div className="p-3 bg-slate-950 rounded-xl border border-slate-800">
                      <span className="text-[10px] text-slate-400 block uppercase font-semibold">Interview</span>
                      <span className="text-lg font-bold text-orange-400">{interviewScore}%</span>
                    </div>
                  </div>
                  <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800">
                    <span className="text-xs font-bold text-white block mb-1">Detected Placement Action:</span>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      Your overall readiness of <strong>{overallProgress}%</strong> qualifies for Tier-1 engineering interviews. Focus on closing your <strong>{majorWeakness}</strong> gap to reach the 85%+ threshold.
                    </p>
                  </div>
                </div>
              )}

              {/* Aptitude View */}
              {activeWidgetDetail.type === "aptitude_detail" && (
                <div className="space-y-3">
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Standard placement screening tests quantitative speed, logical deduction, verbal accuracy, and data analysis.
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Categories Included</span>
                      <span className="text-white font-medium">Quantitative, Logical, Verbal, DI</span>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                      <span className="text-slate-400 block text-[10px] uppercase font-bold">Completion Rule</span>
                      <span className="text-emerald-400 font-medium">All 10 Questions Required</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Coding View */}
              {activeWidgetDetail.type === "coding_detail" && (
                <div className="space-y-3">
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Interactive Python code arena with real-time subprocess execution, test harness validation, and AI progressive hints.
                  </p>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs">
                    <span className="text-slate-400 block text-[10px] uppercase font-bold mb-1">Diagnosed Priority</span>
                    <span className="text-red-400 font-semibold">Recursive Factorial & Fibonacci with Boundary Guards</span>
                  </div>
                </div>
              )}

              {/* Weakness View */}
              {activeWidgetDetail.type === "weakness_detail" && (
                <div className="space-y-3">
                  <div className="p-4 bg-red-950/30 border border-red-500/30 rounded-2xl text-xs space-y-2">
                    <span className="text-red-400 font-bold uppercase block text-[10px]">Why you are weak:</span>
                    <p className="text-slate-200 leading-relaxed">
                      Cross-module analysis detected repeated failure to terminate recursive call stacks without crashing. Both the Coding runner and AI Interviewer detected missing base criteria.
                    </p>
                  </div>
                  <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-300">
                    <strong>Recommended Action:</strong> Revise recursive invariants, practice 8 targeted drills, and re-attempt the AI interview.
                  </div>
                </div>
              )}

              {/* Generic Pipeline or Other Views */}
              {activeWidgetDetail.step && (
                <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 text-xs space-y-2">
                  <span className="text-orange-400 font-bold uppercase block text-[10px]">Stage Objective:</span>
                  <p className="text-slate-300 leading-relaxed">{activeWidgetDetail.step.actionDesc}</p>
                </div>
              )}
            </div>

            {/* Modal Action CTA */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800 gap-3">
              <button
                type="button"
                onClick={() => setActiveWidgetDetail(null)}
                className="px-4 py-2.5 rounded-xl border border-slate-800 text-xs font-semibold text-slate-400 hover:text-white"
              >
                Close Inspector
              </button>

              <button
                type="button"
                onClick={() => {
                  const targetTab = 
                    activeWidgetDetail.type === "aptitude_detail" ? "aptitude" :
                    activeWidgetDetail.type === "coding_detail" ? "coding" :
                    activeWidgetDetail.type === "interview_detail" ? "setup" :
                    activeWidgetDetail.type === "weakness_detail" || activeWidgetDetail.type === "recommendation_detail" || activeWidgetDetail.type === "roadmap_detail" ? "roadmap" :
                    activeWidgetDetail.type === "progress_detail" ? "progress" :
                    activeWidgetDetail.type === "report_detail" || activeWidgetDetail.type === "readiness" ? "combined_report" :
                    activeWidgetDetail.step ? activeWidgetDetail.step.id : "dashboard";
                  setActiveWidgetDetail(null);
                  onNavigate(targetTab);
                }}
                className="px-6 py-2.5 bg-gradient-to-r from-orange-500 via-red-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-orange-500/25 flex items-center gap-2 transition-all hover:scale-105"
              >
                <span>Launch Interactive Module</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
