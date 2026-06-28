#!/usr/bin/env bash
# Operator install: venv + demo sidecars + printable env for MCP clients.
# Usage: ./install.sh [sidecar-name]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "$ROOT/scripts/vitaside_paths.sh"
SIDECAR="${1:-sleep-stress-sidecar}"

./setup.sh
vitaside_export_env "$SIDECAR"

echo ""
echo "=== VitaSide install paths (copy into MCP / Hermes config) ==="
echo "export VITASIDE_ROOT=\"$VITASIDE_ROOT\""
echo "export VITASIDE_MANIFEST=\"$VITASIDE_MANIFEST\""
echo "export OMI_VAULT_PATH=\"$OMI_VAULT_PATH\""
echo ""
echo "Generate JSON: ./write-mcp-config.sh \"$VITASIDE_MANIFEST\" mcp-config.local.json"
echo "Docs: docs/RELEASE.md"