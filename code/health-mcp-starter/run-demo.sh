#!/usr/bin/env bash
# VitaSide one-command demo runner (Sprint 0+1)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"

echo "=== VitaSide Demo ==="
echo "Vault: $OMI_VAULT_PATH"

if [[ ! -d "$OMI_VAULT_PATH/050 Daily Omi/Conversations" ]] || \
   [[ -z "$(find "$OMI_VAULT_PATH/050 Daily Omi/Conversations" -name '*.md' 2>/dev/null | head -1)" ]]; then
  echo "Generating demo data..."
  python3 "$ROOT/gen_demo_data.py"
fi

echo ""
echo "--- 1. Self-test ---"
python3 "$ROOT/health-pattern-mcp.py" --test

echo ""
echo "--- 2. Analyze patterns ---"
python3 "$ROOT/run_demo_check.py" analyze

echo ""
echo "--- 3. What-if simulation ---"
python3 "$ROOT/run_demo_check.py" whatif

echo ""
echo "=== Demo OK ==="
