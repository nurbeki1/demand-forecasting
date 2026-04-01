import "./AlertBanner.css";

const SEVERITY_CONFIG = {
  critical: {
    bg: "linear-gradient(90deg, #ef4444 0%, #dc2626 100%)",
    icon: "!",
    label: "КРИТИЧНО",
  },
  high: {
    bg: "linear-gradient(90deg, #f59e0b 0%, #d97706 100%)",
    icon: "!",
    label: "ВАЖНО",
  },
  medium: {
    bg: "linear-gradient(90deg, #3b82f6 0%, #2563eb 100%)",
    icon: "i",
    label: "ВНИМАНИЕ",
  },
  low: {
    bg: "linear-gradient(90deg, #6b7280 0%, #4b5563 100%)",
    icon: "i",
    label: "ИНФО",
  },
};

export default function AlertBanner({ alerts, onAlertClick }) {
  if (!alerts || alerts.length === 0) return null;

  // Show only critical and high alerts
  const importantAlerts = alerts.filter(
    (a) => a.severity === "critical" || a.severity === "high"
  );

  if (importantAlerts.length === 0) return null;

  // Show the most critical one
  const topAlert = importantAlerts[0];
  const config = SEVERITY_CONFIG[topAlert.severity] || SEVERITY_CONFIG.medium;

  return (
    <div
      className="alert-banner-container"
      style={{ background: config.bg }}
      onClick={() => onAlertClick?.(topAlert)}
    >
      <div className="alert-banner-content">
        <div className="alert-badge">
          <span className="alert-icon">{config.icon}</span>
          <span className="alert-label">{config.label}</span>
        </div>

        <div className="alert-text">
          <span className="alert-title">{topAlert.title}</span>
          <span className="alert-message">{topAlert.message}</span>
        </div>

        <div className="alert-action">
          <span className="action-text">{topAlert.action}</span>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </div>
      </div>

      {importantAlerts.length > 1 && (
        <div className="alert-more">
          +{importantAlerts.length - 1} еще
        </div>
      )}
    </div>
  );
}
