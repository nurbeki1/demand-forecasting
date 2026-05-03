// API Configuration — FastAPI root (no trailing slash, no trailing /api).

const PRODUCTION_DEFAULT = "https://demand-forecasting-production-c886.up.railway.app";
const DEV_LOCAL_DEFAULT = "http://127.0.0.1:8000";

function normalizeApiBase(raw) {
  if (raw == null) return "";
  let u = String(raw).trim();
  if (!u) return "";
  u = u.replace(/\/+$/, "");
  // Avoid .../api/auth/... when the server exposes /auth at the root.
  if (u.endsWith("/api")) {
    u = u.slice(0, -4).replace(/\/+$/, "");
  }
  return u;
}

const viteExplicit =
  import.meta.env.VITE_API_URL != null && String(import.meta.env.VITE_API_URL).trim() !== "";

const resolvedRaw = viteExplicit
  ? import.meta.env.VITE_API_URL
  : import.meta.env.DEV
    ? DEV_LOCAL_DEFAULT
    : PRODUCTION_DEFAULT;

export const API_URL = normalizeApiBase(resolvedRaw);
