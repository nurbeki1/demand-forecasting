import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { API_URL } from "../config";
import { getToken, setCachedUser } from "../utils/authStorage";
import { toast } from "sonner";

function getInitials(name, email) {
  if (name) {
    const parts = name.trim().split(" ");
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return parts[0][0].toUpperCase();
  }
  return email?.[0]?.toUpperCase() || "U";
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("ru-RU", { year: "numeric", month: "long", day: "numeric" });
}

export default function ProfilePage() {
  const { user, logout, checkAuth } = useAuth();
  const navigate = useNavigate();

  const [editing, setEditing] = useState(false);
  const [nameValue, setNameValue] = useState(user?.full_name || "");
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/auth/me`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ full_name: nameValue }),
      });

      if (!res.ok) throw new Error("Ошибка сохранения");

      const updated = await res.json();
      setCachedUser(updated);
      await checkAuth();
      setEditing(false);
      toast.success("Профиль обновлён");
    } catch {
      toast.error("Не удалось сохранить");
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    navigate("/");
    setTimeout(() => logout(), 100);
  };

  const s = {
    page: {
      minHeight: "100vh",
      background: "var(--bg-primary, #0a0a0f)",
      display: "flex",
      justifyContent: "center",
      alignItems: "flex-start",
      padding: "40px 16px",
    },
    card: {
      width: "100%",
      maxWidth: "480px",
    },
    header: {
      display: "flex",
      alignItems: "center",
      gap: "12px",
      marginBottom: "32px",
    },
    backBtn: {
      background: "none",
      border: "1px solid var(--border, #2a2a3e)",
      borderRadius: "8px",
      color: "var(--text-secondary, #888)",
      cursor: "pointer",
      padding: "8px 10px",
      display: "flex",
      alignItems: "center",
    },
    title: {
      fontSize: "20px",
      fontWeight: 600,
      color: "var(--text-primary, #e0e0e0)",
      margin: 0,
    },
    avatarWrap: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      marginBottom: "32px",
      gap: "12px",
    },
    avatar: {
      width: "80px",
      height: "80px",
      borderRadius: "50%",
      background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "28px",
      fontWeight: 700,
      color: "#fff",
    },
    section: {
      background: "var(--bg-secondary, #1a1a2e)",
      border: "1px solid var(--border, #2a2a3e)",
      borderRadius: "12px",
      padding: "20px",
      marginBottom: "16px",
    },
    label: {
      fontSize: "11px",
      textTransform: "uppercase",
      letterSpacing: "0.5px",
      color: "var(--text-tertiary, #666)",
      marginBottom: "6px",
    },
    value: {
      fontSize: "15px",
      color: "var(--text-primary, #e0e0e0)",
      fontWeight: 500,
    },
    emailValue: {
      fontSize: "15px",
      color: "var(--text-secondary, #888)",
    },
    row: {
      marginBottom: "18px",
    },
    input: {
      width: "100%",
      background: "var(--bg-primary, #0a0a0f)",
      border: "1px solid var(--accent, #6366f1)",
      borderRadius: "8px",
      color: "var(--text-primary, #e0e0e0)",
      fontSize: "15px",
      padding: "8px 12px",
      outline: "none",
      boxSizing: "border-box",
    },
    actions: {
      display: "flex",
      gap: "8px",
      marginTop: "8px",
    },
    btnPrimary: {
      flex: 1,
      background: "var(--accent, #6366f1)",
      color: "#fff",
      border: "none",
      borderRadius: "8px",
      padding: "9px 16px",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: 500,
    },
    btnSecondary: {
      flex: 1,
      background: "none",
      color: "var(--text-secondary, #888)",
      border: "1px solid var(--border, #2a2a3e)",
      borderRadius: "8px",
      padding: "9px 16px",
      cursor: "pointer",
      fontSize: "14px",
    },
    editBtn: {
      background: "none",
      border: "1px solid var(--border, #2a2a3e)",
      borderRadius: "8px",
      color: "var(--accent, #6366f1)",
      cursor: "pointer",
      fontSize: "13px",
      padding: "5px 12px",
      marginTop: "8px",
    },
    logoutBtn: {
      width: "100%",
      background: "none",
      border: "1px solid rgba(239,68,68,0.4)",
      borderRadius: "10px",
      color: "#ef4444",
      cursor: "pointer",
      fontSize: "14px",
      fontWeight: 500,
      padding: "12px",
      marginTop: "8px",
    },
  };

  return (
    <div style={s.page}>
      <div style={s.card}>
        {/* Header */}
        <div style={s.header}>
          <button style={s.backBtn} onClick={() => navigate("/user")} aria-label="Назад">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 5l-7 7 7 7" />
            </svg>
          </button>
          <h1 style={s.title}>Профиль</h1>
        </div>

        {/* Avatar */}
        <div style={s.avatarWrap}>
          {user?.avatar_url ? (
            <img src={user.avatar_url} alt="avatar" style={{ ...s.avatar, objectFit: "cover" }} />
          ) : (
            <div style={s.avatar}>{getInitials(user?.full_name, user?.email)}</div>
          )}
        </div>

        {/* Info section */}
        <div style={s.section}>
          {/* Name */}
          <div style={s.row}>
            <div style={s.label}>Имя</div>
            {editing ? (
              <>
                <input
                  style={s.input}
                  value={nameValue}
                  onChange={(e) => setNameValue(e.target.value)}
                  placeholder="Введите имя"
                  autoFocus
                  onKeyDown={(e) => e.key === "Enter" && handleSave()}
                />
                <div style={s.actions}>
                  <button style={s.btnPrimary} onClick={handleSave} disabled={saving}>
                    {saving ? "Сохраняем..." : "Сохранить"}
                  </button>
                  <button
                    style={s.btnSecondary}
                    onClick={() => { setEditing(false); setNameValue(user?.full_name || ""); }}
                  >
                    Отмена
                  </button>
                </div>
              </>
            ) : (
              <>
                <div style={s.value}>{user?.full_name || <span style={{ color: "var(--text-tertiary,#666)" }}>Не указано</span>}</div>
                <button style={s.editBtn} onClick={() => setEditing(true)}>Изменить</button>
              </>
            )}
          </div>

          {/* Email */}
          <div style={s.row}>
            <div style={s.label}>Email</div>
            <div style={s.emailValue}>{user?.email}</div>
          </div>

          {/* Role */}
          <div style={s.row}>
            <div style={s.label}>Роль</div>
            <div style={s.value}>{user?.is_admin ? "Администратор" : "Пользователь"}</div>
          </div>

          {/* Member since */}
          <div style={{ ...s.row, marginBottom: 0 }}>
            <div style={s.label}>Участник с</div>
            <div style={s.value}>{formatDate(user?.created_at)}</div>
          </div>
        </div>

        {/* Logout */}
        <button style={s.logoutBtn} onClick={handleLogout}>
          Выйти из аккаунта
        </button>
      </div>
    </div>
  );
}