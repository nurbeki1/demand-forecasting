import { useMemo } from "react";
import { useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import OnboardingModal from "./onboarding/OnboardingModal";
import ChatSpotlightOnboarding from "./onboarding/ChatSpotlightOnboarding";
import { isOnboardingDoneLocally } from "../utils/onboardingStorage";

function isPlatformArea(pathname) {
  if (pathname.startsWith("/user")) return true;
  if (pathname.startsWith("/admin")) return true;
  if (pathname.startsWith("/subscriptions/payment")) return true;
  return false;
}

/**
 * Renders first-login onboarding only for authenticated users inside app routes
 * (not on landing or public pricing).
 */
export default function OnboardingGate({ children }) {
  const { isAuthenticated, user, isLoading, isAdmin } = useAuth();
  const { pathname } = useLocation();

  const showOnboarding = useMemo(() => {
    if (isLoading || !isAuthenticated || user?.id == null) return false;
    if (user.is_onboarding_completed === true) return false;
    if (isOnboardingDoneLocally(user.id)) return false;
    return isPlatformArea(pathname);
  }, [isAuthenticated, isLoading, user, pathname]);

  /** Chat: spotlight on real UI. Admin / other routes: centered modal. */
  const useChatSpotlight =
    showOnboarding && !isAdmin && pathname === "/user";

  return (
    <>
      {children}
      {useChatSpotlight ? <ChatSpotlightOnboarding /> : null}
      {showOnboarding && !useChatSpotlight ? <OnboardingModal /> : null}
    </>
  );
}
