"""
Thin mcporter client for DeusData codebase-memory-mcp (Obsidian vault indexer).

Used by multi_source_collector.collect_obsidian_notes — read-only search_graph only.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def default_mcp_command() -> str:
    return os.getenv(
        "VITASIDE_CODEBASE_MEMORY_MCP",
        os.path.expanduser("~/.local/bin/codebase-memory-mcp"),
    )


def _mcporter_call(tool: str, args: Dict[str, Any], *, timeout_ms: int = 60000) -> Dict[str, Any]:
    cmd = default_mcp_command()
    if not Path(cmd).expanduser().exists():
        return {"error": "codebase_memory_mcp_missing", "path": cmd}
    proc = subprocess.run(
        [
            "npx",
            "--yes",
            "mcporter",
            "call",
            "--stdio",
            cmd,
            tool,
            "--timeout",
            str(timeout_ms),
            "--args",
            json.dumps(args),
        ],
        capture_output=True,
        text=True,
        timeout=max(5, timeout_ms // 1000 + 10),
        cwd=str(Path(__file__).resolve().parent),
    )
    if proc.returncode != 0:
        return {
            "error": "mcporter_failed",
            "stderr": (proc.stderr or "")[-500:],
            "stdout": (proc.stdout or "")[-500:],
        }
    raw = (proc.stdout or "").strip()
    if not raw:
        return {"error": "empty_response"}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "invalid_json", "raw": raw[:500]}


def list_indexed_projects() -> List[Dict[str, Any]]:
    out = _mcporter_call("list_projects", {})
    if out.get("error"):
        return []
    return list(out.get("projects") or [])


def resolve_project_for_vault(vault: Path) -> Optional[str]:
    explicit = os.getenv("VITASIDE_CODEBASE_MEMORY_PROJECT", "").strip()
    if explicit:
        return explicit
    vault_resolved = vault.expanduser().resolve()
    best: Optional[Tuple[int, str]] = None
    for proj in list_indexed_projects():
        root = proj.get("root_path")
        name = proj.get("name")
        if not root or not name:
            continue
        try:
            root_path = Path(root).resolve()
        except OSError:
            continue
        if vault_resolved == root_path or vault_resolved in root_path.parents or root_path in vault_resolved.parents:
            score = len(str(root_path))
            if best is None or score > best[0]:
                best = (score, str(name))
    return best[1] if best else None


def _is_note_hit(row: Dict[str, Any]) -> bool:
    label = str(row.get("label") or "")
    if label in ("Folder", "Module"):
        return False
    fp = str(row.get("file_path") or row.get("name") or "")
    return fp.endswith(".md") or label in ("File", "Document", "Markdown")


def search_vault_graph(
    project: str,
    query: str,
    *,
    limit: int = 8,
    file_pattern: Optional[str] = None,
) -> List[Dict[str, Any]]:
    args: Dict[str, Any] = {"project": project, "query": query, "limit": limit}
    if file_pattern:
        args["file_pattern"] = file_pattern
    out = _mcporter_call("search_graph", args)
    if out.get("error"):
        return []
    hits = [r for r in (out.get("results") or []) if _is_note_hit(r)]
    return hits


DEFAULT_HEALTH_QUERIES = ("sleep", "stress", "headache", "сон", "стресс", "health", "mood")


def search_health_note_hits(
    vault: Path,
    *,
    queries: Optional[List[str]] = None,
    max_hits: int = 12,
) -> Dict[str, Any]:
    project = resolve_project_for_vault(vault)
    if not project:
        return {
            "backend": "codebase_memory_mcp",
            "status": "no_project",
            "hits": [],
            "project": None,
        }
    seen: set[str] = set()
    hits: List[Dict[str, Any]] = []
    for q in queries or list(DEFAULT_HEALTH_QUERIES):
        for row in search_vault_graph(project, q, limit=6, file_pattern="**/*.md"):
            key = str(row.get("qualified_name") or row.get("file_path") or row.get("name"))
            if key in seen:
                continue
            seen.add(key)
            hits.append({**row, "matched_query": q})
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    return {
        "backend": "codebase_memory_mcp",
        "status": "ok" if hits else "empty",
        "project": project,
        "hits": hits,
    }