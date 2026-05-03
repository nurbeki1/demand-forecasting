import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    headers: {
      // Avoid stale JS/CSS when iterating locally (browser aggressive cache).
      "Cache-Control": "no-store",
    },
  },
  preview: {
    headers: {
      "Cache-Control": "no-store",
    },
  },
});
