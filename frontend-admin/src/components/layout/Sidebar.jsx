import { NavLink, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  LayoutDashboard,
  BarChart3,
  Scale,
  FileText,
  Users,
  LifeBuoy,
  ArrowDownToLine,
  ArrowUpFromLine,
  Cpu,
  MessageSquare,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import LanguageSwitcher from "../LanguageSwitcher";

const iconStroke = 2;
const iconSize = 20;

function IconForecastWorkspace({ size = iconSize, strokeWidth = iconStroke }) {
  return (
    <>
      <BarChart3 size={Math.round(size * 0.72)} strokeWidth={strokeWidth} aria-hidden />
      <Scale size={Math.round(size * 0.66)} strokeWidth={strokeWidth} aria-hidden />
    </>
  );
}

export default function Sidebar() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const adminMenuItems = [
    { path: "/admin", label: t("nav.dashboard"), Icon: LayoutDashboard },
    {
      path: "/admin/forecast",
      label: t("nav.forecastCompare", { defaultValue: "Болжам және салыстыру" }),
      Icon: IconForecastWorkspace,
      duo: true,
    },
    { path: "/admin/reports", label: t("nav.reports"), Icon: FileText },
    { path: "/admin/users", label: t("nav.users"), Icon: Users },
    { path: "/admin/support", label: t("nav.support"), Icon: LifeBuoy },
    { path: "/admin/table", label: t("common.export"), Icon: ArrowDownToLine },
    { path: "/admin/upload", label: t("common.import"), Icon: ArrowUpFromLine },
    { path: "/admin/model", label: t("model.title"), Icon: Cpu },
  ];

  const userMenuItems = [{ path: "/user", label: t("nav.chat"), Icon: MessageSquare }];

  const menuItems = isAdmin ? adminMenuItems : userMenuItems;

  const handleLogout = () => {
    navigate("/");
    setTimeout(() => logout(), 100);
  };

  return (
    <aside className="sidebar" data-admin-sidebar-version="forecast-merge-v2">
      <div className="profile">
        <div className={`avatar ${isAdmin ? "avatar-admin" : "avatar-user"}`}>
          {isAdmin ? "A" : "U"}
        </div>
        <div>
          <div className="name">{user?.email?.split("@")[0] || "User"}</div>
          <div className={`role ${isAdmin ? "role-admin" : "role-user"}`}>
            {isAdmin ? t("common.admin", "Admin") : t("common.user", "User")}
          </div>
        </div>
      </div>

      <nav className="menu">
        {menuItems.map((item) => {
          const { Icon } = item;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `menuItem ${isActive ? "active" : ""}`}
              end={item.path === "/admin" || item.path === "/user"}
            >
              <span
                className={`menuItem-icon${item.duo ? " menuItem-icon--duo" : ""}`}
                aria-hidden
              >
                <Icon size={iconSize} strokeWidth={iconStroke} />
              </span>
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {import.meta.env.DEV && (
        <div
          className="sidebar-dev-hint"
          title="Егер мәзірде әлі екі бөлек «Болжам» / «Салыстыру» көрінсе — vite қайта іске қосыңыз немесе Cmd+Shift+R"
        >
          dev · nav v2 (бір пункт)
        </div>
      )}

      <div className="sidebar-spacer" />

      <div className="sidebar-language-section">
        <div className="sidebar-language-label">{t("settings.language")}</div>
        <LanguageSwitcher variant="buttons" />
      </div>

      <div className="sidebar-block">
        <button
          type="button"
          onClick={handleLogout}
          className="sidebar-logout-button"
          aria-label={t("nav.logout")}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          {t("nav.logout")}
        </button>
      </div>

      <div className="sidebar-block">
        <div className="sidebar-status">
          <span className="sidebar-status-dot" />
          <span className="sidebar-status-text">{t("common.systemOnline")}</span>
        </div>
      </div>
    </aside>
  );
}
