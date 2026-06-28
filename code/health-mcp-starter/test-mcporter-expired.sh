#!/usr/bin/env bash
# VIT-24 VERIFY: mcporter must fail closed when manifest is expired.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

MANIFEST="$TMP/manifest.yaml"
cat > "$MANIFEST" <<EOF
name: expired-mcporter-test
version: "0.1"
issuer: test@local
ttl: "1h"
issued_at: "2020-01-01T00:00:00Z"
allowed_scopes:
  - path: "$ROOT/demo-data/vault/050 Daily Omi"
    permissions: ["read"]
tools:
  - analyze_lifestyle_patterns
EOF

export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
export VITASIDE_MANIFEST="$MANIFEST"
SERVER_STDIO="$PYTHON $ROOT/health-pattern-mcp.py"

set +e
OUT=$(npx mcporter call --stdio "$SERVER_STDIO" analyze_lifestyle_patterns --timeout 60000 2>&1)
CODE=$?
set -e

if [[ "$CODE" -eq 0 ]] && ! echo "$OUT" | grep -qiE 'expired|error|Sidecar'; then
  echo "FAIL: expected expired manifest to block analyze_lifestyle_patterns"
  echo "$OUT" | head -20
  exit 1
fi

echo "PASS: mcporter expired-manifest fail-closed (exit=$CODE)"