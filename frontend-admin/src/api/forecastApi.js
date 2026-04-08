import { getToken } from "./authApi";
import { API_URL } from "../config";

const BASE_URL = API_URL;

function getHeaders() {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function getForecast({ productId, storeId, horizonDays }) {
  const params = new URLSearchParams({
    product_id: productId,
    horizon_days: String(horizonDays),
  });

  if (storeId) params.set("store_id", storeId);

  const url = `${BASE_URL}/forecast?${params.toString()}`;

  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Failed to fetch forecast (${res.status}). ${text}`);
  }
  return res.json();
}

/**
 * Get forecast with Decision Assistant insights and trust layer (v2)
 */
export async function getForecastV2({ productId, storeId, horizonDays }) {
  const params = new URLSearchParams({
    product_id: productId,
    horizon_days: String(horizonDays),
  });

  if (storeId) params.set("store_id", storeId);

  const url = `${BASE_URL}/forecast/v2?${params.toString()}`;

  const res = await fetch(url, { headers: getHeaders() });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Failed to fetch forecast v2 (${res.status}). ${text}`);
  }
  return res.json();
}

export async function getProducts() {
  const res = await fetch(`${BASE_URL}/products`, { headers: getHeaders() });
  if (!res.ok) {
    throw new Error(`Failed to fetch products (${res.status})`);
  }
  return res.json();
}

export async function getHistory(productId, { storeId, limit = 100, offset = 0 } = {}) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  if (storeId) params.set("store_id", storeId);

  const res = await fetch(`${BASE_URL}/history/${productId}?${params}`, {
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch history (${res.status})`);
  }
  return res.json();
}

export async function uploadDataset(file) {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);

  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

export async function getModelCache() {
  const res = await fetch(`${BASE_URL}/models/cache`, { headers: getHeaders() });
  if (!res.ok) {
    throw new Error(`Failed to fetch cache info (${res.status})`);
  }
  return res.json();
}

export async function clearModelCache() {
  const res = await fetch(`${BASE_URL}/models/cache`, {
    method: "DELETE",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to clear cache (${res.status})`);
  }
  return res.json();
}

export async function retrainModel(productId, storeId) {
  const params = new URLSearchParams();
  if (storeId) params.set("store_id", storeId);

  const res = await fetch(`${BASE_URL}/models/retrain/${productId}?${params}`, {
    method: "POST",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to retrain model (${res.status})`);
  }
  return res.json();
}

// =============================================================================
// EXECUTIVE DASHBOARD APIs
// =============================================================================

export async function getExecutiveDashboard() {
  const res = await fetch(`${BASE_URL}/dashboard/executive`, {
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch executive dashboard (${res.status})`);
  }
  return res.json();
}

export async function getDataOperationsStatus() {
  const res = await fetch(`${BASE_URL}/dashboard/data-operations`, {
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch data operations status (${res.status})`);
  }
  return res.json();
}

export async function getAlerts({ severity, alertType, limit = 20 } = {}) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (severity) params.set("severity", severity);
  if (alertType) params.set("alert_type", alertType);

  const res = await fetch(`${BASE_URL}/dashboard/alerts?${params}`, {
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch alerts (${res.status})`);
  }
  return res.json();
}

export async function runScenarioAnalysis(scenario) {
  const res = await fetch(`${BASE_URL}/dashboard/scenario`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(scenario),
  });
  if (!res.ok) {
    throw new Error(`Failed to run scenario analysis (${res.status})`);
  }
  return res.json();
}

export async function exploreForecast(request) {
  const res = await fetch(`${BASE_URL}/dashboard/forecast-explorer`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    throw new Error(`Failed to explore forecasts (${res.status})`);
  }
  return res.json();
}

// =============================================================================
// REPORT DOWNLOAD APIs
// =============================================================================

async function downloadBlob(url) {
  const headers = getHeaders();
  delete headers["Content-Type"];
  const res = await fetch(url, { headers });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Download failed (${res.status}). ${text}`);
  }
  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition") || "";
  const match = disposition.match(/filename=(.+)/);
  const filename = match ? match[1] : "report.xlsx";
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
}

export async function downloadDailyReport() {
  await downloadBlob(`${BASE_URL}/reports/daily`);
}

export async function downloadForecastReport(productId, horizonDays = 7) {
  const params = new URLSearchParams({ horizon_days: String(horizonDays) });
  await downloadBlob(`${BASE_URL}/reports/forecast/${productId}?${params}`);
}

export async function downloadAnalyticsReport() {
  await downloadBlob(`${BASE_URL}/reports/analytics`);
}

export async function downloadKzMarketReport({ productName, wholesalePrice, markupPercent = 25 }) {
  const params = new URLSearchParams({
    product_name: productName,
    wholesale_price: String(wholesalePrice),
    markup_percent: String(markupPercent),
  });
  await downloadBlob(`${BASE_URL}/reports/kz-market?${params}`);
}

// =============================================================================
// FORECAST COMPARISON APIs
// =============================================================================

export async function compareForecast({ productId, storeId, horizonDays = 7 }) {
  const params = new URLSearchParams({
    product_id: productId,
    horizon_days: String(horizonDays),
  });
  if (storeId) params.set("store_id", storeId);

  const res = await fetch(`${BASE_URL}/forecast/compare?${params}`, {
    headers: getHeaders(),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Comparison failed (${res.status}). ${text}`);
  }
  return res.json();
}

export async function acceptComparison(productId, storeId) {
  const params = new URLSearchParams({ product_id: productId });
  if (storeId) params.set("store_id", storeId);

  const res = await fetch(`${BASE_URL}/forecast/compare/accept?${params}`, {
    method: "POST",
    headers: getHeaders(),
  });
  if (!res.ok) {
    throw new Error(`Accept failed (${res.status})`);
  }
  return res.json();
}

// =============================================================================
// SEARCH API
// =============================================================================

export async function searchProducts(query, limit = 10) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  const res = await fetch(`${BASE_URL}/search?${params}`, { headers: getHeaders() });
  if (!res.ok) {
    throw new Error(`Search failed (${res.status})`);
  }
  return res.json();
}
