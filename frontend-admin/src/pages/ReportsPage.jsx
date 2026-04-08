import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import {
  getProducts,
  downloadDailyReport,
  downloadForecastReport,
  downloadAnalyticsReport,
  downloadKzMarketReport,
} from "../api/forecastApi";
import "../styles/reports.css";

function ReportCard({ title, description, icon, children, onDownload, downloading }) {
  const { t } = useTranslation();
  return (
    <div className="report-card">
      <div className="report-card-header">
        <span className="report-card-icon">{icon}</span>
        <div>
          <div className="report-card-title">{title}</div>
          <div className="report-card-desc">{description}</div>
        </div>
      </div>
      <div className="report-card-body">{children}</div>
      <button
        className="btn report-download-btn"
        onClick={onDownload}
        disabled={downloading}
      >
        {downloading ? t('common.loading') : t('reports.download')}
      </button>
    </div>
  );
}

export default function ReportsPage() {
  const { t } = useTranslation();
  const [products, setProducts] = useState([]);
  const [downloading, setDownloading] = useState({});

  // Forecast report params
  const [forecastProduct, setForecastProduct] = useState("");
  const [forecastHorizon, setForecastHorizon] = useState(7);

  // KZ report params
  const [kzProductName, setKzProductName] = useState("");
  const [kzWholesalePrice, setKzWholesalePrice] = useState("");
  const [kzMarkup, setKzMarkup] = useState(25);

  useEffect(() => {
    getProducts()
      .then((data) => {
        setProducts(data);
        if (data.length > 0) setForecastProduct(data[0].product_id);
      })
      .catch(() => {});
  }, []);

  async function handleDownload(key, fn) {
    setDownloading((d) => ({ ...d, [key]: true }));
    try {
      await fn();
      toast.success(t('reports.downloadSuccess', 'Report downloaded!'));
    } catch (err) {
      toast.error(err.message || t('reports.downloadError', 'Download failed'));
    } finally {
      setDownloading((d) => ({ ...d, [key]: false }));
    }
  }

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">{t('reports.title')}</div>
              <div className="subtitle">{t('reports.subtitle', 'Download Excel reports for your data')}</div>
            </div>
          </div>

          <div className="reports-grid">
            {/* Daily Report */}
            <ReportCard
              title={t('reports.daily')}
              description={t('reports.dailyDesc', 'Overview of daily metrics, top products, and alerts')}
              icon="📅"
              onDownload={() => handleDownload("daily", downloadDailyReport)}
              downloading={downloading.daily}
            />

            {/* Forecast Report */}
            <ReportCard
              title={t('reports.forecast')}
              description={t('reports.forecastDesc', 'Detailed forecast analysis for a specific product')}
              icon="📊"
              onDownload={() => {
                if (!forecastProduct) {
                  toast.error(t('reports.selectProductFirst', 'Select a product first'));
                  return;
                }
                handleDownload("forecast", () =>
                  downloadForecastReport(forecastProduct, forecastHorizon)
                );
              }}
              downloading={downloading.forecast}
            >
              <div className="report-params">
                <div className="field">
                  <label>{t('common.product')}</label>
                  <select
                    value={forecastProduct}
                    onChange={(e) => setForecastProduct(e.target.value)}
                  >
                    {products.map((p) => (
                      <option key={p.product_id} value={p.product_id}>
                        {p.product_id}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="field">
                  <label>{t('forecast.horizon', 'Horizon (days)')}</label>
                  <input
                    type="number"
                    min={1}
                    max={30}
                    value={forecastHorizon}
                    onChange={(e) => setForecastHorizon(Number(e.target.value))}
                  />
                </div>
              </div>
            </ReportCard>

            {/* Analytics Report */}
            <ReportCard
              title={t('reports.analytics')}
              description={t('reports.analyticsDesc', 'Comprehensive analytics including trends and categories')}
              icon="📈"
              onDownload={() => handleDownload("analytics", downloadAnalyticsReport)}
              downloading={downloading.analytics}
            />

            {/* KZ Market Report */}
            <ReportCard
              title={t('reports.kzMarket')}
              description={t('reports.kzMarketDesc', 'City-by-city profitability analysis for Kazakhstan')}
              icon="🇰🇿"
              onDownload={() => {
                if (!kzProductName || !kzWholesalePrice) {
                  toast.error(t('reports.fillKzFields', 'Fill in product name and price'));
                  return;
                }
                handleDownload("kz", () =>
                  downloadKzMarketReport({
                    productName: kzProductName,
                    wholesalePrice: Number(kzWholesalePrice),
                    markupPercent: kzMarkup,
                  })
                );
              }}
              downloading={downloading.kz}
            >
              <div className="report-params">
                <div className="field">
                  <label>{t('kz.productName', 'Product Name')}</label>
                  <input
                    type="text"
                    value={kzProductName}
                    onChange={(e) => setKzProductName(e.target.value)}
                    placeholder={t('kz.productName', 'Product Name')}
                  />
                </div>
                <div className="field">
                  <label>{t('kz.wholesale')}</label>
                  <input
                    type="number"
                    min={0}
                    value={kzWholesalePrice}
                    onChange={(e) => setKzWholesalePrice(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
                <div className="field">
                  <label>{t('kz.markup')} (%)</label>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={kzMarkup}
                    onChange={(e) => setKzMarkup(Number(e.target.value))}
                  />
                </div>
              </div>
            </ReportCard>
          </div>
        </div>
      </div>
    </div>
  );
}
