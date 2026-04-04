/**
 * CitiesTable Component
 * Sortable table displaying city analysis data
 */

import { useState } from "react";

const COLUMNS = [
  { key: "city_name", label: "Город", sortable: true },
  { key: "recommended_price_kzt", label: "Цена", sortable: true, format: "currency" },
  { key: "margin_percent", label: "Маржа", sortable: true, format: "percent" },
  { key: "estimated_monthly_demand", label: "Спрос", sortable: true, format: "number" },
  { key: "total_monthly_profit_kzt", label: "Прибыль/мес", sortable: true, format: "currency" },
  { key: "status_icon", label: "Статус", sortable: false },
];

function formatValue(value, format) {
  if (value === null || value === undefined) return "—";

  switch (format) {
    case "currency":
      return `${Math.round(value).toLocaleString()} ₸`;
    case "percent":
      return `${value.toFixed(1)}%`;
    case "number":
      return Math.round(value).toLocaleString();
    default:
      return value;
  }
}

function getStatusColor(statusIcon) {
  if (statusIcon?.includes("🟢") || statusIcon?.includes("✅")) return "profitable";
  if (statusIcon?.includes("🟡") || statusIcon?.includes("⚠️")) return "risky";
  if (statusIcon?.includes("🔴") || statusIcon?.includes("❌")) return "unprofitable";
  return "";
}

export default function CitiesTable({
  cities = [],
  sortBy: initialSortBy = "total_monthly_profit_kzt",
  sortOrder: initialSortOrder = "desc",
  onSort,
  compactView = true,
}) {
  const [sortBy, setSortBy] = useState(initialSortBy);
  const [sortOrder, setSortOrder] = useState(initialSortOrder);
  const [showAll, setShowAll] = useState(!compactView);

  const handleSort = (column) => {
    if (!COLUMNS.find((c) => c.key === column)?.sortable) return;

    const newOrder = sortBy === column && sortOrder === "desc" ? "asc" : "desc";
    setSortBy(column);
    setSortOrder(newOrder);
    onSort?.(column, newOrder);
  };

  // Sort cities
  const sortedCities = [...cities].sort((a, b) => {
    const aVal = a[sortBy];
    const bVal = b[sortBy];

    if (typeof aVal === "string" && typeof bVal === "string") {
      return sortOrder === "asc"
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }

    return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
  });

  // Get top 3 cities by profit for highlighting
  const top3CityNames = [...cities]
    .sort((a, b) => b.total_monthly_profit_kzt - a.total_monthly_profit_kzt)
    .slice(0, 3)
    .map((c) => c.city_name);

  const displayedCities = showAll ? sortedCities : sortedCities.slice(0, 5);

  return (
    <div className="kz-cities-table-container">
      <div className="kz-cities-table-wrapper">
        <table className="kz-cities-table">
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  className={`${col.sortable ? "sortable" : ""} ${
                    sortBy === col.key ? "sorted" : ""
                  }`}
                  onClick={() => handleSort(col.key)}
                >
                  <span className="th-content">
                    {col.label}
                    {col.sortable && sortBy === col.key && (
                      <span className="sort-indicator">
                        {sortOrder === "asc" ? "↑" : "↓"}
                      </span>
                    )}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayedCities.map((city, idx) => {
              const isTop3 = top3CityNames.includes(city.city_name);
              const statusClass = getStatusColor(city.status_icon);

              return (
                <tr
                  key={city.city_id || city.city_name || idx}
                  className={`${isTop3 ? "top-city" : ""} ${statusClass}`}
                >
                  <td className="city-name">
                    {isTop3 && <span className="top-badge">🏆</span>}
                    {city.city_name}
                  </td>
                  <td>{formatValue(city.recommended_price_kzt, "currency")}</td>
                  <td>
                    <span className={`margin-value ${city.margin_percent >= 20 ? "good" : city.margin_percent >= 10 ? "medium" : "low"}`}>
                      {formatValue(city.margin_percent, "percent")}
                    </span>
                  </td>
                  <td>{formatValue(city.estimated_monthly_demand, "number")}</td>
                  <td className="profit-cell">
                    {formatValue(city.total_monthly_profit_kzt, "currency")}
                  </td>
                  <td className="status-cell">
                    <span className={`status-badge ${statusClass}`}>
                      {city.status_icon || "—"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {compactView && cities.length > 5 && (
        <button
          className="kz-show-all-btn"
          onClick={() => setShowAll(!showAll)}
        >
          {showAll ? "Скрыть" : `Показать все (${cities.length})`}
        </button>
      )}
    </div>
  );
}
