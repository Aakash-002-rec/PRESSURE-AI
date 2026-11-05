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
  const [selectedAttemptId, setSelectedAttemptId] = useState(null);
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
    setSelectedAttemptId(null);
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

  async function handleGoToInterview() {
    if (currentInterview && currentInterview.status === "in_progress" && !currentInterview.is_timeout) {
      setActiveTab("interview");
      return;
    }
    try {
      const list = await api.interviews.list();
      const inProgress = list && list.find((iv) => iv.status === "in_progress" && !iv.is_timeout);
      if (inProgress) {
        setCurrentInterview(inProgress);
        setActiveTab("interview");
        return;
      }
    } catch (e) {
      console.warn("Could not check active interview:", e);
    }
    setActiveTab("setup");
  }

  function handleFinishInterview(interviewId) {
    setReportInterviewId(interviewId);
    setSelectedAttemptId(null);
    setActiveTab("combined_report");
  }

  function handleRetakeInterview() {
    handleStartRetest();
  }

  function handleViewReport(interviewId) {
    setReportInterviewId(interviewId);
    setActiveTab("report");
  }

  function handleViewAttemptReport(attemptId) {
    setSelectedAttemptId(attemptId);
    setActiveTab("combined_report");
  }

  const [retestLoading, setRetestLoading] = useState(false);

  async function handleStartRetest() {
    if (retestLoading) return;
    try {
      setRetestLoading(true);
      await api.assessment.startRetest();
      localStorage.removeItem("pressure_ai_aptitude_completed");
      localStorage.removeItem("pressure_ai_coding_completed");
      localStorage.removeItem("pressure_ai_interview_completed");
      setCurrentInterview(null);
      setReportInterviewId(null);
      setSelectedAttemptId(null);
      setActiveTab("aptitude");
    } catch (err) {
      console.error("Failed to start retest attempt:", err);
      alert("Failed to initialize retest: " + (err.message || "Unknown error"));
    } finally {
      setRetestLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-orange-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        user={user}
        onLogout={handleLogout}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onGoToInterview={handleGoToInterview}
        onOpenAuth={() => setAuthModalOpen(true)}
        onOpenHowItWorks={() => setHowItWorksOpen(true)}
      />

      {/* Main Content Area */}
      <ErrorBoundary>
        <main className="flex-1 pb-16">
          {activeTab === "dashboard" && (
            <CandidateDashboard
              user={user}
              onNavigate={(tab) => {
                if (tab === "setup" || tab === "interview") {
                  handleGoToInterview();
                } else {
                  setActiveTab(tab);
                }
              }}
              onStartAptitude={() => setActiveTab("aptitude")}
              onStartCoding={() => setActiveTab("coding")}
              onStartInterview={handleGoToInterview}
              onStartRoadmap={() => setActiveTab("roadmap")}
              onStartRetest={handleStartRetest}
              onViewAttemptReport={handleViewAttemptReport}
              retestLoading={retestLoading}
              onOpenAuth={() => setAuthModalOpen(true)}
            />
          )}

          {activeTab === "aptitude" && (
            <AptitudeView
              user={user}
              onGoToCoding={() => setActiveTab("coding")}
              onGoToDashboard={() => setActiveTab("dashboard")}
              onStartRetest={handleStartRetest}
              onOpenAuth={() => setAuthModalOpen(true)}
            />
          )}

          {activeTab === "coding" && (
            <CodingView
              user={user}
              onGoToInterview={handleGoToInterview}
              onGoToDashboard={() => setActiveTab("dashboard")}
              onStartRetest={handleStartRetest}
              retestLoading={retestLoading}
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
              onRetakeInterview={handleStartRetest}
              onGoToProgress={() => setActiveTab("progress")}
              onGoToCombined={() => setActiveTab("combined_report")}
              onGoToRoadmap={() => setActiveTab("roadmap")}
            />
          )}

          {activeTab === "combined_report" && (
            <CombinedReportView
              user={user}
              attemptId={selectedAttemptId}
              onClearAttemptId={() => setSelectedAttemptId(null)}
              onGoToRoadmap={() => setActiveTab("roadmap")}
              onGoToRetest={handleStartRetest}
              onGoToDashboard={() => {
                setSelectedAttemptId(null);
                setActiveTab("dashboard");
              }}
            />
          )}

          {activeTab === "roadmap" && (
            <RoadmapView
              user={user}
              onGoToRetest={handleStartRetest}
              onGoToDashboard={() => setActiveTab("dashboard")}
            />
          )}

          {activeTab === "progress" && (
            <ProgressView
              onViewReport={handleViewReport}
              onStartNew={handleStartRetest}
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
            <span className="text-white font-bold">MockMind AI</span>
            <span>•</span>
            <span className="text-[11px] text-orange-400 font-medium">
              AI That Thinks Like a Real Interviewer
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
