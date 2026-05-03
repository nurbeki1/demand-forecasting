import { useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import ForecastPanel from "../components/forecast/ForecastPanel";
import ModelComparePanel from "../components/forecast/ModelComparePanel";
import "../styles/dashboard.css";

export default function ForecastWorkspacePage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();

  const tab = searchParams.get("tab") === "compare" ? "compare" : "forecast";

  const setTab = useCallback(
    (next) => {
      setSearchParams(
        (prev) => {
          const p = new URLSearchParams(prev);
          if (next === "forecast") {
            p.delete("tab");
          } else {
            p.set("tab", "compare");
          }
          return p;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  return (
    <div className="appShell">
      <Sidebar />

      <div className="main">
        <Topbar />

        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">{t("forecast.workspaceTitle")}</div>
              <div className="subtitle">{t("forecast.workspaceSubtitle")}</div>
            </div>
          </div>

          <div className="forecast-workspace-tabs" role="tablist" aria-label={t("forecast.workspaceTitle")}>
            <button
              type="button"
              role="tab"
              aria-selected={tab === "forecast"}
              className={`forecast-workspace-tab${tab === "forecast" ? " forecast-workspace-tab--active" : ""}`}
              onClick={() => setTab("forecast")}
            >
              {t("forecast.tabForecast")}
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={tab === "compare"}
              className={`forecast-workspace-tab${tab === "compare" ? " forecast-workspace-tab--active" : ""}`}
              onClick={() => setTab("compare")}
            >
              {t("forecast.tabCompare")}
            </button>
          </div>

          <div role="tabpanel" id={`forecast-tab-${tab}`} aria-labelledby={`tab-${tab}`}>
            {tab === "forecast" ? <ForecastPanel /> : <ModelComparePanel />}
          </div>
        </div>
      </div>
    </div>
  );
}
