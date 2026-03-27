import { createContext, useContext, useState, useEffect } from "react";
import {
  login as apiLogin,
  getMe,
  getToken,
  setToken,
  removeToken,
} from "../api/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await getMe(token);

      // Only allow admins
      if (!userData.is_admin) {
        removeToken();
        setLoading(false);
        return;
      }

      setUser(userData);
    } catch (err) {
      console.error("Auth check failed:", err);
      removeToken();
    } finally {
      setLoading(false);
    }
  }

  async function login(email, password) {
    const { token } = await apiLogin(email, password);
    setToken(token);

    const userData = await getMe(token);
    setUser(userData);

    return token;
  }

  function logout() {
    removeToken();
    setUser(null);
  }

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || false,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}