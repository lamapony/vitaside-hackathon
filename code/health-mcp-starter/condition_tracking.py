"""
Condition-specific tracking packs — extend VitaSide for bipolar, migraine, etc.

Each pack adds signals + metrics + doctor-focused summaries.
NOT diagnosis — self-monitoring for care team discussions.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

_PACKS_DIR = Path(__file__).resolve().parent / "condition_packs"


def list_packs() -> List[Dict[str, str]]:
    out = []
    if not _PACKS_DIR.exists():
        return out
    for p in sorted(_PACKS_DIR.glob("*.yaml")):
        data = _load_yaml(p)
        out.append({
            "id": data.get("id", p.stem),
            "name": data.get("name", p.stem),
            "description": (data.get("description") or "").strip()[:200],
        })
    return out


def _load_yaml(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    return yaml.safe_load(raw) if yaml else {}


def load_pack(condition_id: str) -> Dict[str, Any]:
    path = _PACKS_DIR / f"{condition_id}.yaml"
    if not path.exists():
        raise ValueError(f"Unknown condition pack: {condition_id}. Available: {[p['id'] for p in list_packs()]}")
    data = _load_yaml(path)
    data["_path"] = str(path)
    return data


def _compile_pack_signals(pack: Dict[str, Any]) -> Dict[str, re.Pattern]:
    compiled = {}
    for sig_id, cfg in pack.get("signals", {}).items():
        compiled[sig_id] = re.compile(cfg["keywords"], re.I)
    return compiled


def _match_pack_signals(text: str, pack: Dict[str, Any]) -> List[str]:
    found = []
    for sig_id, pat in _compile_pack_signals(pack).items():
        if pat.search(text):
            found.append(sig_id)
    return found


def _entry_text(entry: Dict[str, Any]) -> str:
    parts = [entry.get("snippet", "")]
    for ex_list in (entry.get("excerpts") or {}).values():
        for ex in ex_list:
            parts.append(ex.get("text", ""))
    return " ".join(parts).lower()


def track_entries(entries: List[Dict], pack: Dict[str, Any], days: int = 90) -> Dict[str, Any]:
    """Analyze entries against a condition pack."""
    by_date: Dict[str, Dict] = {}
    for e in entries:
        d = e.get("date")
        if d:
            by_date[d] = e

    dates = sorted(by_date.keys())[-days:]
    daily: List[Dict[str, Any]] = []
    citations: List[Dict[str, str]] = []

    for d in dates:
        e = by_date[d]
        text = _entry_text(e)
        base_sigs = set(e.get("signals", []))
        pack_sigs = _match_pack_signals(text, pack)
        all_sigs = base_sigs | set(pack_sigs)
        daily.append({"date": d, "signals": sorted(all_sigs), "pack_signals": sorted(pack_sigs)})
        for ps in pack_sigs:
            if len(citations) < 5:
                citations.append({"date": d, "signal": ps, "excerpt": e.get("snippet", "")[:160]})

    metrics = _compute_metrics(pack, daily, dates, by_date)
    track_summary = _track_items_summary(pack, daily)

    return {
        "condition_id": pack.get("id"),
        "condition_name": pack.get("name"),
        "days_analyzed": len(dates),
        "track_items": track_summary,
        "metrics": metrics,
        "citations": citations,
        "doctor_focus": pack.get("doctor_focus", []),
        "disclaimer": pack.get("disclaimer", ""),
    }


def _track_items_summary(pack: Dict[str, Any], daily: List[Dict]) -> List[Dict[str, Any]]:
    items = []
    n = max(len(daily), 1)
    for item in pack.get("track_items", []):
        sigs = set(item.get("signals", []))
        days_hit = sum(1 for d in daily if sigs & set(d.get("signals", [])))
        items.append({
            "id": item.get("id"),
            "label": item.get("label"),
            "days_with_signal": days_hit,
            "frequency": round(days_hit / n, 3),
        })
    return items


def _compute_metrics(
    pack: Dict[str, Any],
    daily: List[Dict],
    dates: List[str],
    by_date: Dict[str, Dict],
) -> List[Dict[str, Any]]:
    cid = pack.get("id")
    results: List[Dict[str, Any]] = []

    if cid == "bipolar":
        volatility = 0
        for i in range(len(daily) - 6):
            window = daily[i : i + 7]
            lows = sum(1 for d in window if "mood_low" in d["signals"])
            highs = sum(1 for d in window if "mood_elevated" in d["signals"] or "mood_good" in d["signals"])
            if lows >= 2 and highs >= 2:
                volatility += 1
        reduced_energy = sum(
            1 for d in daily
            if "sleep_reduced" in d.get("pack_signals", []) and (
                "mood_elevated" in d.get("pack_signals", []) or "mood_good" in d["signals"]
            )
        )
        med_days = sum(1 for d in daily if "medication_mood" in d.get("pack_signals", []))
        results.extend([
            {"id": "mood_volatility", "value": volatility, "unit": "7-day windows", "note": "Weeks with both low and elevated mood signals"},
            {"id": "reduced_sleep_with_energy", "value": reduced_energy, "unit": "days", "note": "Flag for care team discussion — not a diagnosis"},
            {"id": "medication_logging", "value": med_days, "unit": "days", "note": "Days medication mentioned in notes"},
        ])

    elif cid == "migraine":
        headache_days = [d for d in daily if "headache" in d.get("pack_signals", []) or "symptom_pain" in d["signals"]]
        med_same = sum(
            1 for d in headache_days
            if {"med_triptan", "med_ibuprofen"} & set(d.get("pack_signals", []))
        )
        trigger_before = 0
        date_list = [d["date"] for d in daily]
        idx_map = {d: i for i, d in enumerate(date_list)}
        for hd in headache_days:
            i = idx_map.get(hd["date"], -1)
            if i <= 0:
                continue
            prev = daily[i - 1]["signals"]
            if "stress" in prev or "caffeine_alcohol" in prev or "sleep" in prev:
                trigger_before += 1
        results.extend([
            {"id": "episodes_per_month", "value": len(headache_days), "unit": "days/period", "note": f"Over {len(daily)} days analyzed"},
            {"id": "med_same_day", "value": med_same, "unit": "days", "note": "Headache days with acute med mention"},
            {"id": "trigger_lags", "value": trigger_before, "unit": "days", "note": "Headache days preceded by stress/sleep/caffeine signals"},
        ])

    else:
        for m in pack.get("metrics", []):
            results.append({"id": m.get("id"), "label": m.get("label"), "value": None, "note": "Configure metrics in pack YAML"})

    return results


def format_condition_report(data: Dict[str, Any]) -> str:
    lines = [
        f"# {data.get('condition_name')} — Tracking Summary",
        "",
        f"Days analyzed: **{data.get('days_analyzed', 0)}**",
        "",
        "## What we track",
    ]
    for t in data.get("track_items", []):
        lines.append(f"- **{t['label']}**: {t['days_with_signal']} days ({t['frequency']*100:.0f}%)")
    lines += ["", "## Metrics"]
    for m in data.get("metrics", []):
        lines.append(f"- **{m.get('id')}**: {m.get('value')} {m.get('unit', '')} — {m.get('note', '')}")
    lines += ["", "## For your doctor"]
    for q in data.get("doctor_focus", []):
        lines.append(f"- {q}")
    if data.get("citations"):
        lines += ["", "## Your note excerpts"]
        for c in data["citations"][:3]:
            lines.append(f"- {c['date']} ({c['signal']}): \"{c['excerpt'][:100]}…\"")
    lines += ["", f"*{data.get('disclaimer', '')}*"]
    return "\n".join(lines)
