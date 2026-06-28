# VitaSide second-brain MCP (plane B)

Read-only stdio MCP server for **Obsidian vault** search/read and **MemPalace** semantic query. Separate process from `health-pattern-mcp.py` (analytics sidecar), per [[ADR-001]](../../../../../../VitaSide-Research/04-Architecture/ADR-001-mcp-sidecar-for-personal-health.md).

## Tools

| Tool | Purpose |
|------|---------|
| `obsidian_search` | Regex-free substring search over scoped `.md` files with snippets, dates, tags |
| `obsidian_read_note` | Full note body, YAML frontmatter, wikilinks |
| `mempalace_query` | Wraps `mempalace.searcher.search_memories` (optional `pip install mempalace`) |

## Scope & audit

- Reuses `sidecar_protocol.py`: `allowed_scopes`, TTL/revoke via `assert_sidecar_active`, append-only `audit.log` events `second_brain_read` and `path_escape_denied`.
- Path resolution is fail-closed: `resolve_safe_path` rejects traversal outside manifest roots (or `OMI_VAULT_PATH` / `OBSIDIAN_VAULT_ROOT`, defaulting to `demo-data/vault`).

## Run

```bash
cd code/health-mcp-starter
pip install -r requirements.txt
export OMI_VAULT_PATH="$(pwd)/demo-data/vault"
python3 mcp-servers/vitaside-second-brain/server.py
```

### Hermes / mcporter snippet

```json
{
  "mcpServers": {
    "vitaside-second-brain": {
      "command": "python3",
      "args": ["/ABS/PATH/health-mcp-starter/mcp-servers/vitaside-second-brain/server.py"],
      "env": {
        "OMI_VAULT_PATH": "/ABS/PATH/demo-data/vault",
        "MEMPALACE_PALACE_PATH": "/Users/you/.mempalace/palace",
        "VITASIDE_MANIFEST": "/ABS/PATH/sidecars/sleep-stress-sidecar/manifest.yaml"
      }
    }
  }
}
```

Add second-brain tool names to manifest `tools:` when you want explicit allowlisting:

```yaml
tools:
  - obsidian_search
  - obsidian_read_note
  - mempalace_query
```

## VERIFY (VIT-27)

```bash
pytest tests/test_second_brain_read.py -q
```

Gates: fixture vault snippets, path traversal → error + `path_escape_denied` audit row.

## Vault link

Obsidian TRUTH: add pointer to this server under VitaSide MCP servers when syncing hackathon → vault.