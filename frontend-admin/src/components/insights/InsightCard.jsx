import { useState } from "react";
import "./InsightCard.css";
import AlertBanner from "./AlertBanner";

const RISK_COLORS = {
  low: "#4ade80",
  medium: "#fbbf24",
  high: "#ef4444",
};

const CONFIDENCE_COLORS = {
  low: "#ef4444",
  medium: "#fbbf24",
  high: "#4ade80",
};

const STATUS_COLORS = {
  good: "#4ade80",
  warning: "#fbbf24",
  critical: "#ef4444",
};

const SUGGESTION_ICONS = {
  calculator: "🧮",
  search: "🔍",
  shield: "🛡️",
  target: "🎯",
  "trending-up": "📈",
  "trending-down": "📉",
  "bar-chart": "📊",
  grid: "📋",
  calendar: "📅",
  "dollar-sign": "💰",
  "refresh-cw": "🔄",
  "shopping-cart": "🛒",
  "file-text": "📄",
  "git-compare": "⚖️",
  lightbulb: "💡",
};

export default function InsightCard({ data, onFollowUpClick, onSuggestionClick }) {
  const [trustExpanded, setTrustExpanded] = useState(false);

  if (!data) return null;

  const {
    insights,
    trust,
    alert_level,
    total_predicted_demand,
    avg_daily_demand,
    alerts = [],
    suggestions = [],
    has_critical_alert,
  } = data;

  return (
    <div className="insight-card">
      {/* Alert Banner for Critical/High Alerts */}
      {alerts.length > 0 && (
        <AlertBanner
          alerts={alerts}
          onAlertClick={(alert) => onSuggestionClick?.(alert.action)}
        />
      )}

      {/* Demand Highlight */}
      <div className="demand-highlight">
        <div className="demand-value">{Math.round(total_predicted_demand)}</div>
        <div className="demand-label">Total Predicted Demand</div>
        <div className="demand-avg">{avg_daily_demand.toFixed(1)} units/day avg</div>
      </div>

      {/* Summary Section */}
      <div className="insight-section summary-section">
        <h3 className="section-headline">{insights.summary.headline}</h3>
        <p className="section-detail">{insights.summary.detail}</p>
        <div className="metric-chip">{insights.summary.metric_highlight}</div>
      </div>

      {/* Risk Badge */}
      <div className="risk-section">
        <div
          className="risk-badge"
          style={{ backgroundColor: RISK_COLORS[insights.risk.level] }}
        >
          <span className="risk-level">{insights.risk.level.toUpperCase()} RISK</span>
          <span className="risk-score">{(insights.risk.score * 100).toFixed(0)}%</span>
        </div>
        {insights.risk.risk_factors.length > 0 && (
          <div className="risk-factors">
            {insights.risk.risk_factors.map((factor, idx) => (
              <div
                key={idx}
                className="risk-factor"
                style={{ borderLeftColor: RISK_COLORS[factor.severity] }}
              >
                <span className="factor-name">{factor.factor}</span>
                <span className="factor-desc">{factor.description}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Why Section */}
      <div className="insight-section why-section">
        <h4 className="section-title">Why This Forecast?</h4>
        <div className="primary-driver">
          <span className="driver-label">Primary Driver:</span>
          <span className="driver-value">{insights.why_it_happened.primary_driver}</span>
        </div>
        <p className="driver-explanation">{insights.why_it_happened.primary_explanation}</p>

        {insights.why_it_happened.secondary_drivers.length > 0 && (
          <div className="secondary-drivers">
            {insights.why_it_happened.secondary_drivers.map((driver, idx) => (
              <div key={idx} className="secondary-driver">
                <span
                  className={`impact-indicator ${driver.impact}`}
                >
                  {driver.impact === "positive" ? "+" : driver.impact === "negative" ? "-" : "~"}
                </span>
                <span className="driver-name">{driver.driver}</span>
                <span className="driver-expl">{driver.explanation}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions Section */}
      <div className="insight-section actions-section">
        <h4 className="section-title">Recommended Actions</h4>
        <div className="action-list">
          {insights.what_to_do.map((action, idx) => (
            <div key={idx} className="action-item">
              <div className="action-priority">P{action.priority}</div>
              <div className="action-content">
                <div className="action-text">{action.action}</div>
                <div className="action-reason">{action.reason}</div>
                {action.deadline && (
                  <div className="action-deadline">Deadline: {action.deadline}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trust Block */}
      <div className="trust-section">
        <div
          className="trust-header"
          onClick={() => setTrustExpanded(!trustExpanded)}
        >
          <div className="trust-summary">
            <div
              className="confidence-badge"
              style={{ backgroundColor: CONFIDENCE_COLORS[trust.confidence] }}
            >
              {trust.confidence.toUpperCase()} CONFIDENCE
            </div>
            <span className="confidence-score">{(trust.confidence_score * 100).toFixed(0)}%</span>
          </div>
          <span className="expand-icon">{trustExpanded ? "−" : "+"}</span>
        </div>

        {trustExpanded && (
          <div className="trust-details">
            <p className="trust-explanation">{trust.confidence_explanation}</p>

            <div className="trust-meta">
              <div className="meta-item">
                <span className="meta-label">Data freshness:</span>
                <span className="meta-value">{trust.data_freshness}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Model updated:</span>
                <span className="meta-value">{trust.model_updated}</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Sample size:</span>
                <span className="meta-value">{trust.sample_size} data points</span>
              </div>
              <div className="meta-item">
                <span className="meta-label">Demand stability:</span>
                <span className="meta-value">{trust.variance_stability}</span>
              </div>
            </div>

            <div className="trust-factors">
              <h5>Based On:</h5>
              {trust.based_on.map((factor, idx) => (
                <div key={idx} className="trust-factor">
                  <div className="factor-header">
                    <span
                      className="factor-status"
                      style={{ backgroundColor: STATUS_COLORS[factor.status] }}
                    />
                    <span className="factor-name">{factor.name}</span>
                  </div>
                  <div className="factor-value">{factor.value}</div>
                  <div className="factor-bar">
                    <div
                      className="factor-fill"
                      style={{
                        width: `${(factor.score || 0) * 100}%`,
                        backgroundColor: STATUS_COLORS[factor.status],
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {trust.warnings.length > 0 && (
              <div className="trust-warnings">
                <h5>Warnings:</h5>
                {trust.warnings.map((warning, idx) => (
                  <div key={idx} className="warning-item">
                    <span className="warning-icon">!</span>
                    <span>{warning}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI Suggestions - ChatGPT style */}
      {suggestions.length > 0 && (
        <div className="suggestions-section">
          <h4 className="section-title">Что дальше?</h4>
          <div className="suggestions-grid">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                className={`suggestion-card priority-${s.priority}`}
                onClick={() => onSuggestionClick?.(s.prompt)}
              >
                <span className="suggestion-icon">
                  {SUGGESTION_ICONS[s.icon] || "💬"}
                </span>
                <span className="suggestion-text">{s.text}</span>
                {s.priority === "high" && (
                  <span className="suggestion-badge">Важно</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Follow-up Chips (legacy) */}
      {insights.follow_up_questions?.length > 0 && (
        <div className="followup-section">
          <h4 className="section-title">Дополнительно</h4>
          <div className="followup-chips">
            {insights.follow_up_questions.slice(0, 3).map((q, idx) => (
              <button
                key={idx}
                className={`followup-chip ${q.category}`}
                onClick={() => onFollowUpClick?.(q.question)}
              >
                {q.question}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
