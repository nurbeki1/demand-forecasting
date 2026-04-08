import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { getUsers, updateUser, deleteUser } from "../api/userApi";
import { useAuth } from "../context/AuthContext";
import "../styles/users.css";

export default function UserManagementPage() {
  const { t } = useTranslation();
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [searchTimeout, setSearchTimeout] = useState(null);

  const perPage = 20;

  const fetchUsers = useCallback(async (searchQuery, pageNum) => {
    setLoading(true);
    try {
      const data = await getUsers({ search: searchQuery, page: pageNum, perPage });
      setUsers(data.users);
      setTotal(data.total);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers(search, page);
  }, [page, fetchUsers]);

  function handleSearchChange(value) {
    setSearch(value);
    if (searchTimeout) clearTimeout(searchTimeout);
    setSearchTimeout(
      setTimeout(() => {
        setPage(1);
        fetchUsers(value, 1);
      }, 300)
    );
  }

  async function handleToggleAdmin(user) {
    if (user.email === currentUser?.email) {
      toast.error(t('users.cantEditSelf'));
      return;
    }
    try {
      await updateUser(user.id, { is_admin: !user.is_admin });
      toast.success(t('users.updateSuccess'));
      fetchUsers(search, page);
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleToggleActive(user) {
    if (user.email === currentUser?.email) {
      toast.error(t('users.cantEditSelf'));
      return;
    }
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      toast.success(t('users.updateSuccess'));
      fetchUsers(search, page);
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleDelete(user) {
    if (user.email === currentUser?.email) {
      toast.error(t('users.cantEditSelf'));
      return;
    }
    if (!window.confirm(t('users.confirmDelete'))) return;
    try {
      await deleteUser(user.id);
      toast.success(t('users.deleteSuccess'));
      fetchUsers(search, page);
    } catch (err) {
      toast.error(err.message);
    }
  }

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">{t('users.title')}</div>
              <div className="subtitle">{t('users.subtitle')}</div>
            </div>
            <div className="users-total">
              {t('users.total')}: <strong>{total}</strong>
            </div>
          </div>

          {/* Search */}
          <div className="panel">
            <input
              type="text"
              className="users-search"
              placeholder={t('users.searchPlaceholder')}
              value={search}
              onChange={(e) => handleSearchChange(e.target.value)}
            />
          </div>

          {/* Users Table */}
          <div className="card">
            {loading ? (
              <div className="emptyBox">{t('common.loading')}</div>
            ) : users.length === 0 ? (
              <div className="emptyBox">{t('users.noUsers')}</div>
            ) : (
              <>
                <div className="tableWrap">
                  <table className="table users-table">
                    <thead>
                      <tr>
                        <th>{t('users.email')}</th>
                        <th>{t('users.fullName')}</th>
                        <th>{t('users.role')}</th>
                        <th>{t('users.status')}</th>
                        <th>{t('users.createdAt')}</th>
                        <th>{t('users.actions')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((u) => {
                        const isSelf = u.email === currentUser?.email;
                        return (
                          <tr key={u.id} className={!u.is_active ? "user-inactive" : ""}>
                            <td>
                              <div className="user-email-cell">
                                <div
                                  className="user-avatar"
                                  style={{
                                    background: u.is_admin ? "var(--accent)" : "var(--text-tertiary)",
                                  }}
                                >
                                  {(u.full_name || u.email)[0].toUpperCase()}
                                </div>
                                <span>{u.email}</span>
                                {isSelf && <span className="user-you-badge">you</span>}
                              </div>
                            </td>
                            <td>{u.full_name || "—"}</td>
                            <td>
                              <span className={`user-badge ${u.is_admin ? "badge-admin" : "badge-user"}`}>
                                {u.is_admin ? t('users.admin') : t('users.user')}
                              </span>
                            </td>
                            <td>
                              <span className={`user-badge ${u.is_active ? "badge-active" : "badge-inactive"}`}>
                                {u.is_active ? t('users.active') : t('users.inactive')}
                              </span>
                            </td>
                            <td>
                              {u.created_at
                                ? new Date(u.created_at).toLocaleDateString()
                                : "—"}
                            </td>
                            <td>
                              <div className="user-actions">
                                <button
                                  className="user-action-btn"
                                  onClick={() => handleToggleAdmin(u)}
                                  disabled={isSelf}
                                  title={u.is_admin ? t('users.removeAdmin') : t('users.makeAdmin')}
                                >
                                  {u.is_admin ? "👤" : "🛡️"}
                                </button>
                                <button
                                  className="user-action-btn"
                                  onClick={() => handleToggleActive(u)}
                                  disabled={isSelf}
                                  title={u.is_active ? t('users.deactivate') : t('users.activate')}
                                >
                                  {u.is_active ? "⏸️" : "▶️"}
                                </button>
                                <button
                                  className="user-action-btn user-action-delete"
                                  onClick={() => handleDelete(u)}
                                  disabled={isSelf}
                                  title={t('users.deleteUser')}
                                >
                                  🗑️
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {totalPages > 1 && (
                  <div className="pagination">
                    <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
                      {t('common.previous')}
                    </button>
                    <span>
                      {t('common.page')} {page} {t('common.of')} {totalPages}
                    </span>
                    <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
                      {t('common.next')}
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}