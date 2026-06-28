# Second-brain read slice (VIT-27)

**Branch:** `vitaside/second-brain-read`  
**Epic:** VIT-23 · **VERIFY:** `pytest tests/test_second_brain_read.py -q`

## Scope delivered

| Tool | Module | Behavior |
|------|--------|----------|
| `obsidian_search` | `obsidian_io.py` | Scoped vault walk, snippet + tags + optional date filter |
| `obsidian_read_note` | `obsidian_io.py` | Frontmatter, wikilinks, line cap |
| `mempalace_query` | `mempalace_io.py` | Read-only semantic search via MemPalace |
| Path safety | `second_brain_scope.py` | `resolve_safe_path` + `path_escape_denied` audit |
| MCP entry | `server.py` | FastMCP stdio, TTL/revoke gate |

ADR-001 **plane B**: no writes to vault/KG from this server.

## Commands

```bash
cd code/health-mcp-starter
pytest tests/test_second_brain_read.py -q
```

## Unblocks

- VIT-28 Hermes verify (optional second-brain citations in delegation harness)