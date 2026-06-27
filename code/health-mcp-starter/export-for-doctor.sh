#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
export VITASIDE_MANIFEST="${VITASIDE_MANIFEST:-$ROOT/sidecars/sleep-stress-sidecar/manifest.yaml}"
ANON_FLAG="False"
[[ "${1:-}" == "--anon" ]] && ANON_FLAG="True"
cd "$ROOT"
python3 -c "
import importlib.util, json
from pathlib import Path
spec = importlib.util.spec_from_file_location('m', Path('health-pattern-mcp.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
r = m.export_visit_bundle(anonymize=$ANON_FLAG)
print(json.dumps(r, indent=2))
"
echo "Open: open out/vitaside-doctor-$(date +%Y-%m-%d).html"
