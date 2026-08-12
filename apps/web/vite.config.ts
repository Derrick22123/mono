import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  envPrefix: "VITE_",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    // Optional: proxy /agui and /v1 to backend when VITE_API_BASE_URL unset in dev
    // Prefer explicit VITE_API_BASE_URL per spec FR-006
  },
});
