import { useMemo, useState } from "react";

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
import { getForecast } from "../api/forecastApi";

// styles
import "../styles/dashboard.css";

export default function AdminDashboard() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(values) {
    try {
      setError("");
      setLoading(true);
      const res = await getForecast(values);
      setData(res);
    } catch (e) {
      setError(e?.message || "Unknown error");
      setData(null);
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

  return (
    <div className="appShell">
      <Sidebar />

      <div className="main">
        <Topbar />

        <div className="content">
          {/* HEADER */}
          <div className="headerRow">
            <div>
              <div className="title">Dashboard</div>
              <div className="subtitle">Demand Forecast Admin Panel</div>
            </div>

            <button className="btnPrimary" type="button">
              + Add widget
            </button>
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

              {/* CHARTS */}
              <div className="grid2">
                <div className="card">
                  <div className="cardHeader">
                    <div>
                      <div className="cardTitle">Sales Overview</div>
                      <div className="cardSub">Forecast volume</div>
                    </div>
                  </div>
                  <SalesOverviewChart predictions={data.predictions} />
                </div>

                <div className="card">
                  <div className="cardHeader">
                    <div>
                      <div className="cardTitle">Statistics</div>
                      <div className="cardSub">Demand Structure</div>
                    </div>
                  </div>
                  <DemandDonut buckets={derived.buckets} />
                </div>
              </div>

              {/* TABLE + ACTIONS */}
              <div className="grid2">
                <div className="card bigCard">
                  <div className="cardHeader">
                    <div className="cardTitle">Forecast Table</div>
                  </div>
                  <ForecastTable predictions={data.predictions} />
                </div>

                <div className="card bigCard">
                  <div className="cardHeader">
                    <div className="cardTitle">Assigned Action Items</div>
                    <div className="cardSub">Placeholder</div>
                  </div>
                  <div className="emptyBox">
                    There are no action items assigned.
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
