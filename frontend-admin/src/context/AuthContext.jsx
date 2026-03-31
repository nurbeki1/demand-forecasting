/**
 * AuthContext - Centralized Authentication State Management
 *
 * Features:
 * - Proper loading state to prevent race conditions
 * - Cached user data for instant role detection on refresh
 * - Clean logout that removes all auth data
 * - Role-based helpers (isAdmin, isUser)
 */

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  getToken,
  setToken,
  getCachedUser,
  setCachedUser,
  clearAllAuthData,
  initializeAuth,
} from "../utils/authStorage";
import { API_URL } from "../config";

const AuthContext = createContext(null);

// Auth states for clear state machine
const AuthStatus = {
  LOADING: 'loading',
  AUTHENTICATED: 'authenticated',
  UNAUTHENTICATED: 'unauthenticated',
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [authStatus, setAuthStatus] = useState(AuthStatus.LOADING);
  const [error, setError] = useState(null);

  // Initialize auth on mount
  useEffect(() => {
    initializeAuth();
    checkAuth();
  }, []);

  /**
   * Check authentication status
   * Uses cached user for instant role detection, then validates with server
   */
  const checkAuth = useCallback(async () => {
    const token = getToken();

    if (!token) {
      setAuthStatus(AuthStatus.UNAUTHENTICATED);
      setUser(null);
      return;
    }

    // Use cached user data for instant role detection (prevents flash)
    const cachedUser = getCachedUser();
    if (cachedUser) {
      setUser(cachedUser);
      setAuthStatus(AuthStatus.AUTHENTICATED);
    }

    // Validate token with server
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        throw new Error('Token invalid');
      }

      const userData = await response.json();
      setUser(userData);
      setCachedUser(userData);
      setAuthStatus(AuthStatus.AUTHENTICATED);
    } catch (err) {
      console.error("Auth validation failed:", err);
      // Token is invalid - clear everything
      clearAllAuthData();
      setUser(null);
      setAuthStatus(AuthStatus.UNAUTHENTICATED);
    }
  }, []);

  /**
   * Login user
   */
  const login = useCallback(async (email, password) => {
    setError(null);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Login failed");
      }

      const data = await response.json();
      const token = data.access_token;

      // Clear any existing auth data before setting new
      clearAllAuthData();

      // Set new token
      setToken(token);

      // Fetch user data
      const meResponse = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!meResponse.ok) {
        throw new Error("Failed to get user info");
      }

      const userData = await meResponse.json();

      // Update state and cache
      setUser(userData);
      setCachedUser(userData);
      setAuthStatus(AuthStatus.AUTHENTICATED);

      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  /**
   * Register new user
   */
  const register = useCallback(async (email, password) => {
    setError(null);

    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "Registration failed");
      }

      // Auto-login after registration
      return await login(email, password);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [login]);

  /**
   * Logout user - completely clears all auth state
   */
  const logout = useCallback(() => {
    clearAllAuthData();
    setUser(null);
    setAuthStatus(AuthStatus.UNAUTHENTICATED);
    setError(null);
  }, []);

  // Computed values
  const isLoading = authStatus === AuthStatus.LOADING;
  const isAuthenticated = authStatus === AuthStatus.AUTHENTICATED && !!user;
  const isAdmin = isAuthenticated && user?.is_admin === true;
  const isUser = isAuthenticated && user?.is_admin === false;

  const value = {
    // State
    user,
    error,

    // Status flags
    isLoading,
    isAuthenticated,
    isAdmin,
    isUser,
    authStatus,

    // Deprecated - for backwards compatibility
    loading: isLoading,

    // Actions
    login,
    register,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

// Export auth status for external use
export { AuthStatus };