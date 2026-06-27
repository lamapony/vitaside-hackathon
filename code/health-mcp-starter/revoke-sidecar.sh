#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
cd "$ROOT"
NAME="${1:-sleep-stress-sidecar}"
MANIFEST="${VITASIDE_MANIFEST:-$ROOT/sidecars/$NAME/manifest.yaml}"
"$PYTHON" -c "
import sys; sys.path.insert(0, '$ROOT')
from pathlib import Path
from sidecar_protocol import revoke_manifest
m = revoke_manifest(Path('$MANIFEST'))
print('Revoked:', m.get('name'), m.get('revoked_at'))
"
