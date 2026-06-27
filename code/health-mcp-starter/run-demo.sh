#!/usr/bin/env bash
# VitaSide demo — polished narrative, not raw JSON dumps
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
BUNDLE="$ROOT/sidecars/sleep-stress-sidecar/manifest.yaml"
export VITASIDE_MANIFEST="$BUNDLE"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  VitaSide Demo — your data beats generic LLM advice      ║"
echo "╚══════════════════════════════════════════════════════════╝"

if [[ ! -d "$OMI_VAULT_PATH/050 Daily Omi/Conversations" ]] || \
   [[ -z "$(find "$OMI_VAULT_PATH/050 Daily Omi/Conversations" -name '*.md' 2>/dev/null | head -1)" ]]; then
  echo "→ Generating demo vault (90 days, planted patterns)..."
  "$PYTHON" "$ROOT/gen_demo_data.py"
fi

chmod +x "$ROOT/issue-sidecar.sh" "$ROOT/demo_briefing.py" "$ROOT/export-for-doctor.sh"
"$PYTHON" "$ROOT/seed_demo_manual_logs.py" 2>/dev/null || "$PYTHON" -c "from seed_demo_manual_logs import seed_demo_manual_logs_if_empty; seed_demo_manual_logs_if_empty()" || true
"$ROOT/issue-sidecar.sh" sleep-stress-sidecar >/dev/null
rm -f "$ROOT/audit.log"

"$PYTHON" "$ROOT/health-pattern-mcp.py" --test | tail -2

echo ""
echo "→ Running analysis on your vault..."
"$PYTHON" "$ROOT/demo_briefing.py"

echo "→ Exporting visit bundle..."
"$ROOT/export-for-doctor.sh" 2>&1 | grep -E '^(Doctor|Patient|Obsidian|Open|  "bundle)' || true

echo "→ Collaboration (Hermes context + sidecar biometrics)..."
"$PYTHON" "$ROOT/collaboration_demo.py" | tail -12

"$PYTHON" "$ROOT/test_mvp.py" | tail -3

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Demo complete — open reports in browser                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "  open $ROOT/out/vitaside-report-$(date +%Y-%m-%d).html"
echo "  open $ROOT/out/vitaside-doctor-$(date +%Y-%m-%d).html"
echo ""
