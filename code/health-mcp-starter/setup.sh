#!/usr/bin/env bash
# VitaSide MVP setup — one command
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== VitaSide MVP Setup ==="
python3 -m pip install -q -r requirements.txt
python3 gen_demo_data.py 2>/dev/null || true
chmod +x run-demo.sh run-demo-full.sh issue-sidecar.sh collaboration_demo.py
./issue-sidecar.sh sleep-stress-sidecar >/dev/null
./issue-sidecar.sh recovery-sidecar >/dev/null 2>&1 || true

echo ""
echo "Run MVP:     ./run-demo.sh"
echo "Hardening:   ./run-demo-full.sh --hardening"
echo "MCP config:  edit mcp-config.example.json with your paths"
echo ""
python3 health-pattern-mcp.py --test && echo "Setup OK"
