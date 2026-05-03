import { useCallback, useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { useTranslation } from "react-i18next";
import {
  Sparkles,
  LayoutDashboard,
  MessageSquare,
  Layers,
  UserCircle,
  Rocket,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { postOnboardingComplete } from "../../api/onboardingApi";
import { setOnboardingDoneLocally } from "../../utils/onboardingStorage";
import "./OnboardingModal.css";

export default function OnboardingModal() {
  const { t } = useTranslation();
  const { isAdmin, user, checkAuth, mergeUser } = useAuth();
  const [step, setStep] = useState(0);
  const [visible, setVisible] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const id = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(id);
  }, []);

  const steps = useMemo(() => {
    const homeTitle = isAdmin
      ? t("onboarding.steps.home.titleAdmin")
      : t("onboarding.steps.home.titleUser");
    const homeBody = isAdmin
      ? t("onboarding.steps.home.bodyAdmin")
      : t("onboarding.steps.home.bodyUser");
    const featuresTitle = isAdmin
      ? t("onboarding.steps.features.titleAdmin")
      : t("onboarding.steps.features.titleUser");
    const featuresBody = isAdmin
      ? t("onboarding.steps.features.bodyAdmin")
      : t("onboarding.steps.features.bodyUser");
    const settingsBody = isAdmin
      ? t("onboarding.steps.settings.bodyAdmin")
      : t("onboarding.steps.settings.bodyUser");

    return [
      {
        title: t("onboarding.steps.welcome.title"),
        description: t("onboarding.steps.welcome.body"),
        Icon: Sparkles,
      },
      {
        title: homeTitle,
        description: homeBody,
        Icon: isAdmin ? LayoutDashboard : MessageSquare,
      },
      {
        title: featuresTitle,
        description: featuresBody,
        Icon: Layers,
      },
      {
        title: t("onboarding.steps.settings.title"),
        description: settingsBody,
        Icon: UserCircle,
      },
      {
        title: t("onboarding.steps.done.title"),
        description: t("onboarding.steps.done.body"),
        Icon: Rocket,
      },
    ];
  }, [isAdmin, t]);

  const total = steps.length;
  const last = step === total - 1;
  const { title, description, Icon } = steps[step];

  const finalize = useCallback(async () => {
    if (!user?.id) return;
    try {
      const { ok } = await postOnboardingComplete();
      if (ok) {
        await checkAuth();
      } else {
        setOnboardingDoneLocally(user.id);
        mergeUser({ is_onboarding_completed: true });
      }
    } catch {
      setOnboardingDoneLocally(user.id);
      mergeUser({ is_onboarding_completed: true });
    }
  }, [checkAuth, mergeUser, user?.id]);

  const handleFinish = useCallback(async () => {
    if (busy) return;
    setBusy(true);
    try {
      await finalize();
    } finally {
      setBusy(false);
    }
  }, [busy, finalize]);

  const handleNext = useCallback(() => {
    if (last) return;
    setStep((s) => Math.min(s + 1, total - 1));
  }, [last, total]);

  const handleBack = useCallback(() => {
    setStep((s) => Math.max(s - 1, 0));
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const node = (
    <div
      className={`onboarding-overlay ${visible ? "onboarding-overlay--visible" : ""}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
      aria-describedby="onboarding-desc"
    >
      <div className="onboarding-modal">
        <div className="onboarding-modal__accent" aria-hidden />
        <div className="onboarding-modal__body">
          <div className="onboarding-modal__icon" aria-hidden>
            <Icon size={28} strokeWidth={1.75} />
          </div>
          <h2 id="onboarding-title" className="onboarding-modal__title">
            {title}
          </h2>
          <p id="onboarding-desc" className="onboarding-modal__desc">
            {description}
          </p>
          <div className="onboarding-modal__dots" aria-hidden>
            {steps.map((_, i) => (
              <span
                key={i}
                className={`onboarding-modal__dot ${i === step ? "onboarding-modal__dot--active" : ""}`}
              />
            ))}
          </div>
        </div>
        <div
          className={`onboarding-modal__footer ${step > 0 ? "onboarding-modal__footer--spread" : "onboarding-modal__footer--end"}`}
        >
          {step > 0 ? (
            <button type="button" className="onboarding-btn onboarding-btn--ghost" onClick={handleBack}>
              {t("common.back")}
            </button>
          ) : null}
          {!last ? (
            <button type="button" className="onboarding-btn onboarding-btn--primary" onClick={handleNext}>
              {t("common.next")}
            </button>
          ) : (
            <button
              type="button"
              className="onboarding-btn onboarding-btn--primary"
              onClick={handleFinish}
              disabled={busy}
            >
              {busy ? t("common.loading") : t("onboarding.finish")}
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return createPortal(node, document.body);
}
