import { useMemo, useState } from "react";
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

// layout
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";

// ui / logic
import Controls from "../components/Controls";
import ForecastTable from "../components/ForecastTable";

// cards
import KpiCards from "../components/cards/KpiCard";

// charts
import SalesOverviewChart from "../components/charts/SalesOverviewChart";
import DemandDonut from "../components/charts/DemandDonut";

// api
import { getForecast, getHistory } from "../api/forecastApi";

// styles
import "../styles/dashboard.css";

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

export default function AdminDashboard() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(values) {
    try {
      setError("");
      setLoading(true);
      const [forecastRes, historyRes] = await Promise.all([
        getForecast(values),
        getHistory(values.productId, { limit: 30 })
      ]);
      setData(forecastRes);
      setHistoryData(historyRes);
    } catch (e) {
      setError(e?.message || "Unknown error");
      setData(null);
      setHistoryData(null);
    } finally {
      setLoading(false);
    }
  }

  const derived = useMemo(() => {
    if (!data?.predictions?.length) return null;

    const nums = data.predictions.map(
      (x) => Number(x.predicted_units_sold) || 0
    );

    const total = nums.reduce((a, b) => a + b, 0);
    const avg = total / nums.length;

    // Делим прогноз условно на 4 сегмента (для donut)
    const q = Math.ceil(nums.length / 4);
    const buckets = [
      nums.slice(0, q),
      nums.slice(q, q * 2),
      nums.slice(q * 2, q * 3),
      nums.slice(q * 3),
    ].map((arr) => arr.reduce((a, b) => a + b, 0));

    return { total, avg, buckets };
  }, [data]);

  // Combined chart data for history vs forecast
  const comparisonChartData = useMemo(() => {
    if (!data?.predictions) return null;

    const historyRecords = historyData?.records?.slice(-30) || [];
    const forecastRecords = data.predictions || [];

    return {
      labels: [
        ...historyRecords.map((r) => r.date),
        ...forecastRecords.map((p) => p.date),
      ],
      datasets: [
        {
          label: "Historical Sales",
          data: [
            ...historyRecords.map((r) => r.units_sold),
            ...Array(forecastRecords.length).fill(null),
          ],
          borderColor: "#10a37f",
          backgroundColor: "rgba(16, 163, 127, 0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2,
        },
        {
          label: "Forecast",
          data: [
            ...Array(historyRecords.length).fill(null),
            ...forecastRecords.map((p) => p.predicted_units_sold),
          ],
          borderColor: "#6366f1",
          backgroundColor: "rgba(99, 102, 241, 0.1)",
          fill: true,
          borderDash: [5, 5],
          tension: 0.4,
          pointRadius: 3,
          borderWidth: 2,
        },
      ],
    };
  }, [data, historyData]);

  const comparisonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
        labels: { color: "var(--text-secondary)", font: { size: 12 } },
      },
      tooltip: {
        backgroundColor: "var(--bg-tertiary)",
        titleColor: "var(--text-primary)",
        bodyColor: "var(--text-secondary)",
        borderColor: "var(--border)",
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { color: "var(--border-light)" },
        ticks: { color: "var(--text-tertiary)", font: { size: 10 } },
      },
      y: {
        beginAtZero: true,
        grid: { color: "var(--border-light)" },
        ticks: { color: "var(--text-tertiary)", font: { size: 10 } },
      },
    },
  };

  return (
    <div className="appShell">
      <Sidebar />

      <div className="main">
        <Topbar />

        <div className="content">
          {/* HEADER */}
          <div className="headerRow">
            <div>
              <div className="title">Forecasts & Charts</div>
              <div className="subtitle">Generate forecasts and visualize demand data</div>
            </div>
          </div>

          {/* CONTROLS */}
          <div className="panel">
            <Controls onSubmit={handleSubmit} loading={loading} />
            {error && <div className="errorBox">{error}</div>}
          </div>

          {loading && <div className="hint">Loading forecast…</div>}

          {/* DATA */}
          {data && derived && (
            <>
              {/* KPI */}
              <KpiCards
                productId={data.product_id}
                storeId={data.store_id}
                horizonDays={data.horizon_days}
                total={derived.total}
                avg={derived.avg}
                lastDate={data.last_date_in_history}
              />

              {/* COMPARISON CHART - History vs Forecast */}
              {comparisonChartData && (
                <div className="card" style={{ marginBottom: "20px" }}>
                  <div className="cardHeader">
                    <div>
                      <div className="cardTitle">Historical vs Forecast</div>
                      <div className="cardSub">Compare past sales with predicted demand</div>
                    </div>
                  </div>
                  <div style={{ height: "350px" }}>
                    <Line data={comparisonChartData} options={comparisonChartOptions} />
                  </div>
                </div>
              )}

              {/* CHARTS */}
              <div className="grid2">
                <div className="card">
                  <div className="cardHeader">
                    <div>
                      <div className="cardTitle">Forecast Overview</div>
                      <div className="cardSub">Predicted demand volume</div>
                    </div>
                  </div>
                  <SalesOverviewChart predictions={data.predictions} />
                </div>

                <div className="card">
                  <div className="cardHeader">
                    <div>
                      <div className="cardTitle">Demand Distribution</div>
                      <div className="cardSub">Forecast breakdown by period</div>
                    </div>
                  </div>
                  <DemandDonut buckets={derived.buckets} />
                </div>
              </div>

              {/* MODEL METRICS */}
              {data.model_metrics && (
                <div className="card" style={{ marginBottom: "20px" }}>
                  <div className="cardHeader">
                    <div className="cardTitle">Model Performance</div>
                  </div>
                  <div className="metricsGrid">
                    <div className="metricCard">
                      <div className="metricLabel">MAE</div>
                      <div className="metricValue">{data.model_metrics.mae.toFixed(2)}</div>
                    </div>
                    <div className="metricCard">
                      <div className="metricLabel">RMSE</div>
                      <div className="metricValue">{data.model_metrics.rmse.toFixed(2)}</div>
                    </div>
                    <div className="metricCard">
                      <div className="metricLabel">R2 Score</div>
                      <div className="metricValue">{data.model_metrics.r2.toFixed(4)}</div>
                    </div>
                  </div>
                </div>
              )}

              {/* FORECAST TABLE */}
              <div className="card">
                <div className="cardHeader">
                  <div className="cardTitle">Forecast Details</div>
                </div>
                <ForecastTable predictions={data.predictions} />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
