# VitaSide — Local-First Health Intelligence

> **Project status: Frozen (June 2026)**  
> Hackathon + post-hackathon integration complete. Codebase is stable and tested locally.  
> Not actively maintained. See [STATUS.md](STATUS.md) for the full handoff snapshot.

Local-first personal agent: lifestyle signals from Omi notes, Apple Health, Frame glasses, doctor-prescribed devices, and agent context → pattern analysis with citations → doctor-ready summaries. **No cloud by default.**

## Try it

| Mode | Command / link |
|------|----------------|
| **Verify** | `./scripts/vitaside test` |
| **Full demo** | `cd code/health-mcp-starter && ./run-demo.sh` |
| **Doctor demo (GitHub Pages)** | https://lamapony.github.io/vitaside-hackathon/ — full React dashboard, sample data |
| **Dashboard (local + API)** | `cd code/health-mcp-starter && ./serve-ui.sh` → http://127.0.0.1:5173 |

## Repo map

| Path | What |
|------|------|
| `code/health-mcp-starter/` | **Main platform** — MCP server, FastAPI, React UI, sidecar protocol |
| `frame/` | Frame glasses BLE capture (Brilliant Labs) |
| `vitaside/` | Vision lifestyle analyzer + local jsonl storage |
| `data/` | Demo Frame capture events |
| `docs/` | GitHub Pages + technical docs |
| `research/` | Integration research notes |
| `vault/` | Architecture, privacy contracts, pain points |
| `plan/` | Sprint history + depth roadmap |

## Data sources

Omi/Obsidian · Apple Health · Frame glasses · Doctor device window · Hermes agent context · Manual logs · Second-brain (Obsidian + mempalace)

## Real data (when resuming)

```bash
export OMI_VAULT_PATH="~/Documents/Obsidian Vault"
cd code/health-mcp-starter
./issue-sidecar.sh sleep-stress-sidecar
./serve-ui.sh
```

Frame capture: `python frame/pair_and_test.py` → `python frame/runner.py`

## Key docs

- [STATUS.md](STATUS.md) — frozen snapshot, tests, limitations
- [docs/MVP-1.0.md](docs/MVP-1.0.md) — MVP definition
- [code/health-mcp-starter/README.md](code/health-mcp-starter/README.md) — MCP tools + UI
- [plan/DEPTH-ROADMAP.md](plan/DEPTH-ROADMAP.md) — future depth work

**Not a medical device.** Patterns for self-awareness and visit prep only.
