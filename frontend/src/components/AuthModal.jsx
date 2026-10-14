import React, { useState } from "react";
import { X, Sparkles, UserCheck, ShieldCheck, Mail, Lock, User, ArrowRight, AlertCircle } from "lucide-react";
import { api } from "../api";

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("candidate");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      let res;
      if (isRegister) {
        res = await api.auth.register(name, email, password, role);
      } else {
        res = await api.auth.login(email, password);
      }
      localStorage.setItem("pressure_ai_token", res.access_token);
      onAuthSuccess(res.user);
      onClose();
    } catch (err) {
      setError(err.message || "Authentication failed. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  }

  async function handleQuickDemo(demoRole) {
    setError(null);
    setLoading(true);
    try {
      const demoEmail = demoRole === "admin" ? "admin@pressure.ai" : "candidate@pressure.ai";
      const demoPass = demoRole === "admin" ? "admin123" : "candidate123";
      const res = await api.auth.login(demoEmail, demoPass);
      localStorage.setItem("pressure_ai_token", res.access_token);
      onAuthSuccess(res.user);
      onClose();
    } catch (err) {
      setError(`Quick demo login failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 shadow-2xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="text-center mb-5">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            Interview Preparation Portal
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            {isRegister ? "Create Your Account" : "Welcome to PRESSURE-AI"}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {isRegister ? "Join to practice adaptive technical interviews" : "Sign in to access your interview arena & learning roadmap"}
          </p>
        </div>

        {/* Tab Selector */}
        <div className="grid grid-cols-2 gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 mb-5">
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(null); }}
            className={`py-1.5 text-xs font-bold rounded-lg transition-all ${
              !isRegister
                ? "bg-orange-500 text-white shadow-md shadow-orange-500/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(null); }}
            className={`py-1.5 text-xs font-bold rounded-lg transition-all ${
              isRegister
                ? "bg-orange-500 text-white shadow-md shadow-orange-500/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Register New
          </button>
        </div>

        {/* Quick Demo Credentials */}
        <div className="mb-5 p-3 bg-slate-800/60 border border-slate-700/60 rounded-xl">
          <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>⚡ Instant One-Click Demo Access</span>
            <span className="text-[10px] text-orange-400">Pre-configured</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo("candidate")}
              disabled={loading}
              className="flex items-center justify-center gap-1.5 py-2 px-3 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 rounded-lg text-xs font-semibold transition-all hover:scale-[1.02]"
            >
              <UserCheck className="w-3.5 h-3.5" />
              Candidate Demo
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo("admin")}
              disabled={loading}
              className="flex items-center justify-center gap-1.5 py-2 px-3 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-300 rounded-lg text-xs font-semibold transition-all hover:scale-[1.02]"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              Admin Demo
            </button>
          </div>
        </div>

        <div className="relative flex py-2 items-center">
          <div className="flex-grow border-t border-slate-800"></div>
          <span className="flex-shrink mx-3 text-[11px] text-slate-500 uppercase font-medium">Or Use Credentials</span>
          <div className="flex-grow border-t border-slate-800"></div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-xs text-red-400">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="e.g. Alex Johnson"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 bg-slate-950/70 border border-slate-800 focus:border-orange-500 rounded-lg text-xs text-white placeholder-slate-500 outline-none transition-colors"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-950/70 border border-slate-800 focus:border-orange-500 rounded-lg text-xs text-white placeholder-slate-500 outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-950/70 border border-slate-800 focus:border-orange-500 rounded-lg text-xs text-white placeholder-slate-500 outline-none transition-colors"
              />
            </div>
          </div>

          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Account Role</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setRole("candidate")}
                  className={`py-1.5 px-3 rounded-lg text-xs font-medium border text-center transition-all ${
                    role === "candidate"
                      ? "bg-orange-500/20 border-orange-500 text-orange-300"
                      : "bg-slate-950/50 border-slate-800 text-slate-400"
                  }`}
                >
                  Candidate
                </button>
                <button
                  type="button"
                  onClick={() => setRole("admin")}
                  className={`py-1.5 px-3 rounded-lg text-xs font-medium border text-center transition-all ${
                    role === "admin"
                      ? "bg-purple-500/20 border-purple-500 text-purple-300"
                      : "bg-slate-950/50 border-slate-800 text-slate-400"
                  }`}
                >
                  Admin Manager
                </button>
              </div>
            </div>
          )}

          {!isRegister && (
            <p className="text-[10px] text-slate-500 text-center">
              💡 First time? Entering your email will automatically create your account.
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-1 py-2.5 bg-gradient-to-r from-orange-500 to-amber-600 hover:from-orange-600 hover:to-amber-700 text-white font-bold text-xs rounded-lg shadow-lg shadow-orange-500/25 flex items-center justify-center gap-1.5 transition-all disabled:opacity-50"
          >
            {loading ? "Processing..." : isRegister ? "Create Account" : "Sign In / Continue"}
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        <div className="mt-5 text-center">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-xs text-slate-400 hover:text-orange-400 transition-colors"
          >
            {isRegister
              ? "Already have an account? Sign in here"
              : "Don't have an account? Register now"}
          </button>
        </div>
      </div>
    </div>
  );
}
