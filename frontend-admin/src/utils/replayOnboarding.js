import { postOnboardingReset } from "../api/onboardingApi";
import { clearOnboardingDoneLocally } from "./onboardingStorage";

/**
 * Сбросить онбординг: сервер + localStorage, затем синхронизация user.
 *
 * Сразу mergeUser(false) + обновление кэша auth_user нужны, иначе checkAuth()
 * сначала подставит старый auth_user из localStorage с is_onboarding_completed: true
 * и OnboardingGate не откроет тур.
 */
export async function replayPlatformOnboarding(user, checkAuth, mergeUser) {
  if (!user?.id) return;
  clearOnboardingDoneLocally(user.id);
  mergeUser({ is_onboarding_completed: false });

  try {
    const { ok } = await postOnboardingReset();
    if (ok) {
      await checkAuth();
    }
  } catch {
    /* локально флаг уже сброшен */
  }
}
