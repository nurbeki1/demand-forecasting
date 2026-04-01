/**
 * AuthModal - Premium Authentication Modal
 * Login/Register with smooth animations
 */

import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import "./AuthModal.css";

// ============================================
// LOGIN FORM
// ============================================
function LoginForm({ onSwitch, onSuccess, setLoading, loading }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const userData = await login(email, password);
      onSuccess();
      // Navigate based on role
      if (userData?.is_admin) {
        navigate("/admin");
      } else {
        navigate("/user");
      }
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      {error && <div className="auth-error">{error}</div>}

      <div className="auth-field">
        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Введите email"
          required
          disabled={loading}
          autoComplete="email"
        />
      </div>

      <div className="auth-field">
        <label htmlFor="login-password">Пароль</label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Введите пароль"
          required
          disabled={loading}
          minLength={4}
          autoComplete="current-password"
        />
      </div>

      <button type="submit" className="auth-submit" disabled={loading}>
        {loading ? (
          <span className="auth-spinner" />
        ) : (
          <>
            <span>Войти</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </>
        )}
      </button>

      <div className="auth-switch">
        <span>Нет аккаунта?</span>
        <button type="button" onClick={onSwitch}>Регистрация</button>
      </div>
    </form>
  );
}

// ============================================
// REGISTER FORM
// ============================================
function RegisterForm({ onSwitch, onSuccess, setLoading, loading }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Пароли не совпадают");
      return;
    }

    if (password.length < 4) {
      setError("Пароль должен быть минимум 4 символа");
      return;
    }

    setLoading(true);

    try {
      await register(email, password);
      onSuccess();
      navigate("/user");
    } catch (err) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      {error && <div className="auth-error">{error}</div>}

      <div className="auth-field">
        <label htmlFor="register-email">Email</label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Введите email"
          required
          disabled={loading}
          autoComplete="email"
        />
      </div>

      <div className="auth-field">
        <label htmlFor="register-password">Пароль</label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Придумайте пароль"
          required
          disabled={loading}
          minLength={4}
          autoComplete="new-password"
        />
      </div>

      <div className="auth-field">
        <label htmlFor="register-confirm">Подтвердите пароль</label>
        <input
          id="register-confirm"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Повторите пароль"
          required
          disabled={loading}
          minLength={4}
          autoComplete="new-password"
        />
      </div>

      <button type="submit" className="auth-submit" disabled={loading}>
        {loading ? (
          <span className="auth-spinner" />
        ) : (
          <>
            <span>Создать аккаунт</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </>
        )}
      </button>

      <div className="auth-switch">
        <span>Уже есть аккаунт?</span>
        <button type="button" onClick={onSwitch}>Войти</button>
      </div>
    </form>
  );
}

// ============================================
// AUTH MODAL
// ============================================
export default function AuthModal({ isOpen, onClose, onSuccess }) {
  const [activeTab, setActiveTab] = useState("login");
  const [loading, setLoading] = useState(false);
  const modalRef = useRef(null);

  // Close on escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape" && !loading) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
    };
  }, [isOpen, loading, onClose]);

  // Close on backdrop click
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && !loading) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={handleBackdropClick}>
      <div className="auth-modal" ref={modalRef}>
        {/* Close button */}
        <button
          className="auth-modal-close"
          onClick={onClose}
          disabled={loading}
          aria-label="Close"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>

        {/* Header */}
        <div className="auth-modal-header">
          <div className="auth-modal-logo">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <h2 className="auth-modal-title">Добро пожаловать</h2>
          <p className="auth-modal-subtitle">
            {activeTab === "login"
              ? "Войдите для доступа к панели управления"
              : "Создайте аккаунт чтобы начать"}
          </p>
        </div>

        {/* Tabs */}
        <div className="auth-tabs">
          <button
            className={`auth-tab ${activeTab === "login" ? "active" : ""}`}
            onClick={() => setActiveTab("login")}
            disabled={loading}
          >
            Вход
          </button>
          <button
            className={`auth-tab ${activeTab === "register" ? "active" : ""}`}
            onClick={() => setActiveTab("register")}
            disabled={loading}
          >
            Регистрация
          </button>
          <div
            className="auth-tab-indicator"
            style={{ transform: `translateX(${activeTab === "register" ? "100%" : "0"})` }}
          />
        </div>

        {/* Forms */}
        <div className="auth-forms">
          <div
            className="auth-forms-slider"
            style={{ transform: `translateX(${activeTab === "register" ? "-50%" : "0"})` }}
          >
            <div className="auth-form-wrapper">
              <LoginForm
                onSwitch={() => setActiveTab("register")}
                onSuccess={onSuccess}
                setLoading={setLoading}
                loading={loading}
              />
            </div>
            <div className="auth-form-wrapper">
              <RegisterForm
                onSwitch={() => setActiveTab("login")}
                onSuccess={onSuccess}
                setLoading={setLoading}
                loading={loading}
              />
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="auth-divider">
          <span>или продолжить с</span>
        </div>

        {/* Social buttons */}
        <div className="auth-social">
          <button className="auth-social-btn" disabled={loading}>
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Google
          </button>
          <button className="auth-social-btn" disabled={loading}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            GitHub
          </button>
        </div>
      </div>
    </div>
  );
}
