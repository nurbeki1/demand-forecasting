import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { getProducts, compareForecast, acceptComparison } from "../api/forecastApi";
import "../styles/compare.css";

function MetricChange({ label, oldVal, newVal, higherIsBetter = false }) {
  if (oldVal == null || newVal == null) return null;
  const diff = newVal - oldVal;
  const improved = higherIsBetter ? diff > 0 : diff < 0;
  const color = Math.abs(diff) < 0.001 ? "var(--text-tertiary)" : improved ? "var(--success)" : "var(--error)";
  const arrow = diff > 0 ? "+" : "";

  return (
    <tr>
      <td>{label}</td>
      <td>{oldVal.toFixed(4)}</td>
      <td>{newVal.toFixed(4)}</td>
      <td style={{ color, fontWeight: 600 }}>
        {arrow}{diff.toFixed(4)}
      </td>
    </tr>
  );
}

export default function ForecastComparisonPage() {
  const { t } = useTranslation();
  const [products, setProducts] = useState([]);
  const [productId, setProductId] = useState("");
  const [horizonDays, setHorizonDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [accepting, setAccepting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    getProducts()
      .then((data) => {
        setProducts(data);
        if (data.length > 0) setProductId(data[0].product_id);
      })
      .catch(() => {});
  }, []);

  async function handleCompare() {
    if (!productId) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await compareForecast({ productId, horizonDays });
      setResult(data);
      if (!data.current) {
        toast.info(t('compare.noCurrentModel', 'No cached model — showing new model only'));
      }
    } catch (err) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAccept() {
    setAccepting(true);
    try {
      await acceptComparison(productId);
      toast.success(t('compare.accepted', 'New model accepted and saved!'));
      setResult(null);
    } catch (err) {
      toast.error(err.message);
    } finally {
      setAccepting(false);
    }
  }

  // Build chart data
  const chartData = result
    ? result.dates.map((date, i) => ({
        date: date.slice(5), // MM-DD
        ...(result.current ? { current: result.current.predictions[i] } : {}),
        retrained: result.retrained.predictions[i],
      }))
    : [];

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">{t('compare.title', 'Model Comparison')}</div>
              <div className="subtitle">{t('compare.subtitle', 'Compare current model with retrained version')}</div>
            </div>
          </div>

          {/* Controls */}
          <div className="panel">
            <div className="filterRow">
              <div className="field">
                <label>{t('common.product')}</label>
                <select value={productId} onChange={(e) => setProductId(e.target.value)}>
                  {products.map((p) => (
                    <option key={p.product_id} value={p.product_id}>{p.product_id}</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>{t('forecast.horizon', 'Horizon (days)')}</label>
                <input
                  type="number"
                  min={1}
                  max={30}
                  value={horizonDays}
                  onChange={(e) => setHorizonDays(Number(e.target.value))}
                />
              </div>
              <div className="field" style={{ alignSelf: "flex-end" }}>
                <button className="btn" onClick={handleCompare} disabled={loading || !productId}>
                  {loading ? t('compare.comparing', 'Comparing...') : t('compare.compare', 'Compare')}
                </button>
              </div>
            </div>
          </div>

          {loading && (
            <div className="hint">{t('compare.trainingHint', 'Training new model for comparison... This may take a few seconds.')}</div>
          )}

          {result && (
            <>
              {/* Overlay Chart */}
              <div className="card" style={{ marginBottom: 20 }}>
                <div className="cardHeader">
                  <div className="cardTitle">{t('compare.forecastOverlay', 'Forecast Overlay')}</div>
                </div>
                <div style={{ height: 350 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border, #2a2a3e)" />
                      <XAxis dataKey="date" stroke="var(--text-tertiary)" fontSize={12} />
                      <YAxis stroke="var(--text-tertiary)" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          background: "var(--bg-secondary, #1a1a2e)",
                          border: "1px solid var(--border, #2a2a3e)",
                          borderRadius: 8,
                          color: "var(--text-primary)",
                        }}
                      />
                      <Legend />
                      {result.current && (
                        <Line
                          type="monotone"
                          dataKey="current"
                          name={t('compare.currentModel', 'Current Model')}
                          stroke="#6366f1"
                          strokeWidth={2}
                          dot={{ r: 4 }}
                        />
                      )}
                      <Line
                        type="monotone"
                        dataKey="retrained"
                        name={t('compare.retrainedModel', 'Retrained Model')}
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={{ r: 4 }}
                        strokeDasharray={result.current ? "5 5" : undefined}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Metrics Comparison Table */}
              <div className="card" style={{ marginBottom: 20 }}>
                <div className="cardHeader">
                  <div className="cardTitle">{t('compare.metricsComparison', 'Metrics Comparison')}</div>
                </div>
                <div className="tableWrap">
                  <table className="table compare-table">
                    <thead>
                      <tr>
                        <th>{t('compare.metric', 'Metric')}</th>
                        <th>{t('compare.currentModel', 'Current')}</th>
                        <th>{t('compare.retrainedModel', 'Retrained')}</th>
                        <th>{t('compare.change', 'Change')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <MetricChange
                        label={t('forecast.metrics.mae')}
                        oldVal={result.current?.metrics?.mae}
                        newVal={result.retrained.metrics.mae}
                        higherIsBetter={false}
                      />
                      <MetricChange
                        label={t('forecast.metrics.rmse')}
                        oldVal={result.current?.metrics?.rmse}
                        newVal={result.retrained.metrics.rmse}
                        higherIsBetter={false}
                      />
                      <MetricChange
                        label={t('forecast.metrics.r2')}
                        oldVal={result.current?.metrics?.r2}
                        newVal={result.retrained.metrics.r2}
                        higherIsBetter={true}
                      />
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="compare-actions">
                <button
                  className="btn compare-accept-btn"
                  onClick={handleAccept}
                  disabled={accepting}
                >
                  {accepting ? t('common.loading') : t('compare.acceptNew', 'Accept New Model')}
                </button>
                <button
                  className="btn compare-keep-btn"
                  onClick={() => setResult(null)}
                >
                  {t('compare.keepCurrent', 'Keep Current')}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
