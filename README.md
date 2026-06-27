# VitaSide Hackathon Project

**Status: MVP 1.0 complete** — see [`docs/MVP-1.0.md`](docs/MVP-1.0.md)  
**Depth roadmap:** [`plan/DEPTH-ROADMAP.md`](plan/DEPTH-ROADMAP.md)

## Quick Start

From repo root: `./scripts/vitaside test` (acceptance suite).

```bash
cd code/health-mcp-starter
./setup.sh
./run-demo.sh              # full MVP flow
python3 test_mvp.py        # acceptance tests
./run-demo-full.sh --hardening
```

Open reports:
```bash
open out/vitaside-report-$(date +%Y-%m-%d).html
open out/vitaside-doctor-$(date +%Y-%m-%d).html
```

## Real data

```bash
export OMI_VAULT_PATH="/Users/you/Documents/Obsidian Vault"
# Apple: ~/Downloads/apple_health_export/export.xml
./issue-sidecar.sh sleep-stress-sidecar
python3 health-pattern-mcp.py
```

MCP config template: `code/health-mcp-starter/mcp-config.example.json`

## MVP includes

- Sidecar protocol (manifest, TTL, scopes, audit)
- `analyze_patterns` / `simulate_whatif` / reports (markdown, json, html, **doctor**)
- Omi↔Apple daily merge
- Multi-agent `collaborative_insight`
- Two sidecar types: `sleep-stress-sidecar`, `recovery-sidecar`

## Docs

| Doc | Purpose |
|---|---|
| `docs/MVP-1.0.md` | What's shipped |
| `plan/DEPTH-ROADMAP.md` | Growth in depth (D1–D5) |
| `docs/SPEC.md` | Protocol spec |
| `pitch/DEMO-SCRIPT.md` | Live demo script |

## New commands

```bash
./export-for-doctor.sh          # full visit bundle → out/
./export-for-doctor.sh --anon   # anonymized excerpts
./list-sidecars.sh
./revoke-sidecar.sh sleep-stress-sidecar
```

## New MCP tools

| Tool | Purpose |
|---|---|
| `generate_visit_questions` | Doctor visit discussion topics |
| `weekly_summary_report` | Signals by ISO week |
| `compare_periods` | Last N days vs prior N days |
| `export_visit_bundle` | HTML + Obsidian + questions |
| `generate_doctor_report(format="obsidian")` | Obsidian visit prep note |

**Version:** MVP 1.0 + Product Sprints P1–P4
## Frontend (recreated via OpenDesign)

The local dashboard UI (Vite + React) has been fully recreated with OpenDesign principles:
- Design tokens (colors, spacing, radius, typography)
- Consistent component library (cards, pills, nav)
- Lucide icons
- Calm dark theme optimized for long reading of personal data
- Sidebar + tab navigation matching the core flows

```bash
cd code/health-mcp-starter/ui
npm run dev
```

The UI talks to `api_server.py` (FastAPI wrapper over the MCP tools).

Static HTML reports are still generated in `out/` for doctor handoff (can be opened directly or viewed via the "Doctor handoff" tab).

## Skin photo preliminary check (new)
Optional external-service boost for skin concerns (e.g. mole/melanoma awareness before doctor).
- Local ABCDE-inspired analysis (asymmetry, border, color, size) using PIL.
- Requires explicit `user_consent`.
- Optional `use_external` for richer analysis (stub + hybrid like Azure).
- Strong disclaimers everywhere.
- UI upload in Doctor handoff tab.
- Tool: `analyze_skin_photo(image_path, user_consent, use_external)`
- Privacy: image stays local unless consented; only hash + features sent if external.
Example:
npx mcporter call --stdio python3 health-pattern-mcp.py analyze_skin_photo --image_path /tmp/photo.jpg --user_consent true

