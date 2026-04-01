/**
 * AuthModal - Premium Authentication Modal
 * Features:
 * - Email verification flow (send code → verify → set password)
 * - Google OAuth
 * - Login
 */

import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { API_URL } from "../../config";
import "./AuthModal.css";

// ============================================
// REGISTRATION STEPS
// ============================================
const REGISTER_STEPS = {
  EMAIL: "email",
  CODE: "code",
  PASSWORD: "password",
};

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
      if (userData?.is_admin) {
        navigate("/admin");
      } else {
        navigate("/user");
      }
    } catch (err) {
      setError(err.message || "Ошибка входа");
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
// REGISTER FORM - Multi-step
// ============================================
function RegisterForm({ onSwitch, onSuccess, setLoading, loading, onGoogleClick }) {
  const [step, setStep] = useState(REGISTER_STEPS.EMAIL);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [countdown, setCountdown] = useState(0);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Countdown timer for resend
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  // Step 1: Send verification code
  const handleSendCode = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/send-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Не удалось отправить код");
      }

      setStep(REGISTER_STEPS.CODE);
      setCountdown(60); // 60 seconds before can resend
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify code
  const handleVerifyCode = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/verify-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Неверный код");
      }

      setStep(REGISTER_STEPS.PASSWORD);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Complete registration
  const handleCompleteRegistration = async (e) => {
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
      const response = await fetch(`${API_URL}/auth/complete-registration`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, code, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Ошибка регистрации");
      }

      // Auto-login after registration
      await login(email, password);
      onSuccess();
      navigate("/user");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Resend code
  const handleResendCode = () => {
    if (countdown === 0) {
      setStep(REGISTER_STEPS.EMAIL);
      setCode("");
    }
  };

  // Render based on step
  if (step === REGISTER_STEPS.EMAIL) {
    return (
      <form className="auth-form" onSubmit={handleSendCode}>
        {error && <div className="auth-error">{error}</div>}

        <div className="auth-step-indicator">
          <div className="auth-step active">1</div>
          <div className="auth-step-line" />
          <div className="auth-step">2</div>
          <div className="auth-step-line" />
          <div className="auth-step">3</div>
        </div>

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

        <button type="submit" className="auth-submit" disabled={loading}>
          {loading ? (
            <span className="auth-spinner" />
          ) : (
            <>
              <span>Отправить код</span>
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

  if (step === REGISTER_STEPS.CODE) {
    return (
      <form className="auth-form" onSubmit={handleVerifyCode}>
        {error && <div className="auth-error">{error}</div>}

        <div className="auth-step-indicator">
          <div className="auth-step completed">✓</div>
          <div className="auth-step-line active" />
          <div className="auth-step active">2</div>
          <div className="auth-step-line" />
          <div className="auth-step">3</div>
        </div>

        <div className="auth-code-sent">
          <p>Код отправлен на</p>
          <strong>{email}</strong>
        </div>

        <div className="auth-field">
          <label htmlFor="register-code">Код подтверждения</label>
          <input
            id="register-code"
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            placeholder="000000"
            required
            disabled={loading}
            maxLength={6}
            className="auth-code-input"
            autoComplete="one-time-code"
          />
        </div>

        <button type="submit" className="auth-submit" disabled={loading || code.length !== 6}>
          {loading ? (
            <span className="auth-spinner" />
          ) : (
            <>
              <span>Подтвердить</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </>
          )}
        </button>

        <div className="auth-resend">
          {countdown > 0 ? (
            <span>Отправить повторно через {countdown}с</span>
          ) : (
            <button type="button" onClick={handleResendCode}>
              Отправить код повторно
            </button>
          )}
        </div>
      </form>
    );
  }

  // Step 3: Password
  return (
    <form className="auth-form" onSubmit={handleCompleteRegistration}>
      {error && <div className="auth-error">{error}</div>}

      <div className="auth-step-indicator">
        <div className="auth-step completed">✓</div>
        <div className="auth-step-line active" />
        <div className="auth-step completed">✓</div>
        <div className="auth-step-line active" />
        <div className="auth-step active">3</div>
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
  const { login } = useAuth();
  const navigate = useNavigate();

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

  // Google OAuth handler
  const handleGoogleLogin = async (response) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/auth/google`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ credential: response.credential }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Ошибка Google авторизации");
      }

      // Store token and redirect
      localStorage.setItem("token", data.access_token);
      onSuccess();
      navigate(data.is_admin ? "/admin" : "/user");
      window.location.reload(); // Refresh to update auth state
    } catch (err) {
      console.error("Google auth error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Initialize Google OAuth
  useEffect(() => {
    if (isOpen && window.google) {
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        callback: handleGoogleLogin,
      });

      window.google.accounts.id.renderButton(
        document.getElementById("google-signin-button"),
        {
          theme: "filled_black",
          size: "large",
          width: "100%",
          text: "continue_with",
          locale: "ru",
        }
      );
    }
  }, [isOpen, activeTab]);

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
          <span>или</span>
        </div>

        {/* Google Sign-In Button */}
        <div className="auth-google-container">
          <div id="google-signin-button"></div>
        </div>
      </div>
    </div>
  );
}
