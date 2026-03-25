import { getToken } from "./authApi";
import { API_URL } from "../config";

const BASE_URL = API_URL;

function getHeaders() {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Send a message to the AI chat
 * @param {string} message - The message to send
 * @returns {Promise<{reply: string, intent: string, entities: object, suggestions: string[], data?: object}>}
 */
export async function sendChatMessage(message) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Chat request failed (${res.status})`);
  }
  return res.json();
}

/**
 * Get chat history for the current user
 * @param {number} [limit] - Optional limit on number of messages
 * @returns {Promise<Array<{role: string, content: string, timestamp: string, intent?: string, data?: object}>>}
 */
export async function getChatHistory(limit) {
  const params = new URLSearchParams();
  if (limit) params.set("limit", String(limit));

  const url = limit
    ? `${BASE_URL}/chat/history?${params.toString()}`
    : `${BASE_URL}/chat/history`;

  const res = await fetch(url, { headers: getHeaders() });

  if (!res.ok) {
    throw new Error(`Failed to fetch chat history (${res.status})`);
  }
  return res.json();
}

/**
 * Clear chat history for the current user
 * @returns {Promise<{message: string, cleared_messages: number}>}
 */
export async function clearChatHistory() {
  const res = await fetch(`${BASE_URL}/chat/history`, {
    method: "DELETE",
    headers: getHeaders(),
  });

  if (!res.ok) {
    throw new Error(`Failed to clear chat history (${res.status})`);
  }
  return res.json();
}

/**
 * Get analytics summary
 * @returns {Promise<{overview: object, top_by_demand: array, top_by_growth: array, declining: array}>}
 */
export async function getAnalyticsSummary() {
  const res = await fetch(`${BASE_URL}/analytics/summary`, {
    headers: getHeaders(),
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch analytics summary (${res.status})`);
  }
  return res.json();
}

/**
 * Get analytics trends
 * @returns {Promise<{growing: array, declining: array, stable: array}>}
 */
export async function getAnalyticsTrends() {
  const res = await fetch(`${BASE_URL}/analytics/trends`, {
    headers: getHeaders(),
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch analytics trends (${res.status})`);
  }
  return res.json();
}
