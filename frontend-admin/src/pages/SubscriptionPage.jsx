import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import { useAuth } from "../context/AuthContext";
import "../styles/subscription.css";

function PlanCard({
  name,
  priceLine,
  features,
  highlighted,
  badgeText,
  ctaLabel,
  onCta,
  gradientCta,
}) {
  const inner = (
    <div className={`subscription-card__inner ${highlighted ? "subscription-card__inner--pro" : ""}`}>
      <div className="subscription-card__header">
        <div>
          <h2 className="subscription-card__name">{name}</h2>
          <p className={`subscription-card__price ${highlighted ? "subscription-card__price--accent" : ""}`}>
            {priceLine}
          </p>
        </div>
        {badgeText ? (
          <span className="subscription-card__badge">{badgeText}</span>
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
      {gradientCta ? (
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

  if (!highlighted) return <article className="subscription-card">{inner}</article>;

  return (
    <article className="subscription-card subscription-card--highlight">{inner}</article>
  );
}

/** Opens full-page /login (no overlay modal). */
function goRegister(navigate) {
  navigate("/login", { state: { preferRegister: true } });
}

export default function SubscriptionPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { isAuthenticated, isAdmin } = useAuth();

  const openAuth = () => {
    if (isAuthenticated) {
      navigate(isAdmin ? "/admin" : "/user");
      return;
    }
    goRegister(navigate);
  };

  const proClick = () => {
    toast.message(t("subscription.billingSoon"));
    openAuth();
  };

  const enterpriseClick = () => {
    toast.message(t("subscription.billingSoon"));
    openAuth();
  };

  return (
    <div className="subscription-page">
      <div className="subscription-page__glow" aria-hidden />

      <header className="subscription-page__top">
        <button
          type="button"
          className="subscription-page__back"
          onClick={() => navigate(-1)}
          aria-label={t("subscription.back")}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          {t("subscription.back")}
        </button>
      </header>

      <main className="subscription-page__main">
        <h1 className="subscription-page__hero">{t("subscription.heroHeadline")}</h1>
        <p className="subscription-page__title">{t("subscription.plansTitle")}</p>
        <p className="subscription-page__subtitle">{t("subscription.plansSubtitle")}</p>

        <div className="subscription-page__grid">
          <PlanCard
            name={t("subscription.starter")}
            priceLine={t("subscription.priceFree")}
            features={[t("subscription.featFree1"), t("subscription.featFree2"), t("subscription.featFree3")]}
            highlighted={false}
            ctaLabel={t("subscription.ctaFree")}
            onCta={openAuth}
            gradientCta={false}
          />
          <PlanCard
            name={t("subscription.pro")}
            priceLine={t("subscription.pricePro")}
            features={[t("subscription.featPro1"), t("subscription.featPro2"), t("subscription.featPro3")]}
            highlighted
            badgeText={t("subscription.recommended")}
            ctaLabel={t("subscription.ctaPro")}
            onCta={proClick}
            gradientCta
          />
          <PlanCard
            name={t("subscription.enterprise")}
            priceLine={t("subscription.priceEnterprise")}
            features={[t("subscription.featEnt1"), t("subscription.featEnt2"), t("subscription.featEnt3")]}
            highlighted={false}
            ctaLabel={t("subscription.ctaEnterprise")}
            onCta={enterpriseClick}
            gradientCta={false}
          />
        </div>
      </main>
    </div>
  );
}
