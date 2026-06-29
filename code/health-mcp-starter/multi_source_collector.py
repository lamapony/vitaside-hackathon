"""
Multi-source collection: doctor-prescribed device + proactive agent + wearables.

Used by data_sources.build_sources_snapshot() and MCP list_multi_sources.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from codebase_memory_client import search_health_note_hits
from sidecar_protocol import collection_window_active, doctor_device_export_candidates


@dataclass
class HealthEvent:
    source: str
    metric: str
    value: Any
    unit: str
    timestamp: str
    confidence: float
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


_DOCTOR_DEVICE_METRIC_ALIASES: Dict[str, Tuple[str, str]] = {
    "resting_hr": ("resting_hr", "bpm"),
    "restingheartrate": ("resting_hr", "bpm"),
    "heart_rate": ("resting_hr", "bpm"),
    "heartrate": ("resting_hr", "bpm"),
    "hr": ("resting_hr", "bpm"),
    "spo2": ("spo2", "percent"),
    "oxygen_saturation": ("spo2", "percent"),
    "o2": ("spo2", "percent"),
    "sleep_efficiency": ("sleep_efficiency", "ratio"),
    "sleepefficiency": ("sleep_efficiency", "ratio"),
    "sleep_hours": ("sleep_hours", "hours"),
    "sleephours": ("sleep_hours", "hours"),
    "hrv_sdnn": ("hrv_sdnn", "ms"),
    "hrv": ("hrv_sdnn", "ms"),
    "sdnn": ("hrv_sdnn", "ms"),
    "steps": ("steps", "count"),
    "stepcount": ("steps", "count"),
    "step_count": ("steps", "count"),
}

_APPLE_RECORD_TYPE_MAP: Dict[str, Tuple[str, str]] = {
    "HKQuantityTypeIdentifierHeartRate": ("resting_hr", "bpm"),
    "HKQuantityTypeIdentifierRestingHeartRate": ("resting_hr", "bpm"),
    "HKQuantityTypeIdentifierOxygenSaturation": ("spo2", "percent"),
    "HKQuantityTypeIdentifierStepCount": ("steps", "count"),
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": ("hrv_sdnn", "ms"),
    "HKCategoryTypeIdentifierSleepAnalysis": ("sleep_hours", "hours"),
}


def _normalize_doctor_metric(raw: str) -> Optional[Tuple[str, str]]:
    key = (raw or "").strip().lower().replace(" ", "_").replace("-", "_")
    if key in _DOCTOR_DEVICE_METRIC_ALIASES:
        return _DOCTOR_DEVICE_METRIC_ALIASES[key]
    for alias, pair in _DOCTOR_DEVICE_METRIC_ALIASES.items():
        if alias in key or key in alias:
            return pair
    return None


def _parse_doctor_timestamp(raw: Any, *, fallback_day: Optional[date] = None) -> str:
    if raw is None or str(raw).strip() == "":
        d = fallback_day or date.today()
        return datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc).isoformat()
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.replace(microsecond=0).isoformat()
    except ValueError:
        try:
            d = date.fromisoformat(text[:10])
            return datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc).isoformat()
        except ValueError:
            d = fallback_day or date.today()
            return datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc).isoformat()


def _doctor_event(
    metric: str,
    value: Any,
    unit: str,
    timestamp: str,
    *,
    note: str,
    confidence: float = 0.92,
) -> HealthEvent:
    if isinstance(value, float):
        value = round(value, 4)
    return HealthEvent(
        source="doctor_device",
        metric=metric,
        value=value,
        unit=unit,
        timestamp=timestamp,
        confidence=confidence,
        note=note,
    )


def _parse_doctor_device_csv(export_path: Path, *, max_rows: int = 500) -> List[HealthEvent]:
    events: List[HealthEvent] = []
    with export_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            return events
        fields = [f.strip() for f in reader.fieldnames if f]
        lower_fields = {f.lower(): f for f in fields}
        ts_col = next(
            (lower_fields[k] for k in lower_fields if k in ("timestamp", "datetime", "date_time", "time")),
            lower_fields.get("date"),
        )
        metric_col = lower_fields.get("metric") or lower_fields.get("name") or lower_fields.get("type")
        value_col = lower_fields.get("value") or lower_fields.get("reading")
        unit_col = lower_fields.get("unit")

        for row_idx, row in enumerate(reader):
            if row_idx >= max_rows:
                break
            if metric_col and value_col:
                pair = _normalize_doctor_metric(row.get(metric_col, ""))
                if not pair:
                    continue
                metric, default_unit = pair
                try:
                    val = float(str(row.get(value_col, "")).replace(",", "."))
                except (TypeError, ValueError):
                    continue
                unit = (row.get(unit_col) or default_unit) if unit_col else default_unit
                ts = _parse_doctor_timestamp(row.get(ts_col) if ts_col else None)
                events.append(
                    _doctor_event(metric, val, str(unit), ts, note=f"Parsed CSV row {row_idx + 2} from {export_path.name}")
                )
                continue

            day_raw = row.get(ts_col) if ts_col else None
            ts = _parse_doctor_timestamp(day_raw)
            for field in fields:
                if field == ts_col:
                    continue
                pair = _normalize_doctor_metric(field)
                if not pair:
                    continue
                raw_val = row.get(field)
                if raw_val is None or str(raw_val).strip() == "":
                    continue
                try:
                    val = float(str(raw_val).replace(",", "."))
                except (TypeError, ValueError):
                    continue
                metric, unit = pair
                events.append(
                    _doctor_event(metric, val, unit, ts, note=f"Parsed CSV wide row {row_idx + 2} from {export_path.name}")
                )
    return events


def _parse_doctor_device_json(export_path: Path, *, max_items: int = 500) -> List[HealthEvent]:
    try:
        payload = json.loads(export_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items: Iterable[Any]
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("events") or payload.get("records") or payload.get("data") or []
    else:
        return []

    events: List[HealthEvent] = []
    for idx, item in enumerate(items):
        if idx >= max_items:
            break
        if not isinstance(item, dict):
            continue
        pair = _normalize_doctor_metric(str(item.get("metric") or item.get("name") or item.get("type") or ""))
        if not pair:
            continue
        metric, default_unit = pair
        raw_value = item.get("value")
        try:
            val = float(raw_value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        unit = str(item.get("unit") or default_unit)
        ts = _parse_doctor_timestamp(item.get("timestamp") or item.get("date") or item.get("startDate"))
        events.append(_doctor_event(metric, val, unit, ts, note=f"Parsed JSON item {idx + 1} from {export_path.name}"))
    return events


def _parse_doctor_device_apple_xml(export_path: Path, *, max_records: int = 8000) -> List[HealthEvent]:
    try:
        root = ET.parse(export_path).getroot()
    except (ET.ParseError, OSError):
        return []

    events: List[HealthEvent] = []
    for rec_idx, rec in enumerate(root.findall(".//Record")):
        if rec_idx >= max_records:
            break
        rec_type = rec.get("type") or ""
        mapping = _APPLE_RECORD_TYPE_MAP.get(rec_type)
        if not mapping and "HeartRate" in rec_type:
            mapping = ("resting_hr", "bpm")
        elif not mapping and ("OxygenSaturation" in rec_type or "SpO2" in rec_type):
            mapping = ("spo2", "percent")
        elif not mapping and "StepCount" in rec_type:
            mapping = ("steps", "count")
        elif not mapping and "HeartRateVariability" in rec_type:
            mapping = ("hrv_sdnn", "ms")
        elif not mapping and "Sleep" in rec_type:
            mapping = ("sleep_hours", "hours")
        if not mapping:
            continue
        metric, unit = mapping
        raw_val = rec.get("value")
        if raw_val is None:
            continue
        try:
            val = float(raw_val)
        except (TypeError, ValueError):
            continue
        if metric == "sleep_hours" and val > 24:
            val = round(val / 60.0, 3)
        if metric == "spo2" and val <= 1:
            val = round(val * 100, 2)
        ts = _parse_doctor_timestamp(rec.get("startDate") or rec.get("creationDate"))
        events.append(
            _doctor_event(
                metric,
                val,
                unit,
                ts,
                note=f"Apple Health Record type={rec_type} from {export_path.name}",
            )
        )
    return events


def parse_doctor_device_export(export_path: Path) -> List[HealthEvent]:
    """Parse prescribed-device export (CSV wide/long, JSON events, Apple Health XML)."""
    suffix = export_path.suffix.lower()
    if suffix == ".csv":
        return _parse_doctor_device_csv(export_path)
    if suffix == ".json":
        return _parse_doctor_device_json(export_path)
    if suffix == ".xml":
        return _parse_doctor_device_apple_xml(export_path)
    return []


def collect_doctor_device(
    *,
    export_path: Optional[Path] = None,
    simulated: bool = True,
) -> List[HealthEvent]:
    """Doctor-prescribed sensor stream from local export or demo simulation."""
    if export_path and export_path.exists():
        parsed = parse_doctor_device_export(export_path)
        if parsed:
            return parsed
        return [
            HealthEvent(
                source="doctor_device",
                metric="device_export_unparsed",
                value=str(export_path),
                unit="path",
                timestamp=_iso_now(),
                confidence=0.5,
                note="Export file present but no recognizable metrics (CSV/JSON/XML)",
            )
        ]

    if not simulated:
        return []

    today = date.today()
    events: List[HealthEvent] = []
    for offset, (metric, value, unit) in enumerate(
        [
            ("resting_hr", 62, "bpm"),
            ("spo2", 97.2, "percent"),
            ("sleep_efficiency", 0.88, "ratio"),
            ("hrv_sdnn", 48, "ms"),
            ("steps", 8420, "count"),
        ]
    ):
        d = today - timedelta(days=offset)
        events.append(
            HealthEvent(
                source="doctor_device",
                metric=metric,
                value=value,
                unit=unit,
                timestamp=datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
                confidence=0.92,
                note="Simulated high-confidence prescribed device export",
            )
        )
    return events


def collect_proactive_agent(
    host_context: Optional[Dict[str, Any]] = None,
    *,
    manifest: Optional[Dict[str, Any]] = None,
) -> List[HealthEvent]:
    """Hermes / main-agent probes during collection window (tool calls, context deltas)."""
    ctx = host_context or {}
    agent = ctx.get("agent") or "hermes-main"
    events: List[HealthEvent] = []
    for idx, ev in enumerate(ctx.get("events") or []):
        events.append(
            HealthEvent(
                source="proactive_agent",
                metric=f"agent_context_{ev.get('type', 'event')}",
                value=ev.get("note") or ev.get("type") or "context",
                unit="text",
                timestamp=datetime.combine(
                    date.fromisoformat(ev["date"]) if ev.get("date") else date.today(),
                    datetime.min.time(),
                    tzinfo=timezone.utc,
                ).isoformat(),
                confidence=0.78,
                note=f"Proactive sidecar check #{idx + 1} by {agent}",
            )
        )
    if collection_window_active(manifest):
        events.append(
            HealthEvent(
                source="proactive_agent",
                metric="sidecar_poll",
                value="list_multi_sources",
                unit="tool",
                timestamp=_iso_now(),
                confidence=0.9,
                note="Agent polled multi-source lane during active collection window",
            )
        )
    return events


def collect_wearables(
    apple_xml: Optional[Path] = None,
    *,
    days: int = 7,
    demo_fallback: bool = True,
) -> List[HealthEvent]:
    """Wearable lane: Apple Health export when present, else compact demo series."""
    if apple_xml and apple_xml.exists():
        size_mb = round(apple_xml.stat().st_size / (1024 * 1024), 2)
        return [
            HealthEvent(
                source="wearables",
                metric="apple_health_export",
                value=size_mb,
                unit="mb",
                timestamp=_iso_now(),
                confidence=0.8,
                note=str(apple_xml),
            )
        ]

    if not demo_fallback:
        return []

    today = date.today()
    out: List[HealthEvent] = []
    for i in range(min(days, 5)):
        d = today - timedelta(days=i)
        demo = [
            ("steps", 6500 + i * 400, "count"),
            ("sleep_hours", 6.5 + (i % 3) * 0.4, "hours"),
        ]
        for metric, value, unit in demo:
            out.append(
                HealthEvent(
                    source="wearables",
                    metric=metric,
                    value=round(value, 2) if isinstance(value, float) else value,
                    unit=unit,
                    timestamp=datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
                    confidence=0.55,
                    note="Demo wearable series (export Apple Health for real metrics)",
                )
            )
    return out


def _obsidian_fallback_search(vault: Path, query: str) -> List[Dict[str, Any]]:
    """Direct read via vitaside-second-brain obsidian_io when indexer unavailable."""
    root = Path(__file__).resolve().parent
    pkg = root / "mcp-servers" / "vitaside-second-brain"
    for p in (str(root), str(pkg)):
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        from obsidian_io import obsidian_search  # type: ignore
    except ImportError:
        return []
    try:
        out = obsidian_search(str(vault), query)
    except Exception:
        return []
    return list(out.get("files") or [])


def collect_obsidian_notes(
    vault: Path,
    *,
    use_codebase_memory: Optional[bool] = None,
    max_events: int = 10,
) -> tuple[List[HealthEvent], Dict[str, Any]]:
    """
    Obsidian / second-brain lane: codebase-memory-mcp search_graph when indexed,
    else scoped obsidian_io substring search.
    """
    if use_codebase_memory is None:
        use_codebase_memory = os.getenv("VITASIDE_DISABLE_CODEBASE_MEMORY", "").strip().lower() not in (
            "1",
            "true",
            "yes",
        )

    lane_meta: Dict[str, Any] = {"backend": None, "status": "missing", "project": None, "hit_count": 0}
    events: List[HealthEvent] = []

    if use_codebase_memory:
        bundle = search_health_note_hits(vault, max_hits=max_events)
        lane_meta.update(
            {
                "backend": bundle.get("backend"),
                "status": bundle.get("status"),
                "project": bundle.get("project"),
            }
        )
        for hit in bundle.get("hits") or []:
            fp = str(hit.get("file_path") or hit.get("name") or "note")
            q = str(hit.get("matched_query") or "health")
            events.append(
                HealthEvent(
                    source="obsidian_notes",
                    metric="indexed_note_hit",
                    value=fp,
                    unit="path",
                    timestamp=_iso_now(),
                    confidence=0.82,
                    note=f"codebase-memory-mcp query={q!r} name={hit.get('name')}",
                )
            )

    if not events:
        lane_meta["backend"] = lane_meta.get("backend") or "obsidian_io"
        files: List[Dict[str, Any]] = []
        for q in ("sleep", "stress", "сон"):
            files.extend(_obsidian_fallback_search(vault, q))
        seen: set[str] = set()
        for f in files:
            path = str(f.get("path") or "")
            if not path or path in seen:
                continue
            seen.add(path)
            events.append(
                HealthEvent(
                    source="obsidian_notes",
                    metric="note_excerpt",
                    value=f.get("snippet") or path,
                    unit="text",
                    timestamp=f.get("date") or _iso_now(),
                    confidence=0.7,
                    note=path,
                )
            )
            if len(events) >= max_events:
                break
        lane_meta["status"] = "ok" if events else "empty"
        lane_meta["hit_count"] = len(events)

    lane_meta["hit_count"] = len(events)
    return events, lane_meta


def resolve_doctor_device_export(
    vault: Path,
    manifest: Optional[Dict[str, Any]] = None,
) -> Optional[Path]:
    for p in doctor_device_export_candidates(vault, manifest):
        if p.exists():
            return p
    return None


def _resolve_frame_events_path() -> Optional[Path]:
    """Frame lifestyle events: ~/vitaside/data, env override, or repo demo data/."""
    env = os.getenv("VITASIDE_FRAME_DATA", "").strip()
    if env:
        base = Path(os.path.expanduser(env))
        candidate = base if base.name == "lifestyle_events.jsonl" else base / "lifestyle_events.jsonl"
        if candidate.exists():
            return candidate
    for base in (
        Path.home() / "vitaside" / "data",
        Path(__file__).resolve().parent.parent.parent / "data",
    ):
        candidate = base / "lifestyle_events.jsonl"
        if candidate.exists():
            return candidate
    return None


def collect_frame_glasses(max_events: int = 40) -> Tuple[List[HealthEvent], Dict[str, Any]]:
    """Vision lifestyle captures from Frame glasses integration."""
    lane_meta: Dict[str, Any] = {"backend": "vitaside.storage", "status": "missing"}
    events_path = _resolve_frame_events_path()
    if not events_path:
        lane_meta["status"] = "available"
        return [], lane_meta

    lane_meta["resolved_path"] = str(events_path.parent)
    lane_meta["status"] = "connected"
    events: List[HealthEvent] = []
    tag_counts: Dict[str, int] = {}

    try:
        lines = [ln for ln in events_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        lane_meta["status"] = "error"
        return [], lane_meta

    for raw in lines[-max_events:]:
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        ts = str(row.get("timestamp") or _iso_now())
        tags = row.get("lifestyle_tags") or []
        for tag in tags:
            tag_counts[str(tag)] = tag_counts.get(str(tag), 0) + 1
        events.append(
            HealthEvent(
                source="frame_glasses",
                metric="lifestyle_capture",
                value={
                    "tags": tags,
                    "activity_level": row.get("activity_level"),
                    "location_type": row.get("location_type"),
                },
                unit="capture",
                timestamp=ts,
                confidence=0.88,
                note=f"Frame capture tags={tags}",
            )
        )

    lane_meta["event_count"] = len(events)
    lane_meta["top_tags"] = sorted(tag_counts.items(), key=lambda x: -x[1])[:6]
    return events, lane_meta


def build_multi_source_snapshot(
    vault: Path,
    manifest: Dict[str, Any],
    *,
    host_context: Optional[Dict[str, Any]] = None,
    apple_xml: Optional[Path] = None,
    days: int = 14,
    data_mode: str = "auto",
) -> Dict[str, Any]:
    window_active = collection_window_active(manifest)
    device_path = resolve_doctor_device_export(vault, manifest)
    simulated_device = data_mode in ("demo", "auto") and device_path is None

    use_simulated_doctor = device_path is None and (simulated_device or window_active)
    doctor_events = collect_doctor_device(export_path=device_path, simulated=use_simulated_doctor)
    agent_events = collect_proactive_agent(host_context, manifest=manifest)
    wearable_events = collect_wearables(apple_xml, days=days, demo_fallback=data_mode != "explicit")
    obsidian_events, obsidian_lane = collect_obsidian_notes(vault)
    frame_events, frame_lane = collect_frame_glasses()

    all_events = doctor_events + agent_events + wearable_events + obsidian_events + frame_events
    by_source: Dict[str, int] = {}
    for ev in all_events:
        by_source[ev.source] = by_source.get(ev.source, 0) + 1

    doctor_active = len(doctor_events) > 0 and (window_active or simulated_device or device_path is not None)

    return {
        "collection_window_active": window_active,
        "doctor_device_active": doctor_active,
        "proactive_monitoring": window_active or len(agent_events) > 0,
        "lanes": {
            "doctor_device": {
                "status": "connected" if doctor_active else "idle",
                "event_count": len(doctor_events),
                "mode": "simulated" if simulated_device and not device_path else ("export" if device_path else "live"),
                "resolved_path": str(device_path) if device_path else None,
            },
            "proactive_agent": {
                "status": "connected" if agent_events else "available",
                "event_count": len(agent_events),
                "agent": (host_context or {}).get("agent", "hermes-main"),
            },
            "wearables": {
                "status": "connected" if apple_xml else ("demo_fallback" if wearable_events else "missing"),
                "event_count": len(wearable_events),
                "resolved_path": str(apple_xml) if apple_xml else None,
            },
            "obsidian_notes": {
                "status": "connected" if obsidian_events else obsidian_lane.get("status", "missing"),
                "event_count": len(obsidian_events),
                "backend": obsidian_lane.get("backend"),
                "codebase_memory_project": obsidian_lane.get("project"),
            },
            "frame_glasses": {
                "status": frame_lane.get("status", "available"),
                "event_count": frame_lane.get("event_count", len(frame_events)),
                "resolved_path": frame_lane.get("resolved_path"),
                "top_tags": frame_lane.get("top_tags", []),
            },
        },
        "event_count_by_source": by_source,
        "events": [e.to_dict() for e in all_events[:120]],
        "total_events": len(all_events),
    }