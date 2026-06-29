"""VitaSide sidecar manifest, scope enforcement, TTL, and audit logging."""
from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

_SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = _SCRIPT_DIR / "sidecars" / "sleep-stress-sidecar" / "manifest.yaml"
AUDIT_LOG = Path(os.getenv("VITASIDE_AUDIT_LOG", _SCRIPT_DIR / "audit.log"))


def _coerce_utc(dt: datetime.datetime) -> datetime.datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def parse_issued_at(value: Any) -> datetime.datetime:
    if isinstance(value, datetime.datetime):
        return _coerce_utc(value)
    if not value:
        return datetime.datetime.now(datetime.timezone.utc)
    try:
        return _coerce_utc(datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00")))
    except ValueError:
        return datetime.datetime.now(datetime.timezone.utc)


def _parse_ttl(ttl: str, issued_at: Optional[datetime.datetime] = None) -> datetime.datetime:
    issued_at = issued_at or datetime.datetime.now(datetime.timezone.utc)
    issued_at = _coerce_utc(issued_at)
    if ttl.endswith("d"):
        days = int(ttl[:-1])
        return issued_at + datetime.timedelta(days=days)
    if ttl.endswith("h"):
        hours = int(ttl[:-1])
        return issued_at + datetime.timedelta(hours=hours)
    try:
        return _coerce_utc(datetime.datetime.fromisoformat(ttl.replace("Z", "+00:00")))
    except ValueError:
        return issued_at + datetime.timedelta(days=30)


def load_manifest(path: Optional[Path] = None) -> Dict[str, Any]:
    path = Path(path or os.getenv("VITASIDE_MANIFEST", DEFAULT_MANIFEST))
    if not path.exists():
        return {
            "name": "vitaside-default",
            "version": "0.1",
            "issuer": "local",
            "ttl": "30d",
            "issued_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "allowed_scopes": [],
            "tools": ["analyze_lifestyle_patterns", "simulate_whatif", "generate_doctor_report"],
            "quality_gates": ["always_include_confidence", "always_cite_sources", "include_disclaimer"],
            "_manifest_path": str(path),
            "_loaded": False,
        }
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) if yaml else json.loads(raw)
    issued = parse_issued_at(data.get("issued_at"))
    data["issued_at"] = issued.isoformat()
    data["_manifest_path"] = str(path)
    data["_loaded"] = True
    data["_expires_at"] = _parse_ttl(str(data.get("ttl", "30d")), issued).isoformat()
    _enrich_manifest_extensions(data)
    return data


def _parse_instant(value: str) -> datetime.datetime:
    dt = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _enrich_manifest_extensions(manifest: Dict[str, Any]) -> None:
    """Normalize doctor_device source + temporary collection_window TTL."""
    issued = manifest.get("issued_at")
    anchor = _parse_instant(str(issued)) if issued else datetime.datetime.now(datetime.timezone.utc)

    device = manifest.get("doctor_device")
    if isinstance(device, dict):
        device.setdefault("enabled", True)
        paths = device.get("export_paths") or device.get("paths") or []
        if isinstance(paths, str):
            paths = [paths]
        device["export_paths"] = [str(p) for p in paths]
        manifest["doctor_device"] = device

    window = manifest.get("collection_window")
    if isinstance(window, dict):
        window.setdefault("enabled", False)
        if window.get("ttl") and not window.get("expires_at"):
            start = window.get("started_at") or manifest.get("issued_at")
            start_dt = _parse_instant(str(start)) if start else anchor
            window["expires_at"] = _parse_ttl(str(window["ttl"]), start_dt).isoformat()
        if window.get("expires_at") and not window.get("_expires_at"):
            window["_expires_at"] = str(window["expires_at"])
        manifest["collection_window"] = window


def collection_window_active(manifest: Optional[Dict[str, Any]] = None) -> bool:
    """True when doctor-prescribed device collection window is enabled and not expired."""
    if os.getenv("VITASIDE_DEVICE_WINDOW_ACTIVE", "").strip().lower() in ("1", "true", "yes"):
        return True
    manifest = manifest or {}
    window = manifest.get("collection_window") or {}
    if not window.get("enabled"):
        return False
    expires = window.get("_expires_at") or window.get("expires_at")
    if not expires:
        return bool(window.get("active"))
    try:
        exp = _parse_instant(str(expires))
        return datetime.datetime.now(datetime.timezone.utc) < exp
    except ValueError:
        return False


