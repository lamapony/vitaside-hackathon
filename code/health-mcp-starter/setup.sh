#!/usr/bin/env bash
# VitaSide MVP setup — one command (uses project-local .venv)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== VitaSide MVP Setup ==="
if [[ ! -d .venv ]]; then
  echo "Creating .venv..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q -U pip
python -m pip install -q -r requirements.txt
python gen_demo_data.py 2>/dev/null || true
chmod +x run-demo.sh run-demo-full.sh issue-sidecar.sh collaboration_demo.py serve-ui.sh
./issue-sidecar.sh sleep-stress-sidecar >/dev/null
./issue-sidecar.sh recovery-sidecar >/dev/null 2>&1 || true

echo ""
echo "Run MVP:     source .venv/bin/activate && ./run-demo.sh"
echo "Dashboard:   source .venv/bin/activate && ./serve-ui.sh"
echo "Hardening:   ./run-demo-full.sh --hardening"
echo "MCP config:  edit mcp-config.example.json with your paths"
echo ""
python health-pattern-mcp.py --test && echo "Setup OK"
