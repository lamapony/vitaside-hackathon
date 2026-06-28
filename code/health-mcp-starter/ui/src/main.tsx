import React from "react";
import ReactDOM from "react-dom/client";
import { installDemoTransport } from "./demoTransport";
import App from "./App";
import "./styles.css";

// Install the live-first → mock-fallback fetch layer before any component
// renders, so the dashboard always works even if the Python API is not running.
installDemoTransport();

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
