import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";

export default function Topbar() {
  const { user, logout } = useAuth();
  const { darkMode, toggleDarkMode } = useTheme();

  return (
    <div className="topbar">
      <div className="search">
        <input placeholder="Quick search" />
      </div>
      <div className="topActions">
        <button
          className="themeToggle"
          onClick={toggleDarkMode}
          title={darkMode ? "Светлая тема" : "Тёмная тема"}
        >
          {darkMode ? "☀️" : "🌙"}
        </button>
        {user && <span style={{ fontSize: 14 }} className="userEmail">{user.email}</span>}
        <button className="logoutBtn" onClick={logout}>
          Logout
        </button>
      </div>
    </div>
  );
}
