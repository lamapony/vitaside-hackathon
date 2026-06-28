# Sidecar-core slice (VIT-24)

**Branch policy:** `vitaside/sidecar-core`  
**Epic:** VIT-23 · **VERIFY:** `pytest tests/test_sidecar_core.py` + `bash test-mcporter-expired.sh`

## Scope delivered

| Control | Module | Behavior |
|---------|--------|----------|
| TTL | `sidecar_protocol.load_manifest` | `_expires_at` = `issued_at` + `ttl` (`Nd` / `Nh` / ISO instant) |
| Revoke | `revoke_manifest` + `is_revoked` | `revoked_at` stamped; `assert_sidecar_active` fail-closed |
| Scoped paths | `check_scope` / `_scan_omi` | Only files under `allowed_scopes[].path`; empty scopes = dev mode |
| Tool allowlist | `assert_tool_allowed` | Optional gate for issued manifests (`assert_sidecar_active(..., tool=)`); protocol-tested, not wired to every MCP tool yet |
| Audit | `audit.log` | `sidecar_expired`, `sidecar_revoked_access`, `tool_denied`, `scoped_read` |

## Fail-closed path

1. MCP tool performs scoped read → `_scan_omi` → `assert_sidecar_active(manifest)` (TTL + revoke).
2. Expired or revoked manifest → `RuntimeError` (no silent fallback to unscoped data).
3. `get_sidecar_status` remains readable for inspection (does not call `assert_sidecar_active`).

## Commands

```bash
cd code/health-mcp-starter
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/test_sidecar_core.py -q
bash test-mcporter-expired.sh
python3 test_mvp.py
```

## Dependencies unblocked

- VIT-25 (SQLite longitudinal) — scoped storage under same manifest model
- VIT-27 (second-brain read) — reuses scope + audit primitives