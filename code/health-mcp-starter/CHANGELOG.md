# Changelog

All notable changes to the VitaSide MCP implementation (`health-mcp-starter`).

## [0.2.0-productization] — 2026-06-28

### Added
- `install.sh` + `scripts/vitaside_paths.sh` — repo-relative `VITASIDE_MANIFEST` / `OMI_VAULT_PATH` resolver
- `docs/RELEASE.md` — cold-start, verify, and MCP wiring
- Pytest modules for sidecar core, visit packet, SQLite longitudinal store
- `write-mcp-config.sh` emits absolute manifest paths from issued sidecars

### Changed
- `test_mvp.py` runs only under `__main__` so pytest collection does not mutate `VITASIDE_MANIFEST`
- Default manifest resolution in `sidecar_protocol.py` remains relative to package root (no user home paths)

### Verify (release gate)
- `./install.sh` → `./setup.sh` path + issued demo sidecars
- `python -m pytest tests/` — full offline suite
- `python test_mvp.py` — acceptance script
- `bash test-mcporter.sh` — MCP stdio smoke

### Notes
- **G2 trunk:** integration work continues on `vitaside/*` branches; tag `0.2.0-productization` marks packaging slice (VIT-41), not a separate repo fork unless CEO records otherwise.
- **G1:** SPEC assumptions (VIT-29) still human-gated for merge-to-`main` policy.

## [0.1.0-hackathon] — 2026-06 (prior)

- FastMCP health-pattern server, sidecar manifests, TTL/audit, visit packet MVP, demo UI, Azure stub contract.