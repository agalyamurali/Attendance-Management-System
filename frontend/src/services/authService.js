import axiosClient from "../api/axiosClient";

/**
 * Auth service — wraps every call to /api/auth/*.
 * Components call these functions; they never call axios directly.
 */

export async function login(username, password) {
  const response = await axiosClient.post("/api/auth/login", { username, password });
  return response.data; // { access_token, token_type, expires_in_minutes, username, role }
}

export async function getCurrentUser() {
  const response = await axiosClient.get("/api/auth/me");
  return response.data;
}
