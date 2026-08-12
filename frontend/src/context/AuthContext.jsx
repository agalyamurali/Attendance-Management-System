import { createContext, useContext, useState } from "react";
import * as authService from "../services/authService";

/**
 * AuthContext — the single source of truth for "who is logged in."
 *
 * Why Context instead of Redux: the only global state this app needs
 * is "current user + token." Context/useState is enough; a state
 * library would be unjustified overhead for one piece of shared state
 * (per the Phase 1 decision to avoid unnecessary dependencies).
 */

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const username = localStorage.getItem("username");
    const role = localStorage.getItem("role");
    return username ? { username, role } : null;
  });

  async function login(username, password) {
    const data = await authService.login(username, password);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("username", data.username);
    localStorage.setItem("role", data.role);
    setUser({ username: data.username, role: data.role });
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    setUser(null);
  }

  const isAuthenticated = Boolean(user && localStorage.getItem("access_token"));

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
