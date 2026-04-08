/**
 * Settings API - Backend Integration
 * Persists user settings via /settings endpoints
 */

import { getToken } from "./authApi";
import { API_URL } from "../config";

const BASE_URL = API_URL;

function getHeaders() {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

/**
 * Get all user settings
 */
export async function getSettings() {
  const token = getToken();
  if (!token) return {};

  try {
    const res = await fetch(`${BASE_URL}/settings`, { headers: getHeaders() });
    if (!res.ok) return {};
    return res.json();
  } catch {
    return {};
  }
}

/**
 * Update a single setting within a section
 */
export async function updateSettings(section, key, value) {
  const res = await fetch(`${BASE_URL}/settings/${section}`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify({ values: { [key]: value } }),
  });
  if (!res.ok) {
    throw new Error(`Failed to update settings (${res.status})`);
  }
  return res.json();
}

/**
 * Update multiple settings in a section
 */
export async function updateSectionSettings(section, values) {
  const res = await fetch(`${BASE_URL}/settings/${section}`, {
    method: "PATCH",
    headers: getHeaders(),
    body: JSON.stringify({ values }),
  });
  if (!res.ok) {
    throw new Error(`Failed to update settings (${res.status})`);
  }
  return res.json();
}

/**
 * Reset all settings to defaults
 */
export async function resetSettings() {
  const res = await fetch(`${BASE_URL}/settings`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to reset settings (${res.status})`);
  }
  return {};
}

/**
 * Export settings as JSON
 */
export async function exportSettings() {
  const settings = await getSettings();
  return JSON.stringify(settings, null, 2);
}

/**
 * Import settings from JSON
 */
export async function importSettings(jsonString) {
  const settings = JSON.parse(jsonString);
  const res = await fetch(`${BASE_URL}/settings`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify(settings),
  });
  if (!res.ok) {
    throw new Error(`Failed to import settings (${res.status})`);
  }
  return res.json();
}