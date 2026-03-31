/**
 * Centralized Auth Storage Utility
 * Single source of truth for all auth-related localStorage operations
 */

const AUTH_KEYS = {
  TOKEN: 'auth_token',
  USER: 'auth_user',
};

// Keys that might exist from other apps or legacy code - to be cleaned up
const LEGACY_KEYS = [
  'token',
  'admin_token',
  'chat_token',
  'user',
  'user_data',
];

/**
 * Get the auth token
 */
export function getToken() {
  return localStorage.getItem(AUTH_KEYS.TOKEN);
}

/**
 * Set the auth token
 */
export function setToken(token) {
  localStorage.setItem(AUTH_KEYS.TOKEN, token);
}

/**
 * Get cached user data
 */
export function getCachedUser() {
  try {
    const userData = localStorage.getItem(AUTH_KEYS.USER);
    return userData ? JSON.parse(userData) : null;
  } catch {
    return null;
  }
}

/**
 * Cache user data for faster initial load
 */
export function setCachedUser(user) {
  if (user) {
    localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(user));
  } else {
    localStorage.removeItem(AUTH_KEYS.USER);
  }
}

/**
 * Clear all auth data - used on logout
 * Also cleans up any legacy/conflicting keys
 */
export function clearAllAuthData() {
  // Clear our keys
  localStorage.removeItem(AUTH_KEYS.TOKEN);
  localStorage.removeItem(AUTH_KEYS.USER);

  // Clean up legacy/conflicting keys
  LEGACY_KEYS.forEach(key => {
    localStorage.removeItem(key);
  });

  // Clear chat-related data on logout
  localStorage.removeItem('chat_conversations');
  localStorage.removeItem('current_conversation_id');
}

/**
 * Check if user has a token (quick sync check)
 */
export function hasToken() {
  return !!getToken();
}

/**
 * Initialize auth - clean up any conflicting legacy keys
 * Called once when app starts
 */
export function initializeAuth() {
  // If we have our token, clean up any legacy tokens to prevent confusion
  if (hasToken()) {
    LEGACY_KEYS.forEach(key => {
      localStorage.removeItem(key);
    });
  }
}
