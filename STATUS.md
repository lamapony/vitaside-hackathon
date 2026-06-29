# VitaSide — Project Status (Frozen)

**Last updated:** 2026-06-29  
**Status:** Frozen / On hold — not actively maintained

This document is the handoff snapshot for anyone opening the repo later.

---

## What shipped

| Component | Location | Notes |
|-----------|----------|-------|
| MCP server (33+ tools) | `code/health-mcp-starter/health-pattern-mcp.py` | Omi, Apple Health, sidecar, Azure stub, FHIR, skin photo |
| Sidecar protocol | `code/health-mcp-starter/sidecar_protocol.py` | Manifest, TTL, scopes, audit, doctor device window |
| React dashboard | `code/health-mcp-starter/ui/` | Local FastAPI backend on `:8787` |
| Multi-source collector | `code/health-mcp-starter/multi_source_collector.py` | Doctor device, wearables, obsidian, Frame glasses |
| Second-brain MCP | `code/health-mcp-starter/mcp-servers/vitaside-second-brain/` | Scoped Obsidian + mempalace read |
| Frame glasses BLE | `frame/` | Brilliant Labs capture pipeline |
| Frame lifestyle store | `vitaside/` | Pillow analysis + jsonl events |
| Static demo | `docs/`, `demo.html` | [GitHub Pages](https://lamapony.github.io/vitaside-hackathon/) |

---

## Verify (should be green)

```bash
cd code/health-mcp-starter
./setup.sh
OMI_VAULT_PATH="$PWD/demo-data/vault" python3 test_mvp.py   # 67 acceptance checks
OMI_VAULT_PATH="$PWD/demo-data/vault" python3 -m pytest tests/ -q   # 38 unit tests
```

From repo root:

```bash
./scripts/vitaside test
./scripts/vitaside demo
./scripts/vitaside serve-ui
```

---

## Architecture (one sentence)

Local-first MCP sidecar reads scoped health/lifestyle signals (Omi notes, Apple Health, Frame vision, doctor device, agent context), computes patterns with citations, and exports doctor-ready artifacts — no cloud by default.

---

## Known limitations (honest)

- **Azure integration** — contract + stub only; live OpenAI/share needs credentials
- **Frame MCP** (`mcp/frame-glasses-mcp.py`) — stub; hardware path is `frame/` + `/api/frame-glasses`
- **Google Health** — catalog entry + demo fallback; no production parser
- **CI workflow** — template at `docs/ci/vitaside-ci.yml.example` (OAuth `workflow` scope required to push Actions)
- **Personal paths** — never commit real vault paths; use `OMI_VAULT_PATH` + `./issue-sidecar.sh`

---

## If you resume development

1. Read `plan/DEPTH-ROADMAP.md` for post-MVP ideas
2. Point `OMI_VAULT_PATH` at a real Obsidian vault and run weekly
3. Wire live Azure or Frame MCP into main server
4. Restore CI: `cp docs/ci/vitaside-ci.yml.example .github/workflows/vitaside-ci.yml`

---

## License

MIT — see [LICENSE](LICENSE).

**Not a medical device.** Lifestyle pattern summaries for self-awareness and visit preparation only.
