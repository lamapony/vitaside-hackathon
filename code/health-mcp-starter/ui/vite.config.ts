import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
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
