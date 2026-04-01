import { API_URL } from "../config";

function getToken() {
  return localStorage.getItem("chat_token");
}

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
 */
export async function sendChatMessage(message) {
  const res = await fetch(`${API_URL}/chat`, {
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
 */
export async function getChatHistory(limit) {
  const params = new URLSearchParams();
  if (limit) params.set("limit", String(limit));

  const url = limit
    ? `${API_URL}/chat/history?${params.toString()}`
    : `${API_URL}/chat/history`;

  const res = await fetch(url, { headers: getHeaders() });

  if (!res.ok) {
    throw new Error(`Failed to fetch chat history (${res.status})`);
  }
  return res.json();
}

/**
 * Clear chat history for the current user
 */
export async function clearChatHistory() {
  const res = await fetch(`${API_URL}/chat/history`, {
    method: "DELETE",
    headers: getHeaders(),
  });

  if (!res.ok) {
    throw new Error(`Failed to clear chat history (${res.status})`);
  }
  return res.json();
}