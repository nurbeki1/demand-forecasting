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
