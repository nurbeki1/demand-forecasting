/**
 * Executive Dashboard Component
 * Forecast-focused metrics and AI insights
 */

import { useTranslation } from "react-i18next";
import "./ExecutiveDashboard.css";

// =============================================================================
// ICONS
// =============================================================================

const Icons = {
  package: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/>
      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
      <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
    </svg>
  ),
  alertTriangle: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  trendingUp: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
    </svg>
  ),
  target: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
    </svg>
  ),
  activity: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
    </svg>
  ),
  zap: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
    </svg>
  ),
  arrowRight: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
    </svg>
  ),
  refresh: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
    </svg>
  )
};

const iconMap = {
  package: Icons.package,
  "alert-triangle": Icons.alertTriangle,
  "trending-up": Icons.trendingUp,
  target: Icons.target,
  activity: Icons.activity,
  "package-x": Icons.alertTriangle,
  zap: Icons.zap
};

// =============================================================================
// METRIC CARD
// =============================================================================

function MetricCard({ metric }) {
  const icon = iconMap[metric.icon] || Icons.activity;

  return (
    <div className="metric-card">
      <div className="metric-card-header">
        <div className={`metric-icon ${metric.is_positive === false ? 'negative' : ''}`}>
          {icon}
        </div>
        {metric.change !== undefined && (
          <span className={`metric-change ${metric.trend || (metric.change >= 0 ? 'up' : 'down')}`}>
            {metric.change >= 0 ? '+' : ''}{metric.change}%
          </span>
        )}
      </div>
      <div className="metric-value">{metric.value}</div>
      <div className="metric-label">{metric.label}</div>
      {metric.change_period && (
        <div className="metric-period">{metric.change_period}</div>
      )}
    </div>
  );
}

// =============================================================================
// RISK PRODUCTS TABLE
// =============================================================================

