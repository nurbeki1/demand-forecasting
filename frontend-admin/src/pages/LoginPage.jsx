/**
 * LoginPage - Authentication page
 *
 * Note: After successful login, navigation is handled automatically
 * by the PublicRoute guard in App.jsx which redirects authenticated
 * users to their appropriate dashboard.
 */

import { useState } from "react";
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
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRegister, setIsRegister] = useState(false);

  const { login, register } = useAuth();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await register(email, password);
      } else {
        await login(email, password);
      }
      // Navigation is handled automatically by PublicRoute guard
      // which will redirect to appropriate dashboard based on role
    } catch (err) {
      setError(err.message || "Authentication failed");
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <GeometricLogo />

        <div className="login-header">
          <h1>{isRegister ? "Create account" : "Welcome back"}</h1>
          <p>{isRegister ? "Start your journey" : "Sign in to continue"}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-box">{error}</div>}

          <div className="form-group">
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
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
              placeholder="Password"
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
              isRegister ? "Create account" : "Continue"
            )}
          </button>
        </form>

        <div className="login-footer">
          <span>{isRegister ? "Already have an account?" : "Don't have an account?"}</span>
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError("");
            }}
            className="btn-switch"
          >
            {isRegister ? "Sign in" : "Sign up"}
          </button>
        </div>
      </div>
    </div>
  );
}