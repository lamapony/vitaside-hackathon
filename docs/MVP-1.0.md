# VitaSide MVP 1.0 — Completion Status

**Tag:** `mvp-1.0` · **Date:** 2026-06-27 · **Re-verified:** 2026-06-27 (post audit hardening)

## MVP Definition (Done ✅)

| Criterion | Status | Proof |
|---|---|---|
| Sidecar protocol (manifest, TTL, scopes) | ✅ | `sidecar_protocol.py`, `issue-sidecar.sh` |
| MCP server with core tools (analyze, whatif, report) | ✅ | `health-pattern-mcp.py` (30+ tools) |
| Quality gates (confidence, citations, disclaimer) | ✅ | `_with_gates` on all tool outputs |
| HTML patient report | ✅ | `report_html.py` → `out/*.html` |
| HTML doctor view | ✅ | `report_doctor.py` → `out/*-doctor.html` |
| Audit log | ✅ | `audit.log` (gitignored) |
| Collaboration (main + sidecar) | ✅ | `collaborative_insight`, `collaboration_demo.py` |
| One-command demo | ✅ | `run-demo.sh`, `run-demo-full.sh --hardening` |
| Demo data fallback | ✅ | `gen_demo_data.py` (90 days) |
| Real vault path | ✅ | `OMI_VAULT_PATH` env; privacy-first fallback chain |

## Beyond original MVP (also shipped)

| Feature | Status | Proof |
|---------|--------|-------|
| Local dashboard UI | ✅ | `ui/`, `./serve-ui.sh` |
| Smart analytics + data sources catalog | ✅ | `smart_analytics.py`, `data_sources.py` |
| Clinical summary + visit questions | ✅ | `clinical_summary.py`, `generate_visit_questions` |
| N-of-1 compare + FHIR bundle | ✅ | `n1_compare.py`, `fhir_export.py` |
| Condition packs + multi-journal | ✅ | `condition_tracking.py`, `list_journals` |
| Azure hybrid contract | ✅ stub | `azure_contract.py` — live needs credentials |
| Skin ABCDE observations | ✅ safe | `skin_analysis.py` — descriptive only, no risk score |
| API contract for UI | ✅ | `api_server.py`, tested in `test_mvp.py` |

## Run MVP

```bash
# From repo root (recommended)
./scripts/vitaside test
./scripts/vitaside demo

# Or from app dir
cd code/health-mcp-starter
./setup.sh
./run-demo-full.sh --hardening   # must pass 3/3
./serve-ui.sh                    # dashboard :5173, API :8787
open out/vitaside-report-$(date +%Y-%m-%d).html
open out/vitaside-doctor-$(date +%Y-%m-%d).html
```

## Not in MVP (honest backlog)

See `plan/README.md` and `plan/DEPTH-ROADMAP.md`:

- PDF export
- Azure live (credentials)
- Hermes live delegation (script simulation only today)
- Regime detection + FDR in UI
- Real vault ritual (human process)
- E2E automated skin upload tests

## Positioning (locked)

Personal pattern intelligence for self-awareness and doctor visit prep.
**Not** a medical device. No diagnosis claims. No risk scores on skin or lifestyle signals.

## Audit hardening (2026-06-27)

- Removed developer vault path from source defaults
- Added `pillow`, `python-multipart` to `requirements.txt`
- Skin tool: observational ABCDE only; API uses `Form()` for consent; 15 MB limit
- Clinical summary: `observations_for_review` (not `flags_for_review`)
