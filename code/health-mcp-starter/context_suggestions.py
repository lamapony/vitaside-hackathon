"""Extract editable context suggestions from Omi records and local analysis."""
from __future__ import annotations

import re
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from condition_tracking import _compile_pack_signals, load_pack, list_packs
from user_context import load_context

ROOT = Path(__file__).resolve().parent

MED_PATTERNS = [
    (re.compile(r"\b(литий|lithium)\b", re.I), "Lithium"),
    (re.compile(r"\b(ламотриджин|lamotrigine)\b", re.I), "Lamotrigine"),
    (re.compile(r"\b(суматриптан|sumatriptan|триптан|triptan)\b", re.I), "Sumatriptan"),
    (re.compile(r"\b(ибупрофен|ibuprofen|найз|nurofen)\b", re.I), "Ibuprofen"),
    (re.compile(r"\b(парацетамол|paracetamol)\b", re.I), "Paracetamol"),
    (re.compile(r"\b(кветиапин|quetiapine)\b", re.I), "Quetiapine"),
    (re.compile(r"\b(вальпро|valpro)\b", re.I), "Valproate"),
]

CONDITION_HINTS = {
    "migraine": {"name": "Migraine / headaches", "pack": "migraine"},
    "bipolar": {"name": "Bipolar mood rhythm", "pack": "bipolar"},
}

SIGNAL_GOALS = {
    "sleep": "Stabilize sleep rhythm",
    "stress": "Reduce stress load before it hits mood",
    "mood_low": "Track low mood triggers and recovery",
    "symptom_pain": "Reduce headache / pain days",
    "caffeine_alcohol": "Cut late caffeine and watch next-day effects",
}


def _entry_text(entry: Dict[str, Any]) -> str:
    return (entry.get("snippet") or "").strip()


def _suggest_id(prefix: str, key: str) -> str:
    return f"{prefix}-{uuid.uuid5(uuid.NAMESPACE_DNS, key.lower()).hex[:10]}"


