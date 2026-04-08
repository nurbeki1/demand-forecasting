/**
 * LoginPage - Authentication page
 *
 * Note: After successful login, navigation is handled automatically
 * by the PublicRoute guard in App.jsx which redirects authenticated
 * users to their appropriate dashboard.
 */

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { useAuth } from "../context/AuthContext";
import "../styles/login.css";

// Geometric Logo Component with animation
function GeometricLogo() {
  return (
    <div className="logo-container">
      <svg width="48" height="48" viewBox="0 0 36 36" className="logo-icon">
        {/* Octagon */}
        <path
          className="octagon"
          d="M11 2 L25 2 L34 11 L34 25 L25 34 L11 34 L2 25 L2 11 Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
        />
        {/* Diamond */}
        <path
          className="diamond"
          d="M18 8 L26 18 L18 28 L10 18 Z"
          fill="currentColor"
          opacity="0.9"
        />
      </svg>
    </div>
  );
}

export default function LoginPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);

  const { login, register } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      if (isRegister) {
        await register(email, password);
      } else {
        await login(email, password);
      }
    } catch (err) {
      toast.error(err.message || t('auth.serverError'));
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <GeometricLogo />

        <div className="login-header">
          <h1>{isRegister ? t('auth.register') : t('auth.welcome')}</h1>
          <p>{isRegister ? t('auth.registerSubtitle') : t('auth.loginSubtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('auth.email')}
              required
              disabled={loading}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t('auth.password')}
              required
              disabled={loading}
              minLength={4}
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? (
              <span className="loading-spinner"></span>
            ) : (
              isRegister ? t('auth.createAccount') : t('auth.login')
            )}
          </button>
        </form>

        <div className="login-footer">
          <span>{isRegister ? t('auth.haveAccount') : t('auth.noAccount')}</span>
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="btn-switch"
          >
            {isRegister ? t('auth.login') : t('auth.register')}
          </button>
        </div>
      </div>
    </div>
  );
}