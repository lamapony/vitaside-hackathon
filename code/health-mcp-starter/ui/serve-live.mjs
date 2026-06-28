/* VitaSide — stable live server for the built dist.
 *
 * Serves ui/dist (SPA, with index.html fallback) and proxies /api/* to the
 * real local backend (default http://127.0.0.1:8787). No dependencies — uses
 * only Node built-ins. Pair with an ngrok tunnel for a public LIVE demo URL.
 *
 *   npm run build          # build the dist (no VITE_DEMO_LOCK)
 *   node serve-live.mjs    # serves dist + /api proxy on http://127.0.0.1:4180
 *   ngrok http 4180        # public URL -> live app with real backend
 */
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.resolve(__dirname, "dist");
const API_TARGET = process.env.VITASIDE_API_URL || "http://127.0.0.1:8787";
const PORT = process.env.PORT ? Number(process.env.PORT) : 4180;

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".ico": "image/x-icon",
  ".map": "application/json",
  ".txt": "text/plain; charset=utf-8",
};

function sendFile(res, filePath) {
  res.writeHead(200, { "Content-Type": MIME[path.extname(filePath)] || "application/octet-stream" });
  fs.createReadStream(filePath).pipe(res);
}

function serveStatic(req, res) {
  let urlPath = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (urlPath === "/") urlPath = "/index.html";
  let filePath = path.join(DIST, urlPath);
  if (!filePath.startsWith(DIST)) {
    res.writeHead(403);
    res.end("forbidden");
    return;
  }
  fs.stat(filePath, (err, st) => {
    if (!err && st.isFile()) {
      sendFile(res, filePath);
    } else {
      // SPA fallback for client-side routing
      const idx = path.join(DIST, "index.html");
      fs.stat(idx, (e2, s2) => {
        if (e2 || !s2.isFile()) {
          res.writeHead(404);
          res.end("dist not built. Run: npm run build");
        } else {
          res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
          fs.createReadStream(idx).pipe(res);
        }
      });
    }
  });
}

function proxy(req, res) {
  const u = new URL(req.url, API_TARGET);
  const opts = {
    method: req.method,
    hostname: u.hostname,
    port: u.port,
    path: u.pathname + u.search,
    headers: { ...req.headers, host: u.host },
  };
  const up = http.request(opts, (upRes) => {
    res.writeHead(upRes.statusCode || 502, upRes.headers);
    upRes.pipe(res);
  });
  up.on("error", () => {
    res.writeHead(502, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "api_unreachable", message: "VitaSide backend not running on " + API_TARGET }));
  });
  req.pipe(up);
}

const server = http.createServer((req, res) => {
  if (req.url.startsWith("/api/")) proxy(req, res);
  else serveStatic(req, res);
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`VitaSide live server on http://127.0.0.1:${PORT}  (dist + /api -> ${API_TARGET})`);
});
