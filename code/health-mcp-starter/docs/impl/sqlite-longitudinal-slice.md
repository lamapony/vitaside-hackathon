# SQLite longitudinal slice (VIT-25)

**Branch:** `vitaside/sqlite-longitudinal`  
**Epic:** VIT-23 · **VERIFY:** `pytest tests/test_sqlite_longitudinal.py -q`

## Delivered

| Piece | Path |
|-------|------|
| Store + migration | `longitudinal_store.py` |
| Fixture metrics | `fixtures/longitudinal_metrics.json` |
| MCP tool | `get_personal_baselines()` in `health-pattern-mcp.py` |
| Tests | `tests/test_sqlite_longitudinal.py` |
| Vault schema doc | `~/Documents/VitaSide-Research/04-Architecture/sqlite-longitudinal.md` |

## Behavior

- DB default: `{first allowed_scope}/.vitaside/longitudinal.db` (override: `VITASIDE_LONGITUDINAL_DB`)
- Scope: DB path must pass `check_scope` (fail-closed)
- Windows: 7 / 14 / 30 days — mean, std, trend per metric; signal presence frequency
- `migrate()` idempotent (`CREATE IF NOT EXISTS` + `schema_migrations`)

## Commands

```bash
cd code/health-mcp-starter
pytest tests/test_sqlite_longitudinal.py -q
pytest tests/ -q
```