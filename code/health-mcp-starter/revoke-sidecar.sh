#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
NAME="${1:-sleep-stress-sidecar}"
MANIFEST="${VITASIDE_MANIFEST:-$ROOT/sidecars/$NAME/manifest.yaml}"
python3 -c "
import sys; sys.path.insert(0, '$ROOT')
from pathlib import Path
from sidecar_protocol import revoke_manifest
m = revoke_manifest(Path('$MANIFEST'))
print('Revoked:', m.get('name'), m.get('revoked_at'))
"
