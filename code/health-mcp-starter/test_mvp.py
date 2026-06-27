#!/usr/bin/env python3
"""MVP acceptance tests — run: python3 test_mvp.py"""
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
os.environ.setdefault("VITASIDE_MANIFEST", str(ROOT / "sidecars/sleep-stress-sidecar/manifest.yaml"))

spec = importlib.util.spec_from_file_location("vita", ROOT / "health-pattern-mcp.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

FAIL = 0


def check(name, cond):
    global FAIL
    if cond:
        print(f"  OK  {name}")
    else:
        print(f"  FAIL {name}")
        FAIL += 1


print("=== VitaSide MVP 1.0 Tests ===\n")

a = m.analyze_lifestyle_patterns()
check("analyze returns data", a["files_scanned"] > 0)
check("correlations have citations", bool(a["temporal_correlations"][0].get("citations")))
check("disclaimer present", bool(a.get("disclaimer")))

w = m.simulate_whatif({"duration_days": 14, "target_signals": ["mood_low", "stress"]})
check("whatif has outcomes", len(w.get("projected_outcomes", [])) > 0)
check("whatif confidence", w.get("confidence", 0) > 0.3)

c = m.combine_omi_and_apple()
check("omi-apple merge overlap", c.get("overlap_days", 0) > 0)

html = m.generate_doctor_report(format="html")
check("patient html", "Timeline" in html and len(html) > 5000)

doc = m.generate_doctor_report(format="doctor")
check("doctor view", "Doctor View" in doc or "Doctor View" in doc)

col = m.collaborative_insight()
check("collaboration insight", len(col.get("collaborative_insight", "")) > 50)

status = m.get_sidecar_status()
check("sidecar active", not status.get("expired"))

print()
if FAIL:
    print(f"FAILED: {FAIL} checks")
    sys.exit(1)
print("ALL MVP CHECKS PASSED")
