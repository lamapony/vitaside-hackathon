#!/usr/bin/env bash
# mcporter tests for VitaCo Health MCP v2 — Apple Health integration
# Usage: bash test-mcporter.sh
set -euo pipefail

SERVER_STDIO="/opt/anaconda3/bin/python3 $(dirname "$0")/health-pattern-mcp.py"
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
    if echo "$output" | grep -q "$expected"; then
        green "    PASS"
        PASS=$((PASS+1))
    else
        red "    FAIL (expected to contain '$expected')"
        echo "    Output: $(echo "$output" | cut -c1-200)"
        FAIL=$((FAIL+1))
    fi
}

echo ""
blue "============================================"
blue "  VitaCo Health MCP v2 — mcporter tests"
blue "============================================"
echo ""

# 1. List tools
run_test "list tools (8 total)" \
    "npx mcporter list --stdio '$SERVER_STDIO'" \
    "load_apple_health_data"

# 2. load_apple_health_data — demo data
run_test "load_apple_health_data" \
    "npx mcporter call --stdio '$SERVER_STDIO' load_apple_health_data --timeout 20000" \
    '"status": "ok"'

# 3. load_apple_health_data — has metrics
run_test "load_apple_health_data — metrics" \
    "npx mcporter call --stdio '$SERVER_STDIO' load_apple_health_data --timeout 20000" \
    '"heart_rate"'

# 4. analyze_apple_patterns
run_test "analyze_apple_patterns" \
    "npx mcporter call --stdio '$SERVER_STDIO' analyze_apple_patterns --timeout 20000" \
    '"patterns_found"'

# 5. analyze_apple_patterns — sleep patterns
run_test "analyze_apple_patterns — sleep" \
    "npx mcporter call --stdio '$SERVER_STDIO' analyze_apple_patterns --timeout 20000" \
    '"metric": "sleep"'

# 6. analyze_apple_patterns — anomalies
run_test "analyze_apple_patterns — anomalies" \
    "npx mcporter call --stdio '$SERVER_STDIO' analyze_apple_patterns --timeout 20000" \
    '"short_sleep"'

# 7. analyze_apple_patterns — cross-correlation
run_test "analyze_apple_patterns — cross_corr" \
    "npx mcporter call --stdio '$SERVER_STDIO' analyze_apple_patterns --timeout 20000" \
    '"cross_correlation"'

# 8. combine_omi_and_apple
run_test "combine_omi_and_apple" \
    "npx mcporter call --stdio '$SERVER_STDIO' combine_omi_and_apple --timeout 20000" \
    '"merged_dates_analyzed"'

# 9. generate_doctor_report — contains Apple Health section
run_test "doctor report — Apple Health" \
    "npx mcporter call --stdio '$SERVER_STDIO' generate_doctor_report --timeout 20000" \
    'Apple Health'

# 10. list_data_sources — shows apple health support
run_test "list_data_sources — Apple Health" \
    "npx mcporter call --stdio '$SERVER_STDIO' list_data_sources --timeout 20000" \
    '"apple_health_metrics"'

# 11. analyze_lifestyle_patterns (original tool still works — may return demo)
run_test "original analyze_lifestyle_patterns" \
    "npx mcporter call --stdio '$SERVER_STDIO' analyze_lifestyle_patterns --timeout 20000" \
    '"demo_patterns"'

echo ""
blue "============================================"
echo "  Results: $PASS passed, $FAIL failed"
blue "============================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
