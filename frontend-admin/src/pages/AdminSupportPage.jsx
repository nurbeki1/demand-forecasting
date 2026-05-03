import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { TELEGRAM_SUPPORT_URL } from "../config";
import "../styles/dashboard.css";

export default function AdminSupportPage() {
  const { t } = useTranslation();

  const openTelegram = () => {
    if (TELEGRAM_SUPPORT_URL) {
      window.open(TELEGRAM_SUPPORT_URL, "_blank", "noopener,noreferrer");
      return;
    }
    toast.message(t("subscription.telegramSupportMissing"));
  };

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">{t("adminSupport.title")}</div>
              <div className="subtitle">{t("adminSupport.subtitle")}</div>
            </div>
          </div>

          <div className="panel" style={{ marginBottom: "var(--space-5)" }}>
            <div className="cardHeader">
              <div>
                <div className="cardTitle">{t("adminSupport.actionsTitle")}</div>
                <div className="cardSub">{t("adminSupport.actionsSub")}</div>
              </div>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "12px", padding: "4px 0 8px" }}>
              <button type="button" className="btnPrimary" onClick={openTelegram}>
                {t("adminSupport.openTelegram")}
              </button>
              <Link to="/subscriptions" className="btn" style={{ textDecoration: "none" }}>
                {t("adminSupport.openPricing")}
              </Link>
              <Link to="/admin" className="btn" style={{ textDecoration: "none" }}>
                {t("adminSupport.backDashboard")}
              </Link>
            </div>
          </div>

          <div className="card" style={{ marginBottom: "var(--space-5)" }}>
            <div className="cardHeader">
              <div className="cardTitle">{t("adminSupport.operatorTitle")}</div>
              <div className="cardSub">{t("adminSupport.operatorSub")}</div>
            </div>
            <ol
              style={{
                margin: "0 0 0 1.25rem",
                padding: "0 0 8px",
                color: "var(--text-secondary)",
                lineHeight: 1.6,
              }}
            >
              <li>{t("adminSupport.step1")}</li>
              <li>{t("adminSupport.step2")}</li>
              <li>{t("adminSupport.step3")}</li>
            </ol>
          </div>

          <div className="card">
            <div className="cardHeader">
              <div className="cardTitle">{t("adminSupport.envTitle")}</div>
              <div className="cardSub">{t("adminSupport.envSub")}</div>
            </div>
            <pre
              style={{
                margin: 0,
                padding: "12px 16px",
                background: "var(--bg-tertiary)",
                borderRadius: "var(--radius-md)",
                fontSize: "12px",
                color: "var(--text-secondary)",
                overflow: "auto",
                fontFamily: "var(--font-mono)",
              }}
            >
              {`VITE_TELEGRAM_SUPPORT_URL=https://t.me/YourBot\nTELEGRAM_BOT_TOKEN=… (backend)\nTELEGRAM_SUPPORT_GROUP_ID=-100… (backend)`}
            </pre>
            <p style={{ marginTop: "12px", fontSize: "13px", color: "var(--text-tertiary)" }}>
              {t("adminSupport.docsRepo")}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
