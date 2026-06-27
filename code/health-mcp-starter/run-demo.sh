#!/usr/bin/env bash
# VitaSide one-command demo runner
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"

echo "=== VitaSide Demo ==="

if [[ ! -d "$OMI_VAULT_PATH/050 Daily Omi/Conversations" ]] || \
   [[ -z "$(find "$OMI_VAULT_PATH/050 Daily Omi/Conversations" -name '*.md' 2>/dev/null | head -1)" ]]; then
  echo "Generating demo data..."
  python3 "$ROOT/gen_demo_data.py"
fi

echo ""
echo "--- 0. Issue sidecar ---"
chmod +x "$ROOT/issue-sidecar.sh"
export VITASIDE_MANIFEST="$("$ROOT/issue-sidecar.sh" sleep-stress-sidecar 2>&1 | awk -F'"' '/VITASIDE_MANIFEST=/ {print $2}')"
# Re-issue cleanly to set env from bundle path
BUNDLE="$ROOT/sidecars/sleep-stress-sidecar/manifest.yaml"
export VITASIDE_MANIFEST="$BUNDLE"
"$ROOT/issue-sidecar.sh" sleep-stress-sidecar >/dev/null
echo "Manifest: $VITASIDE_MANIFEST"

rm -f "$ROOT/audit.log"

echo ""
echo "--- 1. Self-test ---"
python3 "$ROOT/health-pattern-mcp.py" --test

echo ""
echo "--- 2. Sidecar status ---"
python3 "$ROOT/run_demo_check.py" sidecar

echo ""
echo "--- 3. Analyze (with citations) ---"
python3 "$ROOT/run_demo_check.py" analyze

echo ""
echo "--- 4. What-if ---"
python3 "$ROOT/run_demo_check.py" whatif

echo ""
echo "--- 5. HTML report ---"
python3 "$ROOT/run_demo_check.py" html

echo ""
echo "--- 6. Collaboration ---"
python3 "$ROOT/collaboration_demo.py"

echo ""
echo "--- 7. Audit log ---"
wc -l "$ROOT/audit.log" | awk '{print "audit_lines=" $1}'

echo ""
echo "=== Demo OK ==="
echo "Hardening: ./run-demo-full.sh --hardening"
