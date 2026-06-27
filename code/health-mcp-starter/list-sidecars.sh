#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
REG="$ROOT/sidecars/registry.yaml"
echo "=== VitaSide Sidecars ==="
if [[ -f "$REG" ]]; then
  "$PYTHON" - <<PY
import yaml
from pathlib import Path
r = yaml.safe_load(Path("$REG").read_text())
for name, cfg in r.get("sidecars", {}).items():
    d = " (default)" if cfg.get("default") else ""
    print(f"  - {name}{d}: {cfg.get('description','')}")
PY
fi
echo ""
echo "Issued bundles:"
find "$ROOT/sidecars" -name manifest.yaml 2>/dev/null | while read -r m; do
  revoked=$(grep -E '^revoked_at:' "$m" 2>/dev/null || true)
  status="active"
  [[ -n "$revoked" ]] && status="REVOKED"
  echo "  [$status] $m"
done
