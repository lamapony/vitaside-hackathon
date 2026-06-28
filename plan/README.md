# Plan Directory — Status Dashboard

**Last synced with code:** 2026-06-27 (post audit hardening)

This folder follows the [agent-skills](https://github.com/addyosmani/agent-skills) lifecycle (`/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`). **Plans below are living docs** — when code ships, update the matching plan in the same PR/session.

---

## Reality snapshot (what actually exists today)

| Area | Status | Proof |
|------|--------|-------|
| MCP server (30+ tools) | ✅ Shipped | `health-pattern-mcp.py`, `python3 test_mvp.py` |
| Sidecar protocol (manifest, TTL, scopes, audit) | ✅ Shipped | `sidecar_protocol.py`, `issue-sidecar.sh` |
| Omi parser (context, speakers, quality, time-of-day) | ✅ Shipped | `_parse_omi_file`, `list_data_sources` parser_features |
| Apple Health merge + large XML | ✅ Shipped | `apple_merge.py`, iterparse >50MB |
| Lag correlations, p-values, smart analytics | ✅ Shipped | `smart_analytics.py`, `analytics_depth.py` |
| What-if simulation | ✅ Shipped | `simulate_whatif` |
| HTML patient + doctor reports | ✅ Shipped | `report_html.py`, `report_doctor.py` |
| Local dashboard UI (6 tabs) | ✅ Shipped | `ui/`, `./serve-ui.sh` |
| Clinical summary + N-of-1 + FHIR export | ✅ Shipped | `clinical_summary.py`, `n1_compare.py`, `fhir_export.py` |
| Azure hybrid contract | 🟢 Evaluated (VIT-4) | `azure_contract.py` + `AZURE_SERVICES` map + Google health sources + prototype examples for all ops |
| Skin photo ABCDE tool | ✅ Safe observational | `skin_analysis.py` — **no risk score, no diagnostic flags** |
| Privacy: vault path | ✅ Fixed | No developer path in source; demo fallback |
| Dependencies | ✅ Fixed | `requirements.txt` incl. pillow + python-multipart |

**Verification:** `./scripts/vitaside test` → ALL MVP CHECKS PASSED (~56 checks + API contract)

---

## Which doc to read

| Document | Purpose | Freshness |
|----------|---------|-----------|
| [`../docs/MVP-1.0.md`](../docs/MVP-1.0.md) | Hackathon MVP definition + run commands | ✅ Current |
| [`../docs/MCP-SIDECAR-TECHNICAL-SURVEY.md`](../docs/MCP-SIDECAR-TECHNICAL-SURVEY.md) | **VIT-3** Architecture survey + trade-offs (MCP, stores, patterns, privacy, Azure) | ✅ Just produced |
| [`../vault/Prep-Phase-Plan.md`](../vault/Prep-Phase-Plan.md) | **VIT-12** Prep research, pains, tech scan, course corrections | ✅ 2026-06-28 |
| [`../vault/01-Pain-Points/_index.md`](../vault/01-Pain-Points/_index.md) | Pain point cards PP-01…PP-08 | ✅ VIT-12 |
| [`../vault/03-Tech-Research/_index.md`](../vault/03-Tech-Research/_index.md) | Health AI, MCP, privacy, agent skills | ✅ VIT-12 |
| [`../docs/VIT-4-AZURE-HEALTH-EVALUATION.md`](../docs/VIT-4-AZURE-HEALTH-EVALUATION.md) | **VIT-4** Azure map, Apple/Google/wearables, contract examples | ✅ Current |
| [`../docs/VIT-9-PRIVACY-CONTRACTS.md`](../docs/VIT-9-PRIVACY-CONTRACTS.md) | **VIT-9** Minimization research + `vault/06-Privacy-Contracts/` templates | ✅ Current |
| [`ROCKET-PLAN.md`](ROCKET-PLAN.md) | Original 48h sprint plan (historical + status) | ✅ Marked complete |
| [`DETAILED-IMPLEMENTATION-PLAN.md`](DETAILED-IMPLEMENTATION-PLAN.md) | Full lifecycle phases 1–6 | ✅ Status appended |
| [`TASKS.md`](TASKS.md) | Atomic task checklist | ✅ Synced |
| [`DEPTH-ROADMAP.md`](DEPTH-ROADMAP.md) | Post-MVP depth (real data, doctor, sidecars) | ✅ Current |
| [`DEPTH-SPRINT.md`](DEPTH-SPRINT.md) | Science + clinical utility sprints S1–S6 | 🟡 Partially done (S1–S3) |
| [`PRODUCT-SPRINTS.md`](PRODUCT-SPRINTS.md) | Gap-closure log P1–P4 | ✅ Current |
| [`ORCHESTRATION.md`](ORCHESTRATION.md) | Multi-agent waves + file ownership | ✅ Wave 4 audit added |
| [`QA-REPORT.md`](QA-REPORT.md) | Hardening waves + findings | ✅ Wave 4 audit |

**Do not treat unchecked items in older sections as "still todo"** unless they appear in **Backlog (honest remaining work)** below.

---

## Backlog (honest remaining work)

Priority order for Phase 2+ (post-hackathon):

1. **Real data loop** — point `OMI_VAULT_PATH` at your vault; import Apple Health export; weekly ritual (human process, not code).
2. **PDF export** — browser print CSS or weasyprint for doctor bundle.
3. **Azure live** — credentials + live `enhance_insight` / share URL (contract exists, stub works).
4. **Hermes production** — live delegation, not `collaboration_demo.py` script.
5. **E2E skin tests** — consent gate + invalid image + API Form() upload in `test_mvp.py`.
6. **Regime detection / FDR / bootstrap CI** — DEPTH-SPRINT S3 remainder (`regime_detection.py`, q_value in production path).
7. **Large vault perf** — memory/time profiling on real 10k+ Omi files.
8. **Plan/docs hygiene** — scrub personal paths from `inputs/` and git history if publishing publicly.

---

## Execute

Follow agent-skills mentally: spec → plan → build one slice → test → ship.  
Conductor updates this README when a wave closes.
