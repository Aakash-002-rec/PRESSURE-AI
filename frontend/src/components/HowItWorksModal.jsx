import React from "react";
import { X, Flame, BrainCircuit, Sliders, Sparkles, Target, TrendingUp, CheckCircle } from "lucide-react";

export default function HowItWorksModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 max-h-[90vh] overflow-y-auto shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="mb-6">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-bold mb-2">
            <Flame className="w-3.5 h-3.5" />
            Core Innovation & Architecture
          </div>
          <h2 className="text-2xl font-black text-white">How PRESSURE-AI Works</h2>
          <p className="text-xs text-slate-400 mt-1">
            "PRESSURE-AI is an adaptive AI-powered interview and assessment platform that analyzes candidate responses, identifies weak concepts, dynamically adapts interview difficulty, provides targeted pressure questions, and generates a personalized learning roadmap for improvement."
          </p>
        </div>

        {/* 6 Step Adaptive Feedback Loop */}
        <div className="space-y-4 mb-8">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider text-orange-400">
            The Adaptive Feedback Engine
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs">
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
              <span className="w-6 h-6 rounded-lg bg-orange-500/10 text-orange-400 font-bold flex items-center justify-center mb-2">
                1
              </span>
              <strong className="text-white block mb-1">Answer Evaluation</strong>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Strict JSON evaluation grading correctness, conceptual depth, completeness, and relevance.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
              <span className="w-6 h-6 rounded-lg bg-orange-500/10 text-orange-400 font-bold flex items-center justify-center mb-2">
                2
              </span>
              <strong className="text-white block mb-1">Weakness Detection</strong>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Rule engine tracks topic scores over time, flagging repeated deficits and isolating missing concepts.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
              <span className="w-6 h-6 rounded-lg bg-orange-500/10 text-orange-400 font-bold flex items-center justify-center mb-2">
                3
              </span>
              <strong className="text-white block mb-1">Adaptive Difficulty</strong>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Transitions between Beginner, Intermediate, and Advanced dynamically based on proven ability.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
              <span className="w-6 h-6 rounded-lg bg-orange-500/10 text-orange-400 font-bold flex items-center justify-center mb-2">
                4
              </span>
              <strong className="text-white block mb-1">3-Level Hints</strong>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Gentle conceptual clues (L1) to specific guidance (L2) and strong directional clues (L3) without giving solutions.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-red-950/20 border border-red-500/30">
              <span className="w-6 h-6 rounded-lg bg-red-500/20 text-red-400 font-bold flex items-center justify-center mb-2">
                5
              </span>
              <strong className="text-red-300 block mb-1">🔥 Pressure Mode</strong>
              <p className="text-slate-300 leading-relaxed text-[11px]">
                On repeated weakness, triggers deep scenario/debugging follow-ups challenging the concept from multiple angles.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
              <span className="w-6 h-6 rounded-lg bg-orange-500/10 text-orange-400 font-bold flex items-center justify-center mb-2">
                6
              </span>
              <strong className="text-white block mb-1">Roadmap & Retest</strong>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Generates a 5-stage personalized roadmap with practice questions and longitudinal progress comparisons.
              </p>
            </div>
          </div>
        </div>

        {/* Demo Scenario Guide */}
        <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-orange-400" />
            Official Demo Walkthrough Guide
          </h3>
          <ol className="space-y-1.5 text-xs text-slate-300 list-decimal list-inside leading-relaxed">
            <li>Click <strong>Candidate Demo</strong> to sign in instantly.</li>
            <li>Select <strong>Python</strong>, <strong>Intermediate</strong>, <strong>Mixed</strong> (10 questions).</li>
            <li>Use the <strong>"Fill Strong Answer"</strong> button on first questions to watch difficulty escalate to Advanced.</li>
            <li>On a <strong>Recursion</strong> question, click <strong>"Fill Weak Answer"</strong>.</li>
            <li>Request a <strong>Hint</strong> to see progressive clues.</li>
            <li>Give another weak answer on Recursion to watch <strong className="text-red-400">🔥 PRESSURE MODE</strong> ignite!</li>
            <li>Experience targeted deep follow-up questions testing Recursion mechanics.</li>
            <li>Complete the interview to view the comprehensive report, Recursion learning roadmap, and progress tracking comparison.</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
