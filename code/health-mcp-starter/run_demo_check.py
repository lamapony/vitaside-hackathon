#!/usr/bin/env python3
"""CLI checks for demo runner."""
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
    tc = r.get("temporal_correlations", [])[:1]
    if tc:
        c = tc[0]
        print(f"top_correlation={c['cause']}->{c['effect']} citations={len(c.get('citations', []))}")
    if r["files_scanned"] == 0:
        sys.exit(1)
    if tc and not tc[0].get("citations"):
        print("WARN: missing citations on top correlation")


def cmd_whatif():
    scenario = {
        "intervention": "consistent_sleep_7_5h",
        "duration_days": 14,
        "target_signals": ["mood_low", "stress", "symptom_pain"],
    }
    r = m.simulate_whatif(scenario)
    print(json.dumps({"confidence": r["confidence"], "outcomes": len(r["projected_outcomes"])}, indent=2))
    if not r.get("projected_outcomes"):
        sys.exit(1)


def cmd_html():
    html = m.generate_doctor_report(format="html")
    if "<title>VitaSide Report" not in html or "Timeline" not in html:
        sys.exit(1)
    print(f"html_ok bytes={len(html)}")
    out = ROOT / "out" / f"vitaside-report-test.html"
    if out.exists():
        print(f"saved={out}")


def cmd_sidecar():
    s = m.get_sidecar_status()
    print(json.dumps({"name": s.get("name"), "expired": s.get("expired"), "audit_entries": s.get("audit", {}).get("entries")}, indent=2))


if __name__ == "__main__":
    cmds = {"analyze": cmd_analyze, "whatif": cmd_whatif, "html": cmd_html, "sidecar": cmd_sidecar}
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    cmds[cmd]()
