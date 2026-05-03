import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { useAuth } from "../context/AuthContext";
import { TELEGRAM_SUPPORT_URL } from "../config";
import "../styles/subscription.css";

/** Premium ML / plan badge — `subscription_plan` only (same as chat picker). */
function userAllowsPremiumModels(user) {
  if (!user) return false;
  const p = String(user.subscription_plan ?? "free").toLowerCase();
  return p === "paid" || p === "pro" || p === "subscriber";
}

function PlanCard({
  name,
  priceLine,
  tagline,
  features,
  footnote,
  highlighted,
  badgeText,
  ctaLabel,
  onCta,
  gradientCta,
  isCurrentPlan,
}) {
  const inner = (
    <div
      className={`subscription-card__inner ${highlighted ? "subscription-card__inner--pro" : ""}${isCurrentPlan ? " subscription-card__inner--current" : ""}`}
    >
      <div className="subscription-card__header">
        <div>
          <h2 className="subscription-card__name">{name}</h2>
          <p className={`subscription-card__price ${highlighted ? "subscription-card__price--accent" : ""}`}>
            {priceLine}
          </p>
          {tagline ? <p className="subscription-card__tagline">{tagline}</p> : null}
        </div>
        {badgeText ? (
          <span className={`subscription-card__badge${isCurrentPlan ? " subscription-card__badge--active" : ""}`}>{badgeText}</span>
        ) : null}
      </div>
      <ul className="subscription-card__features">
        {features.map((f) => (
          <li key={f}>
            <span className="subscription-card__check" aria-hidden>
              ✓
            </span>
            {f}
          </li>
        ))}
      </ul>
      {footnote ? <p className="subscription-card__footnote">{footnote}</p> : null}
      {isCurrentPlan ? (
        <button type="button" className="subscription-btn subscription-btn--current-plan" onClick={onCta}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden>
            <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span>{ctaLabel}</span>
        </button>
      ) : gradientCta ? (
        <button type="button" className="subscription-btn subscription-btn--gradient" onClick={onCta}>
          <span>{ctaLabel}</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </button>
      ) : (
        <button type="button" className="subscription-btn subscription-btn--outline" onClick={onCta}>
          {ctaLabel}
        </button>
      )}
    </div>
  );

  const articleClass = ["subscription-card"];
  if (highlighted) articleClass.push("subscription-card--highlight");
  if (isCurrentPlan) articleClass.push("subscription-card--is-current");

  return <article className={articleClass.join(" ")}>{inner}</article>;
}

/** Opens full-page /login (no overlay modal). */
function goRegister(navigate) {
  navigate("/login", { state: { preferRegister: true } });
}

