import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

// ----- Scenarios -----
export function fetchScenarios() {
  return api.get("/scenarios").then((res) => res.data.scenarios);
}

export function fetchScenario(id) {
  return api.get(`/scenarios/${id}`).then((res) => res.data);
}

export function createScenario(data) {
  return api.post("/scenarios", data).then((res) => res.data);
}

export function deleteScenario(id) {
  return api.delete(`/scenarios/${id}`).then((res) => res.data);
}

// ----- Sessions -----
export function createSession(scenarioId) {
  return api.post("/sessions", { scenario_id: scenarioId }).then((res) => res.data);
}

export function fetchSessions(skip = 0, limit = 20) {
  return api.get("/sessions", { params: { skip, limit } }).then((res) => res.data);
}

export function fetchSession(id) {
  return api.get(`/sessions/${id}`).then((res) => res.data);
}

export function endSession(id) {
  return api.post(`/sessions/${id}/end`).then((res) => res.data);
}

export function fetchSummary(id) {
  return api.get(`/sessions/${id}/summary`).then((res) => res.data);
}

export function deleteSession(id) {
  return api.delete(`/sessions/${id}`).then((res) => res.data);
}

export default api;
