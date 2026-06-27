# VitaSide MVP 1.0 — Completion Status

**Tag:** `mvp-1.0` · **Date:** 2026-06-27

## MVP Definition (Done ✅)

| Criterion | Status | Proof |
|---|---|---|
| Sidecar protocol (manifest, TTL, scopes) | ✅ | `sidecar_protocol.py`, `issue-sidecar.sh` |
| MCP server with 3 core tools (analyze, whatif, report) | ✅ | `health-pattern-mcp.py` |
| Quality gates (confidence, citations, disclaimer) | ✅ | All tool outputs |
| HTML patient report | ✅ | `report_html.py` → `out/*.html` |
| HTML doctor view | ✅ | `report_doctor.py` → `out/*-doctor.html` |
| Audit log | ✅ | `audit.log` |
| Collaboration (main + sidecar) | ✅ | `collaborative_insight`, `collaboration_demo.py` |
| One-command demo | ✅ | `run-demo.sh`, `run-demo-full.sh --hardening` |
| Demo data fallback | ✅ | `gen_demo_data.py` (90 days) |
| Real vault path | ✅ | `OMI_VAULT_PATH` env |

## Run MVP

```bash
cd code/health-mcp-starter
./setup.sh
./run-demo-full.sh --hardening   # must pass 3/3
open out/vitaside-report-$(date +%Y-%m-%d).html
open out/vitaside-doctor-$(date +%Y-%m-%d).html
```

## Not in MVP (Depth backlog)

See `plan/DEPTH-ROADMAP.md`.

## Positioning (locked)

Personal pattern intelligence for self-awareness and doctor visit prep.
**Not** a medical device. No diagnosis claims.
