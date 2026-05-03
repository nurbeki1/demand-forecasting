import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { getToken } from "../utils/authStorage";
import { API_URL } from "../config";
import "../styles/subscription.css";

function userAllowsPremiumModels(user) {
  if (!user) return false;
  const p = String(user.subscription_plan ?? "free").toLowerCase();
  return p === "paid" || p === "pro" || p === "subscriber";
}

function digitsOnly(s) {
  return String(s).replace(/\D/g, "");
}

/** Most cards (Visa/MC) are 16 digits; extra digits are not accepted in this demo field. */
const CARD_DIGITS_MAX = 16;

function formatCardGroups(digits) {
  const d = digits.slice(0, CARD_DIGITS_MAX);
  const parts = [];
  for (let i = 0; i < d.length; i += 4) {
    parts.push(d.slice(i, i + 4));
  }
  return parts.join(" ");
}

/** Uppercase like on physical cards; letters + space/hyphen/apostrophe only. */
function sanitizeCardholderName(raw, maxLen = 26) {
  return raw.toUpperCase().replace(/[^\p{L}\s'-]/gu, "").slice(0, maxLen);
}

function formatExpiryMmYy(raw) {
  const d = digitsOnly(raw).slice(0, 4);
  if (d.length <= 2) return d;
  return `${d.slice(0, 2)}/${d.slice(2)}`;
}

function validateExpiry(mmYy) {
  const d = digitsOnly(mmYy);
  if (d.length !== 4) return false;
  const mm = Number(d.slice(0, 2));
  return mm >= 1 && mm <= 12;
}

const CVV_DIGITS_MAX = 4;

const REDIRECT_SECONDS = 10;

export default function SubscriptionPaymentPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { user, isAdmin, isAuthenticated, refreshUser } = useAuth();

  const planParam = (params.get("plan") || "pro").toLowerCase();
  const plan = planParam === "enterprise" ? "enterprise" : "pro";

  const planTitle = plan === "enterprise" ? t("payment.planEnterprise") : t("payment.planPro");

  const [nameOnCard, setNameOnCard] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [expiry, setExpiry] = useState("");
  const [cvv, setCvv] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [paid, setPaid] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(REDIRECT_SECONDS);

  const alreadyPremium = user && userAllowsPremiumModels(user);

  const formValid = useMemo(() => {
    const num = digitsOnly(cardNumber);
    const cv = digitsOnly(cvv);
    return (
      nameOnCard.trim().length >= 2 &&
      num.length === 16 &&
      validateExpiry(expiry) &&
      cv.length >= 3 &&
      cv.length <= 4
    );
  }, [nameOnCard, cardNumber, expiry, cvv]);

  useEffect(() => {
    if (!paid) return undefined;
    const id = setInterval(() => {
      setSecondsLeft((s) => (s <= 1 ? 0 : s - 1));
    }, 1000);
    return () => clearInterval(id);
  }, [paid]);

  useEffect(() => {
    if (!paid || secondsLeft > 0) return;
    navigate(isAdmin ? "/admin" : "/user", { replace: true });
  }, [paid, secondsLeft, navigate, isAdmin]);

  const handlePay = async (e) => {
    e.preventDefault();
    setError("");
    if (!formValid) {
      setError(t("payment.invalidCard"));
      return;
    }
    const token = getToken();
    if (!token) {
      navigate("/login", { state: { from: `/subscriptions/payment?plan=${plan}` } });
      return;
    }
    setSubmitting(true);
    try {
      const opts = {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ plan }),
      };
      let res = await fetch(`${API_URL}/subscription/mock-checkout`, opts);
      if (res.status === 404) {
        res = await fetch(`${API_URL}/auth/mock-subscribe`, opts);
      }
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error(t("payment.notFoundHint"));
        }
        let msg = t("payment.error");
        const det = data.detail;
        if (typeof det === "string") msg = det;
        else if (Array.isArray(det) && det.length) {
          msg = det.map((x) => x.msg || JSON.stringify(x)).join("; ");
        }
        throw new Error(msg);
      }
      await refreshUser();
      setSecondsLeft(REDIRECT_SECONDS);
      setPaid(true);
    } catch (err) {
      setError(err.message || t("payment.error"));
    } finally {
      setSubmitting(false);
    }
  };

  const goBackFromPayment = () => {
    if (isAuthenticated) {
      navigate(isAdmin ? "/admin" : "/user");
      return;
    }
    navigate("/");
  };

  return (
    <div className="subscription-page subscription-pay-page">
      <div className="subscription-page__glow" aria-hidden />

      <header className="subscription-page__top">
        <div className="subscription-page__top-row">
          <button
            type="button"
            className="subscription-page__back"
            onClick={goBackFromPayment}
            aria-label={t("payment.back")}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            {t("payment.back")}
          </button>
        </div>
      </header>

      <main className="subscription-page__main subscription-pay-page__main">
        <h1 className="subscription-page__hero">{t("payment.title")}</h1>
        <p className="subscription-page__subtitle subscription-pay-page__subtitle">{t("payment.subtitleDemo")}</p>

        <div className="subscription-pay-panel">
          <div className="subscription-pay-panel__plan">
            <span className="subscription-pay-panel__plan-label">{t("payment.selectedPlan")}</span>
            <span className="subscription-pay-panel__plan-value">{planTitle}</span>
          </div>

          {alreadyPremium && !paid ? (
            <p className="subscription-pay-panel__notice">{t("payment.alreadyPremium")}</p>
          ) : null}

          {paid ? (
            <div className="subscription-pay-success">
              <h2 className="subscription-pay-success__title">{t("payment.successTitle")}</h2>
              <p className="subscription-pay-success__body">{t("payment.successBody")}</p>
              <p className="subscription-pay-success__timer">
                {t("payment.redirecting", { seconds: secondsLeft })}
              </p>
            </div>
          ) : (
            <form className="subscription-pay-form" onSubmit={handlePay} noValidate>
              {error ? <div className="subscription-pay-form__error">{error}</div> : null}

              <label className="subscription-pay-field">
                <span>{t("payment.cardholder")}</span>
                <input
                  type="text"
                  name="cc-name"
                  autoComplete="cc-name"
                  value={nameOnCard}
                  onChange={(e) => setNameOnCard(sanitizeCardholderName(e.target.value))}
                  disabled={submitting}
                  placeholder="JANE DOE"
                  maxLength={26}
                  spellCheck={false}
                />
              </label>

              <label className="subscription-pay-field">
                <span>{t("payment.cardNumber")}</span>
                <input
                  type="text"
                  inputMode="numeric"
                  autoComplete="cc-number"
                  value={cardNumber}
                  onChange={(e) => {
                    const d = digitsOnly(e.target.value).slice(0, CARD_DIGITS_MAX);
                    setCardNumber(formatCardGroups(d));
                  }}
                  disabled={submitting}
                  placeholder="4242 4242 4242 4242"
                  maxLength={CARD_DIGITS_MAX + Math.floor((CARD_DIGITS_MAX - 1) / 4)}
                />
              </label>

              <div className="subscription-pay-field-row">
                <label className="subscription-pay-field">
                  <span>{t("payment.expiry")}</span>
                  <input
                    type="text"
                    inputMode="numeric"
                    autoComplete="cc-exp"
                    value={expiry}
                    onChange={(e) => setExpiry(formatExpiryMmYy(e.target.value))}
                    disabled={submitting}
                    placeholder="12/28"
                    maxLength={5}
                  />
                </label>
                <label className="subscription-pay-field">
                  <span>{t("payment.cvv")}</span>
                  <input
                    type="password"
                    inputMode="numeric"
                    autoComplete="cc-csc"
                    value={cvv}
                    onChange={(e) => setCvv(digitsOnly(e.target.value).slice(0, CVV_DIGITS_MAX))}
                    disabled={submitting}
                    placeholder="123"
                    maxLength={CVV_DIGITS_MAX}
                  />
                </label>
              </div>

              <button type="submit" className="subscription-btn subscription-btn--gradient" disabled={submitting}>
                {submitting ? t("payment.processing") : t("payment.pay")}
              </button>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}
