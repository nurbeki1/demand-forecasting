import { NavLink, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import LanguageSwitcher from "../LanguageSwitcher";

export default function Sidebar() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Admin menu items - all under /admin prefix
  const adminMenuItems = [
    { path: "/admin", label: t('nav.dashboard'), icon: "🎯" },
    { path: "/admin/forecast", label: t('forecast.title'), icon: "📊" },
    { path: "/admin/compare", label: t('nav.compare', 'Compare'), icon: "⚖️" },
    { path: "/admin/reports", label: t('nav.reports'), icon: "📑" },
    { path: "/admin/users", label: t('nav.users'), icon: "👥" },
    { path: "/admin/table", label: t('common.export'), icon: "📋" },
    { path: "/admin/upload", label: t('common.import'), icon: "📤" },
    { path: "/admin/model", label: t('model.title'), icon: "🤖" },
  ];

  // Regular user menu items - AI Chat (settings is inside ChatPage)
  const userMenuItems = [
    { path: "/user", label: t('nav.chat'), icon: "💬" },
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
        <div className={`avatar ${isAdmin ? "avatar-admin" : "avatar-user"}`}>
          {isAdmin ? "A" : "U"}
        </div>
        <div>
          <div className="name">{user?.email?.split("@")[0] || "User"}</div>
          <div className={`role ${isAdmin ? "role-admin" : "role-user"}`}>
            {isAdmin ? t('common.admin', 'Admin') : t('common.user', 'User')}
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
      <div className="sidebar-spacer" />

      {/* Language Switcher */}
      <div className="sidebar-language-section">
        <div className="sidebar-language-label">
          {t('settings.language')}
        </div>
        <LanguageSwitcher variant="buttons" />
      </div>

      {/* Logout Button */}
      <div className="sidebar-block">
        <button
          onClick={handleLogout}
          className="sidebar-logout-button"
          aria-label={t('nav.logout')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          {t('nav.logout')}
        </button>
      </div>

      {/* Status Indicator */}
      <div className="sidebar-block">
        <div className="sidebar-status">
          <span className="sidebar-status-dot"></span>
          <span className="sidebar-status-text">
            {t('common.systemOnline')}
          </span>
        </div>
      </div>
    </aside>
  );
}