function RiskProductsTable({ products, onProductClick, t }) {
  if (!products || products.length === 0) {
    return (
      <div className="dashboard-card">
        <div className="card-header">
          <h3>{t('dashboard.highRiskProducts')}</h3>
        </div>
        <div className="empty-state">
          <span>{t('dashboard.noHighRisk')}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-card">
      <div className="card-header">
        <h3>{t('dashboard.highRiskProducts')}</h3>
        <span className="card-badge critical">{products.length} items</span>
      </div>
      <div className="risk-table">
        {products.map((product, idx) => (
          <div
            key={idx}
            className={`risk-row severity-${product.risk_level}`}
            onClick={() => onProductClick?.(product)}
          >
            <div className="risk-product-info">
              <span className="risk-product-id">{product.product_id}</span>
              <span className="risk-product-name">{product.name}</span>
              <span className="risk-category">{product.category}</span>
            </div>
            <div className="risk-metrics">
              <div className="risk-metric">
                <span className="risk-metric-label">{t('dashboard.currentStock')}</span>
                <span className="risk-metric-value">{product.current_inventory}</span>
              </div>
              <div className="risk-metric">
                <span className="risk-metric-label">{t('dashboard.sevenDayDemand')}</span>
                <span className="risk-metric-value">{product.predicted_demand_7d}</span>
              </div>
              <div className="risk-metric">
                <span className="risk-metric-label">{t('dashboard.daysLeft')}</span>
                <span className={`risk-metric-value ${product.days_until_stockout < 5 ? 'critical' : ''}`}>
                  {product.days_until_stockout}
                </span>
              </div>
            </div>
            <div className="risk-action">
              <button className="action-btn">
                {product.recommended_action}
                {Icons.arrowRight}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// CATEGORY INSIGHTS
// =============================================================================

function CategoryInsights({ categories, t }) {
  return (
    <div className="dashboard-card">
      <div className="card-header">
        <h3>{t('dashboard.categoryPerformance')}</h3>
      </div>
      <div className="category-grid">
        {categories?.map((cat, idx) => (
          <div key={idx} className={`category-card trend-${cat.trend}`}>
            <div className="category-header">
              <span className="category-name">{cat.category}</span>
              <span className={`category-trend ${cat.trend}`}>
                {cat.trend === 'growing' ? '↑' : cat.trend === 'declining' ? '↓' : '→'}
                {Math.abs(cat.change_percent).toFixed(1)}%
              </span>
            </div>
            <div className="category-stats">
              <div className="category-stat">
                <span className="stat-value">{cat.total_products}</span>
                <span className="stat-label">{t('dashboard.products')}</span>
              </div>
              <div className="category-stat">
                <span className="stat-value">{cat.avg_demand.toFixed(0)}</span>
                <span className="stat-label">{t('dashboard.avgDemand')}</span>
              </div>
              <div className="category-stat">
                <span className="stat-value">{cat.alert_count}</span>
                <span className="stat-label">{t('alerts.title')}</span>
              </div>
            </div>
            <div className="category-top">
              Top: <strong>{cat.top_product}</strong>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// AI INSIGHTS
// =============================================================================

function AIInsightsPanel({ insights, onInsightClick, t }) {
  const categoryIcons = {
    trend: Icons.trendingUp,
    risk: Icons.alertTriangle,
    opportunity: Icons.zap,
    anomaly: Icons.activity
  };

  const categoryColors = {
    trend: 'blue',
    risk: 'red',
    opportunity: 'green',
    anomaly: 'amber'
  };

  return (
    <div className="dashboard-card ai-insights-card">
      <div className="card-header">
        <h3>{t('dashboard.aiInsights')}</h3>
        <span className="ai-badge">
          {Icons.zap}
          {t('dashboard.autoGenerated')}
        </span>
      </div>
      <div className="insights-list">
        {insights?.map((insight, idx) => (
          <div
            key={idx}
            className={`insight-item ${categoryColors[insight.category]}`}
            onClick={() => onInsightClick?.(insight)}
          >
            <div className="insight-icon">
              {categoryIcons[insight.category] || Icons.activity}
            </div>
            <div className="insight-content">
              <div className="insight-header">
                <span className="insight-title">{insight.title}</span>
                <span className={`insight-severity ${insight.severity}`}>
                  {insight.severity}
                </span>
              </div>
              <p className="insight-description">{insight.description}</p>
              {insight.affected_items && insight.affected_items.length > 0 && (
                <div className="insight-tags">
                  {insight.affected_items.slice(0, 3).map((item, i) => (
                    <span key={i} className="insight-tag">{item}</span>
                  ))}
                  {insight.affected_items.length > 3 && (
                    <span className="insight-tag more">+{insight.affected_items.length - 3}</span>
                  )}
                </div>
              )}
              {insight.action_query && (
                <button className="insight-action">
                  {t('dashboard.exploreThis')}
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
// ALERTS PANEL
// =============================================================================

function AlertsPanel({ alerts, t }) {
  if (!alerts || alerts.length === 0) {
    return null;
  }

  return (
    <div className="dashboard-card alerts-card">
      <div className="card-header">
        <h3>{t('dashboard.activeAlerts')}</h3>
        <span className="card-badge warning">{alerts.length} {t('common.active').toLowerCase()}</span>
      </div>
      <div className="alerts-list">
        {alerts.map((alert, idx) => (
          <div key={idx} className={`alert-item ${alert.severity}`}>
            <div className="alert-icon">{Icons.alertTriangle}</div>
            <div className="alert-content">
              <span className="alert-title">{alert.title}</span>
              <span className="alert-message">{alert.message}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// MAIN EXECUTIVE DASHBOARD
// =============================================================================

export default function ExecutiveDashboard({ data, loading, onRefresh, onProductClick, onInsightClick }) {
  const { t } = useTranslation();

  if (loading) {
    return (
      <div className="executive-dashboard loading">
        <div className="loading-spinner" />
        <span>{t('dashboard.loadingDashboard')}</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="executive-dashboard empty">
        <span>{t('common.noData')}</span>
        <button onClick={onRefresh}>{t('common.refresh')}</button>
      </div>
    );
  }

  return (
    <div className="executive-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-info">
          <h2>{t('dashboard.executiveDashboard')}</h2>
          <span className="last-updated">
            {t('dashboard.lastUpdated')} {data.data_freshness || 'Just now'}
          </span>
        </div>
        <button className="refresh-btn" onClick={onRefresh}>
          {Icons.refresh}
          {t('common.refresh')}
        </button>
      </div>

      {/* Metrics Grid */}
      <div className="metrics-grid">
        {data.metrics?.map((metric, idx) => (
          <MetricCard key={idx} metric={metric} />
        ))}
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Left Column */}
        <div className="dashboard-column primary">
          <RiskProductsTable
            products={data.high_risk_products}
            onProductClick={onProductClick}
            t={t}
          />
          <CategoryInsights categories={data.category_insights} t={t} />
        </div>

        {/* Right Column */}
        <div className="dashboard-column secondary">
          <AIInsightsPanel
            insights={data.ai_insights}
            onInsightClick={onInsightClick}
            t={t}
          />
          <AlertsPanel alerts={data.active_alerts} t={t} />
        </div>
      </div>
    </div>
  );
}