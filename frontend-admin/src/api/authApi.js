import { API_URL } from "../config";
const BASE_URL = API_URL;

export async function login(email, password) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Login failed");
  }

  const data = await res.json();

  // Check if user is admin
  if (!data.is_admin) {
    throw new Error("Admin access required. Contact administrator.");
  }

  return {
    token: data.access_token,
    isAdmin: data.is_admin,
  };
}

export async function getMe(token) {
  const res = await fetch(`${BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!res.ok) {
    throw new Error("Failed to get user info");
  }

  return await res.json();
}

export function getToken() {
  return localStorage.getItem("admin_token");
}

export function setToken(token) {
  localStorage.setItem("admin_token", token);
}

export function removeToken() {
  localStorage.removeItem("admin_token");
}

export function isAuthenticated() {
  return !!getToken();
}