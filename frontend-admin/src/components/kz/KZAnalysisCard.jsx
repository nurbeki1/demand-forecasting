/**
 * KZAnalysisCard Component
 * Main card component displaying KZ market analysis with all sub-components
 */

import { useState } from "react";
import MarkupSlider from "./MarkupSlider";
import CitiesTable from "./CitiesTable";
import KazakhstanMap from "./KazakhstanMap";
import "./KZAnalysisCard.css";

function formatCurrency(value, currency = "KZT") {
  if (value === null || value === undefined) return "—";
  const formatted = Math.round(value).toLocaleString();
  return currency === "KZT" ? `${formatted} ₸` : `$${formatted}`;
}

// Collapsible section component
function CollapsibleSection({ title, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`kz-collapsible ${isOpen ? "open" : ""}`}>
      <button className="kz-collapsible-header" onClick={() => setIsOpen(!isOpen)}>
        <span>{title}</span>
        <span className="kz-collapsible-icon">{isOpen ? "−" : "+"}</span>
      </button>
      {isOpen && <div className="kz-collapsible-content">{children}</div>}
    </div>
  );
}

export default function KZAnalysisCard({ data, onMarkupChange }) {
  const [currentMarkup, setCurrentMarkup] = useState(data?.markup_percent || 25);
  const [highlightedCity, setHighlightedCity] = useState(null);
  const [isRecalculating, setIsRecalculating] = useState(false);

  if (!data) return null;

  const {
    product_name,
    product_cost_usd,
    product_cost_kzt,
    currency_rate,
    cities = [],
    best_cities = [],
    avoid_cities = [],
    total_potential_profit_kzt,
    investment,
    competitor_analysis,
    warnings = [],
    is_profitable,
  } = data;

  const handleMarkupChange = async (newMarkup) => {
    setCurrentMarkup(newMarkup);
    if (onMarkupChange) {
      setIsRecalculating(true);
      try {
        await onMarkupChange(newMarkup);
      } finally {
        setIsRecalculating(false);
      }
    }
  };

  const handleCityClick = (cityId) => {
    setHighlightedCity(highlightedCity === cityId ? null : cityId);
  };

  // Determine overall status
  const statusClass = is_profitable ? "profitable" : warnings.length > 0 ? "risky" : "unprofitable";
  const statusIcon = is_profitable ? "✅" : warnings.length > 0 ? "⚠️" : "❌";

  return (
    <div className={`kz-analysis-card ${statusClass}`}>
      {/* Header */}
      <div className="kz-header">
        <div className="kz-header-content">
          <span className="kz-status-icon">{statusIcon}</span>
          <div className="kz-header-text">
            <h3 className="kz-product-name">{product_name || "Анализ рынка КЗ"}</h3>
            <span className="kz-header-subtitle">Анализ рынка Казахстана</span>
          </div>
        </div>
        {is_profitable && (
          <span className="kz-profitable-badge">Выгодно</span>
        )}
      </div>

      {/* Price Summary */}
      <div className="kz-price-summary">
        <div className="kz-price-item">
          <span className="kz-price-label">Оптовая цена</span>
          <span className="kz-price-value">{formatCurrency(product_cost_usd, "USD")}</span>
          <span className="kz-price-converted">{formatCurrency(product_cost_kzt, "KZT")}</span>
        </div>
        <div className="kz-price-divider" />
        <div className="kz-price-item">
          <span className="kz-price-label">Курс USD/KZT</span>
          <span className="kz-price-value">{currency_rate?.toFixed(2) || "—"}</span>
        </div>
        <div className="kz-price-divider" />
        <div className="kz-price-item highlight">
          <span className="kz-price-label">Потенциал прибыли/мес</span>
          <span className="kz-price-value success">{formatCurrency(total_potential_profit_kzt, "KZT")}</span>
        </div>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="kz-warnings">
          {warnings.map((warning, idx) => (
            <div key={idx} className="kz-warning-item">
              <span className="kz-warning-icon">⚠️</span>
              <span>{warning}</span>
            </div>
          ))}
        </div>
      )}

      {/* Best/Avoid Cities Quick View */}
      {(best_cities.length > 0 || avoid_cities.length > 0) && (
        <div className="kz-cities-quick">
          {best_cities.length > 0 && (
            <div className="kz-cities-group best">
              <span className="kz-cities-group-label">🏆 Лучшие города:</span>
              <span className="kz-cities-list">{best_cities.join(", ")}</span>
            </div>
          )}
          {avoid_cities.length > 0 && (
            <div className="kz-cities-group avoid">
              <span className="kz-cities-group-label">⛔ Избегать:</span>
              <span className="kz-cities-list">{avoid_cities.join(", ")}</span>
            </div>
          )}
        </div>
      )}

      {/* Markup Slider */}
      <div className="kz-section">
        <MarkupSlider
          value={currentMarkup}
          onChange={handleMarkupChange}
          disabled={isRecalculating}
        />
        {isRecalculating && (
          <div className="kz-recalculating">
            <span className="kz-spinner" />
            <span>Пересчёт...</span>
          </div>
        )}
      </div>

      {/* Cities Table */}
      {cities.length > 0 && (
        <div className="kz-section">
          <h4 className="kz-section-title">📊 Анализ по городам</h4>
          <CitiesTable
            cities={cities}
            onSort={(col, order) => console.log("Sort:", col, order)}
            compactView={true}
          />
        </div>
      )}

      {/* Kazakhstan Map */}
      {cities.length > 0 && (
        <div className="kz-section">
          <KazakhstanMap
            cities={cities}
            onCityClick={handleCityClick}
            highlightedCity={highlightedCity}
          />
        </div>
      )}

      {/* Investment Summary */}
      {investment && (
        <CollapsibleSection title="💰 Инвестиции" defaultOpen={true}>
          <div className="kz-investment-grid">
            {investment.initial_investment_kzt && (
              <div className="kz-investment-item">
                <span className="kz-investment-label">Начальные инвестиции</span>
                <span className="kz-investment-value">
                  {formatCurrency(investment.initial_investment_kzt, "KZT")}
                </span>
              </div>
            )}
            {investment.monthly_operating_costs && (
              <div className="kz-investment-item">
                <span className="kz-investment-label">Операционные расходы/мес</span>
                <span className="kz-investment-value">
                  {formatCurrency(investment.monthly_operating_costs, "KZT")}
                </span>
              </div>
            )}
            {investment.break_even_months && (
              <div className="kz-investment-item">
                <span className="kz-investment-label">Срок окупаемости</span>
                <span className="kz-investment-value highlight">
                  {investment.break_even_months} мес.
                </span>
              </div>
            )}
            {investment.roi_percent && (
              <div className="kz-investment-item">
                <span className="kz-investment-label">ROI</span>
                <span className="kz-investment-value success">
                  {investment.roi_percent.toFixed(1)}%
                </span>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* Competitor Analysis */}
      {competitor_analysis && (
        <CollapsibleSection title="🔍 Конкуренты">
          <div className="kz-competitor-analysis">
            {competitor_analysis.avg_market_price && (
              <div className="kz-competitor-item">
                <span className="kz-competitor-label">Средняя рыночная цена</span>
                <span className="kz-competitor-value">
                  {formatCurrency(competitor_analysis.avg_market_price, "KZT")}
                </span>
              </div>
            )}
            {competitor_analysis.price_range && (
              <div className="kz-competitor-item">
                <span className="kz-competitor-label">Диапазон цен</span>
                <span className="kz-competitor-value">
                  {formatCurrency(competitor_analysis.price_range.min, "KZT")} — {formatCurrency(competitor_analysis.price_range.max, "KZT")}
                </span>
              </div>
            )}
            {competitor_analysis.competition_level && (
              <div className="kz-competitor-item">
                <span className="kz-competitor-label">Уровень конкуренции</span>
                <span className={`kz-competitor-value level-${competitor_analysis.competition_level}`}>
                  {competitor_analysis.competition_level === "high" ? "Высокий" :
                   competitor_analysis.competition_level === "medium" ? "Средний" : "Низкий"}
                </span>
              </div>
            )}
            {competitor_analysis.main_competitors && competitor_analysis.main_competitors.length > 0 && (
              <div className="kz-competitor-list">
                <span className="kz-competitor-label">Основные конкуренты:</span>
                <ul>
                  {competitor_analysis.main_competitors.map((c, idx) => (
                    <li key={idx}>{c}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* Risk Analysis (always available) */}
      <CollapsibleSection title="⚡ Риски и рекомендации">
        <div className="kz-risk-analysis">
          <div className="kz-risk-section">
            <h5>Основные риски:</h5>
            <ul>
              <li>Колебания курса валют</li>
              <li>Таможенные сборы и логистика</li>
              <li>Сезонность спроса</li>
              {competitor_analysis?.competition_level === "high" && (
                <li>Высокая конкуренция на рынке</li>
              )}
            </ul>
          </div>
          <div className="kz-risk-section">
            <h5>Рекомендации:</h5>
            <ul>
              <li>Начните с городов из списка "Лучшие"</li>
              <li>Отслеживайте курс валют ежедневно</li>
              <li>Учитывайте сезонные колебания спроса</li>
              {best_cities.length > 0 && (
                <li>Фокус на: {best_cities.slice(0, 2).join(", ")}</li>
              )}
            </ul>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );
}
