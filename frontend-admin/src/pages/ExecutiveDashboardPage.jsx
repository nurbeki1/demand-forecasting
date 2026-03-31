/**
 * Executive Dashboard Page
 * Wraps the ExecutiveDashboard component with data fetching
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import ExecutiveDashboard from "../components/dashboard/ExecutiveDashboard";
import { getExecutiveDashboard } from "../api/forecastApi";

export default function ExecutiveDashboardPage() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getExecutiveDashboard();
      setDashboardData(data);
    } catch (err) {
      console.error("Failed to fetch dashboard:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const handleRefresh = () => {
    fetchDashboard();
  };

  const handleProductClick = (product) => {
    // Navigate to forecast with product selected
    navigate(`/admin/forecast?product=${product.product_id}`);
  };

  const handleInsightClick = (insight) => {
    // Navigate to forecast with the insight query
    if (insight.action_query) {
      navigate(`/admin/forecast?query=${encodeURIComponent(insight.action_query)}`);
    }
  };

  if (error) {
    return (
      <div className="appShell">
        <Sidebar />
        <div className="main">
          <Topbar title="Executive Dashboard" />
          <div className="content">
            <div style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              minHeight: "400px",
              gap: "16px",
              color: "var(--text-tertiary)"
            }}>
              <span style={{ color: "var(--error)" }}>Error: {error}</span>
              <button
                onClick={handleRefresh}
                style={{
                  padding: "10px 20px",
                  background: "var(--accent)",
                  border: "none",
                  borderRadius: "8px",
                  color: "white",
                  cursor: "pointer"
                }}
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar title="Executive Dashboard" />
        <div className="content">
          <ExecutiveDashboard
            data={dashboardData}
            loading={loading}
            onRefresh={handleRefresh}
            onProductClick={handleProductClick}
            onInsightClick={handleInsightClick}
          />
        </div>
      </div>
    </div>
  );
}
