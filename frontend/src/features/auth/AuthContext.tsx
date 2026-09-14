import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { clearStoredToken, getStoredToken, setStoredToken } from "./tokenStorage";

export interface User {
  id: string;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const reqSeq = useRef(0);

  const refreshUser = async () => {
    const seq = ++reqSeq.current;
    try {
      const token = getStoredToken();
      const headers: Record<string, string> = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_BASE}/auth/me`, {
        method: "GET",
        credentials: "include", // send and receive HttpOnly cookies
        headers,
        cache: "no-store", // Prevents WebKit/Safari from serving cached 401
      });

      if (seq !== reqSeq.current) {
        // Discard stale response if another auth event started
        return;
      }

      if (res.ok) {
        const data = await res.json();
        setUser(data);
      } else {
        clearStoredToken();
        setUser(null);
      }
    } catch {
      if (seq === reqSeq.current) {
        setUser(null);
      }
    } finally {
      if (seq === reqSeq.current) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (email: string, password: string) => {
    reqSeq.current++; // Invalidate any pending initial refreshUser
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      cache: "no-store",
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Authentication failed" }));
      throw new Error(err.detail || "Authentication failed");
    }

    const userData = await res.json();
    if (userData.session_token) {
      setStoredToken(userData.session_token);
    }
    setUser(userData);
  };

  const register = async (email: string, password: string) => {
    reqSeq.current++;
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      cache: "no-store",
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(err.detail || "Registration failed");
    }

    // Automatically establish session via login
    await login(email, password);
  };

  const logout = async () => {
    reqSeq.current++;
    const token = getStoredToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        credentials: "include",
        headers,
        cache: "no-store",
      });
    } finally {
      clearStoredToken();
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
