import { useState, useRef } from "react";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { uploadDataset, clearModelCache, getModelCache } from "../api/forecastApi";

export default function UploadPage() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);
  const [cacheInfo, setCacheInfo] = useState(null);

  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;

    if (!file.name.endsWith(".csv")) {
      setError("Please upload a CSV file");
      return;
    }

    setLoading(true);
    setError("");
    setSuccess(null);

    try {
      const result = await uploadDataset(file);
      setSuccess(result);
      await loadCacheInfo();
    } catch (err) {
      setError(err.message || "Upload failed");
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
      setSuccess({ message: "Cache cleared successfully" });
    } catch (err) {
      setError(err.message);
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
              <div className="title">Upload Data</div>
              <div className="subtitle">Upload a new CSV dataset</div>
            </div>
          </div>

          <div className="card">
            <div className="cardHeader">
              <div className="cardTitle">Upload Dataset</div>
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
                {loading ? "Uploading..." : "Drop CSV file here or click to browse"}
              </div>
              <div className="uploadHint">
                Required columns: Date, Product ID, Demand Forecast
              </div>
              <input
                ref={inputRef}
                type="file"
                accept=".csv"
                className="uploadInput"
                onChange={handleInputChange}
              />
            </div>

            {error && <div className="errorBox">{error}</div>}

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
                <div className="cardTitle">Model Cache</div>
                <div className="cardSub">Cached ML models for faster predictions</div>
              </div>
              <button className="btn" onClick={handleClearCache}>
                Clear Cache
              </button>
            </div>

            {cacheInfo ? (
              <div>
                <div style={{ marginBottom: 12 }}>
                  Cached models: <strong>{cacheInfo.cached_models}</strong>
                </div>

                {cacheInfo.cached_models > 0 && (
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Model Key</th>
                        <th>MAE</th>
                        <th>RMSE</th>
                        <th>R2</th>
                        <th>Trained At</th>
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
                Load Cache Info
              </button>
            )}
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <div className="cardHeader">
              <div className="cardTitle">CSV Format Requirements</div>
            </div>
            <div style={{ color: "#4a6580", lineHeight: 1.8, fontFamily: "'Space Mono', monospace", fontSize: "13px" }}>
              <p style={{ color: "#e8f4fc", marginBottom: "12px" }}>Your CSV file should contain the following columns:</p>
              <ul style={{ paddingLeft: "20px" }}>
                <li><span style={{ color: "#00e5ff" }}>Date</span> - Date in YYYY-MM-DD format</li>
                <li><span style={{ color: "#00e5ff" }}>Product ID</span> - Product identifier (e.g., P0001)</li>
                <li><span style={{ color: "#00e5ff" }}>Store ID</span> - Store identifier (optional)</li>
                <li><span style={{ color: "#00e5ff" }}>Demand Forecast</span> - Forecasted demand (target variable)</li>
                <li><span style={{ color: "#00e5ff" }}>Category</span> - Product category</li>
                <li><span style={{ color: "#00e5ff" }}>Region</span> - Geographic region</li>
                <li><span style={{ color: "#00e5ff" }}>Price</span> - Product price</li>
                <li><span style={{ color: "#00e5ff" }}>Inventory Level</span> - Current inventory</li>
                <li><span style={{ color: "#00e5ff" }}>Weather Condition</span> - Weather (Sunny, Rainy, etc.)</li>
                <li><span style={{ color: "#00e5ff" }}>Seasonality</span> - Season (Spring, Summer, etc.)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
