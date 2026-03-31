/**
 * Structured Response Block Components
 * Renders different types of assistant response blocks
 */

import { useState } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Cell
} from "recharts";
import "./ResponseBlocks.css";

// =============================================================================
// ICONS
// =============================================================================

const Icons = {
  alertTriangle: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  trendingUp: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
    </svg>
  ),
  trendingDown: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>
    </svg>
  ),
  info: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
    </svg>
  ),
  checkCircle: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
    </svg>
  ),
  arrowRight: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
    </svg>
  )
};

// =============================================================================
// METRICS BLOCK
// =============================================================================

export function MetricsBlock({ title, metrics }) {
  return (
    <div className="response-block metrics-block">
      {title && <h4 className="block-title">{title}</h4>}
      <div className="metrics-grid">
        {metrics.map((metric, idx) => (
          <div key={idx} className="metric-card">
            <span className="metric-label">{metric.label}</span>
            <div className="metric-value-row">
              <span className="metric-value">
                {metric.value}
                {metric.unit && <span className="metric-unit">{metric.unit}</span>}
              </span>
              {metric.change !== undefined && (
                <span className={`metric-change ${metric.change_direction || (metric.change >= 0 ? 'up' : 'down')}`}>
                  {metric.change_direction === 'up' || metric.change >= 0 ? '↑' : '↓'}
                  {Math.abs(metric.change)}%
                </span>
              )}
            </div>
            {metric.is_good !== undefined && (
              <span className={`metric-status ${metric.is_good ? 'good' : 'bad'}`}>
                {metric.is_good ? Icons.checkCircle : Icons.alertTriangle}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// RANKED LIST BLOCK
// =============================================================================

export function RankedListBlock({ title, items, onItemClick }) {
  return (
    <div className="response-block ranked-list-block">
      {title && <h4 className="block-title">{title}</h4>}
      <div className="ranked-list">
        {items.map((item, idx) => (
          <div
            key={idx}
            className={`ranked-item ${item.risk_level || ''}`}
            onClick={() => onItemClick?.(item)}
          >
            <span className="rank-badge">#{item.rank}</span>
            <div className="ranked-item-info">
              <span className="ranked-item-name">{item.name}</span>
              {item.product_id && (
                <span className="ranked-item-id">{item.product_id}</span>
              )}
            </div>
            <div className="ranked-item-value">
              <span className="value">{item.value}</span>
              <span className="metric-label">{item.metric_label}</span>
            </div>
            {item.trend && (
              <span className={`trend-indicator ${item.trend}`}>
                {item.trend === 'rising' ? Icons.trendingUp :
                 item.trend === 'falling' ? Icons.trendingDown : '→'}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// COMPARISON BLOCK
// =============================================================================

export function ComparisonBlock({ title, data }) {
  const { product_a, product_b, rows } = data;

  return (
    <div className="response-block comparison-block">
      {title && <h4 className="block-title">{title}</h4>}

      {/* Header */}
      <div className="comparison-header">
        <div className="comparison-product product-a">
          <span className="product-label">A</span>
          <span className="product-id">{product_a?.id || 'Product A'}</span>
        </div>
        <div className="comparison-vs">VS</div>
        <div className="comparison-product product-b">
          <span className="product-label">B</span>
          <span className="product-id">{product_b?.id || 'Product B'}</span>
        </div>
      </div>

      {/* Comparison Rows */}
      <div className="comparison-table">
        {rows?.map((row, idx) => (
          <div key={idx} className="comparison-row">
            <div className={`comparison-cell value-a ${row.winner === 'a' ? 'winner' : ''}`}>
              {row.value_a}
            </div>
            <div className="comparison-cell dimension">
              {row.dimension}
            </div>
            <div className={`comparison-cell value-b ${row.winner === 'b' ? 'winner' : ''}`}>
              {row.value_b}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// EXPLANATION BLOCK
// =============================================================================

export function ExplanationBlock({ title, content }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="response-block explanation-block">
      {title && <h4 className="block-title">{title}</h4>}

      <p className="explanation-summary">{content.summary}</p>

      {content.top_drivers && content.top_drivers.length > 0 && (
        <div className="drivers-section">
          <h5 className="drivers-title">Key Factors</h5>
          <div className="drivers-list">
            {content.top_drivers.map((driver, idx) => (
              <div key={idx} className={`driver-item impact-${driver.impact}`}>
                <span className={`driver-direction ${driver.direction}`}>
                  {driver.direction === 'increases' ? '↑' :
                   driver.direction === 'decreases' ? '↓' : '→'}
                </span>
                <div className="driver-info">
                  <span className="driver-factor">{driver.factor}</span>
                  <span className="driver-explanation">{driver.explanation}</span>
                </div>
                <span className={`driver-impact ${driver.impact}`}>{driver.impact}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {(content.seasonal_effect || content.trend_effect || content.promotion_effect) && (
        <button
          className="expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Show less' : 'Show more details'}
        </button>
      )}

      {expanded && (
        <div className="additional-factors">
          {content.seasonal_effect && (
            <div className="factor-item">
              <span className="factor-label">Seasonal:</span>
              <span>{content.seasonal_effect}</span>
            </div>
          )}
          {content.trend_effect && (
            <div className="factor-item">
              <span className="factor-label">Trend:</span>
              <span>{content.trend_effect}</span>
            </div>
          )}
          {content.promotion_effect && (
            <div className="factor-item">
              <span className="factor-label">Promotion:</span>
              <span>{content.promotion_effect}</span>
            </div>
          )}
          {content.region_effect && (
            <div className="factor-item">
              <span className="factor-label">Region:</span>
              <span>{content.region_effect}</span>
            </div>
          )}
        </div>
      )}

      {content.confidence_reasoning && (
        <div className="confidence-note">
          {Icons.info}
          <span>{content.confidence_reasoning}</span>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// ALERT BLOCK
// =============================================================================

export function AlertBlock({ title, alerts, onAlertAction }) {
  const severityOrder = { critical: 0, warning: 1, info: 2 };
  const sortedAlerts = [...alerts].sort((a, b) =>
    severityOrder[a.severity] - severityOrder[b.severity]
  );

  return (
    <div className="response-block alert-block">
      {title && <h4 className="block-title">{title}</h4>}
      <div className="alerts-list">
        {sortedAlerts.map((alert, idx) => (
          <div key={idx} className={`alert-item severity-${alert.severity}`}>
            <div className="alert-icon">
              {alert.severity === 'critical' ? Icons.alertTriangle : Icons.info}
            </div>
            <div className="alert-content">
              <div className="alert-header">
                <span className="alert-title">{alert.title}</span>
                <span className={`alert-badge ${alert.severity}`}>
                  {alert.severity}
                </span>
              </div>
              <p className="alert-message">{alert.message}</p>
              {alert.recommended_action && (
                <button
                  className="alert-action-btn"
                  onClick={() => onAlertAction?.(alert)}
                >
                  {alert.recommended_action}
                  {Icons.arrowRight}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// CHART BLOCK
// =============================================================================

export function ChartBlock({ chartData }) {
  const { chart_type, title, data, x_key, y_keys, colors } = chartData;

  const defaultColors = {
    history: '#60a5fa',
    forecast: '#34d399',
    value: '#8b5cf6'
  };

  const getColor = (key) => colors?.[key] || defaultColors[key] || '#6366f1';

  if (chart_type === 'line') {
    return (
      <div className="response-block chart-block">
        {title && <h4 className="block-title">{title}</h4>}
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={data} margin={{ top: 10, right: 10, bottom: 5, left: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey={x_key} tick={{ fontSize: 11, fill: '#6b7280' }} />
              <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} width={45} />
              <Tooltip
                contentStyle={{
                  background: '#1e1e2e',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  fontSize: 12
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              {y_keys.map((key) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={getColor(key)}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  strokeDasharray={key === 'forecast' ? '5 5' : undefined}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  if (chart_type === 'bar' || chart_type === 'comparison') {
    return (
      <div className="response-block chart-block">
        {title && <h4 className="block-title">{title}</h4>}
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data} margin={{ top: 10, right: 10, bottom: 5, left: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey={x_key} tick={{ fontSize: 11, fill: '#6b7280' }} />
              <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} width={45} />
              <Tooltip
                contentStyle={{
                  background: '#1e1e2e',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  fontSize: 12
                }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              {y_keys.map((key, idx) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={getColor(key) || ['#6366f1', '#8b5cf6', '#a855f7'][idx % 3]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return null;
}

// =============================================================================
// SUGGESTED ACTIONS
// =============================================================================

export function SuggestedActions({ actions, onActionClick }) {
  if (!actions || actions.length === 0) return null;

  const categoryColors = {
    explore: 'blue',
    compare: 'purple',
    forecast: 'green',
    alert: 'red',
    insight: 'amber'
  };

  return (
    <div className="suggested-actions">
      <span className="actions-label">Next steps:</span>
      <div className="actions-chips">
        {actions.map((action, idx) => (
          <button
            key={idx}
            className={`action-chip ${categoryColors[action.category] || 'blue'}`}
            onClick={() => onActionClick?.(action.query)}
          >
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// CONFIDENCE BADGE
// =============================================================================

export function ConfidenceBadge({ level, showLabel = true }) {
  const config = {
    high: { color: 'green', label: 'High Confidence' },
    medium: { color: 'amber', label: 'Medium Confidence' },
    low: { color: 'red', label: 'Low Confidence' }
  };

  const { color, label } = config[level] || config.medium;

  return (
    <span className={`confidence-badge ${color}`}>
      <span className="confidence-dot" />
      {showLabel && <span className="confidence-label">{label}</span>}
    </span>
  );
}

// =============================================================================
// MAIN RESPONSE RENDERER
// =============================================================================

export function ResponseBlockRenderer({ blocks, chartData, alerts, suggestedActions, onActionClick }) {
  // Sort blocks by priority
  const sortedBlocks = [...blocks].sort((a, b) => a.priority - b.priority);

  return (
    <div className="response-blocks">
      {sortedBlocks.map((block, idx) => {
        switch (block.type) {
          case 'metrics':
            return <MetricsBlock key={idx} title={block.title} metrics={block.content} />;
          case 'ranked_list':
            return <RankedListBlock key={idx} title={block.title} items={block.content} onItemClick={(item) => onActionClick?.(`Show details for ${item.product_id}`)} />;
          case 'comparison':
            return <ComparisonBlock key={idx} title={block.title} data={block.content} />;
          case 'explanation':
            return <ExplanationBlock key={idx} title={block.title} content={block.content} />;
          case 'alert':
            return <AlertBlock key={idx} title={block.title} alerts={block.content} onAlertAction={(alert) => onActionClick?.(alert.recommended_action)} />;
          case 'summary':
            return (
              <div key={idx} className="response-block summary-block">
                <p>{block.content}</p>
              </div>
            );
          default:
            return null;
        }
      })}

      {chartData && <ChartBlock chartData={chartData} />}

      {alerts && alerts.length > 0 && !blocks.some(b => b.type === 'alert') && (
        <AlertBlock alerts={alerts} onAlertAction={(alert) => onActionClick?.(alert.recommended_action)} />
      )}

      {suggestedActions && suggestedActions.length > 0 && (
        <SuggestedActions actions={suggestedActions} onActionClick={onActionClick} />
      )}
    </div>
  );
}

export default ResponseBlockRenderer;
