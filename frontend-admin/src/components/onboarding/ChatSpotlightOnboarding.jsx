import { useEffect, useRef, useCallback } from "react";
import { driver } from "driver.js";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { postOnboardingComplete } from "../../api/onboardingApi";
import { setOnboardingDoneLocally } from "../../utils/onboardingStorage";
import "driver.js/dist/driver.css";
import "./ChatSpotlightOnboarding.css";

function buildChatTourSteps(t) {
  const steps = [];
  const add = (selector, key, side = "right", align = "center") => {
    if (document.querySelector(selector)) {
      steps.push({
        element: selector,
        popover: {
          title: t(`onboarding.spotlight.${key}Title`),
          description: t(`onboarding.spotlight.${key}Body`),
          side,
          align,
        },
      });
    }
  };

  add('[data-onboarding="chat-new"]', "newChat", "right", "center");
  add('[data-onboarding="chat-recent"]', "recentChats", "right", "start");
  add('[data-onboarding="chat-settings"]', "settings", "right", "center");
  add('[data-onboarding="chat-subscription"]', "subscription", "right", "center");
  add('[data-onboarding="chat-profile"]', "profile", "right", "center");

  if (document.querySelector('[data-onboarding="chat-composer-empty"]')) {
    add('[data-onboarding="chat-composer-empty"]', "composer", "top", "center");
    add('[data-onboarding="chat-suggestions"]', "suggestions", "top", "center");
  } else if (document.querySelector('[data-onboarding="chat-composer-filled"]')) {
    add('[data-onboarding="chat-composer-filled"]', "composer", "top", "center");
  }

  return steps;
}

/**
 * Spotlight tour for /user (chat): highlights sidebar + composer; same completion as /auth/me/onboarding-complete.
 */
export default function ChatSpotlightOnboarding() {
  const { t } = useTranslation();
  const { user, checkAuth, mergeUser } = useAuth();
  const driverObjRef = useRef(null);
  const completedRef = useRef(false);

  const finalize = useCallback(async () => {
    if (!user?.id) return;
    try {
      const { ok } = await postOnboardingComplete();
      if (ok) await checkAuth();
      else {
        setOnboardingDoneLocally(user.id);
        mergeUser({ is_onboarding_completed: true });
      }
    } catch {
      setOnboardingDoneLocally(user.id);
      mergeUser({ is_onboarding_completed: true });
    }
  }, [checkAuth, mergeUser, user?.id]);

  useEffect(() => {
    let cancelled = false;
    let pollId = null;
    let tries = 0;
    const maxTries = 14;

    const startWithSteps = (steps) => {
      if (cancelled || steps.length === 0) return;

      const d = driver({
        showProgress: true,
        progressText: t("onboarding.progressText"),
        animate: true,
        smoothScroll: false,
        allowClose: true,
        overlayOpacity: 0.58,
        overlayColor: "#0a0a0f",
        stagePadding: 10,
        stageRadius: 12,
        popoverClass: "onboarding-driver-popover",
        popoverOffset: 14,
        nextBtnText: t("common.next"),
        prevBtnText: t("common.back"),
        doneBtnText: t("onboarding.finish"),
        steps,
        onHighlighted: () => {
          requestAnimationFrame(() => driverObjRef.current?.refresh());
        },
        /* driver.js hooks get { config, state } — there is no `driver` on opts; use closure `d`. */
        onNextClick: () => {
          if (d.isLastStep()) {
            completedRef.current = true;
            void finalize();
            d.destroy();
            return;
          }
          d.moveNext();
        },
        onPrevClick: () => {
          d.movePrevious();
        },
        onCloseClick: () => {
          completedRef.current = false;
          d.destroy();
        },
      });

      driverObjRef.current = d;
      d.drive();
    };

    const poll = () => {
      if (cancelled) return;
      const steps = buildChatTourSteps(t);
      if (steps.length > 0) {
        startWithSteps(steps);
        return;
      }
      tries += 1;
      if (tries < maxTries) {
        pollId = window.setTimeout(poll, 220);
      }
    };

    pollId = window.setTimeout(poll, 320);

    return () => {
      cancelled = true;
      window.clearTimeout(pollId);
      completedRef.current = false;
      driverObjRef.current?.destroy();
      driverObjRef.current = null;
    };
  }, [t, finalize]);

  return null;
}
