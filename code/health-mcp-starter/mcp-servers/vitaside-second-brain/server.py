#!/usr/bin/env python3
"""VitaSide second-brain MCP server (read-only): Obsidian + MemPalace. ADR-001 plane B."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_PKG = Path(__file__).resolve().parent
_ROOT = _PKG.parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from mcp.server.fastmcp import FastMCP

from second_brain_scope import assert_read_allowed, default_vault_root
from obsidian_io import obsidian_read_note as _read_note, obsidian_search as _search
from mempalace_io import mempalace_query as _mp_query

mcp = FastMCP("vitaside-second-brain")


def _gate(tool: str) -> None:
    assert_read_allowed(tool)


@mcp.tool()
def obsidian_search(
    vault_path: str,
    query: str,
    date_range: Optional[Dict[str, str]] = None,
    file_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Search markdown notes under a scoped Obsidian vault path."""
    _gate("obsidian_search")
    if not vault_path:
        vault_path = str(default_vault_root())
    return _search(vault_path, query, date_range=date_range, file_types=file_types)


@mcp.tool()
def obsidian_read_note(path: str, max_lines: Optional[int] = 500) -> Dict[str, Any]:
    """Read a single note with frontmatter and wikilinks (read-only)."""
    _gate("obsidian_read_note")
    try:
        return _read_note(path, max_lines=max_lines)
    except ValueError as e:
        return {"error": str(e), "path": path}
    except FileNotFoundError as e:
        return {"error": str(e), "path": path}


@mcp.tool()
def mempalace_query(
    kg_query: str,
    limit: int = 5,
    include_drawers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Semantic query against MemPalace drawers (read-only)."""
    _gate("mempalace_query")
    return _mp_query(kg_query, limit=limit, include_drawers=include_drawers)


if __name__ == "__main__":
    mcp.run()