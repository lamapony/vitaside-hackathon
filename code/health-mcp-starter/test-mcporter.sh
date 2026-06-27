#!/usr/bin/env bash
# mcporter integration tests — VitaSide MCP 1.1
# Usage: bash test-mcporter.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/venv-python.sh"
export OMI_VAULT_PATH="${OMI_VAULT_PATH:-$ROOT/demo-data/vault}"
export VITASIDE_MANIFEST="${VITASIDE_MANIFEST:-$ROOT/sidecars/sleep-stress-sidecar/manifest.yaml}"

SERVER_STDIO="$PYTHON $ROOT/health-pattern-mcp.py"
PASS=0
FAIL=0

green() { printf "\033[32m%s\033[0m\n" "$1"; }
red()   { printf "\033[31m%s\033[0m\n" "$1"; }
blue()  { printf "\033[34m%s\033[0m\n" "$1"; }

run_test() {
    local name="$1"
    local cmd="$2"
    local expected="$3"
    blue "  TEST: $name"
    output=$(eval "$cmd" 2>/dev/null) || {
        red "    FAIL (exit code $?)"
        FAIL=$((FAIL+1))
        return
    }
    if "$PYTHON" - "$expected" "$output" <<'PY'
import json, sys

needle = sys.argv[1].strip().strip('"')
raw = sys.argv[2]

def load_payload(text: str):
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def matches(obj, token: str) -> bool:
    token_l = token.lower()
    if isinstance(obj, dict):
        return any(
            token_l in str(key).lower() or matches(value, token)
            for key, value in obj.items()
        )
    if isinstance(obj, list):
        return any(matches(item, token) for item in obj)
    return token_l in str(obj).lower()

payload = load_payload(raw)
if payload is not None and matches(payload, needle):
    sys.exit(0)
sys.exit(0 if needle in raw else 1)
PY
    then
        green "    PASS"
        PASS=$((PASS+1))
    else
        red "    FAIL (expected JSON key '$expected')"
        echo "    Output: $(echo "$output" | cut -c1-200)"
        FAIL=$((FAIL+1))
    fi
}

echo ""
blue "============================================"
blue "  VitaSide MCP 1.1 — mcporter tests"
blue "============================================"
echo ""

run_test "list tools — smart_analysis" \
    "npx mcporter list --stdio '$SERVER_STDIO'" \
    "smart_analysis"

run_test "find_correlation (fast)" \
    "npx mcporter call --stdio '$SERVER_STDIO' find_correlation --timeout 60000 --args '{\"metric_a\":\"sleep\",\"metric_b\":\"stress\",\"lag\":1}'" \
    "co_occurrences"

run_test "get_actionable_briefing" \
    "npx mcporter call --stdio '$SERVER_STDIO' get_actionable_briefing --timeout 120000" \
    "top_insights"

run_test "smart_analysis" \
    "npx mcporter call --stdio '$SERVER_STDIO' smart_analysis --timeout 120000" \
    "personal_baselines"

run_test "list_data_sources" \
    "npx mcporter call --stdio '$SERVER_STDIO' list_data_sources --timeout 60000" \
    "omi_vault"

run_test "get_analysis_mechanics" \
    "npx mcporter call --stdio '$SERVER_STDIO' get_analysis_mechanics --timeout 30000" \
    "pipeline"

run_test "combine_omi_and_apple" \
    "npx mcporter call --stdio '$SERVER_STDIO' combine_omi_and_apple --timeout 120000" \
    "overlap_days"

run_test "simulate_whatif" \
    "npx mcporter call --stdio '$SERVER_STDIO' simulate_whatif --timeout 120000 --args '{\"scenario\":{\"duration_days\":14}}'" \
    "projected_outcomes"

run_test "generate_visit_questions" \
    "npx mcporter call --stdio '$SERVER_STDIO' generate_visit_questions --timeout 60000" \
    '"questions"'

run_test "get_sidecar_status" \
    "npx mcporter call --stdio '$SERVER_STDIO' get_sidecar_status --timeout 30000" \
    "expires_at"

run_test "collaborative_insight" \
    "npx mcporter call --stdio '$SERVER_STDIO' collaborative_insight --timeout 60000" \
    '"collaborative_insight"'

run_test "collaborative_insight with host_context" \
    "npx mcporter call --stdio '$SERVER_STDIO' collaborative_insight --timeout 60000 --args '{\"host_context\":{\"agent\":\"hermes\",\"events\":[{\"date\":\"2026-05-02\",\"type\":\"travel\",\"note\":\"Red-eye flight\"},{\"date\":\"2026-05-16\",\"type\":\"deadline\",\"note\":\"Launch week\"}]}}'" \
    '"collaborative_insight"'

# Depth tools — run only when backend registers them
TOOLS_LIST=$(npx mcporter list --stdio "$SERVER_STDIO" 2>/dev/null || true)
SKIP=0

run_optional_test() {
    local name="$1"
    local tool="$2"
    local cmd="$3"
    local expected="$4"
    if ! echo "$TOOLS_LIST" | grep -q "$tool"; then
        blue "  SKIP: $name (tool not registered)"
        SKIP=$((SKIP+1))
        return
    fi
    run_test "$name" "$cmd" "$expected"
}

echo ""
blue "--- Optional depth tools (backend) ---"

run_optional_test "get_clinical_summary" "get_clinical_summary" \
    "npx mcporter call --stdio '$SERVER_STDIO' get_clinical_summary --timeout 120000" \
    '"headline"'

run_optional_test "run_n1_compare" "run_n1_compare" \
    "npx mcporter call --stdio '$SERVER_STDIO' run_n1_compare --timeout 120000 --args '{\"exposure_signal\":\"stress\",\"outcome_signal\":\"mood_low\",\"window_days\":2}'" \
    '"interpretation"'

run_optional_test "export_fhir_bundle" "export_fhir_bundle" \
    "npx mcporter call --stdio '$SERVER_STDIO' export_fhir_bundle --timeout 120000" \
    '"resourceType"'

echo ""
blue "============================================"
echo "  Results: $PASS passed, $FAIL failed, $SKIP skipped"
blue "============================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
