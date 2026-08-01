import React, { createContext, useState, useEffect } from "react";
import api from "../api/axios";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // Keep token only in memory so a page refresh forces re-login
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Set token in axios headers when token changes
  useEffect(() => {
    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
      delete api.defaults.headers.common["Authorization"];
    }
  }, [token]);

  // Do not persist token across reloads. Verify token whenever it changes.
  useEffect(() => {
    const verifyToken = async () => {
      if (token) {
        try {
          const response = await api.get("/auth/me");
          setUser(response.data);
        } catch (error) {
          // Token invalid, clear it
          setToken(null);
          setUser(null);
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    };
    verifyToken();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await api.post("/auth/login", { email, password });
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      };
    }
  };

  const register = async (email, password, username = null) => {
    try {
      const response = await api.post("/auth/register", {
        email,
        password,
        username,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Registration failed",
      };
    }
  };

  const verifyOtp = async (email, otp) => {
    try {
      const response = await api.post("/auth/verify-otp", { email, otp });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Verification failed",
      };
    }
  };

  const requestPasswordReset = async (email) => {
    try {
      const response = await api.post("/auth/forgot-password", { email });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Password reset request failed",
      };
    }
  };

  const resetPassword = async (email, otp, newPassword) => {
    try {
      const response = await api.post("/auth/reset-password", {
        email,
        otp,
        new_password: newPassword,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Password reset failed",
      };
    }
  };

  const logout = () => {
    // notify backend to blacklist token if present
    if (token) {
      try {
        api.post("/auth/logout");
      } catch (e) {
        // ignore
      }
    }
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = () => {
    return !!token && !!user;
  };

  const isAdmin = () => {
    return user?.role === "admin" || user?.role === "super_admin";
  };

  const value = {
    user,
    token,
    login,
    register,
    verifyOtp,
    requestPasswordReset,
    resetPassword,
    logout,
    isAuthenticated,
    isAdmin,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

