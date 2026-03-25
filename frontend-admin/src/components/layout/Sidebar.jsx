import { NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="sidebar">
      <div className="profile">
        <div className="avatar">DF</div>
        <div>
          <div className="name">{user?.email?.split("@")[0] || "User"}</div>
          <div className="role">Admin</div>
        </div>
      </div>

      <nav className="menu">
        <NavLink
          to="/"
          className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
        >
          Dashboard
        </NavLink>
        <NavLink
          to="/charts"
          className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
        >
          Charts
        </NavLink>
        <NavLink
          to="/table"
          className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
        >
          Table
        </NavLink>
        <NavLink
          to="/upload"
          className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
        >
          Upload Data
        </NavLink>
        <NavLink
          to="/chat"
          className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
        >
          AI Chat
        </NavLink>
      </nav>
    </aside>
  );
}
