#!/usr/bin/env bash
# Seed local manual context from template (no PHI copied from Omi vault).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$ROOT/docs/templates/user_context.example.json"
TARGET="$ROOT/local-data/user_context.json"
mkdir -p "$ROOT/local-data"
if [[ -f "$TARGET" ]]; then
  echo "OK: $TARGET already exists (unchanged)"
  exit 0
fi
cp "$TEMPLATE" "$TARGET"
# strip template-only key
python3 - <<'PY' "$TARGET"
import json, sys
path = sys.argv[1]
data = json.loads(open(path, encoding="utf-8").read())
data.pop("_comment", None)
open(path, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
PY
echo "Created $TARGET from template"