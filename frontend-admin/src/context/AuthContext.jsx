import { createContext, useContext, useState, useEffect } from "react";
import {
  login as apiLogin,
  register as apiRegister,
  getToken,
  setToken,
  removeToken,
} from "../api/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Проверяем токен при загрузке
    const token = getToken();
    if (token) {
      // Декодируем JWT для получения email (простой вариант)
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setUser({ email: payload.sub });
      } catch {
        removeToken();
      }
    }
    setLoading(false);
  }, []);

  async function login(email, password) {
    const token = await apiLogin(email, password);
    setToken(token);
    setUser({ email });
    return token;
  }

  async function register(email, password) {
    await apiRegister(email, password);
    // После регистрации автоматически логинимся
    return login(email, password);
  }

  function logout() {
    removeToken();
    setUser(null);
  }

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
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
