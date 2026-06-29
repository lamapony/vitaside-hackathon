#!/usr/bin/env bash
# Resolve PYTHON: project .venv when present, else system python3.
# Usage: source "$ROOT/scripts/venv-python.sh"
_venv_root="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
if [[ -x "$_venv_root/.venv/bin/python" ]]; then
  PYTHON="$_venv_root/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi
export PYTHON
