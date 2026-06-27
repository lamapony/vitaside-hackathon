"""Local user-entered context for the VitaSide dashboard.

This is intentionally simple JSON storage. It lets the UI capture important
manual context without sending anything to a cloud service or modifying Omi notes.
"""
from __future__ import annotations

import datetime
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "local-data"
CONTEXT_PATH = DATA_DIR / "user_context.json"


DEFAULT_CONTEXT: Dict[str, Any] = {
    "profile": {
        "display_name": "",
        "age": "",
        "timezone": "",
        "main_goal": "",
        "doctor_notes": "",
    },
    "conditions": [],
    "medications": [],
    "goals": [],
    "manual_logs": [],
    "updated_at": None,
}


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _merge_defaults(data: Dict[str, Any]) -> Dict[str, Any]:
    merged = json.loads(json.dumps(DEFAULT_CONTEXT))
    for key, value in data.items():
        merged[key] = value
    for key, value in DEFAULT_CONTEXT["profile"].items():
        merged.setdefault("profile", {})
        merged["profile"].setdefault(key, value)
    return merged


def load_context() -> Dict[str, Any]:
    if not CONTEXT_PATH.exists():
        return _merge_defaults({})
    try:
        return _merge_defaults(json.loads(CONTEXT_PATH.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        backup = CONTEXT_PATH.with_suffix(".broken.json")
        CONTEXT_PATH.replace(backup)
        return _merge_defaults({"recovered_from": str(backup)})


def save_context(data: Dict[str, Any]) -> Dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    context = _merge_defaults(data)
    context["updated_at"] = _now()
    CONTEXT_PATH.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    return context


def update_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    context = load_context()
    merged = {**context.get("profile", {}), **profile}
    merged["source"] = "manual"
    context["profile"] = merged
    return save_context(context)


def replace_list(kind: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    if kind not in {"conditions", "medications", "goals"}:
        raise ValueError(f"Unsupported context list: {kind}")
    context = load_context()
    normalized = []
    for item in items:
        row = _normalize_item(item)
        row["source"] = "manual"
        normalized.append(row)
    context[kind] = normalized
    return save_context(context)


def add_manual_log(log: Dict[str, Any]) -> Dict[str, Any]:
    context = load_context()
    item = _normalize_item(log)
    item.setdefault("id", uuid.uuid4().hex[:12])
    item.setdefault("date", datetime.date.today().isoformat())
    item.setdefault("type", "note")
    item["source"] = "manual"
    context.setdefault("manual_logs", [])
    context["manual_logs"].insert(0, item)
    context["manual_logs"] = context["manual_logs"][:200]
    return save_context(context)


def delete_manual_log(log_id: str) -> Dict[str, Any]:
    context = load_context()
    context["manual_logs"] = [log for log in context.get("manual_logs", []) if log.get("id") != log_id]
    return save_context(context)


def _normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    clean = {str(k): v for k, v in item.items() if v not in (None, "")}
    clean.setdefault("id", uuid.uuid4().hex[:12])
    return clean


def summarize_context(context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or load_context()
    profile = context.get("profile", {})
    recent_logs = context.get("manual_logs", [])[:5]
    return {
        "display_name": profile.get("display_name", ""),
        "main_goal": profile.get("main_goal", ""),
        "conditions_count": len(context.get("conditions", [])),
        "medications_count": len(context.get("medications", [])),
        "goals_count": len(context.get("goals", [])),
        "manual_logs_count": len(context.get("manual_logs", [])),
        "recent_logs": recent_logs,
        "updated_at": context.get("updated_at"),
    }


def write_context_note(context: Dict[str, Any] | None = None) -> Path:
    context = context or load_context()
    out = ROOT / "out"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"vitaside-user-context-{datetime.date.today().isoformat()}.md"
    profile = context.get("profile", {})
    lines = [
        "# VitaSide User Context",
        "",
        "Manual context entered locally in the VitaSide dashboard.",
        "",
        "## Profile",
        f"- Name: {profile.get('display_name', '')}",
        f"- Age: {profile.get('age', '')}",
        f"- Main goal: {profile.get('main_goal', '')}",
        f"- Doctor notes: {profile.get('doctor_notes', '')}",
        "",
        "## Conditions",
    ]
    lines.extend(_markdown_items(context.get("conditions", []), ["name", "status", "notes"]))
    lines += ["", "## Medications"]
    lines.extend(_markdown_items(context.get("medications", []), ["name", "dose", "schedule", "notes"]))
    lines += ["", "## Goals"]
    lines.extend(_markdown_items(context.get("goals", []), ["title", "target", "notes"]))
    lines += ["", "## Recent manual logs"]
    lines.extend(_markdown_items(context.get("manual_logs", [])[:20], ["date", "type", "text", "severity"]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _markdown_items(items: List[Dict[str, Any]], keys: List[str]) -> List[str]:
    if not items:
        return ["- None yet"]
    rows = []
    for item in items:
        parts = [str(item.get(key, "")).strip() for key in keys if item.get(key)]
        rows.append(f"- {' · '.join(parts)}")
    return rows
