/**
 * /login — AuthModal flows (login + email-code register), dedicated page layout.
 */

import { useState, useEffect, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { LoginForm, RegisterForm } from "../components/landing/AuthModal";
import { setToken, setCachedUser } from "../utils/authStorage";
import { postAuthPath } from "../utils/postAuthRedirect";
import { API_URL } from "../config";
import "../components/landing/AuthModal.css";

export default function LoginPage() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState("login");
  const [loading, setLoading] = useState(false);
  const [googleError, setGoogleError] = useState("");

  useEffect(() => {
    if (location.state?.preferRegister) {
      setActiveTab("register");
    }
  }, [location.state]);

  const getGoogleLocale = () => {
    const locales = { kk: "kk", ru: "ru", en: "en" };
    return locales[i18n.language] || "en";
  };

  const handleGoogleLogin = useCallback(
    async (response) => {
      setLoading(true);
      setGoogleError("");
      try {
        const res = await fetch(`${API_URL}/auth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ credential: response.credential }),
        });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || t("auth.googleError"));
        }
        setToken(data.access_token);
        setCachedUser({
          is_admin: data.is_admin,
          email: data.email || "",
        });
        const targetPath = postAuthPath(data.is_admin, location.state?.from);
        window.location.href = targetPath;
      } catch (err) {
        setGoogleError(err.message || t("auth.serverError"));
      } finally {
        setLoading(false);
      }
    },
    [t, location.state]
  );

  useEffect(() => {
    if (typeof window === "undefined" || !window.google?.accounts?.id) return;
    if (!import.meta.env.VITE_GOOGLE_CLIENT_ID) return;

    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleGoogleLogin,
    });

    const el = document.getElementById("google-signin-login-page");
    if (!el) return;
    el.innerHTML = "";
    window.google.accounts.id.renderButton(el, {
      theme: "filled_black",
      size: "large",
      width: "100%",
      text: "continue_with",
      locale: getGoogleLocale(),
    });
  }, [activeTab, handleGoogleLogin, i18n.language]);

  return (
    <div className="auth-login-page-root">
      <div className="auth-login-page-backdrop" aria-hidden />
      <header className="auth-login-page-header">
        <Link to="/" className="auth-login-page-back-link">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          {t("nav.home")}
        </Link>
      </header>
      <main className="auth-login-page-shell">
        <div className="auth-modal auth-login-page-panel">
          <div className="auth-modal-header">
            <div className="auth-modal-logo">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <h2 className="auth-modal-title">{t("auth.welcome")}</h2>
            <p className="auth-modal-subtitle">
              {activeTab === "login" ? t("auth.loginSubtitle") : t("auth.registerSubtitle")}
            </p>
          </div>

          <div className="auth-tabs">
            <button
              type="button"
              className={`auth-tab ${activeTab === "login" ? "active" : ""}`}
              onClick={() => setActiveTab("login")}
              disabled={loading}
            >
              {t("auth.loginTab")}
            </button>
            <button
              type="button"
              className={`auth-tab ${activeTab === "register" ? "active" : ""}`}
              onClick={() => setActiveTab("register")}
              disabled={loading}
            >
              {t("auth.registerTab")}
            </button>
            <div
              className="auth-tab-indicator"
              style={{ transform: `translateX(${activeTab === "register" ? "100%" : "0"})` }}
            />
          </div>

          <div className="auth-forms">
            <div
              className="auth-forms-slider"
              style={{ transform: `translateX(${activeTab === "register" ? "-50%" : "0"})` }}
            >
              <div className="auth-form-wrapper">
                <LoginForm
                  onSwitch={() => setActiveTab("register")}
                  onSuccess={() => {}}
                  setLoading={setLoading}
                  loading={loading}
                />
              </div>
              <div className="auth-form-wrapper">
                <RegisterForm
                  onSwitch={() => setActiveTab("login")}
                  onSuccess={() => {}}
                  setLoading={setLoading}
                  loading={loading}
                />
              </div>
            </div>
          </div>

          <div className="auth-divider">
            <span>{t("auth.or")}</span>
          </div>

          <div className="auth-google-container">
            {googleError && (
              <div key={googleError} className="auth-error auth-google-error">
                {googleError}
              </div>
            )}
            <div id="google-signin-login-page" />
          </div>
        </div>
      </main>
    </div>
  );
}
