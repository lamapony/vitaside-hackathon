#!/usr/bin/env bash
# Issue a VitaSide sidecar bundle (manifest + server pointer)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
NAME="${1:-sleep-stress-sidecar}"
BUNDLE="$ROOT/sidecars/$NAME"
MANIFEST="$BUNDLE/manifest.yaml"

mkdir -p "$BUNDLE"

VAULT="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
ISSUER="${VITASIDE_ISSUER:-doctor@example.com}"
TTL="${VITASIDE_TTL:-30d}"

cat > "$MANIFEST" <<EOF
name: "$NAME"
version: "0.1"
description: "Sleep-stress-metabolism pattern sidecar for VitaSide protocol demo"
issuer: "$ISSUER"
ttl: "$TTL"
issued_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
allowed_scopes:
  - path: "$VAULT/050 Daily Omi"
    permissions: ["read"]
tools:
  - analyze_lifestyle_patterns
  - simulate_whatif
  - generate_doctor_report
  - find_correlation
  - list_data_sources
quality_gates:
  - always_include_confidence
  - always_cite_sources
  - include_disclaimer
server:
  command: python3
  args: ["$ROOT/health-pattern-mcp.py"]
EOF

echo "=== VitaSide Sidecar Issued ==="
echo "Name:   $NAME"
echo "Bundle: $BUNDLE"
echo "TTL:    $TTL"
echo ""
echo "Add to Hermes / Cursor MCP config:"
echo ""
cat <<CFG
{
  "mcpServers": {
    "vitaside-$NAME": {
      "command": "python3",
      "args": ["$ROOT/health-pattern-mcp.py"],
      "env": {
        "VITASIDE_MANIFEST": "$MANIFEST",
        "OMI_VAULT_PATH": "$VAULT"
      }
    }
  }
}
CFG
echo ""
echo "Or export and run:"
echo "  export VITASIDE_MANIFEST=\"$MANIFEST\""
echo "  export OMI_VAULT_PATH=\"$VAULT\""
echo "  python3 $ROOT/health-pattern-mcp.py"
