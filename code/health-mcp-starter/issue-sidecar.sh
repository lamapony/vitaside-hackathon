#!/usr/bin/env bash
# Issue a VitaSide sidecar bundle (manifest + server pointer)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
NAME="${1:-sleep-stress-sidecar}"
BUNDLE="$ROOT/sidecars/$NAME"
MANIFEST="$BUNDLE/manifest.yaml"
CONDITION_PACK=""
EXTRA_TOOLS=""

case "$NAME" in
  recovery-sidecar)
    DESC="Post-viral / fatigue recovery pattern sidecar"
    ;;
  bipolar-monitoring-sidecar)
    DESC="Bipolar mood, sleep & medication self-monitoring sidecar"
    CONDITION_PACK="bipolar"
    EXTRA_TOOLS="
  - list_condition_packs
  - track_condition
  - condition_report"
    ;;
  migraine-tracking-sidecar)
    DESC="Migraine episodes, acute meds & trigger pattern sidecar"
    CONDITION_PACK="migraine"
    EXTRA_TOOLS="
  - list_condition_packs
  - track_condition
  - condition_report"
    ;;
  azure-hybrid-sidecar)
    DESC="Local-first patterns + optional Azure OpenAI / share boost"
    EXTRA_TOOLS="
  - get_azure_contract
  - preview_azure_payload
  - azure_enhance_insight
  - azure_share_report"
    AZURE_BLOCK="
enable_azure_boost: true
azure:
  allowed_operations:
    - enhance_insight
    - share_report
  data_policy:
    max_excerpt_chars: 140
    anonymize_by_default: true"
    ;;
  *)
    DESC="Sleep-stress-metabolism pattern sidecar for VitaSide protocol demo"
    ;;
esac

mkdir -p "$BUNDLE"

VAULT="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
ISSUER="${VITASIDE_ISSUER:-doctor@example.com}"
TTL="${VITASIDE_TTL:-30d}"

CONDITION_LINE=""
if [[ -n "$CONDITION_PACK" ]]; then
  CONDITION_LINE="condition_pack: \"$CONDITION_PACK\""
fi
AZURE_BLOCK="${AZURE_BLOCK:-}"

cat > "$MANIFEST" <<EOF
name: "$NAME"
version: "0.1"
description: "$DESC"
issuer: "$ISSUER"
ttl: "$TTL"
issued_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
$CONDITION_LINE
$AZURE_BLOCK
allowed_scopes:
  - path: "$VAULT/050 Daily Omi"
    permissions: ["read"]

doctor_device:
  enabled: true
  export_paths:
    - "{{vault}}/Doctor Device/export.csv"
    - "{{vault}}/Apple Health/export.xml"

collection_window:
  enabled: true
  ttl: "14d"
  started_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

tools:
  - health_check
  - analyze_lifestyle_patterns
  - simulate_whatif
  - generate_doctor_report
  - build_visit_packet
  - generate_visit_questions
  - collaborative_insight
  - find_correlation
  - list_data_sources
  - list_multi_sources
  - monitor_device_window
  - export_doctor_handoff_print$EXTRA_TOOLS
quality_gates:
  - always_include_confidence
  - always_cite_sources
  - include_disclaimer
server:
  command: $PYTHON
  args: ["$ROOT/health-pattern-mcp.py"]
EOF

echo "=== VitaSide Sidecar Issued ==="
echo "Name:   $NAME"
echo "Bundle: $BUNDLE"
echo "TTL:    $TTL"
[[ -n "$CONDITION_PACK" ]] && echo "Pack:   $CONDITION_PACK"
echo ""
echo "Add to Hermes / Cursor MCP config:"
echo ""
ENV_BLOCK=""
if [[ -n "$CONDITION_PACK" ]]; then
  ENV_BLOCK=",
        \"VITASIDE_CONDITION_PACK\": \"$CONDITION_PACK\""
fi
cat <<CFG
{
  "mcpServers": {
    "vitaside-$NAME": {
      "command": "$PYTHON",
      "args": ["$ROOT/health-pattern-mcp.py"],
      "env": {
        "VITASIDE_MANIFEST": "$MANIFEST",
        "OMI_VAULT_PATH": "$VAULT"$ENV_BLOCK
      }
    }
  }
}
CFG
echo ""
echo "Or export and run:"
echo "  export VITASIDE_MANIFEST=\"$MANIFEST\""
echo "  export OMI_VAULT_PATH=\"$VAULT\""
[[ -n "$CONDITION_PACK" ]] && echo "  export VITASIDE_CONDITION_PACK=\"$CONDITION_PACK\""
echo "  $PYTHON $ROOT/health-pattern-mcp.py"
