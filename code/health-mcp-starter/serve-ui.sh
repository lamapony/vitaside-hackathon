#!/usr/bin/env bash
# Start the VitaSide local dashboard (API + Vite UI).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
UI="$ROOT/ui"
API_PORT="${VITASIDE_API_PORT:-8787}"
UI_PORT="${VITASIDE_UI_PORT:-5173}"
SMOKE=0

for arg in "$@"; do
  case "$arg" in
    --smoke)
      SMOKE=1
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      echo "Usage: $0 [--smoke]" >&2
      exit 2
      ;;
  esac
done

export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
export VITASIDE_MANIFEST="${VITASIDE_MANIFEST:-$ROOT/sidecars/sleep-stress-sidecar/manifest.yaml}"

if [[ ! -d "$OMI_VAULT_PATH" ]]; then
  "$PYTHON" "$ROOT/gen_demo_data.py"
fi

if [[ ! -f "$VITASIDE_MANIFEST" ]]; then
  "$ROOT/issue-sidecar.sh" sleep-stress-sidecar >/dev/null
fi

if [[ ! -d "$UI/node_modules" ]]; then
  echo "Installing UI dependencies..."
  (cd "$UI" && npm install)
fi

port_in_use() {
  "$PYTHON" - "$1" <<'PY'
import socket, sys
s = socket.socket()
try:
    s.bind(("127.0.0.1", int(sys.argv[1])))
except OSError:
    sys.exit(0)
else:
    sys.exit(1)
finally:
    s.close()
PY
}

find_free_port() {
  local port="$1"
  while port_in_use "$port"; do
    port=$((port + 1))
  done
  echo "$port"
}

api_health_ok() {
  "$PYTHON" - "$1" <<'PY'
import sys, urllib.request
try:
    urllib.request.urlopen(f"http://127.0.0.1:{sys.argv[1]}/api/health", timeout=1)
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
}

api_belongs_to_checkout() {
  "$PYTHON" - "$1" "$ROOT" <<'PY'
import json, sys, urllib.request
port, root = sys.argv[1], sys.argv[2]
try:
    data = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=1))
except Exception:
    sys.exit(1)
sys.exit(0 if data.get("root") == root else 2)
PY
}

REUSE_API=0
if api_health_ok "$API_PORT"; then
  if api_belongs_to_checkout "$API_PORT"; then
    echo "Reusing VitaSide API already on http://127.0.0.1:$API_PORT"
    REUSE_API=1
  else
    echo "Port $API_PORT is occupied by a different API — picking a fresh port for this checkout"
    API_PORT="$(find_free_port "$((API_PORT + 1))")"
  fi
else
  API_PORT="$(find_free_port "$API_PORT")"
  if [[ "$API_PORT" != "${VITASIDE_API_PORT:-8787}" ]]; then
    echo "Port ${VITASIDE_API_PORT:-8787} busy — using API port $API_PORT"
  fi
fi

export VITASIDE_API_PORT="$API_PORT"

UI_PORT="$(find_free_port "$UI_PORT")"
if [[ "$UI_PORT" != "${VITASIDE_UI_PORT:-5173}" ]]; then
  echo "Port ${VITASIDE_UI_PORT:-5173} busy — using UI port $UI_PORT"
fi

cleanup() {
  [[ "${REUSE_API:-0}" -eq 0 && -n "${API_PID:-}" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "${UI_PID:-}" ]] && kill "$UI_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [[ "$REUSE_API" -eq 0 ]]; then
  echo "Starting VitaSide API on http://127.0.0.1:$API_PORT"
  (cd "$ROOT" && "$PYTHON" -m uvicorn api_server:app --host 127.0.0.1 --port "$API_PORT") &
  API_PID=$!
fi

echo "Starting VitaSide UI on http://127.0.0.1:$UI_PORT"
(cd "$UI" && npm run dev -- --port "$UI_PORT") &
UI_PID=$!

"$PYTHON" - <<PY
import time
import urllib.request
import webbrowser
import sys

api = "http://127.0.0.1:$API_PORT/api/health"
ui = "http://127.0.0.1:$UI_PORT"
smoke = bool(int("$SMOKE"))

def wait_for(url):
    for _ in range(80):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.25)
    return False

def read(url, timeout=2):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        body = response.read(400).decode("utf-8", "replace")
        return response.status, body

def smoke_probe():
    checks = [
        ("ui", ui, ""),
        ("api-health", api, '"ok":true'),
        ("briefing", f"{ui}/api/briefing", "top_insights"),
        ("timeline", f"{ui}/api/timeline", "entries"),
        ("smart", f"{ui}/api/smart", "personal_baselines"),
        ("questions", f"{ui}/api/questions", "questions"),
        ("n1", f"{ui}/api/n1-compare?exposure_signal=stress&outcome_signal=mood_low&window_days=2", "exposure_signal"),
    ]
    deadline = time.time() + 30
    pending = list(checks)
    passed = {}
    last_error = {}
    while pending and time.time() < deadline:
        next_pending = []
        for name, url, expected in pending:
            try:
                status, body = read(url)
                if status == 200 and (not expected or expected in body):
                    passed[name] = status
                else:
                    last_error[name] = f"status={status} expected={expected!r}"
                    next_pending.append((name, url, expected))
            except Exception as exc:
                last_error[name] = f"{type(exc).__name__}: {exc}"
                next_pending.append((name, url, expected))
        pending = next_pending
        if pending:
            time.sleep(0.5)
    for name, _, _ in checks:
        if name in passed:
            print(f"SMOKE PASS {name}")
        else:
            print(f"SMOKE FAIL {name}: {last_error.get(name, 'not checked')}")
    return not pending

if smoke:
    if not wait_for(api) or not wait_for(ui):
        print("SMOKE FAIL startup: API/UI did not become ready")
        sys.exit(1)
    ok = smoke_probe()
    print("VitaSide dashboard:", ui)
    sys.exit(0 if ok else 1)

api_ok = wait_for(api)
ui_ok = wait_for(ui)
if api_ok and ui_ok:
    webbrowser.open(ui)
else:
    print(f"Warning: API ready={api_ok}, UI ready={ui_ok}")
print("VitaSide dashboard:", ui)
PY

if [[ "$SMOKE" -eq 1 ]]; then
  exit 0
fi

wait
