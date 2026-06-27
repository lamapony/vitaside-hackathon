#!/usr/bin/env bash
# Generate mcporter / Cursor MCP config from an issued sidecar manifest.
# Usage: ./write-mcp-config.sh MANIFEST.yaml [output.json]
# Env:   OMI_VAULT_PATH overrides vault derived from manifest scopes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
MANIFEST="${1:?Usage: write-mcp-config.sh MANIFEST.yaml [output.json]}"
OUT="${2:-$ROOT/mcp-config.json}"

if [[ ! -f "$MANIFEST" ]]; then
    echo "Manifest not found: $MANIFEST" >&2
    exit 1
fi

"$PYTHON" - "$MANIFEST" "$OUT" "$ROOT" "$PYTHON" <<'PY'
import json
import os
import sys
from pathlib import Path

import yaml

manifest_path = Path(sys.argv[1]).resolve()
out_path = Path(sys.argv[2])
root = Path(sys.argv[3])
default_python = sys.argv[4]

m = yaml.safe_load(manifest_path.read_text()) or {}
name = m.get("name", "vitaside-sidecar")
server_key = f"vitaside-{name}"

vault = os.environ.get("OMI_VAULT_PATH", "")
if not vault and m.get("allowed_scopes"):
    scope_path = m["allowed_scopes"][0].get("path", "")
    for suffix in ("/050 Daily Omi", "/050 Daily Omi/"):
        if scope_path.endswith(suffix.rstrip("/")):
            vault = scope_path[: -len(suffix.rstrip("/"))]
            break
    if not vault:
        vault = scope_path
if not vault:
    vault = str(root / "demo-data" / "vault")

server = m.get("server") or {}
cmd = server.get("command", default_python)
args = server.get("args") or [str(root / "health-pattern-mcp.py")]

env = {
    "VITASIDE_MANIFEST": str(manifest_path),
    "OMI_VAULT_PATH": vault,
}
if m.get("condition_pack"):
    env["VITASIDE_CONDITION_PACK"] = m["condition_pack"]

config = {
    "mcpServers": {
        server_key: {
            "command": cmd,
            "args": args,
            "env": env,
        }
    }
}

out_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {out_path}")
print(f"  server: {server_key}")
print(f"  manifest: {manifest_path}")
print(f"  vault: {vault}")
PY