def doctor_device_export_candidates(
    vault: Path,
    manifest: Optional[Dict[str, Any]] = None,
) -> List[Path]:
    """Resolve doctor_device export paths from manifest, env, and vault defaults."""
    manifest = manifest or {}
    vault_s = str(vault)
    candidates: List[Path] = []

    env_path = os.getenv("VITASIDE_DOCTOR_DEVICE_EXPORT", "").strip()
    if env_path:
        candidates.append(Path(env_path).expanduser())

    device = manifest.get("doctor_device") or {}
    if device.get("enabled", True):
        for raw in device.get("export_paths") or []:
            expanded = (
                str(raw)
                .replace("{{vault}}", vault_s)
                .replace("${vault}", vault_s)
            )
            candidates.append(Path(os.path.expanduser(expanded)))

    candidates.extend(
        [
            vault / "Doctor Device" / "export.csv",
            vault / "Apple Health" / "export.xml",
        ]
    )
    seen: set[str] = set()
    ordered: List[Path] = []
    for p in candidates:
        key = str(p)
        if key in seen or key == ".":
            continue
        seen.add(key)
        ordered.append(p)
    return ordered


def is_expired(manifest: Dict[str, Any]) -> bool:
    exp = manifest.get("_expires_at")
    if not exp:
        return False
    try:
        expires = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=datetime.timezone.utc)
        return now > expires
    except ValueError:
        return False


def allowed_roots(manifest: Dict[str, Any]) -> List[Path]:
    roots = []
    for scope in manifest.get("allowed_scopes", []):
        p = Path(os.path.expanduser(scope["path"])).resolve()
        roots.append(p)
    return roots


def check_scope(manifest: Dict[str, Any], target: Path) -> bool:
    """Return True if target is under an allowed scope, or scopes are empty (dev mode)."""
    roots = allowed_roots(manifest)
    if not roots:
        return True
    target = target.resolve()
    return any(target == r or r in target.parents for r in roots)


def assert_tool_allowed(manifest: Dict[str, Any], tool: str) -> None:
    allowed = manifest.get("tools") or []
    if not allowed:
        return
    if tool not in allowed:
        audit("tool_denied", {"tool": tool, "manifest": manifest.get("name")})
        raise RuntimeError(f"Tool '{tool}' is not allowed by sidecar manifest '{manifest.get('name')}'")


def audit(event: str, detail: Dict[str, Any]) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event": event,
        **detail,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def audit_summary(limit: int = 20) -> Dict[str, Any]:
    if not AUDIT_LOG.exists():
        return {"entries": 0, "recent": []}
    lines = AUDIT_LOG.read_text(encoding="utf-8").strip().splitlines()
    recent = [json.loads(l) for l in lines[-limit:]]
    tools = {}
    files = set()
    for r in recent:
        tools[r.get("tool", r.get("event", "?"))] = tools.get(r.get("tool", r.get("event", "?")), 0) + 1
        for fp in r.get("files", []):
            files.add(fp)
    return {"entries": len(lines), "recent": recent, "tools_used": tools, "unique_files": len(files)}


def is_revoked(manifest: Dict[str, Any]) -> bool:
    return bool(manifest.get("revoked_at"))


def revoke_manifest(path: Optional[Path] = None) -> Dict[str, Any]:
    path = Path(path or os.getenv("VITASIDE_MANIFEST", DEFAULT_MANIFEST))
    if not path.exists():
        raise FileNotFoundError(str(path))
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) if yaml else json.loads(raw)
    data["revoked_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    text = yaml.dump(data, allow_unicode=True, sort_keys=False) if yaml else json.dumps(data, indent=2)
    path.write_text(text, encoding="utf-8")
    audit("sidecar_revoked", {"manifest": str(path), "name": data.get("name")})
    return data


def assert_sidecar_active(
    manifest: Optional[Dict[str, Any]] = None,
    *,
    tool: Optional[str] = None,
) -> Dict[str, Any]:
    m = manifest or load_manifest()
    if tool:
        assert_tool_allowed(m, tool)
    if is_revoked(m):
        audit("sidecar_revoked_access", {"manifest": m.get("name")})
        raise RuntimeError(f"Sidecar '{m.get('name')}' was revoked at {m.get('revoked_at')}")
    if is_expired(m):
        audit("sidecar_expired", {"manifest": m.get("name")})
        raise RuntimeError(f"Sidecar '{m.get('name')}' expired at {m.get('_expires_at')}")
    return m
