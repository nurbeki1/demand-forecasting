import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Sidebar() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  // Admin menu items - all under /admin prefix
  const adminMenuItems = [
    { path: "/admin", label: "Dashboard", icon: "🎯" },
    { path: "/admin/forecast", label: "Forecasts & Charts", icon: "📊" },
    { path: "/admin/table", label: "Data Table", icon: "📋" },
    { path: "/admin/upload", label: "Upload CSV", icon: "📤" },
    { path: "/admin/model", label: "ML Model", icon: "🤖" },
  ];

  // Regular user menu items - AI Chat
  const userMenuItems = [
    { path: "/user", label: "AI Chat", icon: "💬" },
  ];

  const menuItems = isAdmin ? adminMenuItems : userMenuItems;

  const handleLogout = () => {
    navigate("/");
    setTimeout(() => logout(), 100);
  };

  return (
    <aside className="sidebar">
      {/* Profile Section */}
      <div className="profile">
        <div className="avatar" style={{
          background: isAdmin ? "var(--accent)" : "var(--success)"
        }}>
          {isAdmin ? "A" : "U"}
        </div>
        <div>
          <div className="name">{user?.email?.split("@")[0] || "User"}</div>
          <div className="role" style={{
            color: isAdmin ? "var(--accent)" : "var(--text-tertiary)"
          }}>
            {isAdmin ? "Administrator" : "User"}
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="menu">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
            end={item.path === "/admin" || item.path === "/user"}
          >
            <span>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Logout Button */}
      <div style={{
        padding: "16px",
        borderTop: "1px solid var(--border)"
      }}>
        <button
          onClick={handleLogout}
          style={{
            width: "100%",
            padding: "12px 16px",
            background: "var(--bg-secondary)",
            border: "1px solid var(--border)",
            borderRadius: "12px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            cursor: "pointer",
            color: "var(--text-secondary)",
            fontSize: "14px",
            transition: "all 0.2s ease"
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          Sign Out
        </button>
      </div>

      {/* Status Indicator */}
      <div style={{
        padding: "0 16px 16px"
      }}>
        <div style={{
          padding: "12px 16px",
          background: "var(--bg-secondary)",
          borderRadius: "12px",
          display: "flex",
          alignItems: "center",
          gap: "10px"
        }}>
          <span style={{
            width: "8px",
            height: "8px",
            background: "var(--success)",
            borderRadius: "50%"
          }}></span>
          <span style={{
            fontSize: "13px",
            color: "var(--text-secondary)"
          }}>
            System Online
          </span>
        </div>
      </div>
    </aside>
  );
}
