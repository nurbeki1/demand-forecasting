import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/dashboard.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="loginPage">
      <div className="loginCard">
        <div className="loginHeader">
          <div style={{
            width: "48px",
            height: "48px",
            margin: "0 auto 16px",
            background: "linear-gradient(135deg, var(--pulse) 0%, var(--signal) 100%)",
            borderRadius: "12px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "20px",
            fontWeight: "bold",
            color: "var(--void)"
          }}>
            DF
          </div>
          <h1>Admin Panel</h1>
          <p>Sign in with admin credentials</p>
        </div>

        <form onSubmit={handleSubmit} className="loginForm">
          {error && <div className="errorBox">{error}</div>}

          <div className="formGroup">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@example.com"
              required
              disabled={loading}
            />
          </div>

          <div className="formGroup">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
              disabled={loading}
              minLength={4}
            />
          </div>

          <button type="submit" className="btnPrimary" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="loginFooter">
          <p style={{
            color: "var(--text-secondary)",
            fontSize: "12px",
            fontFamily: "var(--font-mono)"
          }}>
            Admin access only. Contact administrator for access.
          </p>
        </div>
      </div>
    </div>
  );
}