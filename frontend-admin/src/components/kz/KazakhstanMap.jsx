/**
 * KazakhstanMap Component
 * Uses official SVG map from open-data-kazakhstan
 * Dark theme: black fill, white borders
 * viewBox: 800x293
 */

import { useState, useEffect, useRef } from "react";

// City positions for viewBox 800x293 (calculated from geographic coordinates)
// Kazakhstan: ~46.5°E to 87.5°E longitude, ~40°N to 55.5°N latitude
const CITIES = {
  almaty: { x: 608, y: 218, name: "Алматы" },
  astana: { x: 490, y: 68, name: "Астана" },
  shymkent: { x: 448, y: 235, name: "Шымкент" },
  karaganda: { x: 520, y: 95, name: "Караганда" },
  aktobe: { x: 200, y: 85, name: "Актобе" },
  taraz: { x: 485, y: 225, name: "Тараз" },
  pavlodar: { x: 600, y: 48, name: "Павлодар" },
  oskemen: { x: 715, y: 90, name: "Усть-Каменогорск" },
  semey: { x: 660, y: 80, name: "Семей" },
  atyrau: { x: 100, y: 145, name: "Атырау" },
  kostanay: { x: 330, y: 28, name: "Костанай" },
  kyzylorda: { x: 360, y: 182, name: "Кызылорда" },
  aktau: { x: 85, y: 205, name: "Актау" },
  petropavl: { x: 445, y: 18, name: "Петропавловск" },
  oral: { x: 92, y: 65, name: "Уральск" },
  taldykorgan: { x: 640, y: 178, name: "Талдыкорган" },
  turkestan: { x: 420, y: 218, name: "Туркестан" },
  ekibastuz: { x: 565, y: 58, name: "Экибастуз" },
  temirtau: { x: 515, y: 88, name: "Темиртау" },
  kokshetau: { x: 450, y: 38, name: "Кокшетау" },
  jezkazgan: { x: 410, y: 135, name: "Жезказган" },
};

function normalizeCityName(name) {
  if (!name) return null;
  const normalized = name.toLowerCase().replace(/[- ]/g, "_");

  const mapping = {
    "алматы": "almaty",
    "астана": "astana",
    "шымкент": "shymkent",
    "караганда": "karaganda",
    "актобе": "aktobe",
    "тараз": "taraz",
    "павлодар": "pavlodar",
    "усть-каменогорск": "oskemen",
    "усть_каменогорск": "oskemen",
    "семей": "semey",
    "атырау": "atyrau",
    "костанай": "kostanay",
    "кызылорда": "kyzylorda",
    "актау": "aktau",
    "петропавловск": "petropavl",
    "уральск": "oral",
    "талдыкорган": "taldykorgan",
    "туркестан": "turkestan",
    "экибастуз": "ekibastuz",
    "темиртау": "temirtau",
    "кокшетау": "kokshetau",
    "жезказган": "jezkazgan",
  };

  for (const [ru, en] of Object.entries(mapping)) {
    if (normalized.includes(ru)) return en;
  }

  for (const key of Object.keys(CITIES)) {
    if (normalized.includes(key)) return key;
  }

  return null;
}

function getStatusColor(status) {
  switch (status) {
    case "profitable": return "#22c55e";
    case "risky": return "#eab308";
    case "unprofitable": return "#ef4444";
    default: return "#ffffff";
  }
}

