/**
 * Auth API - Legacy compatibility layer
 *
 * This file maintains backwards compatibility for existing code
 * that imports from authApi. All actual logic is in authStorage.js
 */

import { getToken, setToken, clearAllAuthData } from "../utils/authStorage";
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

  return {
    token: data.access_token,
    isAdmin: data.is_admin,
  };
}

export async function register(email, password) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Registration failed");
  }

  return await res.json();
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

// Re-export from authStorage for backwards compatibility
export { getToken, setToken };

export function removeToken() {
  clearAllAuthData();
}

export function isAuthenticated() {
  return !!getToken();
}