import { API_URL } from "../config";
import { getToken } from "../utils/authStorage";

/**
 * Mark onboarding complete on the server.
 * @returns {{ ok: boolean, user: object | null }}
 */
export async function postOnboardingComplete() {
  const token = getToken();
  if (!token) return { ok: false, user: null };

  try {
    const res = await fetch(`${API_URL}/auth/me/onboarding-complete`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return { ok: false, user: null };
    const user = await res.json();
    return { ok: true, user };
  } catch {
    return { ok: false, user: null };
  }
}

/** Сброс флага на сервере (снова показать тур). */
export async function postOnboardingReset() {
  const token = getToken();
  if (!token) return { ok: false, user: null };

  try {
    const res = await fetch(`${API_URL}/auth/me/onboarding-reset`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return { ok: false, user: null };
    const user = await res.json();
    return { ok: true, user };
  } catch {
    return { ok: false, user: null };
  }
}
