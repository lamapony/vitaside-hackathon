# VitaSide release — operator guide

**Version:** `0.2.0-productization` (VIT-41)  
**Impl root:** `code/health-mcp-starter` in the vitaside-hackathon monorepo

## Prerequisites

- Python 3.11+ (3.12 tested)
- Optional: `npx mcporter` for MCP smoke tests
- **No secrets in git:** use `mcp-config.local.json` (gitignored) for machine paths

## Cold start (fresh clone)

```bash
cd code/health-mcp-starter
./install.sh                    # runs setup.sh + issues demo sidecars
source .venv/bin/activate
```

`install.sh` prints `export` lines for:

| Variable | Purpose |
|----------|---------|
| `VITASIDE_ROOT` | Repo root of this package |
| `VITASIDE_MANIFEST` | Active sidecar YAML (TTL, scopes, tool allow-list) |
| `OMI_VAULT_PATH` | Obsidian vault root (defaults to `demo-data/vault`) |

Override vault for real data (G3 — not committed):

```bash
export OMI_VAULT_PATH="/path/to/your/Obsidian Vault"
./write-mcp-config.sh "$VITASIDE_MANIFEST" mcp-config.local.json
```

## Verify (offline)

One command (VIT-45):

```bash
source .venv/bin/activate   # or: python3 -m venv .venv && source .venv/bin/activate
make ci
```

`make ci` runs: pip deps, demo sidecar issue, pytest with `sidecar_protocol` coverage ≥80%, `test-mcporter.sh`, `test-mcporter-expired.sh`, `health-pattern-mcp.py --test`. Uses `demo-data/vault` only — no real `OMI_VAULT_PATH`.

Manual equivalent:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -q --cov=sidecar_protocol --cov-fail-under=80
python test_mvp.py
bash test-mcporter.sh
bash test-mcporter-expired.sh
python health-pattern-mcp.py --test
```

GitHub Actions: `.github/workflows/vitaside-ci.yml` at monorepo root (paths under `code/health-mcp-starter/`).

Expected: pytest green, mcporter smoke passes, expired manifest fail-closed.

## MCP / Hermes wiring

1. Issue or refresh a sidecar: `./issue-sidecar.sh sleep-stress-sidecar`
2. Generate config: `./write-mcp-config.sh sidecars/sleep-stress-sidecar/manifest.yaml mcp-config.local.json`
3. Merge `mcpServers` into Cursor mcporter config or `~/.hermes/config.yaml` under `mcp_servers` (G4 — live Hermes VERIFY is VIT-44).

`mcp-config.example.json` uses placeholders; never commit real usernames or vault paths.

## Path resolver (scripts)

```bash
source scripts/vitaside_paths.sh
vitaside_export_env recovery-sidecar
echo "$VITASIDE_MANIFEST"
```

Python default when `VITASIDE_MANIFEST` is unset: `sidecars/sleep-stress-sidecar/manifest.yaml` relative to `sidecar_protocol.py`.

## Version tag

```bash
git tag -a 0.2.0-productization -m "VIT-41 packaging slice"
```

CEO **G2** decides when integration branches merge to `main`; this tag documents the packaging milestone only.

## Related docs

- Monorepo status: `../../STATUS.md`
- Agent onboarding: `../../docs/AGENT-ONBOARDING.md`
- Changelog: `CHANGELOG.md`