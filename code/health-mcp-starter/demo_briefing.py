#!/usr/bin/env python3
"""Polished demo output — shows value beyond generic LLM advice."""
import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).parent
os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
os.environ.setdefault("VITASIDE_MANIFEST", str(ROOT / "sidecars/sleep-stress-sidecar/manifest.yaml"))

spec = importlib.util.spec_from_file_location("vita", ROOT / "health-pattern-mcp.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

from actionable_insights import build_actionable_briefing, format_briefing_terminal


def main():
    entries = m._scan_omi(120, tool="demo_briefing")
    analysis = m.analyze_lifestyle_patterns()
    merge = m.combine_omi_and_apple()
    whatif = m._simulate_whatif_core(
        entries,
        {"intervention": "consistent_sleep_7_5h", "duration_days": 14, "target_signals": ["mood_low", "stress"]},
    )
    period = m.compare_periods(14)
    brief = build_actionable_briefing(analysis, merge, whatif, period)
    print(format_briefing_terminal(brief))

    qs = m.generate_visit_questions()
    print("  Questions for your doctor (from YOUR patterns):")
    for q in qs.get("questions", [])[:3]:
        ev = q.get("evidence", "")
        print(f"     • {q['question'][:120]}{'…' if len(q['question']) > 120 else ''}")
        if ev:
            print(f"       📎 \"{ev[:80]}…\"")
    print("")
    print(f"  Reports: out/vitaside-report-*.html  |  out/vitaside-doctor-*.html")
    print("")


if __name__ == "__main__":
    main()