export default function KazakhstanMap({ cities = [], onCityClick, highlightedCity }) {
  const [hoveredCity, setHoveredCity] = useState(null);
  const [svgContent, setSvgContent] = useState(null);
  const containerRef = useRef(null);

  // Load SVG content
  useEffect(() => {
    fetch("/kz-map.svg")
      .then(res => res.text())
      .then(text => {
        // Extract just the path d attribute from the SVG
        const match = text.match(/<path[^>]*d="([^"]+)"/);
        if (match) {
          setSvgContent(match[1]);
        }
      })
      .catch(err => console.error("Failed to load KZ map:", err));
  }, []);

  const mappedCities = cities.map((city) => {
    const cityKey = normalizeCityName(city.city_name) || city.city_id;
    const coords = CITIES[cityKey];
    return { ...city, coords, cityKey };
  }).filter((c) => c.coords);

  const hoveredCityData = hoveredCity ? mappedCities.find(c => c.cityKey === hoveredCity) : null;

  return (
    <div className="kz-map-container" ref={containerRef}>
      <div className="kz-map-header">
        <h4>🗺️ Карта Казахстана</h4>
        <div className="kz-map-legend">
          <span className="legend-item">
            <span className="legend-dot profitable" />
            Выгодно
          </span>
          <span className="legend-item">
            <span className="legend-dot risky" />
            Риск
          </span>
          <span className="legend-item">
            <span className="legend-dot unprofitable" />
            Невыгодно
          </span>
        </div>
      </div>

      <svg viewBox="0 0 800 293" className="kz-map-svg" preserveAspectRatio="xMidYMid meet">
        {/* Background */}
        <rect x="0" y="0" width="800" height="293" fill="#000000" />

        {/* Kazakhstan outline from official SVG */}
        {svgContent && (
          <path
            d={svgContent}
            fill="#0a0a12"
            stroke="#ffffff"
            strokeWidth="0.8"
            strokeLinejoin="round"
            className="kz-country-outline"
          />
        )}

        {/* Fallback while loading */}
        {!svgContent && (
          <text x="400" y="150" textAnchor="middle" fill="#666" fontSize="14">
            Загрузка карты...
          </text>
        )}

        {/* City markers */}
        <g className="kz-cities">
          {Object.entries(CITIES).map(([id, city]) => {
            const cityData = mappedCities.find(c => c.cityKey === id);
            const isHovered = hoveredCity === id;
            const isHighlighted = highlightedCity === id;
            const status = cityData?.status;
            const hasData = !!cityData;
            const color = hasData ? getStatusColor(status) : "rgba(255,255,255,0.4)";

            return (
              <g
                key={id}
                className={`kz-city ${isHovered ? 'hovered' : ''} ${isHighlighted ? 'highlighted' : ''}`}
                onMouseEnter={() => hasData && setHoveredCity(id)}
                onMouseLeave={() => setHoveredCity(null)}
                onClick={() => hasData && onCityClick?.(id)}
                style={{ cursor: hasData ? 'pointer' : 'default' }}
              >
                {/* Pulse animation for profitable cities */}
                {status === 'profitable' && (
                  <circle
                    cx={city.x}
                    cy={city.y}
                    r="5"
                    fill="none"
                    stroke="#22c55e"
                    strokeWidth="1.5"
                    className="city-pulse"
                  />
                )}

                {/* Glow effect */}
                {hasData && (
                  <circle
                    cx={city.x}
                    cy={city.y}
                    r="8"
                    fill={color}
                    opacity="0.25"
                  />
                )}

                {/* Main marker dot */}
                <circle
                  cx={city.x}
                  cy={city.y}
                  r={hasData ? 4 : 2.5}
                  fill={color}
                  stroke={hasData ? "#000" : "none"}
                  strokeWidth="0.5"
                  className="city-marker"
                />

                {/* City label (only show for main cities or on hover) */}
                {(isHovered || isHighlighted) && (
                  <text
                    x={city.x}
                    y={city.y - 10}
                    textAnchor="middle"
                    fill="#fff"
                    fontSize="9"
                    fontWeight="500"
                    className="city-label"
                  >
                    {city.name}
                  </text>
                )}
              </g>
            );
          })}
        </g>

        {/* Tooltip */}
        {hoveredCityData && CITIES[hoveredCity] && (
          <g transform={`translate(${Math.min(CITIES[hoveredCity].x + 12, 680)}, ${Math.max(CITIES[hoveredCity].y - 45, 10)})`}>
            <rect
              x="0"
              y="0"
              width="110"
              height="48"
              rx="4"
              fill="rgba(0,0,0,0.92)"
              stroke="rgba(255,255,255,0.2)"
              strokeWidth="0.5"
            />
            <text x="8" y="16" fill="#fff" fontSize="10" fontWeight="600">
              {hoveredCityData.city_name}
            </text>
            <text x="8" y="30" fill="#22c55e" fontSize="9" fontWeight="500">
              {Math.round(hoveredCityData.total_monthly_profit_kzt || 0).toLocaleString()} ₸/мес
            </text>
            <text x="8" y="42" fill="#888" fontSize="8">
              {hoveredCityData.status === 'profitable' ? '✅ Выгодно' : hoveredCityData.status === 'risky' ? '⚠️ Риск' : '❌ Невыгодно'}
            </text>
          </g>
        )}
      </svg>
    </div>
  );
}
