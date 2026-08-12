/**
 * Shared Axios instance — the ONLY place that knows about the JWT and
 * the base API URL. Every service file (authService, employeeService,
 * etc.) imports this instead of importing axios directly.
 *
 * Two interceptors do the actual work:
 *   - request interceptor: attaches "Authorization: Bearer <token>"
 *     to every outgoing request, reading the token from localStorage.
 *   - response interceptor: if any request comes back 401 (token
 *     missing/invalid/expired), clear the stored token and redirect
 *     to /login. Components never handle this themselves.
 */

import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("username");
      localStorage.removeItem("role");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default axiosClient;
