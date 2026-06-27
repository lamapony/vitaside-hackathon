#!/usr/bin/env python3
"""CLI checks for demo runner (analyze + what-if)."""
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location("vita", ROOT / "health-pattern-mcp.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def cmd_analyze():
    r = m.analyze_lifestyle_patterns()
    print(f"files_scanned={r['files_scanned']} unique_dates={r['unique_dates']}")
    print(f"signals={json.dumps(r['signals_distribution'], ensure_ascii=False)}")
    tc = r.get("temporal_correlations", [])[:3]
    print(f"top_correlations={json.dumps(tc, ensure_ascii=False)}")
    if r["files_scanned"] == 0:
        sys.exit(1)


def cmd_whatif():
    scenario = {
        "intervention": "consistent_sleep_7_5h",
        "duration_days": 14,
        "target_signals": ["mood_low", "stress", "symptom_pain"],
    }
    r = m.simulate_whatif(scenario)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    if not r.get("projected_outcomes"):
        sys.exit(1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    {"analyze": cmd_analyze, "whatif": cmd_whatif}[cmd]()
