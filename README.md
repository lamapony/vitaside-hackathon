# VitaSide — Local-First Health Intelligence Platform

**Status:** MVP 1.0 + multi-source integration (unified branch)  
**Live demo (static):** https://lamapony.github.io/vitaside-hackathon/  
**Full platform:** `code/health-mcp-starter/` (MCP + React dashboard)

VitaSide connects lifestyle signals from multiple local sources — Omi voice notes, Apple Health, Frame glasses vision capture, doctor-prescribed devices, and agent context — into doctor-ready summaries. All processing stays on device by default.

## Quick Start

```bash
cd code/health-mcp-starter
./setup.sh
python3 test_mvp.py        # acceptance tests
./run-demo.sh              # full MVP flow
./serve-ui.sh              # React dashboard → http://127.0.0.1:5173
```

From repo root: `./scripts/vitaside test`

## What's in this repo

| Area | Purpose |
|---|---|
| `code/health-mcp-starter/` | **Main platform** — 33 MCP tools, FastAPI, React UI, sidecar protocol |
| `frame/` | Brilliant Labs Frame glasses BLE capture (from GitHub hackathon) |
| `vitaside/` | Lightweight analyzer + local storage for Frame lifestyle events |
| `data/` | Demo Frame capture events (for dashboard / GitHub Pages) |
| `docs/` | GitHub Pages static demo + project docs |
| `research/` | Frame integration research + factory notes |
| `mcp/` | Frame glasses MCP stub (to be wired into main server) |

## Data sources (unified)

- **Omi / Obsidian** — daily voice journal notes
- **Apple Health** — export.xml merge
- **Frame glasses** — vision lifestyle tags via BLE capture
- **Doctor device** — temporary prescribed sensor window
- **Proactive agent** — Hermes context during collection
- **Manual logs** — dashboard quick entries
- **Second brain** — scoped Obsidian + mempalace read (VIT-27)

## Real data

```bash
export OMI_VAULT_PATH="~/Documents/Obsidian Vault"
./issue-sidecar.sh sleep-stress-sidecar
python3 health-pattern-mcp.py
```

Frame capture:
```bash
python frame/pair_and_test.py   # pair glasses
python frame/runner.py          # capture → ~/vitaside/data/
```

## Docs

| Doc | Purpose |
|---|---|
| `docs/MVP-1.0.md` | What's shipped in MVP |
| `code/health-mcp-starter/README.md` | MCP tools + UI setup |
| `plan/README.md` | Status dashboard + backlog |
| `research/vitaside-frame-integration.md` | Frame glasses integration notes |

## Skin photo ABCDE check (optional)

Descriptive image features only — **not a diagnosis, not a risk score**.

- Local ABCDE-inspired observations (asymmetry, border contrast, colour variety, size in px)
- Requires explicit `user_consent`; photo guide included in response
- UI upload in Doctor Handoff tab with consent confirm + size limit (15 MB)
- Tool: `analyze_skin_photo(image_path, user_consent, use_external)`

**Not a medical device.** Patterns for self-awareness and visit prep only.
