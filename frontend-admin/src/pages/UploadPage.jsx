import { useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { uploadDataset, clearModelCache, getModelCache } from "../api/forecastApi";

export default function UploadPage() {
  const { t } = useTranslation();
  const [isDragOver, setIsDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [cacheInfo, setCacheInfo] = useState(null);

  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;

    if (!file.name.endsWith(".csv")) {
      toast.error(t('upload.pleaseUploadCsv'));
      return;
    }

    setLoading(true);
    setSuccess(null);

    try {
      const result = await uploadDataset(file);
      setSuccess(result);
      toast.success(result.message || t('upload.uploadSuccess'));
      await loadCacheInfo();
    } catch (err) {
      toast.error(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  async function loadCacheInfo() {
    try {
      const info = await getModelCache();
      setCacheInfo(info);
    } catch {
      // ignore
    }
  }

  async function handleClearCache() {
    try {
      await clearModelCache();
      await loadCacheInfo();
      toast.success(t('upload.cacheClearedSuccess'));
    } catch (err) {
      toast.error(err.message);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }

  function handleDragOver(e) {
    e.preventDefault();
    setIsDragOver(true);
  }

  function handleDragLeave() {
    setIsDragOver(false);
  }

  function handleInputChange(e) {
    const file = e.target.files[0];
    handleFile(file);
  }

  return (
    <div className="appShell">
      <Sidebar />
      <div className="main">
        <Topbar />
        <div className="content">
          <div className="headerRow">
            <div>
              <div className="title">{t('upload.title')}</div>
              <div className="subtitle">{t('upload.subtitle')}</div>
            </div>
          </div>

          <div className="card">
            <div className="cardHeader">
              <div className="cardTitle">{t('upload.uploadDataset')}</div>
            </div>

            <div
              className={`uploadZone ${isDragOver ? "dragover" : ""}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => inputRef.current?.click()}
            >
              <div className="uploadIcon">+</div>
              <div className="uploadText">
                {loading ? t('upload.uploading') : t('upload.dropHere')}
              </div>
              <div className="uploadHint">
                {t('upload.requiredColumns')}
              </div>
              <input
                ref={inputRef}
                type="file"
                accept=".csv"
                className="uploadInput"
                onChange={handleInputChange}
              />
            </div>

            {success && (
              <div className="successBox">
                {success.message}
                {success.records && (
                  <div style={{ marginTop: 8 }}>
                    Records loaded: <strong>{success.records}</strong>
                  </div>
                )}
                {success.models_cleared !== undefined && (
                  <div>Models cleared: <strong>{success.models_cleared}</strong></div>
                )}
              </div>
            )}
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <div className="cardHeader">
              <div>
                <div className="cardTitle">{t('upload.modelCache')}</div>
                <div className="cardSub">{t('upload.cachedModels')}</div>
              </div>
              <button className="btn" onClick={handleClearCache}>
                {t('upload.clearCache')}
              </button>
            </div>

            {cacheInfo ? (
              <div>
                <div style={{ marginBottom: 12 }}>
                  {t('upload.cachedModelsCount')} <strong>{cacheInfo.cached_models}</strong>
                </div>

                {cacheInfo.cached_models > 0 && (
                  <table className="table">
                    <thead>
                      <tr>
                        <th>{t('upload.modelKey')}</th>
                        <th>{t('forecast.metrics.mae')}</th>
                        <th>{t('forecast.metrics.rmse')}</th>
                        <th>{t('forecast.metrics.r2')}</th>
                        <th>{t('upload.trainedAt')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(cacheInfo.details).map(([key, val]) => (
                        <tr key={key}>
                          <td>{key}</td>
                          <td>{val.metrics.mae.toFixed(2)}</td>
                          <td>{val.metrics.rmse.toFixed(2)}</td>
                          <td>{val.metrics.r2.toFixed(4)}</td>
                          <td>{new Date(val.trained_at).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            ) : (
              <button className="btn" onClick={loadCacheInfo}>
                {t('upload.loadCacheInfo')}
              </button>
            )}
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <div className="cardHeader">
              <div className="cardTitle">{t('upload.csvFormat')}</div>
            </div>
            <div style={{ color: "#4a6580", lineHeight: 1.8, fontFamily: "'Space Mono', monospace", fontSize: "13px" }}>
              <p style={{ color: "#e8f4fc", marginBottom: "12px" }}>{t('upload.csvFormatDesc')}</p>
              <ul style={{ paddingLeft: "20px" }}>
                <li><span style={{ color: "#00e5ff" }}>Date</span> - {t('upload.dateFormat')}</li>
                <li><span style={{ color: "#00e5ff" }}>Product ID</span> - {t('upload.productIdFormat')}</li>
                <li><span style={{ color: "#00e5ff" }}>Store ID</span> - Store identifier (optional)</li>
                <li><span style={{ color: "#00e5ff" }}>Demand Forecast</span> - {t('upload.demandFormat')}</li>
                <li><span style={{ color: "#00e5ff" }}>Category</span> - Product category</li>
                <li><span style={{ color: "#00e5ff" }}>Region</span> - Geographic region</li>
                <li><span style={{ color: "#00e5ff" }}>Price</span> - Product price</li>
                <li><span style={{ color: "#00e5ff" }}>Inventory Level</span> - Current inventory</li>
                <li><span style={{ color: "#00e5ff" }}>Weather Condition</span> - Weather</li>
                <li><span style={{ color: "#00e5ff" }}>Seasonality</span> - Season</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
