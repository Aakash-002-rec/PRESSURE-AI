import React, { useState, useEffect, Component } from "react";
import Navbar from "./components/Navbar";
import AuthModal from "./components/AuthModal";
import CandidateDashboard from "./components/CandidateDashboard";
import AptitudeView from "./components/AptitudeView";
import CodingView from "./components/CodingView";
import SetupView from "./components/SetupView";
import InterviewRoomView from "./components/InterviewRoomView";
import ReportView from "./components/ReportView";
import CombinedReportView from "./components/CombinedReportView";
import RoadmapView from "./components/RoadmapView";
import ProgressView from "./components/ProgressView";
import AdminView from "./components/AdminView";
import HowItWorksModal from "./components/HowItWorksModal";
import { api } from "./api";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-xl mx-auto px-4 py-20 text-center">
          <div className="p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-2">Display Reset Needed</h2>
            <p className="text-xs text-slate-400 mb-6">
              An unexpected render error occurred: {this.state.error?.message || "Render exception"}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false });
                window.location.reload();
              }}
              className="px-6 py-2.5 bg-orange-500 hover:bg-orange-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-orange-500/25"
            >
              Reload Platform
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [currentInterview, setCurrentInterview] = useState(null);
  const [reportInterviewId, setReportInterviewId] = useState(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [howItWorksOpen, setHowItWorksOpen] = useState(false);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    checkCurrentUser();
  }, []);

  async function checkCurrentUser() {
    const token = localStorage.getItem("pressure_ai_token");
    if (token) {
      try {
        const me = await api.auth.getMe();
        setUser(me);
        if (me.role === "admin") {
          setActiveTab("admin");
        } else {
          setActiveTab("dashboard");
        }
      } catch (err) {
        console.warn("Session expired or invalid:", err);
        localStorage.removeItem("pressure_ai_token");
        setUser(null);
        setActiveTab("dashboard");
      }
    } else {
      setActiveTab("dashboard");
    }
    setInitializing(false);
  }

  function handleLogout() {
    localStorage.removeItem("pressure_ai_token");
    setUser(null);
    setCurrentInterview(null);
    setReportInterviewId(null);
    setActiveTab("dashboard");
  }

  function handleAuthSuccess(userData) {
    setUser(userData);
    if (userData.role === "admin") {
      setActiveTab("admin");
    } else {
      setActiveTab("dashboard");
    }
  }

  function handleStartInterview(interview) {
    setCurrentInterview(interview);
    setActiveTab("interview");
  }

  function handleFinishInterview(interviewId) {
    setReportInterviewId(interviewId);
    setActiveTab("report");
  }

  function handleRetakeInterview() {
    setCurrentInterview(null);
    setReportInterviewId(null);
    setActiveTab("setup");
  }

  function handleViewReport(interviewId) {
    setReportInterviewId(interviewId);
    setActiveTab("report");
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-orange-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        user={user}
        onLogout={handleLogout}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenAuth={() => setAuthModalOpen(true)}
        onOpenHowItWorks={() => setHowItWorksOpen(true)}
      />

      {/* Main Content Area */}
      <ErrorBoundary>
        <main className="flex-1 pb-16">
          {activeTab === "dashboard" && (
            <CandidateDashboard
              user={user}
              onNavigate={(tab) => setActiveTab(tab)}
              onStartAptitude={() => setActiveTab("aptitude")}
              onStartCoding={() => setActiveTab("coding")}
              onStartInterview={() => setActiveTab("setup")}
              onStartRoadmap={() => setActiveTab("roadmap")}
              onOpenAuth={() => setAuthModalOpen(true)}
            />
          )}

          {activeTab === "aptitude" && (
            <AptitudeView
              user={user}
              onGoToCoding={() => setActiveTab("coding")}
              onGoToDashboard={() => setActiveTab("dashboard")}
              onOpenAuth={() => setAuthModalOpen(true)}
            />
          )}

          {activeTab === "coding" && (
            <CodingView
              user={user}
              onGoToInterview={() => setActiveTab("setup")}
              onGoToDashboard={() => setActiveTab("dashboard")}
              onOpenAuth={() => setAuthModalOpen(true)}
            />
          )}

          {activeTab === "setup" && (
            <SetupView
              user={user}
              onStartInterview={handleStartInterview}
              onOpenAuth={() => setAuthModalOpen(true)}
            />
          )}

          {activeTab === "interview" && currentInterview && (
            <InterviewRoomView
              interview={currentInterview}
              onFinishInterview={handleFinishInterview}
            />
          )}

          {activeTab === "report" && reportInterviewId && (
            <ReportView
              interviewId={reportInterviewId}
              onRetakeInterview={handleRetakeInterview}
              onGoToProgress={() => setActiveTab("progress")}
              onGoToCombined={() => setActiveTab("combined_report")}
              onGoToRoadmap={() => setActiveTab("roadmap")}
            />
          )}

          {activeTab === "combined_report" && (
            <CombinedReportView
              user={user}
              onGoToRoadmap={() => setActiveTab("roadmap")}
              onGoToRetest={() => setActiveTab("setup")}
              onGoToDashboard={() => setActiveTab("dashboard")}
            />
          )}

          {activeTab === "roadmap" && (
            <RoadmapView
              user={user}
              onGoToRetest={() => setActiveTab("setup")}
              onGoToDashboard={() => setActiveTab("dashboard")}
            />
          )}

          {activeTab === "progress" && (
            <ProgressView
              onViewReport={handleViewReport}
              onStartNew={() => setActiveTab("setup")}
              onGoToRoadmap={() => setActiveTab("roadmap")}
            />
          )}

          {activeTab === "admin" && (
            <AdminView onViewReport={handleViewReport} />
          )}
        </main>
      </ErrorBoundary>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-6 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 font-semibold text-slate-400">
            <span>PRESSURE-AI</span>
            <span>•</span>
            <span className="text-[11px] text-orange-400 font-normal">
              Placement Preparation, Technical Interview & Adaptive Learning Platform
            </span>
          </div>
          <div>
            Aptitude • Isolated Code Arena • AI Mock Interview • 🔥 Pressure Mode • Unified Skill Profile
          </div>
        </div>
      </footer>

      {/* Modals */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      <HowItWorksModal
        isOpen={howItWorksOpen}
        onClose={() => setHowItWorksOpen(false)}
      />
    </div>
  );
}