export default function SubscriptionPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user, isAuthenticated, isAdmin } = useAuth();

  const accountPlanLabel =
    user && userAllowsPremiumModels(user)
      ? t("subscription.planPremium")
      : t("subscription.planFree");

  const openAuth = () => {
    if (isAuthenticated) {
      toast.success(t("subscription.starterActive"));
      setTimeout(() => navigate(isAdmin ? "/admin" : "/user"), 1500);
      return;
    }
    goRegister(navigate);
  };

  const goCheckout = (plan) => {
    const path = `/subscriptions/payment?plan=${plan}`;
    if (!isAuthenticated) {
      navigate("/login", { state: { from: path } });
      return;
    }
    navigate(path);
  };

  const proClick = () => goCheckout("pro");

  const enterpriseClick = () => {
    if (TELEGRAM_SUPPORT_URL) {
      window.open(TELEGRAM_SUPPORT_URL, "_blank", "noopener,noreferrer");
      return;
    }
    toast.message(t("subscription.telegramSupportMissing"));
  };

  const goBackFromSubscriptions = () => {
    if (isAuthenticated) {
      navigate(isAdmin ? "/admin" : "/user");
      return;
    }
    navigate("/");
  };

  const hasPremiumPlan = Boolean(isAuthenticated && user && userAllowsPremiumModels(user));

  const goToAppFromPricing = () => {
    navigate(isAdmin ? "/admin" : "/user");
  };

  return (
    <div className="subscription-page">
      <div className="subscription-page__glow" aria-hidden />

      <header className="subscription-page__top">
        <div className="subscription-page__top-row">
          <button
            type="button"
            className="subscription-page__back"
            onClick={goBackFromSubscriptions}
            aria-label={t("subscription.back")}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            {t("subscription.back")}
          </button>
          {isAuthenticated && user ? (
            <div
              className="subscription-account-meta"
              title={`${user.email} — ${accountPlanLabel}`}
              aria-label={`${t("subscription.signedInAs")} ${user.email}. ${t("subscription.currentPlan")} ${accountPlanLabel}`}
            >
              <span className="subscription-account-meta__email">{user.email}</span>
              <span className="subscription-account-meta__sep" aria-hidden="true">
                ·
              </span>
              <span
                className={`subscription-account-meta__plan${userAllowsPremiumModels(user) ? " subscription-account-meta__plan--premium" : ""}`}
              >
                {accountPlanLabel}
              </span>
            </div>
          ) : null}
        </div>
      </header>

      <main className="subscription-page__main">
        <h1 className="subscription-page__hero">{t("subscription.heroHeadline")}</h1>
        <p className="subscription-page__title">{t("subscription.plansTitle")}</p>
        <p className="subscription-page__subtitle">{t("subscription.plansSubtitle")}</p>

        <div className="subscription-page__grid">
          <PlanCard
            name={t("subscription.starter")}
            priceLine={t("subscription.priceFree")}
            tagline={t("subscription.starterTagline")}
            features={[
              t("subscription.featFree1"),
              t("subscription.featFree2"),
              t("subscription.featFree3"),
              t("subscription.featFree4"),
              t("subscription.featFree5"),
              t("subscription.featFree6"),
            ]}
            footnote={t("subscription.starterFootnote")}
            highlighted={false}
            ctaLabel={t("subscription.ctaFree")}
            onCta={openAuth}
            gradientCta={false}
          />
          <PlanCard
            name={t("subscription.pro")}
            priceLine={t("subscription.pricePro")}
            tagline={hasPremiumPlan ? t("subscription.proActiveTagline") : t("subscription.proTagline")}
            features={[
              t("subscription.featPro1"),
              t("subscription.featPro2"),
              t("subscription.featPro3"),
              t("subscription.featPro4"),
              t("subscription.featPro5"),
              t("subscription.featPro6"),
            ]}
            footnote={hasPremiumPlan ? t("subscription.proActiveFootnote") : t("subscription.proFootnote")}
            highlighted
            isCurrentPlan={hasPremiumPlan}
            badgeText={hasPremiumPlan ? t("subscription.activeBadge") : t("subscription.recommended")}
            ctaLabel={hasPremiumPlan ? t("subscription.currentPlanButton") : t("subscription.ctaPro")}
            onCta={hasPremiumPlan ? goToAppFromPricing : proClick}
            gradientCta={!hasPremiumPlan}
          />
          <PlanCard
            name={t("subscription.enterprise")}
            priceLine={t("subscription.priceEnterprise")}
            tagline={t("subscription.enterpriseTagline")}
            features={[
              t("subscription.featEnt1"),
              t("subscription.featEnt2"),
              t("subscription.featEnt3"),
              t("subscription.featEnt4"),
              t("subscription.featEnt5"),
              t("subscription.featEnt6"),
            ]}
            footnote={t("subscription.enterpriseFootnote")}
            highlighted={false}
            ctaLabel={t("subscription.ctaEnterprise")}
            onCta={enterpriseClick}
            gradientCta={false}
          />
        </div>

        <p className="subscription-page__compare-note">{t("subscription.compareNote")}</p>
      </main>
    </div>
  );
}
