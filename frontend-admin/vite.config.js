import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // Тек осы порт: екінші vite 5174-ке секіріп ескі бума көрініп қалмасын.
    // Егер «Port already in use» болса: екінші терминалдағы eski `npm run dev` процесін тоқтатыңыз.
    port: 5173,
    strictPort: true,
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
