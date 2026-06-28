"""Read-only Obsidian vault search and note reads."""
from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from second_brain_scope import audit_read, resolve_safe_path, vault_roots

_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
_TAG = re.compile(r"(?<!\w)#([\w/-]+)")
_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(text: str) -> Dict[str, Any]:
    m = _FRONTMATTER.match(text)
    if not m:
        return {}
    block = m.group(1)
    fm: Dict[str, Any] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def _note_date(path: Path, text: str, fm: Dict[str, Any]) -> Optional[str]:
    for key in ("date", "created", "updated"):
        if key in fm:
            return str(fm[key])
    stem = path.stem
    if re.match(r"\d{4}-\d{2}-\d{2}", stem):
        return stem
    return None


def _in_date_range(note_date: Optional[str], date_range: Optional[Dict[str, str]]) -> bool:
    if not date_range:
        return True
    if not note_date:
        return True
    try:
        d = datetime.date.fromisoformat(note_date[:10])
    except ValueError:
        return True
    start = date_range.get("from")
    end = date_range.get("to")
    if start:
        if d < datetime.date.fromisoformat(start[:10]):
            return False
    if end:
        if d > datetime.date.fromisoformat(end[:10]):
            return False
    return True


def _snippet(text: str, query: str, width: int = 200) -> str:
    q = query.lower()
    body = _FRONTMATTER.sub("", text, count=1)
    low = body.lower()
    idx = low.find(q)
    if idx < 0:
        compact = " ".join(body.split())
        return compact[:width] + ("…" if len(compact) > width else "")
    start = max(0, idx - 40)
    chunk = body[start : start + width]
    return ("…" if start else "") + chunk.replace("\n", " ") + ("…" if start + width < len(body) else "")


def obsidian_search(
    vault_path: str,
    query: str,
    date_range: Optional[Dict[str, str]] = None,
    file_types: Optional[List[str]] = None,
) -> Dict[str, Any]:
    roots = vault_roots()
    vault = Path(vault_path).expanduser()
    if vault.is_absolute():
        vault = vault.resolve()
    else:
        vault = (roots[0] / vault).resolve()
    resolve_safe_path(str(vault))  # ensure vault root in scope

    exts = {e if e.startswith(".") else f".{e}" for e in (file_types or ["md"])}
    q = query.lower().strip()
    files: List[Dict[str, Any]] = []

    for path in sorted(vault.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in exts:
            continue
        try:
            resolve_safe_path(str(path))
        except ValueError:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = _parse_frontmatter(text)
        if q and q not in text.lower():
            continue
        nd = _note_date(path, text, fm)
        if not _in_date_range(nd, date_range):
            continue
        tags = list({t for t in _TAG.findall(text)})
        files.append(
            {
                "path": str(path),
                "snippet": _snippet(text, query),
                "date": nd,
                "tags": tags,
            }
        )

    audit_read("obsidian_search", vault, {"query": query, "count": len(files)})
    return {"files": files, "count": len(files)}


def obsidian_read_note(path: str, max_lines: Optional[int] = 500) -> Dict[str, Any]:
    resolved, _ = resolve_safe_path(path)
    if not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    text = resolved.read_text(encoding="utf-8", errors="replace")
    fm = _parse_frontmatter(text)
    body = _FRONTMATTER.sub("", text, count=1) if fm else text
    lines = body.splitlines()
    if max_lines is not None and max_lines > 0:
        lines = lines[: max_lines]
    links = list({m.group(1) for m in _WIKILINK.finditer(text)})
    audit_read("obsidian_read_note", resolved, {"lines": len(lines)})
    return {
        "path": str(resolved),
        "content": "\n".join(lines),
        "frontmatter": fm,
        "links": links,
    }