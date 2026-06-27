"""Daily Apple Health series for Omi merge."""
from __future__ import annotations

import datetime
import random
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional


def demo_daily(days: int = 90, seed: int = 42) -> Dict[str, Dict[str, float]]:
    rng = random.Random(seed)
    today = datetime.date.today()
    out: Dict[str, Dict[str, float]] = {}
    for i in range(days):
        d = (today - datetime.timedelta(days=days - 1 - i)).isoformat()
        poor_sleep = rng.random() < 0.35
        out[d] = {
            "sleep_hours": round(rng.uniform(5.2, 7.8) if poor_sleep else rng.uniform(6.8, 8.2), 2),
            "steps": int(rng.uniform(3500, 11000)),
            "heart_rate_avg": round(rng.uniform(68, 82), 1),
            "hrv_sdnn": round(rng.uniform(28, 55), 1),
        }
    return out


def parse_daily(xml_path: Optional[Path], limit_records: int = 8000) -> Dict[str, Dict[str, float]]:
    if not xml_path or not xml_path.exists():
        return demo_daily()

    size_mb = xml_path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        return _parse_daily_iterparse(xml_path)

    by_date: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for rec in root.findall(".//Record")[:limit_records]:
            t = rec.get("type", "")
            val = rec.get("value")
            start = rec.get("startDate", "")[:10]
            if not start or not val:
                continue
            try:
                v = float(val)
            except ValueError:
                continue
            if "HeartRate" in t:
                by_date[start]["heart_rate_avg"].append(v)
            elif "StepCount" in t:
                by_date[start]["steps"].append(v)
            elif "HeartRateVariabilitySDNN" in t:
                by_date[start]["hrv_sdnn"].append(v)
            elif "SleepAnalysis" in t or "Sleep" in t:
                by_date[start]["sleep_minutes"].append(v if v < 24 else v / 60)
    except ET.ParseError:
        return demo_daily()

    out: Dict[str, Dict[str, float]] = {}
    for d, metrics in by_date.items():
        row: Dict[str, float] = {}
        if metrics.get("heart_rate_avg"):
            row["heart_rate_avg"] = round(sum(metrics["heart_rate_avg"]) / len(metrics["heart_rate_avg"]), 1)
        if metrics.get("steps"):
            row["steps"] = sum(metrics["steps"])
        if metrics.get("hrv_sdnn"):
            row["hrv_sdnn"] = round(sum(metrics["hrv_sdnn"]) / len(metrics["hrv_sdnn"]), 1)
        if metrics.get("sleep_minutes"):
            row["sleep_hours"] = round(sum(metrics["sleep_minutes"]) / 60, 2)
        if row:
            out[d] = row
    return out or demo_daily()


def _parse_daily_iterparse(xml_path: Path) -> Dict[str, Dict[str, float]]:
    """Stream-parse large Apple Health exports without loading full tree."""
    by_date: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    count = 0
    try:
        for _event, elem in ET.iterparse(xml_path, events=("end",)):
            if elem.tag != "Record":
                elem.clear()
                continue
            count += 1
            if count > 200_000:
                break
            t = elem.get("type", "")
            val = elem.get("value")
            start = (elem.get("startDate") or "")[:10]
            elem.clear()
            if not start or not val:
                continue
            try:
                v = float(val)
            except ValueError:
                continue
            if "HeartRate" in t:
                by_date[start]["heart_rate_avg"].append(v)
            elif "StepCount" in t:
                by_date[start]["steps"].append(v)
            elif "HeartRateVariabilitySDNN" in t:
                by_date[start]["hrv_sdnn"].append(v)
            elif "Sleep" in t:
                by_date[start]["sleep_minutes"].append(v if v < 24 else v / 60)
    except ET.ParseError:
        return demo_daily()

    out: Dict[str, Dict[str, float]] = {}
    for d, metrics in by_date.items():
        row: Dict[str, float] = {}
        if metrics.get("heart_rate_avg"):
            row["heart_rate_avg"] = round(sum(metrics["heart_rate_avg"]) / len(metrics["heart_rate_avg"]), 1)
        if metrics.get("steps"):
            row["steps"] = sum(metrics["steps"])
        if metrics.get("hrv_sdnn"):
            row["hrv_sdnn"] = round(sum(metrics["hrv_sdnn"]) / len(metrics["hrv_sdnn"]), 1)
        if metrics.get("sleep_minutes"):
            row["sleep_hours"] = round(sum(metrics["sleep_minutes"]) / 60, 2)
        if row:
            out[d] = row
    return out or demo_daily()


def merge_with_omi(omi_by_date: Dict[str, Dict], apple_daily: Dict[str, Dict]) -> Dict[str, Any]:
    overlap = sorted(set(omi_by_date) & set(apple_daily))
    insights = []
    confirm_poor = mismatch_good = 0

    for d in overlap:
        omi = omi_by_date[d]
        apple = apple_daily[d]
        sq = omi.get("sleep_quality", "unknown")
        sleep_h = apple.get("sleep_hours")
        if sq == "poor" and sleep_h is not None and sleep_h < 6.5:
            confirm_poor += 1
        if sq == "good" and sleep_h is not None and sleep_h < 6.0:
            mismatch_good += 1

    if confirm_poor:
        insights.append({
            "pattern": "omi_poor_sleep_confirmed_by_apple",
            "count": confirm_poor,
            "description": "Omi poor-sleep notes align with Apple sleep_hours < 6.5h on same day",
        })
    if mismatch_good:
        insights.append({
            "pattern": "subjective_objective_mismatch",
            "count": mismatch_good,
            "description": "Omi reports good sleep but Apple shows < 6h (worth discussing with doctor)",
        })

    stress_low_hrv = 0
    for d in overlap:
        if "stress" in omi_by_date[d].get("signals", []) and apple_daily[d].get("hrv_sdnn", 99) < 35:
            stress_low_hrv += 1
    if stress_low_hrv:
        insights.append({
            "pattern": "stress_with_low_hrv",
            "count": stress_low_hrv,
            "description": "Stress signals in Omi co-occur with low HRV on Apple same day",
        })

    return {
        "overlap_days": len(overlap),
        "merged_insights": insights,
        "sample_days": [
            {"date": d, "omi_signals": list(omi_by_date[d].get("signals", [])),
             "apple": apple_daily[d], "sleep_quality": omi_by_date[d].get("sleep_quality")}
            for d in overlap[-5:]
        ],
    }
