const API_BASE = "http://localhost:8000";

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("pressure_ai_token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch (e) {
      errorDetail = response.statusText || errorDetail;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  auth: {
    login: (email, password) =>
      request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    register: (name, email, password, role = "candidate") =>
      request("/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password, role }),
      }),
    getMe: () => request("/auth/me"),
  },
  domains: {
    getAll: () => request("/domains"),
    getTopics: (domainId) => request(`/domains/${domainId}/topics`),
  },
  interviews: {
    create: (data) =>
      request("/interviews", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    list: () => request("/interviews"),
    get: (id) => request(`/interviews/${id}`),
    getNextQuestion: (id) => request(`/interviews/${id}/questions/next`),
    submitAnswer: (questionId, payload) => {
      const body = typeof payload === "string" ? { answer_text: payload } : payload;
      return request(`/questions/${questionId}/answer`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    },
    getHint: (questionId) =>
      request(`/questions/${questionId}/hint`, {
        method: "POST",
      }),
    getModelAnswer: (questionId) => request(`/questions/${questionId}/model-answer`),
    getReport: (id) => request(`/interviews/${id}/report`),
    getRecommendations: (id) => request(`/interviews/${id}/recommendations`),
  },
  aptitude: {
    getQuestions: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return request(`/aptitude/questions?${query}`);
    },
    getSolutions: (questionIds) =>
      request("/aptitude/solutions", {
        method: "POST",
        body: JSON.stringify({ question_ids: questionIds }),
      }),
    submit: (data) =>
      request("/aptitude/submit", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    getLatest: () => request("/aptitude/latest"),
  },
  coding: {
    getProblems: (params = {}) => {
      const query = new URLSearchParams(params).toString();
      return request(`/coding/problems?${query}`);
    },
    getProblem: (id) => request(`/coding/problems/${id}`),
    getSolution: (id) => request(`/coding/problems/${id}/solution`),
    run: (data) =>
      request("/coding/run", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    submit: (data) =>
      request("/coding/submit", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    getLatest: () => request("/coding/latest"),
    getStatus: () => request("/coding/status"),
    generateProblem: (params = {}) =>
      request("/coding/generate", {
        method: "POST",
        body: JSON.stringify(params),
      }),
  },
  assessment: {
    getCombined: () => request("/assessments/combined"),
    getRoadmap: (topic) => request(`/roadmap/tasks${topic ? `?topic=${encodeURIComponent(topic)}` : ""}`),
    updateRoadmap: (data) =>
      request("/roadmap/tasks/update", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    getPractice: (topic = "Recursion", difficulty) => {
      const p = new URLSearchParams();
      if (topic) p.append("topic", topic);
      if (difficulty) p.append("difficulty", difficulty);
      return request(`/practice/questions?${p.toString()}`);
    },
    submitPractice: (data) =>
      request("/practice/submit", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },
  progress: {
    get: () => request("/progress"),
  },
  admin: {
    getDashboard: () => request("/admin/dashboard"),
    getCandidates: () => request("/admin/candidates"),
    getReport: (id) => request(`/admin/interviews/${id}/report`),
  },
};
