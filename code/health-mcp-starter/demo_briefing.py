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
    brief = analysis.get("actionable_briefing") or build_actionable_briefing(
        analysis, merge, whatif, period, analysis.get("smart_analysis")
    )
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
    print("  --- Condition tracking (self-monitoring packs) ---")
    for pack in m.list_condition_packs().get("packs", []):
        print(f"     • {pack['id']}: {pack['name']}")
    for cid in ("migraine", "bipolar"):
        t = m.track_condition(cid, 90)
        items = ", ".join(
            f"{x['label'].split('(')[0].strip()}: {x['days_with_signal']}d"
            for x in t.get("track_items", [])[:3]
        )
        print(f"     {cid}: {items}")
    print("     Use: track_condition('migraine') | condition_report('bipolar')")
    print("")
    print("  --- Your journals (Omi + manual logs) ---")
    j = m.list_journals()
    hi = m.headache_insights()
    print(f"     Omi: {j.get('omi_days', 0)} days · Manual: {j.get('manual_log_days', 0)} days · Combined: {j.get('combined_days', 0)} days")
    print(f"     Headache days: {hi.get('headache_days', 0)} — {hi.get('summary', '')[:100]}")
    for t in hi.get("triggers", [])[:2]:
        ex = (t.get("examples") or [{}])[0]
        print(f"     • Before headache: {t.get('label')} ({t.get('lift')}×) e.g. {ex.get('headache_date')}")
    print("     Tools: list_journals() | headache_insights() | journal_summary('headache')")
    print("")


if __name__ == "__main__":
    main()
