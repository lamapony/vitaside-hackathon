import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const base = process.env.VITE_BASE_PATH ?? "/";

export default defineConfig({
  base,
  plugins: [react()],
  server: {
    port: 5173,
    allowedHosts: true,
    proxy: {
      "/api": `http://127.0.0.1:${process.env.VITASIDE_API_PORT ?? "8787"}`
    }
  },
  preview: {
    allowedHosts: true
  }
});
