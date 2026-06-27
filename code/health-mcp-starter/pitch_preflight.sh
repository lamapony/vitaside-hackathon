#!/usr/bin/env bash
# Pre-pitch verification — run 5 min before stage
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
cd "$ROOT"
export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
export VITASIDE_MANIFEST="${VITASIDE_MANIFEST:-$ROOT/sidecars/sleep-stress-sidecar/manifest.yaml}"

RED='\033[31m'; GRN='\033[32m'; YLW='\033[33m'; NC='\033[0m'
pass() { echo -e "${GRN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; FAIL=$((FAIL+1)); }
warn() { echo -e "${YLW}!${NC} $1"; }
FAIL=0

echo "=== VitaSide Pitch Preflight ==="
echo ""

pass "Running test_mvp.py..."
"$PYTHON" test_mvp.py >/dev/null || fail "test_mvp.py failed"

pass "Running demo hardening (1 run)..."
./run-demo-full.sh 1 >/dev/null || fail "run-demo-full.sh failed"

TODAY=$(date +%Y-%m-%d)
for f in "out/vitaside-report-$TODAY.html" "out/vitaside-doctor-$TODAY.html"; do
  [[ -f "$f" && $(wc -c <"$f") -gt 2000 ]] && pass "Report $f" || fail "Missing or tiny $f"
done

"$PYTHON" - <<'PY' || exit 1
import importlib.util, os, sys
from pathlib import Path
ROOT = Path(".")
os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data/vault"))
os.environ.setdefault("VITASIDE_MANIFEST", str(ROOT / "sidecars/sleep-stress-sidecar/manifest.yaml"))
spec = importlib.util.spec_from_file_location("v", ROOT / "health-pattern-mcp.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

a = m.analyze_lifestyle_patterns()
if a.get("files_scanned", 0) < 30:
    print("FAIL: files_scanned < 30"); sys.exit(1)
ranked = (a.get("smart_analysis") or {}).get("ranked_correlations") or []
if not ranked:
    print("FAIL: no ranked correlations"); sys.exit(1)
top = ranked[0]
cite = (top.get("citations") or [{}])[0]
print(f"PITCH_TOP={top['cause']}->{top['effect']}")
print(f"PITCH_LIFT={top.get('lift_ratio')}")
print(f"PITCH_DATE={cite.get('date','')}")
print(f"PITCH_QUOTE={cite.get('excerpt','')[:60]}")
print(f"PITCH_DAYS={a.get('unique_dates')}")

brief = m.get_actionable_briefing()
if not brief.get("top_insights"):
    print("FAIL: empty briefing"); sys.exit(1)
if not (brief["top_insights"][0].get("evidence_quote") or brief["top_insights"][0].get("detail")):
    print("WARN: top insight missing citation")

s = m.get_sidecar_status()
if s.get("expired"):
    print("FAIL: sidecar expired — re-issue"); sys.exit(1)
print(f"SIDECAR_EXPIRES={s.get('expires_at','')[:10]}")
PY

if cd ui && npm run build >/dev/null 2>&1; then pass "UI build"; else warn "UI build failed (optional if not showing UI)"; fi

echo ""
if [[ "$FAIL" -gt 0 ]]; then
  echo -e "${RED}PREFLIGHT FAILED ($FAIL)${NC} — fix before pitch"
  exit 1
fi
echo -e "${GRN}PREFLIGHT OK${NC} — open out/vitaside-report-$TODAY.html and rehearse pitch/DEMO-SCRIPT.md"
echo "  ./serve-ui.sh   (optional second screen)"
