"""Read-only MemPalace semantic query (plane B; no writes)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from second_brain_scope import audit_read

try:
    from mempalace.searcher import search_memories
except ImportError:  # pragma: no cover
    search_memories = None  # type: ignore


def palace_path() -> str:
    return os.path.expanduser(
        os.getenv("MEMPALACE_PALACE_PATH", str(Path.home() / ".mempalace" / "palace"))
    )


def mempalace_query(
    kg_query: str,
    limit: int = 5,
    include_drawers: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if not kg_query.strip():
        return {"results": [], "total": 0, "error": "empty query"}

    if search_memories is None:
        return {
            "results": [],
            "total": 0,
            "error": "mempalace package not installed",
            "hint": "pip install mempalace",
        }

    wing = include_drawers[0] if include_drawers and len(include_drawers) == 1 else None
    raw = search_memories(kg_query, palace_path=palace_path(), wing=wing, n_results=max(1, min(limit, 25)))
    if raw.get("error"):
        audit_read("mempalace_query", Path(palace_path()), {"query": kg_query, "error": raw["error"]})
        return {"results": [], "total": 0, **raw}

    results: List[Dict[str, Any]] = []
    for hit in raw.get("results") or []:
        wing_name = hit.get("wing", "unknown")
        if include_drawers and wing_name not in include_drawers:
            continue
        drawer_id = f"{wing_name}/{hit.get('room', 'unknown')}/{hit.get('source_file', '?')}"
        content = hit.get("text", "")
        results.append(
            {
                "id": drawer_id,
                "content": content,
                "metadata": {
                    "wing": wing_name,
                    "room": hit.get("room"),
                    "source_file": hit.get("source_file"),
                    "similarity": hit.get("similarity"),
                },
                "citations": [
                    {
                        "source": hit.get("source_file"),
                        "excerpt": content[:240] + ("…" if len(content) > 240 else ""),
                    }
                ],
            }
        )

    audit_read("mempalace_query", Path(palace_path()), {"query": kg_query, "total": len(results)})
    return {"results": results[:limit], "total": len(results)}