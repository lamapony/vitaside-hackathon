#!/usr/bin/env bash
# Print Hermes mcp_servers YAML block (stdout). Does NOT edit ~/.hermes/config.yaml (G4 = Dima).
# Usage: ./scripts/print-hermes-profile-yaml.sh [sidecar-name]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/vitaside_paths.sh"
SIDECAR="${1:-sleep-stress-sidecar}"
vitaside_export_env "$SIDECAR"
PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$(command -v python3)"
fi
KEY="vitaside-${SIDECAR%%-sidecar}"
KEY="${KEY//-/_}"
KEY="${KEY//_sidecar/}"
# normalize: vitaside-sleep-stress
KEY="vitaside-${SIDECAR%-sidecar}"
KEY="${KEY%-}"

cat <<YAML
# Paste under mcp_servers: in ~/.hermes/config.yaml (G4). Restart Hermes after merge.
${KEY}:
  command: ${PYTHON}
  args:
    - ${ROOT}/health-pattern-mcp.py
  env:
    VITASIDE_MANIFEST: ${VITASIDE_MANIFEST}
    OMI_VAULT_PATH: ${OMI_VAULT_PATH}
  timeout: 180
YAML