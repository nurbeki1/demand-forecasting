/** localStorage fallback when POST /auth/me/onboarding-complete is unavailable */

const key = (userId) => `onboarding_completed:${userId}`;

export function isOnboardingDoneLocally(userId) {
  if (userId == null) return false;
  try {
    return localStorage.getItem(key(userId)) === "1";
  } catch {
    return false;
  }
}

export function setOnboardingDoneLocally(userId) {
  if (userId == null) return;
  try {
    localStorage.setItem(key(userId), "1");
  } catch {
    /* ignore quota / private mode */
  }
}

/** Remove local fallback so the tour can run again (after server reset or offline retry). */
export function clearOnboardingDoneLocally(userId) {
  if (userId == null) return;
  try {
    localStorage.removeItem(key(userId));
  } catch {
    /* ignore */
  }
}
