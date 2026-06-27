# VitaSide Hackathon Project

**Status: MVP 1.0 complete** — see [`docs/MVP-1.0.md`](docs/MVP-1.0.md)  
**Depth roadmap:** [`plan/DEPTH-ROADMAP.md`](plan/DEPTH-ROADMAP.md)

## Quick Start

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

**Disclaimer:** Personal lifestyle patterns only — not a medical diagnosis.
