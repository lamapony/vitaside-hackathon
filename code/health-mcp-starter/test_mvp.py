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

qs = m.generate_visit_questions()
check("visit questions", qs.get("count", 0) >= 1)

wk = m.weekly_summary_report()
check("weekly summary", wk.get("week_count", 0) >= 1)

bundle = m.export_visit_bundle()
check("visit bundle", bundle.get("questions_count", 0) >= 1)

brief = m.get_actionable_briefing()
check("actionable briefing", len(brief.get("top_insights", [])) >= 1)
check("briefing has citations", bool(brief.get("top_insights", [{}])[0].get("evidence_quote") or brief.get("top_insights", [{}])[0].get("detail")))
check("briefing local narrative", bool(brief.get("local_narrative", {}).get("narrative")))

smart = m.smart_analysis()
check("smart analysis baselines", smart.get("personal_baselines", {}).get("days_analyzed", 0) > 0)
check("smart attention or weekday", bool(smart.get("attention_now") or smart.get("weekday_effects")))
check("personal baselines computed", len(smart.get("personal_baselines", {}).get("signals", {})) >= 3)

narr = m.get_local_narrative("ru")
check("local narrative evidence map", len(narr.get("evidence_map", [])) >= 1)

analysis = m.analyze_lifestyle_patterns()
check("analysis includes smart", "smart_analysis" in analysis)
check("personal baseline in analysis", analysis.get("baseline", {}).get("sleep", {}).get("personal") is not False or analysis.get("baseline", {}).get("stress"))

ds = m.list_data_sources()
check("data sources catalog", len(ds.get("sources", [])) >= 5)
check("omi vault connected", any(s.get("id") == "omi_vault" and s.get("status") in ("connected", "demo") for s in ds.get("sources", [])))
check("analysis pipeline documented", len(ds.get("analysis_pipeline", [])) >= 8)
check("tool resource map", "analyze_lifestyle_patterns" in ds.get("tool_resource_map", {}))

mech = m.get_analysis_mechanics()
check("mechanics principles", len(mech.get("principles", [])) >= 3)
check("mechanics pipeline steps", len(mech.get("pipeline", [])) >= 8)

packs = m.list_condition_packs()
check("condition packs listed", len(packs.get("packs", [])) >= 2)

mig = m.track_condition("migraine", 90)
check("migraine track items", len(mig.get("track_items", [])) >= 3)
check("migraine metrics", len(mig.get("metrics", [])) >= 2)

rep = m.condition_report("bipolar", 90, "markdown")
check("bipolar report markdown", "Tracking Summary" in rep and "Self-monitoring" in rep)

# Azure contract (stub mode — no credentials required)
m._MANIFEST = None
os.environ["VITASIDE_MANIFEST"] = str(ROOT / "sidecars/azure-hybrid-sidecar/manifest.yaml")
if not (ROOT / "sidecars/azure-hybrid-sidecar/manifest.yaml").exists():
    import subprocess
    subprocess.run(["bash", str(ROOT / "issue-sidecar.sh"), "azure-hybrid-sidecar"], check=True, cwd=ROOT)
contract = m.get_azure_contract()
check("azure contract version", contract.get("contract_version") == "1.0")
preview = m.preview_azure_payload("enhance_insight", user_consent=True)
check("azure payload preview", "payload" in preview and preview["payload"].get("local_summary"))
enh = m.azure_enhance_insight(user_consent=True)
check("azure enhance stub", enh.get("source") in ("local_stub", "local_narrative_engine", "azure_openai") and bool(enh.get("narrative")))
share = m.azure_share_report(user_consent=True, ttl_hours=48)
check("azure share stub", "upload_token_preview" in share or share.get("share_url"))

journals = m.list_journals()
check("journals listed", len(journals.get("journals", [])) >= 4)
check("omi journal has days", journals.get("omi_days", 0) >= 30)

hi = m.headache_insights()
check("headache insights", hi.get("headache_days", 0) >= 2 or len(hi.get("triggers", [])) >= 1)
check("headache disclaimer", bool(hi.get("disclaimer")))

js = m.journal_summary("headache")
check("headache journal summary", js.get("journal_id") == "headache")

cs = m.get_clinical_summary()
check("clinical summary headline", len(cs.get("headline", "")) > 10)
check("clinical summary trends or patterns", bool(cs.get("trends") or cs.get("top_patterns")))

n1 = m.run_n1_compare("stress", "mood_low", 2)
check("n1 compare interpretation", len(n1.get("interpretation", "")) > 20)
check("n1 compare rates", "exposure_outcome_rate" in n1 or "note" in n1)

fhir = m.export_fhir_bundle()
check("fhir bundle type", fhir.get("bundle", {}).get("resourceType") == "Bundle")
check("fhir bundle entries", fhir.get("entry_count", 0) >= 3)

check("doctor view clinical section", "14-day trends" in doc or "Problem list" in doc)

print("\n=== API contract (UI startup) ===\n")
try:
    from fastapi.testclient import TestClient

    spec_api = importlib.util.spec_from_file_location("api_server_mod", ROOT / "api_server.py")
    api_mod = importlib.util.module_from_spec(spec_api)
    spec_api.loader.exec_module(api_mod)
    client = TestClient(api_mod.app)
    startup_paths = [
        "/api/briefing",
        "/api/timeline",
        "/api/sidecar",
        "/api/condition-packs",
        "/api/user-context",
        "/api/questions",
        "/api/clinical-summary",
        "/api/n1-compare?exposure_signal=stress&outcome_signal=mood_low",
        "/api/next-steps?condition_id=migraine",
    ]
    for path in startup_paths:
        response = client.get(path)
        body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        check(
            f"API {path} 2xx",
            200 <= response.status_code < 300 and not body.get("error"),
        )

    schema = api_mod.app.openapi()
    check("API openapi schema", bool(schema.get("paths")))
    report_responses = schema["paths"]["/api/reports/{filename}"]["get"].get("responses", {})
    check("API openapi report 404", "404" in report_responses)
    briefing_responses = schema["paths"]["/api/briefing"]["get"].get("responses", {})
    check("API openapi briefing 500", "500" in briefing_responses)
    skin_responses = schema["paths"]["/api/analyze-skin-photo"]["post"].get("responses", {})
    check("API openapi skin consent 400", "400" in skin_responses)

    missing_report = client.get("/api/reports/nonexistent.html")
    check(
        "API report 404",
        missing_report.status_code == 404 and missing_report.json().get("error") == "not_found",
    )
except Exception as exc:
    check("API contract import", False)
    print(f"  FAIL API contract: {exc}")

print()
if FAIL:
    print(f"FAILED: {FAIL} checks")
    sys.exit(1)
print("ALL MVP CHECKS PASSED")
