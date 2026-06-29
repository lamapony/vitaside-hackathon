# VIT-68 — codebase-memory-mcp in multi-source path

**Repo:** `health-mcp-starter` (workspace copy)  
**Agent:** Systems Architect

## Delivered

- `codebase_memory_client.py` — mcporter → `search_graph` / `list_projects`, vault→project resolution (`VITASIDE_CODEBASE_MEMORY_PROJECT` override).
- `multi_source_collector.collect_obsidian_notes()` — indexer first, fallback `obsidian_io` (plane B).
- `build_multi_source_snapshot()` lane `obsidian_notes` + events `source=obsidian_notes`.
- `data_sources.TOOL_RESOURCE_MAP` updated for `list_multi_sources` / `monitor_device_window`.
- Tests: `tests/test_codebase_memory_notes.py` (4 passed).

## Env

| Variable | Purpose |
|----------|---------|
| `VITASIDE_CODEBASE_MEMORY_MCP` | Path to binary (default `~/.local/bin/codebase-memory-mcp`) |
| `VITASIDE_CODEBASE_MEMORY_PROJECT` | Force indexed project name |
| `VITASIDE_DISABLE_CODEBASE_MEMORY=1` | Skip indexer; direct obsidian_io only |

## Verify

```bash
cd health-mcp-starter
python3 -m pytest tests/test_codebase_memory_notes.py -q
```