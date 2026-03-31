/**
 * User Dashboard Page
 * Simple dashboard for regular (non-admin) users
 */

import { useAuth } from "../context/AuthContext";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";

export default function UserDashboard() {
  const { user } = useAuth();

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar title="Dashboard" />
        <div className="content">
          {/* Welcome Section */}
          <div className="headerRow">
            <div>
              <div className="title">Welcome, {user?.email?.split("@")[0] || "User"}</div>
              <div className="subtitle">Your personal dashboard</div>
            </div>
          </div>

          {/* User Info Card */}
          <div className="card">
            <div className="cardHeader">
              <div className="cardTitle">Account Information</div>
            </div>
            <div style={{ padding: "20px 0" }}>
              <div style={{
                display: "grid",
                gridTemplateColumns: "120px 1fr",
                gap: "16px",
                fontSize: "14px"
              }}>
                <span style={{ color: "var(--text-tertiary)" }}>Email:</span>
                <span style={{ color: "var(--text-primary)" }}>{user?.email}</span>

                <span style={{ color: "var(--text-tertiary)" }}>Role:</span>
                <span style={{
                  color: "var(--accent)",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px"
                }}>
                  <span style={{
                    width: "8px",
                    height: "8px",
                    background: "var(--success)",
                    borderRadius: "50%"
                  }}></span>
                  Regular User
                </span>

                <span style={{ color: "var(--text-tertiary)" }}>Status:</span>
                <span style={{ color: "var(--success)" }}>Active</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="cardHeader">
              <div className="cardTitle">Quick Actions</div>
            </div>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "16px",
              padding: "20px 0"
            }}>
              <div style={{
                padding: "24px",
                background: "var(--bg-secondary)",
                borderRadius: "12px",
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}>
                <div style={{ fontSize: "32px", marginBottom: "12px" }}>📊</div>
                <div style={{ fontWeight: "600", color: "var(--text-primary)" }}>View Reports</div>
                <div style={{ fontSize: "13px", color: "var(--text-tertiary)", marginTop: "4px" }}>
                  Access your reports
                </div>
              </div>

              <div style={{
                padding: "24px",
                background: "var(--bg-secondary)",
                borderRadius: "12px",
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}>
                <div style={{ fontSize: "32px", marginBottom: "12px" }}>⚙️</div>
                <div style={{ fontWeight: "600", color: "var(--text-primary)" }}>Settings</div>
                <div style={{ fontSize: "13px", color: "var(--text-tertiary)", marginTop: "4px" }}>
                  Manage your account
                </div>
              </div>

              <div style={{
                padding: "24px",
                background: "var(--bg-secondary)",
                borderRadius: "12px",
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.2s ease"
              }}>
                <div style={{ fontSize: "32px", marginBottom: "12px" }}>❓</div>
                <div style={{ fontWeight: "600", color: "var(--text-primary)" }}>Help</div>
                <div style={{ fontSize: "13px", color: "var(--text-tertiary)", marginTop: "4px" }}>
                  Get support
                </div>
              </div>
            </div>
          </div>

          {/* Info Notice */}
          <div style={{
            padding: "16px 20px",
            background: "rgba(99, 102, 241, 0.1)",
            border: "1px solid rgba(99, 102, 241, 0.2)",
            borderRadius: "12px",
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}>
            <span style={{ fontSize: "20px" }}>ℹ️</span>
            <div>
              <div style={{ fontWeight: "500", color: "var(--text-primary)" }}>
                Limited Access
              </div>
              <div style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px" }}>
                Contact an administrator for additional permissions.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}