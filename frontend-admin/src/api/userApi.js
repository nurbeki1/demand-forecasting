import { getToken } from "./authApi";
import { API_URL } from "../config";

const BASE_URL = API_URL;

function getHeaders() {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

export async function getUsers({ search, page = 1, perPage = 20, isActive } = {}) {
  const params = new URLSearchParams({ page: String(page), per_page: String(perPage) });
  if (search) params.set("search", search);
  if (isActive !== undefined) params.set("is_active", String(isActive));

  const res = await fetch(`${BASE_URL}/admin/users?${params}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch users (${res.status})`);
  return res.json();
}

export async function getUser(userId) {
  const res = await fetch(`${BASE_URL}/admin/users/${userId}`, { headers: getHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch user (${res.status})`);
  return res.json();
}

export async function updateUser(userId, data) {
  const res = await fetch(`${BASE_URL}/admin/users/${userId}`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Update failed (${res.status})`);
  }
  return res.json();
}

export async function deleteUser(userId) {
  const res = await fetch(`${BASE_URL}/admin/users/${userId}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Delete failed (${res.status})`);
  }
  return res.json();
}