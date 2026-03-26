import { useAuth } from "../../context/AuthContext";

export default function Topbar() {
  const { user, logout } = useAuth();

  return (
    <div className="topbar">
      <div className="search">
        <input placeholder="⌘ Quick search..." />
      </div>

      <div className="topActions">
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "6px 12px",
          background: "rgba(0, 255, 136, 0.1)",
          border: "1px solid rgba(0, 255, 136, 0.2)",
          borderRadius: "6px"
        }}>
          <span style={{
            width: "6px",
            height: "6px",
            background: "#00ff88",
            borderRadius: "50%",
            animation: "pulse-glow 2s ease-in-out infinite"
          }}></span>
          <span style={{
            fontFamily: "'Space Mono', monospace",
            fontSize: "11px",
            color: "#00ff88"
          }}>
            Live
          </span>
        </div>

        {user && (
          <span className="userEmail">
            {user.email}
          </span>
        )}

        <button className="logoutBtn" onClick={logout}>
          Logout
        </button>
      </div>
    </div>
  );
}