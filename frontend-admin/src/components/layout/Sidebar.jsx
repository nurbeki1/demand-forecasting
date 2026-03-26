import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Sidebar() {
  const { user } = useAuth();

  const menuItems = [
    { path: "/", label: "Dashboard", icon: "◉" },
    { path: "/charts", label: "Charts", icon: "◈" },
    { path: "/table", label: "Table", icon: "☰" },
    { path: "/upload", label: "Upload", icon: "↑" },
    { path: "/chat", label: "AI Chat", icon: "◇" },
    { path: "/model", label: "ML Model", icon: "⬡" },
  ];

  return (
    <aside className="sidebar">
      <div className="profile">
        <div className="avatar">DF</div>
        <div>
          <div className="name">{user?.email?.split("@")[0] || "User"}</div>
          <div className="role">Admin Panel</div>
        </div>
      </div>

      <nav className="menu">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
          >
            <span style={{ fontSize: "16px", opacity: 0.7 }}>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div style={{
        padding: "16px",
        borderTop: "1px solid rgba(0, 229, 255, 0.12)",
        marginTop: "auto"
      }}>
        <div style={{
          padding: "12px",
          background: "rgba(0, 229, 255, 0.08)",
          borderRadius: "8px",
          border: "1px solid rgba(0, 229, 255, 0.15)"
        }}>
          <div style={{
            fontFamily: "'Space Mono', monospace",
            fontSize: "10px",
            color: "#4a6580",
            textTransform: "uppercase",
            letterSpacing: "0.1em",
            marginBottom: "4px"
          }}>
            System Status
          </div>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "8px"
          }}>
            <span style={{
              width: "8px",
              height: "8px",
              background: "#00ff88",
              borderRadius: "50%",
              boxShadow: "0 0 10px #00ff88"
            }}></span>
            <span style={{
              fontFamily: "'Space Mono', monospace",
              fontSize: "12px",
              color: "#00ff88"
            }}>
              Online
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