def extract_suggestions(entries: List[Dict[str, Any]], briefing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    briefing = briefing or {}
    signal_counts: Counter = Counter()
    med_hits: Dict[str, Dict[str, Any]] = {}
    condition_hits: Dict[str, Dict[str, Any]] = {}
    log_candidates: List[Dict[str, Any]] = []
    goal_candidates: List[Dict[str, Any]] = []

    pack_signals: Dict[str, Dict[str, re.Pattern]] = {}
    for pack in list_packs():
        try:
            pack_signals[pack["id"]] = _compile_pack_signals(load_pack(pack["id"]))
        except ValueError:
            continue

    for entry in entries:
        text = _entry_text(entry)
        if not text:
            continue
        date = entry.get("date", "")
        lower = text.lower()
        for sig in entry.get("signals", []):
            signal_counts[sig] += 1

        for pattern, label in MED_PATTERNS:
            if pattern.search(text):
                key = label.lower()
                row = med_hits.setdefault(key, {
                    "id": _suggest_id("med", key),
                    "name": label,
                    "source": "records",
                    "confidence": 0.0,
                    "mentions": 0,
                    "evidence_date": date,
                    "evidence_excerpt": text[:160],
                    "notes": "Detected in voice notes",
                })
                row["mentions"] += 1
                row["confidence"] = min(0.95, 0.45 + row["mentions"] * 0.12)
                if date >= row.get("evidence_date", ""):
                    row["evidence_date"] = date
                    row["evidence_excerpt"] = text[:160]

        for pack_id, patterns in pack_signals.items():
            matched = [sig for sig, pat in patterns.items() if pat.search(text)]
            if not matched:
                continue
            hint = CONDITION_HINTS.get(pack_id, {"name": pack_id, "pack": pack_id})
            key = pack_id
            row = condition_hits.setdefault(key, {
                "id": _suggest_id("cond", key),
                "name": hint["name"],
                "status": "tracking",
                "source": "records",
                "confidence": 0.0,
                "mentions": 0,
                "evidence_date": date,
                "evidence_excerpt": text[:160],
                "notes": f"Signals: {', '.join(sorted(set(matched))[:4])}",
            })
            row["mentions"] += 1
            row["confidence"] = min(0.95, 0.4 + row["mentions"] * 0.08)

        if any(sig in entry.get("signals", []) for sig in ("symptom_pain", "stress", "mood_low", "sleep")):
            log_candidates.append({
                "id": _suggest_id("log", f"{date}-{text[:40]}"),
                "date": date,
                "type": _log_type(entry),
                "text": text[:220],
                "severity": "",
                "tags": entry.get("signals", [])[:4],
                "source": "records",
                "confidence": 0.7,
            })

    top_signals = [sig for sig, _ in signal_counts.most_common(3)]
    for sig in top_signals:
        if sig in SIGNAL_GOALS:
            goal_candidates.append({
                "id": _suggest_id("goal", sig),
                "title": SIGNAL_GOALS[sig],
                "target": f"Monitor {sig.replace('_', ' ')} over the next 2 weeks",
                "notes": f"Mentioned in {signal_counts[sig]} note days",
                "source": "records",
                "confidence": min(0.9, 0.35 + signal_counts[sig] * 0.04),
            })

    for ins in (briefing.get("top_insights") or [])[:2]:
        if ins.get("action"):
            goal_candidates.append({
                "id": _suggest_id("goal", ins["headline"]),
                "title": ins["headline"],
                "target": ins.get("action", ""),
                "notes": "From your top local insight",
                "source": "records",
                "confidence": 0.85,
                "evidence_date": ins.get("evidence_date"),
                "evidence_excerpt": ins.get("evidence_quote"),
            })

    profile = {}
    if top_signals:
        primary = top_signals[0].replace("_", " ")
        profile["main_goal"] = f"Improve {primary} based on your recent notes"
        profile["source"] = "records"
        profile["confidence"] = 0.75

    return {
        "profile": profile,
        "conditions": sorted(condition_hits.values(), key=lambda x: -x["confidence"]),
        "medications": sorted(med_hits.values(), key=lambda x: -x["confidence"]),
        "goals": _dedupe_goals(goal_candidates),
        "manual_logs": log_candidates[:12],
        "stats": {
            "entries_scanned": len(entries),
            "top_signals": dict(signal_counts.most_common(6)),
        },
    }


def _log_type(entry: Dict[str, Any]) -> str:
    signals = set(entry.get("signals", []))
    if "symptom_pain" in signals:
        return "symptom"
    if "sleep" in signals or entry.get("sleep_quality") in ("poor", "good"):
        return "sleep"
    if "mood_low" in signals or "mood_good" in signals:
        return "mood"
    if "stress" in signals:
        return "trigger"
    return "note"


def _dedupe_goals(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out = []
    for item in items:
        key = (item.get("title") or "").lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out[:6]


def diff_against_saved(suggestions: Dict[str, Any]) -> Dict[str, Any]:
    saved = load_context()

    def _key(item: Dict[str, Any], field: str) -> str:
        return str(item.get(field, "")).strip().lower()

    saved_conds = {_key(c, "name") for c in saved.get("conditions", [])}
    saved_meds = {_key(m, "name") for m in saved.get("medications", [])}
    saved_goals = {_key(g, "title") for g in saved.get("goals", [])}
    saved_logs = {(l.get("date"), l.get("text", "")[:80]) for l in saved.get("manual_logs", [])}

    return {
        "profile": suggestions.get("profile") if not saved.get("profile", {}).get("main_goal") else {},
        "conditions": [c for c in suggestions.get("conditions", []) if _key(c, "name") not in saved_conds],
        "medications": [m for m in suggestions.get("medications", []) if _key(m, "name") not in saved_meds],
        "goals": [g for g in suggestions.get("goals", []) if _key(g, "title") not in saved_goals],
        "manual_logs": [
            l for l in suggestions.get("manual_logs", [])
            if (l.get("date"), l.get("text", "")[:80]) not in saved_logs
        ],
        "stats": suggestions.get("stats", {}),
    }


def apply_suggestions(suggestions: Dict[str, Any], mode: str = "fill_empty") -> Dict[str, Any]:
    from user_context import save_context

    context = load_context()
    applied = {"profile": False, "conditions": 0, "medications": 0, "goals": 0, "manual_logs": 0}

    prof = suggestions.get("profile") or {}
    if prof.get("main_goal"):
        if mode == "refresh_auto" or not context["profile"].get("main_goal"):
            if mode == "refresh_auto" or context["profile"].get("source") != "manual":
                context["profile"]["main_goal"] = prof["main_goal"]
                context["profile"]["source"] = "records"
                applied["profile"] = True

    def merge_list(kind: str, name_field: str, incoming: List[Dict[str, Any]]):
        existing = context.get(kind, [])
        index = {str(i.get(name_field, "")).lower(): i for i in existing if i.get(name_field)}
        count = 0
        for item in incoming:
            key = str(item.get(name_field, "")).lower()
            if not key:
                continue
            if key in index:
                if mode == "refresh_auto" and index[key].get("source") != "manual":
                    index[key].update({k: v for k, v in item.items() if k != "id"})
                    count += 1
            else:
                row = {k: v for k, v in item.items()}
                row.setdefault("id", item.get("id") or uuid.uuid4().hex[:12])
                existing.append(row)
                index[key] = row
                count += 1
        context[kind] = existing
        return count

    applied["conditions"] = merge_list("conditions", "name", suggestions.get("conditions", []))
    applied["medications"] = merge_list("medications", "name", suggestions.get("medications", []))
    applied["goals"] = merge_list("goals", "title", suggestions.get("goals", []))

    existing_logs = context.setdefault("manual_logs", [])
    seen = {(l.get("date"), l.get("text", "")[:80]) for l in existing_logs}
    for log in suggestions.get("manual_logs", []):
        key = (log.get("date"), log.get("text", "")[:80])
        if key in seen:
            continue
        row = {k: v for k, v in log.items()}
        row.setdefault("id", uuid.uuid4().hex[:12])
        existing_logs.insert(0, row)
        seen.add(key)
        applied["manual_logs"] += 1
    context["manual_logs"] = existing_logs[:200]

    saved = save_context(context)
    return {"context": saved, "applied": applied}
