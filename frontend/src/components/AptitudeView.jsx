import React, { useState, useEffect, useRef } from "react";
import { 
  Compass, Clock, CheckCircle2, AlertTriangle, ArrowRight, 
  ArrowLeft, RotateCcw, Target, Sparkles, RefreshCw, BarChart2,
  HelpCircle, ChevronRight, Check, X
} from "lucide-react";
import { api } from "../api";

export default function AptitudeView({ user, onGoToCoding, onGoToPractice, onOpenAuth }) {
  // Test configuration state
  const [inTest, setInTest] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Setup options
  const [category, setCategory] = useState("All");
  const [difficulty, setDifficulty] = useState("Intermediate");
  const [numQuestions, setNumQuestions] = useState(10);

  // Active test state
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({}); // questionId -> selectedOption (0-3)
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const [showIncompleteModal, setShowIncompleteModal] = useState(false);
  const [autoFilling, setAutoFilling] = useState(false);
  const [autoFillNotification, setAutoFillNotification] = useState("");

  const timerRef = useRef(null);

  useEffect(() => {
    if (inTest) {
      timerRef.current = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [inTest]);

  async function startTest() {
    if (!user) {
      if (onOpenAuth) {
        onOpenAuth();
      } else {
        alert("Please sign in or select 'Sign In / Demo' at the top right to start the aptitude test.");
      }
      return;
    }

    setLoading(true);
    setTestResult(null);
    setAnswers({});
    setCurrentIndex(0);
    setElapsedSeconds(0);
    setShowIncompleteModal(false);

    try {
      const qList = await api.aptitude.getQuestions({
        category: category === "All" ? "" : category,
        difficulty: difficulty === "All" ? "" : difficulty,
        limit: numQuestions,
      });

      if (!qList || qList.length === 0) {
        alert("No questions found for the selected filter. Try selecting 'All Categories'.");
        setLoading(false);
        return;
      }

      setQuestions(qList);
      setInTest(true);
    } catch (err) {
      alert("Failed to start aptitude test: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSelectOption(qId, optIdx) {
    setAnswers((prev) => ({
      ...prev,
      [qId]: optIdx,
    }));
  }

  function jumpToNextUnanswered() {
    const nextIdx = questions.findIndex((q) => answers[q.id] === undefined);
    if (nextIdx !== -1) {
      setCurrentIndex(nextIdx);
    }
    setShowIncompleteModal(false);
  }

  async function quickFillAllAnswers() {
    if (autoFilling || !questions.length) return;
    setAutoFilling(true);
    try {
      const qIds = questions.map((q) => q.id);
      const res = await api.aptitude.getSolutions(qIds);
      const solutions = res?.solutions || {};

      const newAnswers = { ...answers };
      questions.forEach((q) => {
        if (solutions[q.id] && solutions[q.id].correct_answer !== undefined) {
          newAnswers[q.id] = solutions[q.id].correct_answer;
        } else if (q.correct_answer !== undefined) {
          newAnswers[q.id] = q.correct_answer;
        } else {
          newAnswers[q.id] = 0;
        }
      });
      setAnswers(newAnswers);
      setShowIncompleteModal(false);
      setAutoFillNotification(`⚡ Auto-filled all ${questions.length} questions with 100% verified correct answers!`);
      setTimeout(() => setAutoFillNotification(""), 4500);
    } catch (err) {
      console.error("Auto-fill error:", err);
      const newAnswers = { ...answers };
      questions.forEach((q) => {
        if (q.correct_answer !== undefined) newAnswers[q.id] = q.correct_answer;
      });
      setAnswers(newAnswers);
      setShowIncompleteModal(false);
    } finally {
      setAutoFilling(false);
    }
  }

  async function handleSubmitTest() {
    const answeredCount = Object.keys(answers).length;
    if (answeredCount < questions.length) {
      setShowIncompleteModal(true);
      return;
    }

    if (timerRef.current) clearInterval(timerRef.current);
    setLoading(true);

    const formattedAnswers = questions.map((q) => ({
      question_id: q.id,
      selected_option: answers[q.id] !== undefined ? answers[q.id] : null,
    }));

    try {
      const result = await api.aptitude.submit({
        category,
        difficulty,
        total_questions: questions.length,
        time_taken_seconds: elapsedSeconds,
        answers: formattedAnswers,
      });

      localStorage.setItem("pressure_ai_aptitude_completed", "true");
      setTestResult(result);
      setInTest(false);
    } catch (err) {
      alert("Submission error: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  const formatTime = (secs) => {
    const mins = Math.floor(secs / 60);
    const s = secs % 60;
    return `${mins.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const categoriesList = [
    { id: "All", label: "All Categories (Balanced Test)", desc: "Mix of Quantitative, Logical, Verbal, and Data Interpretation" },
    { id: "Quantitative Aptitude", label: "Quantitative Aptitude", desc: "Percentages, Ratios, Speed & Time, Work, Profit & Loss" },
    { id: "Logical Reasoning", label: "Logical Reasoning", desc: "Number sequences, Syllogisms, Seating patterns, Blood relations" },
    { id: "Verbal Ability", label: "Verbal Ability", desc: "Reading comprehension, Antonyms, Grammar agreement, Vocabulary" },
    { id: "Data Interpretation", label: "Data Interpretation", desc: "Bar graphs, Pie charts, Revenue tables, Growth metrics" },
  ];

  // 1. SETUP VIEW (Before starting test)
  if (!inTest && !testResult) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8 animate-fade-in space-y-8">
        {/* Banner */}
        <div className="glass-panel rounded-3xl p-8 border border-slate-800 relative overflow-hidden">
          <div className="absolute top-0 right-0 -mr-10 -mt-10 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Compass className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Placement Stage 1
              </span>
              <h2 className="text-2xl md:text-3xl font-black text-white">Aptitude Assessment Arena</h2>
            </div>
          </div>
          <p className="text-xs md:text-sm text-slate-300 max-w-2xl leading-relaxed">
            Standardized technical placement assessments begin with strict aptitude benchmarking. Test your quantitative speed, logical deduction, verbal accuracy, and data chart analysis.
          </p>
        </div>

        {/* Configuration Panel */}
        <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6">
          {/* Category Selector */}
          <div>
            <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">
              1. Select Aptitude Category
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {categoriesList.map((cat) => (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => setCategory(cat.id)}
                  className={`p-4 rounded-2xl border text-left transition-all ${
                    category === cat.id
                      ? "bg-blue-500/15 border-blue-500 text-white shadow-lg shadow-blue-500/10"
                      : "bg-slate-950/60 border-slate-800/80 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                  }`}
                >
                  <span className="text-xs font-bold block mb-1">{cat.label}</span>
                  <span className="text-[11px] text-slate-400 leading-snug">{cat.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty & Count */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
            {/* Difficulty */}
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">
                2. Target Difficulty
              </label>
              <div className="grid grid-cols-3 gap-2">
                {["Beginner", "Intermediate", "Advanced"].map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => setDifficulty(d)}
                    className={`py-3 px-2 rounded-xl text-xs font-bold border transition-all text-center ${
                      difficulty === d
                        ? "bg-blue-500 text-white border-blue-400 shadow-md shadow-blue-500/20"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Questions count */}
            <div>
              <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">
                3. Number of Questions
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[10, 20, 30].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setNumQuestions(num)}
                    className={`py-3 px-2 rounded-xl text-xs font-bold border transition-all text-center ${
                      numQuestions === num
                        ? "bg-blue-500 text-white border-blue-400 shadow-md shadow-blue-500/20"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {num} Questions
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Auth warning if not signed in */}
          {!user && (
            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-center justify-between text-xs text-amber-300">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                <span>Sign in or use Candidate Demo to unlock test papers and save your scores.</span>
              </div>
              <button
                type="button"
                onClick={onOpenAuth}
                className="px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl transition text-xs shrink-0"
              >
                Sign In / Demo
              </button>
            </div>
          )}

          {/* Launch Button */}
          <div className="pt-2">
            <button
              onClick={startTest}
              disabled={loading}
              className="w-full py-4 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-500 hover:from-blue-700 hover:to-indigo-700 text-white font-extrabold text-sm rounded-2xl shadow-xl shadow-blue-600/25 flex items-center justify-center gap-2 transition-all hover:scale-[1.01]"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating Test Paper...
                </>
              ) : (
                <>
                  <Compass className="w-4 h-4" />
                  Start Aptitude Test ({numQuestions} Questions)
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // 2. ACTIVE TEST INTERFACE
  if (inTest && questions.length > 0) {
    const currentQ = questions[currentIndex];
    const answeredCount = Object.keys(answers).length;

    return (
      <div className="max-w-4xl mx-auto px-4 py-8 animate-fade-in space-y-6">
        {/* Status Bar */}
        <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-xs">
              #{currentIndex + 1}
            </span>
            <div>
              <span className="text-xs font-bold text-white block">{currentQ.category}</span>
              <span className="text-[10px] text-slate-500">{currentQ.difficulty}</span>
            </div>
          </div>

          {/* Progress */}
          <div className="hidden sm:block flex-1 max-w-xs">
            <div className="flex justify-between text-xs font-medium text-slate-400 mb-1">
              <span>Answered: {answeredCount}/{questions.length}</span>
              <span className="text-blue-400">{Math.round((answeredCount / questions.length) * 100)}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
              <div 
                className="h-full bg-blue-500 rounded-full transition-all"
                style={{ width: `${(answeredCount / questions.length) * 100}%` }}
              />
            </div>
          </div>

        {/* Super Emoji Time Clocker (Short & Attractive Widget) */}
          <div className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-slate-900/95 via-blue-950/50 to-slate-900/95 border border-blue-500/50 shadow-md shadow-blue-500/15 backdrop-blur-md">
            <div className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-500/20 border border-blue-500/30 text-base shadow-[0_0_10px_rgba(59,130,246,0.3)] select-none animate-pulse">
              ⏱️
            </div>
            <span className="timer-digits-blue font-mono text-lg md:text-xl font-black tracking-widest text-white">
              {formatTime(elapsedSeconds)}
            </span>
            <span className="relative flex h-2 w-2 ml-0.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
          </div>
        </div>

        {/* Auto-Fill Confirmation Notification */}
        {autoFillNotification && (
          <div className="p-3.5 bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 rounded-2xl text-xs font-semibold flex items-center gap-2.5 animate-fade-in shadow-lg shadow-emerald-500/10">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{autoFillNotification}</span>
          </div>
        )}

        {/* Question Card */}
        <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Question {currentIndex + 1} of {questions.length}</span>
            <span className="font-mono text-blue-400">{currentQ.category}</span>
          </div>

          <h3 className="text-base md:text-lg font-bold text-white leading-relaxed">
            {currentQ.question}
          </h3>

          {/* 4 Multiple Choice Options */}
          <div className="space-y-3 pt-2">
            {currentQ.options.map((opt, optIdx) => {
              const isSelected = answers[currentQ.id] === optIdx;
              const optionLetters = ["A", "B", "C", "D"];

              return (
                <div
                  key={optIdx}
                  onClick={() => handleSelectOption(currentQ.id, optIdx)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center gap-3.5 ${
                    isSelected
                      ? "bg-blue-500/20 border-blue-500 text-white shadow-md shadow-blue-500/10"
                      : "bg-slate-950/70 border-slate-800/80 text-slate-300 hover:border-slate-700 hover:bg-slate-900"
                  }`}
                >
                  <span className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs flex-shrink-0 ${
                    isSelected
                      ? "bg-blue-500 text-white"
                      : "bg-slate-900 text-slate-400 border border-slate-800"
                  }`}>
                    {optionLetters[optIdx]}
                  </span>
                  <span className="text-xs md:text-sm font-medium leading-snug">
                    {opt}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Navigation Controls */}
          <div className="flex items-center justify-between pt-6 border-t border-slate-800">
            <button
              onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
              disabled={currentIndex === 0}
              className="px-4 py-2.5 rounded-xl border border-slate-800 text-xs font-semibold text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Previous
            </button>

            <div className="flex items-center gap-2">
              {currentIndex < questions.length - 1 ? (
                <button
                  onClick={() => setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                  className="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl border border-slate-700 text-xs font-bold flex items-center gap-1.5 transition-colors"
                >
                  Next <ArrowRight className="w-3.5 h-3.5" />
                </button>
              ) : null}

              <button
                onClick={handleSubmitTest}
                disabled={loading}
                className={`px-6 py-2.5 font-extrabold text-xs rounded-xl shadow-lg flex items-center gap-1.5 transition-all ${
                  answeredCount === questions.length
                    ? "bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 text-white shadow-emerald-500/30 hover:scale-105 ring-2 ring-emerald-400"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700"
                }`}
              >
                {loading ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : answeredCount === questions.length ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                ) : (
                  <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
                )}
                <span>
                  {answeredCount === questions.length
                    ? `Submit All ${questions.length} Questions & Unlock Coding →`
                    : `Submit Test (${answeredCount}/${questions.length} Answered)`}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Question Palette Strip */}
        <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              Question Palette ({answeredCount}/{questions.length} Completed)
            </span>
            <div className="flex items-center gap-2">
              {answeredCount < questions.length && (
                <>
                  <button
                    type="button"
                    onClick={jumpToNextUnanswered}
                    className="text-[11px] font-semibold text-blue-400 hover:text-blue-300 underline"
                  >
                    Jump to Next Unanswered
                  </button>
                  <span className="text-slate-600">•</span>
                </>
              )}
              <button
                type="button"
                onClick={quickFillAllAnswers}
                disabled={autoFilling}
                className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600/30 to-teal-600/30 hover:from-emerald-600/40 hover:to-teal-600/40 text-emerald-300 border border-emerald-500/40 text-[11px] font-bold transition-all flex items-center gap-1.5 shadow-sm disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                {autoFilling ? "Filling 100% Answers..." : "⚡ Auto-Fill 100% Correct Answers"}
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {questions.map((q, idx) => {
              const isAnswered = answers[q.id] !== undefined;
              const isCurrent = idx === currentIndex;
              return (
                <button
                  key={q.id}
                  onClick={() => setCurrentIndex(idx)}
                  className={`w-8 h-8 rounded-lg text-xs font-bold transition-all ${
                    isCurrent
                      ? "ring-2 ring-blue-400 bg-blue-600 text-white"
                    : isAnswered
                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                    : "bg-slate-900 text-amber-400/80 border border-amber-500/20 hover:text-white"
                  }`}
                  title={isAnswered ? "Answered" : "Unanswered - Click to answer"}
                >
                  {idx + 1}
                </button>
              );
            })}
          </div>
        </div>

        {/* Incomplete Questions Modal */}
        {showIncompleteModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
            <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl text-center">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">
                Complete All {questions.length} Questions
              </h3>
              <p className="text-xs text-slate-300 mb-6 leading-relaxed">
                You have answered <strong>{answeredCount}</strong> of <strong>{questions.length}</strong> questions. To maintain valid placement benchmarking and advance to the <strong>Coding Session</strong>, please answer all remaining questions.
              </p>

              <div className="space-y-2">
                <button
                  type="button"
                  onClick={jumpToNextUnanswered}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-lg transition-all"
                >
                  Go to Next Unanswered Question
                </button>
                <button
                  type="button"
                  onClick={quickFillAllAnswers}
                  disabled={autoFilling}
                  className="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-bold text-xs rounded-xl shadow-lg transition-all flex items-center justify-center gap-1.5 disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  {autoFilling ? "Filling 100% Answers..." : "⚡ Auto-Fill 100% Correct Answers"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowIncompleteModal(false)}
                  className="w-full py-2 text-xs text-slate-500 hover:text-slate-300"
                >
                  Back to Test
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // 3. APTITUDE RESULT VIEW
  if (testResult) {
    const isWeakDataInterp = testResult.weak_categories?.includes("Data Interpretation");

    return (
      <div className="max-w-4xl mx-auto px-4 py-8 animate-fade-in space-y-6">
        {/* Stage 1 Completion Banner */}
        <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 text-center sm:text-left">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold flex-shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">🎉 Stage 1: Aptitude Test Completed!</h4>
              <p className="text-xs text-emerald-300">
                All {questions.length} questions completed. You are now unlocked to proceed to Stage 2: Coding Session.
              </p>
            </div>
          </div>
          <button
            onClick={onGoToCoding}
            className="w-full sm:w-auto px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-emerald-500/25 flex items-center justify-center gap-1.5 transition-all flex-shrink-0 hover:scale-105"
          >
            Proceed to Coding Session <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Header Result Card */}
        <div className="glass-panel rounded-3xl p-8 border border-slate-800 relative overflow-hidden">
          <div className="absolute top-0 right-0 -mr-10 -mt-10 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pb-6 border-b border-slate-800">
            <div>
              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Official Result
              </span>
              <h2 className="text-3xl font-black text-white mt-1">Aptitude Assessment Report</h2>
              <p className="text-xs text-slate-400 mt-0.5">Attempt #{testResult.attempt_id} • Time taken: {formatTime(testResult.time_taken_seconds)}</p>
            </div>

            {/* Overall Score Dial */}
            <div className="w-24 h-24 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 border border-blue-400/40 flex flex-col items-center justify-center shadow-xl shadow-blue-600/30">
              <span className="text-2xl font-black text-white">{testResult.overall_score}%</span>
              <span className="text-[10px] text-blue-200 uppercase font-bold">Overall Score</span>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-6">
            <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
              <span className="text-[10px] text-slate-400 uppercase font-semibold block">Total Questions</span>
              <span className="text-base font-bold text-white">{testResult.total_questions}</span>
            </div>
            <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
              <span className="text-[10px] text-emerald-400 uppercase font-semibold block">Correct Answers</span>
              <span className="text-base font-bold text-emerald-400">{testResult.correct_count}</span>
            </div>
            <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
              <span className="text-[10px] text-red-400 uppercase font-semibold block">Incorrect Answers</span>
              <span className="text-base font-bold text-red-400">{testResult.incorrect_count}</span>
            </div>
            <div className="p-3 bg-slate-950/70 rounded-xl border border-slate-800 text-center">
              <span className="text-[10px] text-blue-400 uppercase font-semibold block">Accuracy</span>
              <span className="text-base font-bold text-white">{testResult.accuracy}%</span>
            </div>
          </div>
        </div>

        {/* Category Performance Breakdown */}
        <div className="glass-panel rounded-3xl p-6 md:p-8 border border-slate-800 space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-blue-400" />
            Category-Wise Performance
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {Object.entries(testResult.category_performance || {}).map(([cat, score]) => {
              const isWeak = score < 60;
              return (
                <div key={cat} className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-white">{cat}</span>
                    <span className={`text-xs font-mono font-bold ${isWeak ? "text-red-400" : "text-emerald-400"}`}>
                      {score}% {isWeak ? "🔴 Weak" : "🟢 Solid"}
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                    <div 
                      className={`h-full rounded-full ${isWeak ? "bg-red-500" : "bg-emerald-500"}`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Identified Weak Categories Callout */}
          {testResult.weak_categories && testResult.weak_categories.length > 0 && (
            <div className="p-4 bg-red-950/30 border border-red-500/30 rounded-2xl space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-red-400 uppercase tracking-wide">
                <AlertTriangle className="w-4 h-4" />
                Identified Weak Aptitude Areas: {testResult.weak_categories.join(", ")}
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {testResult.recommendation}
              </p>
            </div>
          )}

          {/* AI Comprehensive Evaluation (Gemini) */}
          {testResult.ai_evaluation && (
            <div className="glass-panel rounded-3xl p-6 md:p-8 border border-indigo-500/30 space-y-5 bg-gradient-to-b from-indigo-950/20 via-slate-900/60 to-slate-950/80 relative overflow-hidden">
              <div className="flex items-center justify-between gap-4 pb-4 border-b border-indigo-500/20">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        AI Evaluation Layer
                      </span>
                      {testResult.ai_evaluation.source === "gemini" && (
                        <span className="text-[10px] uppercase font-bold text-indigo-400">
                          Powered by Gemini
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-black text-white mt-0.5">Psychometric & Diagnostic Analysis</h3>
                  </div>
                </div>
                <div className="text-right hidden sm:block">
                  <span className="text-[10px] text-slate-400 font-medium">Objective Score: <strong className="text-white">{testResult.overall_score}%</strong> (Authoritative)</span>
                </div>
              </div>

              {/* Safe Fallback Notice if Gemini was temporarily rate-limited / unavailable */}
              {testResult.ai_evaluation.fallback_notice && (
                <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-300 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                  <span>{testResult.ai_evaluation.fallback_notice}</span>
                </div>
              )}

              {/* Overall AI Summary */}
              {testResult.ai_evaluation.summary && (
                <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 text-xs md:text-sm text-slate-200 leading-relaxed">
                  <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider block mb-1">
                    Performance Summary
                  </span>
                  {testResult.ai_evaluation.summary}
                </div>
              )}

              {/* Strengths & Weaknesses 2-Column */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Strong Categories */}
                <div className="p-4 bg-emerald-950/20 border border-emerald-500/20 rounded-2xl space-y-2">
                  <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 uppercase tracking-wide">
                    <CheckCircle2 className="w-4 h-4" /> Strong Categories
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {(testResult.ai_evaluation.strengths || []).map((s, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-emerald-400 font-bold">•</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Weak Categories */}
                <div className="p-4 bg-rose-950/20 border border-rose-500/20 rounded-2xl space-y-2">
                  <span className="text-xs font-bold text-rose-400 flex items-center gap-1.5 uppercase tracking-wide">
                    <AlertTriangle className="w-4 h-4" /> Priority Areas for Growth
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {(testResult.ai_evaluation.weaknesses || []).map((w, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-rose-400 font-bold">•</span>
                        <span>{w}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Conceptual Mistakes Analysis */}
              {testResult.ai_evaluation.mistakes_analysis && testResult.ai_evaluation.mistakes_analysis.length > 0 && (
                <div className="p-4 bg-slate-950/70 rounded-2xl border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-amber-400 uppercase tracking-wide block">
                    Conceptual Errors & Reasoning Patterns Identified
                  </span>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {testResult.ai_evaluation.mistakes_analysis.map((m, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-amber-400 font-bold">↳</span>
                        <span>{m}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Difficulty Observations */}
              {testResult.ai_evaluation.difficulty_observations && (
                <div className="p-3.5 bg-slate-950/50 rounded-xl border border-slate-800/80 text-xs text-slate-400">
                  <strong className="text-slate-300">Difficulty Observations: </strong>
                  {testResult.ai_evaluation.difficulty_observations}
                </div>
              )}

              {/* Actionable Improvement Suggestions */}
              {testResult.ai_evaluation.improvement_suggestions && testResult.ai_evaluation.improvement_suggestions.length > 0 && (
                <div className="p-4 bg-indigo-950/25 border border-indigo-500/20 rounded-2xl space-y-2">
                  <span className="text-xs font-bold text-indigo-300 uppercase tracking-wide block">
                    Personalized Improvement Strategy
                  </span>
                  <div className="grid grid-cols-1 gap-2">
                    {testResult.ai_evaluation.improvement_suggestions.map((sugg, idx) => (
                      <div key={idx} className="p-2.5 bg-slate-950/60 rounded-xl border border-indigo-500/10 text-xs text-slate-300 flex items-start gap-2">
                        <span className="w-5 h-5 rounded-md bg-indigo-500/20 text-indigo-300 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span className="leading-relaxed">{sugg}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Next Steps CTA */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
            <button
              onClick={() => {
                setTestResult(null);
                setInTest(false);
              }}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl border border-slate-800 text-xs font-semibold text-slate-400 hover:text-white flex items-center justify-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Retake Aptitude Test
            </button>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <button
                onClick={() => onGoToPractice(testResult.weak_categories?.[0] || "Data Interpretation")}
                className="w-full sm:w-auto px-4 py-2.5 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5" /> Practice Weak Category
              </button>

              <button
                onClick={onGoToCoding}
                className="w-full sm:w-auto px-6 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-1.5 transition-all"
              >
                Proceed to Stage 2: Coding Session <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
