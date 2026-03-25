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
} from "chart.js";

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { getProducts, getForecast, getHistory } from "../api/forecastApi";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function ChartsPage() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState("");
  const [horizonDays, setHorizonDays] = useState(14);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [historyData, setHistoryData] = useState(null);
  const [forecastData, setForecastData] = useState(null);

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

    try {
      const [history, forecast] = await Promise.all([
        getHistory(selectedProduct, { limit: 100 }),
        getForecast({
          productId: selectedProduct,
          horizonDays: horizonDays,
        }),
      ]);

      setHistoryData(history);
      setForecastData(forecast);
    } catch (err) {
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
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
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        tension: 0.3,
      },
      {
        label: "Forecast",
        data: [
          ...Array(historyData?.records?.slice(-30).length || 0).fill(null),
          ...(forecastData?.predictions?.map((p) => p.predicted_units_sold) || []),
        ],
        borderColor: "#3ad17b",
        backgroundColor: "rgba(58, 209, 123, 0.1)",
        borderDash: [5, 5],
        tension: 0.3,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "top" },
      title: {
        display: true,
        text: `Sales & Forecast - ${selectedProduct}`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: "Units Sold" },
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
                  style={{
                    height: 38,
                    minWidth: 180,
                    border: "1px solid #e7eaee",
                    borderRadius: 12,
                    padding: "0 12px",
                  }}
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
