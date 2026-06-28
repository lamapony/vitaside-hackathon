#!/usr/bin/env bash
# Resolve VitaSide repo-root paths (no hardcoded hackathon machine paths).
# Usage: source "$ROOT/scripts/vitaside_paths.sh"
#   vitaside_root
#   vitaside_manifest [sidecar-name]   # default: sleep-stress-sidecar
set -euo pipefail

vitaside_root() {
  if [[ -n "${VITASIDE_ROOT:-}" ]]; then
    printf '%s\n' "$VITASIDE_ROOT"
    return 0
  fi
  local here="${BASH_SOURCE[1]:-${BASH_SOURCE[0]}}"
  here="$(cd "$(dirname "$here")/.." && pwd)"
  printf '%s\n' "$here"
}

vitaside_manifest() {
  local root sidecar rel
  root="$(vitaside_root)"
  sidecar="${1:-sleep-stress-sidecar}"
  rel="$root/sidecars/$sidecar/manifest.yaml"
  if [[ ! -f "$rel" ]]; then
    echo "Sidecar manifest missing: $rel (run: ./issue-sidecar.sh $sidecar)" >&2
    return 1
  fi
  printf '%s\n' "$rel"
}

vitaside_export_env() {
  local root manifest
  root="$(vitaside_root)"
  manifest="$(vitaside_manifest "${1:-sleep-stress-sidecar}")"
  export VITASIDE_ROOT="$root"
  export VITASIDE_MANIFEST="$manifest"
  export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$root/demo-data/vault}"
}