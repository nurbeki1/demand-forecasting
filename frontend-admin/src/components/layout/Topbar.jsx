import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function Topbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate("/");
    setTimeout(() => logout(), 100);
  };

  return (
    <div className="topbar">
      <div className="search">
        <span style={{ color: "var(--text-tertiary)" }}>🔍</span>
        <input placeholder="Search..." />
      </div>

      <div className="topActions">
        {user && (
          <span className="userEmail">
            {user.email}
          </span>
        )}

        <button className="logoutBtn" onClick={handleLogout}>
          Sign out
        </button>
      </div>
    </div>
  );
}