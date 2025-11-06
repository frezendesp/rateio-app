import axios from "axios";

const api = axios.create({
  baseURL: "/api"
});

export async function fetchDashboardSummary() {
  const response = await api.get("/dashboard/summary");
  return response.data;
}

export async function fetchExpenses() {
  const response = await api.get("/expenses");
  return response.data;
}

export async function fetchRecurrences() {
  const response = await api.get("/recurrences");
  return response.data;
}

export async function fetchPeople() {
  const response = await api.get("/people");
  return response.data;
}

export async function fetchAccounts() {
  const response = await api.get("/accounts");
  return response.data;
}

export default api;
