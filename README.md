# VitaSide — Local-First Health Intelligence

> **Frozen (June 2026)** — stable, tested, not actively maintained.  
> Handoff: [STATUS.md](STATUS.md) · Agent setup: [docs/AGENT-ONBOARDING.md](docs/AGENT-ONBOARDING.md)

Local-first agent sidecar: Omi notes, Apple Health, Frame glasses, doctor devices → pattern analysis with citations → doctor-ready summaries. **No cloud by default.**

## Quick start

```bash
git clone https://github.com/lamapony/vitaside-hackathon.git
cd vitaside-hackathon
make install          # venv + demo vault + sidecar
make test             # 67 acceptance checks — should pass
make serve-ui         # http://127.0.0.1:5173
```

All commands: `make help` or `./scripts/vitaside help`

## Links to share

| Audience | URL / doc |
|----------|-----------|
| **Doctor / demo viewer** | https://lamapony.github.io/vitaside-hackathon/ |
| **Agent operator (MCP)** | [docs/AGENT-ONBOARDING.md](docs/AGENT-ONBOARDING.md) |
| **Repo** | https://github.com/lamapony/vitaside-hackathon |

## Try it

| Mode | Command |
|------|---------|
| Verify | `make test` |
| Unit tests | `make pytest` |
| Full CLI demo | `make demo` |
| Local dashboard | `make serve-ui` |
| Rebuild Pages | `make pages` |
| MCP config file | `make mcp-config` |

## Repo map

| Path | What |
|------|------|
| `code/health-mcp-starter/` | MCP server, FastAPI, React UI, sidecar protocol |
| `frame/` | Frame glasses BLE capture |
| `vitaside/` | Vision lifestyle analyzer + storage |
| `data/` | Demo Frame events |
| `docs/` | Docs + GitHub Pages SPA |
| `vault/` | Architecture & privacy contracts |
| `plan/` | Sprint history (historical) |

## Real data (when resuming)

```bash
export OMI_VAULT_PATH="$HOME/Documents/Obsidian Vault"
cd code/health-mcp-starter
./issue-sidecar.sh sleep-stress-sidecar
make serve-ui   # from repo root, or ./serve-ui.sh here
make mcp-config # writes mcp-config.local.json for Cursor/Hermes
```

## Key docs

- [STATUS.md](STATUS.md) — snapshot, tests, limitations
- [docs/README.md](docs/README.md) — documentation index
- [docs/AGENT-ONBOARDING.md](docs/AGENT-ONBOARDING.md) — connect an agent
- [code/health-mcp-starter/README.md](code/health-mcp-starter/README.md) — MCP tools + UI
- [CONTRIBUTING.md](CONTRIBUTING.md) — fork guidelines

MIT License · **Not a medical device** — visit prep patterns only.
