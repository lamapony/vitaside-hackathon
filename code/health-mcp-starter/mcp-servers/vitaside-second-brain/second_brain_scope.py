"""ADR-001 plane B: scoped read-only paths for Obsidian vault (reuses sidecar_protocol)."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import sidecar_protocol as sp  # noqa: E402


def default_vault_root() -> Path:
    raw = os.getenv("OBSIDIAN_VAULT_ROOT") or os.getenv("OMI_VAULT_PATH") or ""
    if raw:
        return Path(os.path.expanduser(raw)).resolve()
    return (_ROOT / "demo-data" / "vault").resolve()


def vault_roots(manifest: Optional[Dict[str, Any]] = None) -> List[Path]:
    m = manifest or sp.load_manifest()
    roots = list(sp.allowed_roots(m))
    env_raw = os.getenv("OBSIDIAN_VAULT_ROOT") or os.getenv("OMI_VAULT_PATH")
    if env_raw:
        env_root = Path(os.path.expanduser(env_raw)).resolve()
        if env_root not in roots:
            roots.append(env_root)
    if roots:
        return roots
    return [default_vault_root()]


def resolve_safe_path(
    user_path: str,
    *,
    vault_hint: Optional[str] = None,
    manifest: Optional[Dict[str, Any]] = None,
) -> Tuple[Path, List[Path]]:
    """
    Resolve user_path under an allowed vault root. Raises ValueError on escape.
    vault_hint may be a vault root or a path inside the vault (used to pick root).
    """
    roots = vault_roots(manifest)
    candidate = Path(os.path.expanduser(user_path))
    if not candidate.is_absolute():
        base = None
        if vault_hint:
            hint = Path(os.path.expanduser(vault_hint)).resolve()
            for r in roots:
                if hint == r or r in hint.parents:
                    base = r
                    break
            if base is None and hint.exists():
                for r in roots:
                    if hint == r or r in hint.parents:
                        base = r
                        break
        base = base or roots[0]
        candidate = (base / candidate).resolve()
    else:
        candidate = candidate.resolve()

    for root in roots:
        root = root.resolve()
        if candidate == root or root in candidate.parents:
            return candidate, roots

    sp.audit(
        "path_escape_denied",
        {"path": str(user_path), "resolved": str(candidate), "roots": [str(r) for r in roots]},
    )
    raise ValueError(f"Path is outside allowed vault scopes: {candidate}")


_SECOND_BRAIN_TOOLS = frozenset(
    {"obsidian_search", "obsidian_read_note", "mempalace_query"},
)


def assert_read_allowed(tool: str, manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    m = manifest or sp.load_manifest()
    sp.assert_sidecar_active(m)
    allowed = m.get("tools") or []
    if allowed and any(t in allowed for t in _SECOND_BRAIN_TOOLS):
        sp.assert_tool_allowed(m, tool)
    return m


def audit_read(tool: str, path: Path, extra: Optional[Dict[str, Any]] = None) -> None:
    detail: Dict[str, Any] = {"tool": tool, "path": str(path)}
    if extra:
        detail.update(extra)
    sp.audit("second_brain_read", detail)