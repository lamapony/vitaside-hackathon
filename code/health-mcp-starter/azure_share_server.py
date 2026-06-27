#!/usr/bin/env python3
"""
Local demo Azure Function simulator for share_report.
Run: python azure_share_server.py
Then set AZURE_FUNCTION_SHARE_URL=http://localhost:8765/share

It stores minimized payload in ./out/share/ with TTL and returns a local file:// or http link.
For real Azure: deploy this logic as Azure Function (HTTP trigger) + Blob Storage.
"""

import json
import os
import time
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from pathlib import Path

SHARE_DIR = Path("out/share")
SHARE_DIR.mkdir(parents=True, exist_ok=True)

class ShareHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/share":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except Exception:
            self.send_error(400, "bad json")
            return

        payload = data.get("payload", {})
        ttl = int(data.get("ttl_hours", 48))

        fp = payload.get("data_minimization", {}).get("payload_fingerprint", "unknown")
        now = datetime.utcnow()
        expires = now + timedelta(hours=ttl)

        # Save the payload (minimized by contract)
        fname = f"share-{fp}-{now.strftime('%Y%m%d-%H%M')}.json"
        fpath = SHARE_DIR / fname
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump({
                "payload": payload,
                "received_at": now.isoformat() + "Z",
                "expires_at": expires.isoformat() + "Z",
                "ttl_hours": ttl,
            }, f, ensure_ascii=False, indent=2)

        # For demo: local file link (in real use: https link to static or function that serves it)
        link = f"file://{fpath.absolute()}"

        resp = {
            "source": "local_demo_share",
            "share_url": link,
            "expires_at": expires.isoformat() + "Z",
            "upload_token_preview": f"demo-{fp[:8]}",
            "note": "Local demo only. Deploy equivalent to Azure Functions + Blob for real links.",
            "fingerprint": fp,
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(resp, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        print(f"[{datetime.now().isoformat()}] {args[0]}")

if __name__ == "__main__":
    port = 8765
    print(f"Starting local Azure share simulator on http://localhost:{port}/share")
    print("Set env: export AZURE_FUNCTION_SHARE_URL=http://localhost:8765/share")
    print("Then in MCP call azure_share_report with consent.")
    server = HTTPServer(("", port), ShareHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")