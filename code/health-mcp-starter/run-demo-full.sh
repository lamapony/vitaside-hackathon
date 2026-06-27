#!/usr/bin/env bash
# VitaSide full demo — single run or 3× hardening with timing
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
RUNS="${1:-1}"
if [[ "$RUNS" == "--hardening" || "$RUNS" == "3" ]]; then RUNS=3; fi

run_once() {
  local n="$1"
  echo ""
  echo "########## RUN $n / $RUNS ##########"
  local t0=$SECONDS

  if [[ ! -d "$OMI_VAULT_PATH/050 Daily Omi/Conversations" ]] || \
     [[ -z "$(find "$OMI_VAULT_PATH/050 Daily Omi/Conversations" -name '*.md' 2>/dev/null | head -1)" ]]; then
    python3 "$ROOT/gen_demo_data.py"
  fi

  chmod +x "$ROOT/issue-sidecar.sh" "$ROOT/collaboration_demo.py"
  BUNDLE="$ROOT/sidecars/sleep-stress-sidecar/manifest.yaml"
  export VITASIDE_MANIFEST="$BUNDLE"
  "$ROOT/issue-sidecar.sh" sleep-stress-sidecar >/dev/null
  [[ "$n" == "1" ]] && rm -f "$ROOT/audit.log"

  echo "--- issue OK ---"
  python3 "$ROOT/health-pattern-mcp.py" --test
  python3 "$ROOT/run_demo_check.py" sidecar
  python3 "$ROOT/run_demo_check.py" analyze
  python3 "$ROOT/run_demo_check.py" whatif
  python3 "$ROOT/run_demo_check.py" html
  python3 "$ROOT/collaboration_demo.py"
  wc -l "$ROOT/audit.log" | awk '{print "audit_lines=" $1}'

  local elapsed=$((SECONDS - t0))
  echo "RUN $n elapsed: ${elapsed}s"
  if [[ "$elapsed" -gt 30 ]]; then
    echo "WARN: run exceeded 30s budget"
  fi
}

echo "=== VitaSide Full Demo (runs=$RUNS) ==="
for i in $(seq 1 "$RUNS"); do
  run_once "$i"
done
echo ""
echo "=== ALL RUNS OK ($RUNS/3 hardening) ==="
