import { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import InsightCard from "../components/insights/InsightCard";
import { getProducts, getForecast, getForecastV2, getHistory } from "../api/forecastApi";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function ChartsPage() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [horizonDays, setHorizonDays] = useState(14);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [historyData, setHistoryData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [insightData, setInsightData] = useState(null);
  const [useV2, setUseV2] = useState(true);

  useEffect(() => {
    loadProducts();
  }, []);

  async function loadProducts() {
    try {
      const data = await getProducts();
      setProducts(data);
      if (data.length > 0) {
        setSelectedProduct(data[0].product_id);
      }
    } catch (err) {
      setError("Failed to load products");
    }
  }

  async function handleLoadData() {
    if (!selectedProduct) return;

    setLoading(true);
    setError("");
    setInsightData(null);

    try {
      const [history, forecast] = await Promise.all([
        getHistory(selectedProduct, { limit: 100 }),
        useV2
          ? getForecastV2({
              productId: selectedProduct,
              horizonDays: horizonDays,
            })
          : getForecast({
              productId: selectedProduct,
              horizonDays: horizonDays,
            }),
      ]);

      setHistoryData(history);
      setForecastData(forecast);

      // If v2, set insight data
      if (useV2 && forecast.insights) {
        setInsightData(forecast);
      }
    } catch (err) {
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }

  function handleFollowUpClick(question) {
    // Navigate to chat with the question
    console.log("Follow-up question:", question);
    // TODO: Integrate with chat
  }

  function handleSuggestionClick(prompt) {
    // Navigate to chat with the suggestion prompt
    console.log("Suggestion prompt:", prompt);
    // Store in sessionStorage for chat to pick up
    sessionStorage.setItem("chat_prefill", prompt);
    // Navigate to admin chat
    window.location.href = "/admin/chat";
  }

  const chartData = {
    labels: [
      ...(historyData?.records?.slice(-30).map((r) => r.date) || []),
      ...(forecastData?.predictions?.map((p) => p.date) || []),
    ],
    datasets: [
      {
        label: "Historical Sales",
        data: [
          ...(historyData?.records?.slice(-30).map((r) => r.units_sold) || []),
          ...Array(forecastData?.predictions?.length || 0).fill(null),
        ],
        borderColor: "#00e5ff",
        backgroundColor: "rgba(0, 229, 255, 0.1)",
        fill: true,
        tension: 0.4,
        pointBackgroundColor: "#00e5ff",
        pointBorderColor: "#00e5ff",
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
      {
        label: "Forecast",
        data: [
          ...Array(historyData?.records?.slice(-30).length || 0).fill(null),
          ...(forecastData?.predictions?.map((p) => p.predicted_units_sold) || []),
        ],
        borderColor: "#00ff88",
        backgroundColor: "rgba(0, 255, 136, 0.1)",
        fill: true,
        borderDash: [5, 5],
        tension: 0.4,
        pointBackgroundColor: "#00ff88",
        pointBorderColor: "#00ff88",
        pointRadius: 3,
        pointHoverRadius: 5,
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 11,
          },
        },
      },
      title: {
        display: true,
        text: `Sales & Forecast - ${selectedProduct}`,
        color: "#e8f4fc",
        font: {
          family: "'Space Mono', monospace",
          size: 14,
          weight: "bold",
        },
      },
      tooltip: {
        backgroundColor: "rgba(5, 13, 26, 0.95)",
        titleColor: "#00e5ff",
        bodyColor: "#e8f4fc",
        borderColor: "rgba(0, 229, 255, 0.3)",
        borderWidth: 1,
        titleFont: {
          family: "'Space Mono', monospace",
        },
        bodyFont: {
          family: "'Space Mono', monospace",
        },
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: {
          color: "rgba(0, 229, 255, 0.08)",
        },
        ticks: {
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 10,
          },
        },
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: "Units Sold",
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 11,
          },
        },
        grid: {
          color: "rgba(0, 229, 255, 0.08)",
        },
        ticks: {
          color: "#4a6580",
          font: {
            family: "'Space Mono', monospace",
            size: 10,
          },
        },
      },
    },
  };

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">Charts</div>
              <div className="subtitle">Compare historical data with forecasts</div>
            </div>
          </div>

          <div className="panel">
            <div className="productSelect">
              <div className="field">
                <label>Product</label>
                <select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                >
                  {products.map((p) => (
                    <option key={p.product_id} value={p.product_id}>
                      {p.product_id} - {p.category}
                    </option>
                  ))}
                </select>
              </div>

              <div className="field">
                <label>Forecast Days</label>
                <input
                  type="number"
                  value={horizonDays}
                  onChange={(e) => setHorizonDays(Number(e.target.value))}
                  min={1}
                  max={30}
                />
              </div>

              <button
                className="btn"
                onClick={handleLoadData}
                disabled={loading || !selectedProduct}
              >
                {loading ? "Loading..." : "Load Data"}
              </button>

              <label className="toggle-label" style={{ display: "flex", alignItems: "center", gap: "8px", marginLeft: "16px" }}>
                <input
                  type="checkbox"
                  checked={useV2}
                  onChange={(e) => setUseV2(e.target.checked)}
                  style={{ width: "16px", height: "16px" }}
                />
                <span style={{ fontSize: "12px", color: "#4a6580" }}>Decision Assistant</span>
              </label>
            </div>

            {error && <div className="errorBox">{error}</div>}
          </div>

          {forecastData && (
            <>
              <div className="card">
                <div className="cardHeader">
                  <div className="cardTitle">Sales Overview</div>
                </div>
                <div className="chartBox" style={{ height: 400 }}>
                  <Line data={chartData} options={chartOptions} />
                </div>
              </div>

              {forecastData.model_metrics && (
                <div className="metricsGrid">
                  <div className="metricCard">
                    <div className="metricLabel">MAE</div>
                    <div className="metricValue">
                      {forecastData.model_metrics.mae.toFixed(2)}
                    </div>
                  </div>
                  <div className="metricCard">
                    <div className="metricLabel">RMSE</div>
                    <div className="metricValue">
                      {forecastData.model_metrics.rmse.toFixed(2)}
                    </div>
                  </div>
                  <div className="metricCard">
                    <div className="metricLabel">R2 Score</div>
                    <div className="metricValue">
                      {forecastData.model_metrics.r2.toFixed(4)}
                    </div>
                  </div>
                </div>
              )}

              {/* Decision Assistant Insight Card */}
              {insightData && (
                <div style={{ marginTop: "24px" }}>
                  <InsightCard
                    data={insightData}
                    onFollowUpClick={handleFollowUpClick}
                    onSuggestionClick={handleSuggestionClick}
                  />
                </div>
              )}
            </>
          )}

          {!forecastData && !loading && (
            <div className="card">
              <div className="emptyBox">
                Select a product and click "Load Data" to view charts
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}