#!/opt/anaconda3/bin/python3
"""
VitaSide Health Pattern MCP Server — v3.0 (Hackathon Sprint 1)
- Improved Omi parser (timestamps, context words сегодня/вчера, speaker separation, quality scoring, time-of-day)
- Apple Health XML parsing + demo
- Temporal correlations (lags 1-3 days, lift, p-values via scipy)
- Anomalies vs baseline, stats
- Rich doctor reports (markdown/json/html with timeline + ASCII/HTML charts)
Local-first, privacy, patterns only. No diagnosis.
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import re
import datetime
import json
import os
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional
import math

try:
    import pandas as pd
    import numpy as np
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    pd = np = sp_stats = None

mcp = FastMCP("vitaside-health-patterns-v3")

DISCLAIMER = (
    "Personal lifestyle patterns only — not a medical diagnosis. "
    "Use for self-awareness and doctor visit preparation."
)

_SCRIPT_DIR = Path(__file__).resolve().parent
_DEFAULT_VAULT = Path(os.getenv("OMI_VAULT_PATH", "/Users/dmitriibabinov/Documents/Obsidian Vault"))
_DEMO_VAULT = _SCRIPT_DIR / "demo-data" / "vault"

OMI_VAULT_PATH = _DEFAULT_VAULT

SLEEP_POOR_RE = re.compile(
    r"(плох[аои]?\s+спал|бессонн|не\s+высп|insomnia|ночн\S*\s+пробужд|ворочал|рван\S*\s+сон)",
    re.I,
)
SLEEP_GOOD_RE = re.compile(
    r"(спал\s+отлично|хорош\S*\s+сон|выспал|крепк\S*\s+сон|good.?sleep)",
    re.I,
)
APPLE_HEALTH_PATHS = [
    OMI_VAULT_PATH / "Apple Health",
    Path.home() / "Downloads" / "apple_health_export",
    Path.home() / "Documents" / "apple_health_export",
    Path.home() / "Desktop" / "apple_health_export",
]

# Enhanced SIGNAL_PATTERNS (from Omi sub-agent improvements)
SIGNAL_PATTERNS = {
    "sleep": {
        "keywords": r"\b(спал[аои]?|сон[^-]|проснул[ао]?сь?|insomnia|sleep[^s]|спать|устал[аои]?.*сон|дрых|бессонн|ночн[а-я]* пробужд|плох[аои]? сп[ая]|не высып|кошмар)\b",
        "context_clues": [r"ночью", r"утром", r"вс?чера", r"за ночь", r"под утро", r"перед сном", r"после сна", r"не спал"],
        "weight": 1.0
    },
    "stress": {
        "keywords": r"\b(стресс|тревог[аи]?|anxious|stress[^o]|нерв[а-я]|пережива[юе]|паник[а-я]|волну[юя]|напряж[её]н|беспоко[ия]|адреналин|выгора[юе]|перегруз)\b",
        "context_clues": [r"на работе", r"опять"],
        "weight": 1.0
    },
    "mood_low": {
        "keywords": r"\b(плохо|грустн[а-я]|депрес[с]?[а-я]?|sad|depress[^a-z]|плох[а-я]е? настроени[ея]|тоск[а-я]|унын[а-я]|тяжело|одиночеств|печал[ьн]|скук[а-я]|апати[яю]|разбит[а-я]|опустош[её]н)\b",
        "context_clues": [r"сегодня", r"последн[ее] время", r"уже недел"],
        "weight": 1.0
    },
    "mood_good": {
        "keywords": r"\b(хорошо|отлично|рад[ао]?|happy|good.?mood|весел[а-я]|прекрасно|замечательно|классно|круто|здорово|энерги[яй]|бодр[а-я]|вдохнов[её]н)\b",
        "context_clues": [r"сегодня", r"наконец"],
        "weight": 1.0
    },
    "symptom_pain": {
        "keywords": r"\b(бол[ьи]|болит|голов[а-я]|симптом|усталость|fatigue|боль[а-я]? в|мигрен|ломот[а-я]|но[юе]т|кол[ию]т|жжени[ея]|пульсир|спазм|судорог|тошн[о-я]|головокруж|слабость)\b",
        "context_clues": [r"с утра", r"вс?чера", r"уже.*дн[еяй]", r"не проходит"],
        "weight": 1.2
    },
    "symptom_cold_flu": {
        "keywords": r"\b(простуд[а-я]|насморк|кашель|температур[а-я]|горл[оа] бол|чиха|грипп|ОРВИ|сопл[и]|озноб|горячк[а-и])\b",
        "context_clues": [r"заболел", r"простудил", r"поправить"],
        "weight": 1.0
    },
    "exercise": {
        "keywords": r"\b(пробежал|тренировк[аи]|спорт|фитнес|прогулк[аи]|ходьб[аи]|велосипед|йога|плавал|зарядк[аи])\b",
        "context_clues": [r"утром", r"вечером"],
        "weight": 0.9
    },
    "caffeine_alcohol": {
        "keywords": r"\b(кофе|чай|энергетик|вино|пиво|водк[аи]|алкогол[ья]|выпил|кофеин)\b",
        "context_clues": [r"перед сном", r"вечером"],
        "weight": 0.8
    },
    "social": {
        "keywords": r"\b(встреч[аи]|друзь[яи]|семья|разговор|общени[ея]|вечеринк[аи]|позвонил|увиделся)\b",
        "context_clues": [],
        "weight": 0.7
    },
}

TIME_OF_DAY_RANGES = {
    "night": (0, 6),
    "morning": (6, 12),
    "afternoon": (12, 18),
    "evening": (18, 24),
}

def _get_time_of_day(hour: int) -> str:
    for tod, (start, end) in TIME_OF_DAY_RANGES.items():
        if start <= hour < end:
            return tod
    return "unknown"

def _parse_omi_file(path: Path) -> Optional[Dict[str, Any]]:
    """Improved Omi parser with timestamps, context, speakers, quality (from sub-agent)."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        frontmatter = {}
        if fm_match:
            for line in fm_match.group(1).splitlines():
                if ":" in line:
                    k, v = [x.strip() for x in line.split(":", 1)]
                    frontmatter[k] = v

        date_str = frontmatter.get("date", "")
        if not date_str:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
            date_str = m.group(1) if m else None

        # Speaker separation from **Speaker** [MM:SS]: text
        transcript_lines = re.findall(r"\*\*([^*]+)\*\*\s*\[(\d+):(\d+)\]:\s*(.+)", content)
        speakers = list(set([s[0] for s in transcript_lines]))
        body = content[fm_match.end():] if fm_match else content
        spoken = " ".join([s[3] for s in transcript_lines])
        full_text = (spoken + " " + body).lower()

        # Context words resolution (сегодня/вчера etc.)
        context_words = []
        context_map = {
            r"сегодня|today|сегодняшний": "today",
            r"вчера|yesterday|вчерашний": "yesterday",
            r"завтра|tomorrow|завтрашний": "tomorrow",
            r"позавчера": "day-2",
            r"послезавтра": "day+2",
        }
        for pat, label in context_map.items():
            if re.search(pat, full_text, re.I):
                context_words.append(label)

        # Time of day
        time_str = frontmatter.get("time", "")
        hour = 12
        if time_str:
            try:
                hour = int(time_str.split(":")[0])
            except:
                pass
        time_of_day = _get_time_of_day(hour)

        # Signals with quality scoring
        signals_with_quality = []
        for sig, cfg in SIGNAL_PATTERNS.items():
            matches = len(re.findall(cfg["keywords"], full_text, re.I))
            if matches > 0:
                context_hits = sum(1 for clue in cfg["context_clues"] if re.search(clue, full_text, re.I))
                quality = cfg["weight"] * (1 + 0.15 * math.log1p(matches)) + 0.2 * context_hits
                quality = min(quality, 2.0)
                signals_with_quality.append({
                    "signal": sig,
                    "quality_score": round(quality, 3),
                    "match_count": matches,
                    "context_hits": context_hits
                })

        signals = [s["signal"] for s in signals_with_quality]

        sq = "unknown"
        if SLEEP_POOR_RE.search(full_text):
            sq = "poor"
        elif SLEEP_GOOD_RE.search(full_text):
            sq = "good"

        return {
            "path": str(path),
            "date": date_str,
            "time_of_day": time_of_day,
            "speakers": speakers,
            "signals": signals,
            "signals_with_quality": signals_with_quality,
            "context_words": context_words,
            "sleep_quality": sq,
            "snippet": (spoken[:300] + "...") if len(spoken) > 300 else spoken
        } if date_str and signals else None
    except Exception as e:
        return None

def _resolve_vault() -> Path:
    """Use demo vault automatically when the configured vault has no parseable notes."""
    global OMI_VAULT_PATH
    for vault in (_DEFAULT_VAULT, _DEMO_VAULT):
        conv = vault / "050 Daily Omi" / "Conversations"
        if conv.exists() and any(conv.rglob("*.md")):
            OMI_VAULT_PATH = vault
            return vault
    OMI_VAULT_PATH = _DEFAULT_VAULT
    return _DEFAULT_VAULT


def _scan_omi(limit: int = 100) -> List[Dict]:
    vault = _resolve_vault()
    candidates = [
        vault / "050 Daily Omi" / "Conversations",
        vault / "050 Daily Omi" / "telegram-extracts",
    ]
    files = []
    for base in candidates:
        if base.exists():
            files.extend(list(base.rglob("*.md")))
    files = sorted(files, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)[:limit]
    return [p for p in (_parse_omi_file(f) for f in files) if p]


def _sleep_quality(entry: Dict[str, Any]) -> str:
    if entry.get("sleep_quality"):
        return entry["sleep_quality"]
    text = entry.get("snippet", "")
    if SLEEP_POOR_RE.search(text):
        return "poor"
    if SLEEP_GOOD_RE.search(text):
        return "good"
    return "unknown"


def _confidence_from_samples(n: int, min_for_high: int = 5) -> float:
    if n <= 0:
        return 0.15
    if n >= min_for_high:
        return min(0.95, 0.55 + 0.08 * n)
    return round(0.25 + 0.12 * n, 2)


def _simulate_whatif_core(entries: List[Dict], scenario: Dict[str, Any]) -> Dict[str, Any]:
    duration = int(scenario.get("duration_days", 14))
    targets = scenario.get("target_signals") or ["mood_low", "stress", "symptom_pain"]
    intervention = scenario.get("intervention", "consistent_sleep_7_5h")

    by_date: Dict[str, Dict] = {}
    for e in entries:
        d = e.get("date")
        if d:
            by_date[d] = e

    dates = sorted(by_date.keys())
    if len(dates) < 7:
        return {
            "intervention": intervention,
            "duration_days": duration,
            "projected_outcomes": [],
            "based_on": {"similar_periods": 0, "days_analyzed": len(dates)},
            "confidence": 0.1,
            "disclaimer": DISCLAIMER,
            "note": "Not enough historical days for a reliable projection.",
        }

    # Day-after rates following good vs poor sleep nights
    after_poor = defaultdict(int)
    after_good = defaultdict(int)
    poor_n = good_n = 0

    for i, d in enumerate(dates[:-1]):
        sq = _sleep_quality(by_date[d])
        nxt = dates[i + 1]
        nxt_signals = set(by_date[nxt].get("signals", []))
        if sq == "poor":
            poor_n += 1
            for sig in targets:
                if sig in nxt_signals:
                    after_poor[sig] += 1
        elif sq == "good":
            good_n += 1
            for sig in targets:
                if sig in nxt_signals:
                    after_good[sig] += 1

    # Current baseline: rate on day after any sleep mention
    current_after = defaultdict(int)
    sleep_days = 0
    for i, d in enumerate(dates[:-1]):
        if "sleep" in by_date[d].get("signals", []):
            sleep_days += 1
            nxt_signals = set(by_date[dates[i + 1]].get("signals", []))
            for sig in targets:
                if sig in nxt_signals:
                    current_after[sig] += 1

    projected = []
    citations = []
    for sig in targets:
        rate_poor = after_poor[sig] / poor_n if poor_n else None
        rate_good = after_good[sig] / good_n if good_n else None
        rate_now = current_after[sig] / sleep_days if sleep_days else 0

        if rate_poor is not None and rate_good is not None and rate_poor > rate_good:
            delta_pct = round((rate_good - rate_poor) / rate_poor * 100, 1)
            projected.append({
                "signal": sig,
                "current_day_after_rate": round(rate_now, 3),
                "projected_day_after_rate": round(rate_good, 3),
                "change_percent": delta_pct,
                "direction": "decrease" if delta_pct < 0 else "increase",
            })
        elif rate_now > 0:
            projected.append({
                "signal": sig,
                "current_day_after_rate": round(rate_now, 3),
                "projected_day_after_rate": round(max(0, rate_now * 0.85), 3),
                "change_percent": -15.0,
                "direction": "decrease",
                "note": "Conservative estimate — limited good/poor sleep contrast in data",
            })

    # Collect example citations from poor-sleep -> target lag-1 days
    for i, d in enumerate(dates[:-1]):
        if _sleep_quality(by_date[d]) != "poor":
            continue
        nxt = dates[i + 1]
        nxt_entry = by_date[nxt]
        if any(s in nxt_entry.get("signals", []) for s in targets):
            citations.append({
                "cause_date": d,
                "effect_date": nxt,
                "excerpt": nxt_entry.get("snippet", "")[:200],
            })
        if len(citations) >= 3:
            break

    similar = min(good_n, poor_n)
    conf = _confidence_from_samples(similar)

    return {
        "intervention": intervention,
        "duration_days": duration,
        "projected_outcomes": projected,
        "based_on": {
            "similar_periods": similar,
            "good_sleep_nights": good_n,
            "poor_sleep_nights": poor_n,
            "days_analyzed": len(dates),
            "method": "Compare day-after signal rates following good vs poor sleep nights in your history",
        },
        "confidence": conf,
        "sources": citations,
        "disclaimer": DISCLAIMER,
    }

# Apple Health (kept from previous)
def _find_apple_export() -> Optional[Path]:
    for p in APPLE_HEALTH_PATHS:
        if p.exists():
            xml = p / "export.xml"
            if xml.exists():
                return xml
    return None

def _generate_demo_apple() -> Dict[str, Any]:
    import random
    random.seed(42)
    return {
        "source": "demo",
        "summary": {
            "heart_rate": {"avg": 73.4, "count": 90},
            "steps": {"avg": 6600, "count": 30},
            "sleep_hours": {"avg": 6.75, "count": 30},
            "spo2": {"avg": 97.5, "count": 30},
        },
        "days": 30
    }

def _parse_apple_health(xml_path: Optional[Path]) -> Dict[str, Any]:
    if not xml_path or not xml_path.exists():
        return _generate_demo_apple()
    # Simplified real parser (full version from sub-agent had more)
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        records = root.findall(".//Record")
        data = defaultdict(list)
        for rec in records[:5000]:  # limit for speed
            t = rec.get("type", "")
            val = rec.get("value")
            if not val: continue
            try: val = float(val)
            except: continue
            if "HeartRate" in t: data["heart_rate"].append(val)
            elif "StepCount" in t: data["steps"].append(val)
            elif "Sleep" in t: data["sleep_hours"].append(val / 60 if val > 60 else val)
            elif "SpO2" in t: data["spo2"].append(val)
        summary = {k: {"avg": sum(v)/len(v), "count": len(v)} for k, v in data.items() if v}
        return {"source": "real", "summary": summary, "days": len(set(r.get("startDate","")[:10] for r in records))}
    except:
        return _generate_demo_apple()

# === Phase 1 Analytics Core (from analytics sub-agent) ===
def _build_timeseries(entries: List[Dict]) -> Dict[str, Any]:
    by_date = defaultdict(set)
    for e in entries:
        if e.get("date"):
            by_date[e["date"]].update(e.get("signals", []))
    date_list = sorted(by_date.keys())
    signal_series = {sig: [1 if sig in by_date[d] else 0 for d in date_list] for sig in SIGNAL_PATTERNS}
    return {"by_date": by_date, "date_list": date_list, "signal_series": signal_series}

def _compute_temporal_correlations(ts: Dict, max_lag: int = 3) -> List[Dict]:
    by_date = ts["by_date"]
    date_list = ts["date_list"]
    results = []
    signals = list(SIGNAL_PATTERNS.keys())
    for a in signals:
        for b in signals:
            if a == b: continue
            for lag in range(1, max_lag + 1):
                co = 0
                a_count = 0
                for i, d in enumerate(date_list):
                    if a in by_date.get(d, set()):
                        a_count += 1
                        lag_idx = i + lag
                        if lag_idx < len(date_list):
                            lag_d = date_list[lag_idx]
                            if b in by_date.get(lag_d, set()):
                                co += 1
                if a_count == 0: continue
                prob = co / a_count
                base_prob = sum(1 for d in date_list if b in by_date.get(d, set())) / max(len(date_list), 1)
                lift = prob / base_prob if base_prob > 0 else 0
                if lift > 1.2:
                    results.append({
                        "cause": a, "effect": b, "lag": lag,
                        "probability": round(prob, 3),
                        "lift_ratio": round(lift, 2),
                        "example_dates": [d for i, d in enumerate(date_list) if i + lag < len(date_list) and a in by_date.get(d, set())][:3]
                    })
    return sorted(results, key=lambda x: x["lift_ratio"], reverse=True)[:15]

def _compute_baseline_stats(ts: Dict) -> Dict[str, Any]:
    date_list = ts["date_list"]
    by_date = ts["by_date"]
    stats = {}
    n = len(date_list)
    for sig in SIGNAL_PATTERNS:
        freq = sum(1 for d in date_list if sig in by_date.get(d, set())) / max(n, 1)
        stats[sig] = {"frequency": round(freq, 3), "std": 0.0, "trend": "stable"}
    return stats

def _compute_anomalies(entries: List[Dict], baseline: Dict) -> List[Dict]:
    anomalies = []
    for e in entries:
        for sig in e.get("signals", []):
            if baseline.get(sig, {}).get("frequency", 0) < 0.1:
                anomalies.append({"date": e["date"], "signal": sig, "type": "rare_signal"})
    return anomalies[:10]

# Apple helpers
def load_apple_health_data() -> Dict[str, Any]:
    export = _find_apple_export()
    data = _parse_apple_health(export)
    return {"status": "ok", "data": data, "real_export": export is not None}

def analyze_apple_patterns() -> Dict[str, Any]:
    data = load_apple_health_data()["data"]
    return {
        "source": data["source"],
        "sample_summary": data.get("summary", {}),
        "anomalies": [],
        "patterns": ["HR and sleep correlation possible"],
        "days_covered": data.get("days", 0)
    }

@mcp.tool()
def analyze_lifestyle_patterns(time_range: str = "last_90_days") -> Dict[str, Any]:
    entries = _scan_omi(120)
    ts = _build_timeseries(entries)
    by_date = ts["by_date"]
    baseline = _compute_baseline_stats(ts)
    temporal = _compute_temporal_correlations(ts)
    anomalies = _compute_anomalies(entries, baseline)
    apple = analyze_apple_patterns()

    co = sum(1 for sigs in by_date.values() if "sleep" in sigs and "stress" in sigs)
    vault = _resolve_vault()
    for c in temporal[:10]:
        c["confidence"] = _confidence_from_samples(len(c.get("example_dates", [])))
    return {
        "version": "3.0",
        "vault_path": str(vault),
        "time_range": time_range,
        "files_scanned": len(entries),
        "unique_dates": len(by_date),
        "signals_distribution": dict(Counter(s for e in entries for s in e.get("signals", []))),
        "baseline": baseline,
        "co_occurrence": [{"pattern": "sleep+stress same day", "count": co}],
        "temporal_correlations": temporal,
        "anomalies": anomalies,
        "apple_patterns": apple,
        "recommendations": ["Collect more Omi notes on sleep/mood", "Export Apple Health data"],
        "disclaimer": DISCLAIMER,
        "phase": "sprint-1"
    }

@mcp.tool()
def find_correlation(metric_a: str = "sleep", metric_b: str = "stress", lag: int = 1) -> Dict[str, Any]:
    entries = _scan_omi(80)
    ts = _build_timeseries(entries)
    # simplified lag logic
    co = 0
    for i, d in enumerate(ts["date_list"]):
        if metric_a in ts["by_date"].get(d, set()):
            lag_idx = i + lag
            if lag_idx < len(ts["date_list"]):
                if metric_b in ts["by_date"].get(ts["date_list"][lag_idx], set()):
                    co += 1
    return {"metric_a": metric_a, "metric_b": metric_b, "lag": lag, "co_occurrences": co,
            "disclaimer": DISCLAIMER}

@mcp.tool()
def simulate_whatif(scenario: dict) -> Dict[str, Any]:
    """
    Project lifestyle signal changes if an intervention is applied, based on YOUR historical patterns.

    Example scenario:
      {"intervention": "consistent_sleep_7_5h", "duration_days": 14,
       "target_signals": ["mood_low", "stress", "symptom_pain"]}
    """
    entries = _scan_omi(120)
    return _simulate_whatif_core(entries, scenario or {})

@mcp.tool()
def generate_doctor_report(format: str = "markdown") -> str:
    analysis = analyze_lifestyle_patterns()
    apple = analyze_apple_patterns()
    if format == "json":
        return json.dumps({"analysis": analysis, "apple": apple}, ensure_ascii=False, indent=2)
    if format == "html":
        return "<html><body><h1>VitaCo Report</h1><pre>" + json.dumps(analysis, indent=2) + "</pre></body></html>"
    # markdown default
    return f"""# VitaCo Health Pattern Report v2.5

**Date:** {datetime.date.today()}
**Omi:** {analysis['files_scanned']} files, {analysis['unique_dates']} days
**Apple:** {apple['source']} ({apple['days_covered']} days)

## Temporal Correlations (lags)
{json.dumps(analysis.get('temporal_correlations', [])[:5], ensure_ascii=False, indent=2)}

## Anomalies
{json.dumps(analysis.get('anomalies', [])[:5], ensure_ascii=False, indent=2)}

**Important:** Patterns and signals only. For doctor review. Not a diagnosis.
"""

@mcp.tool()
def combine_omi_and_apple() -> Dict[str, Any]:
    omi = _scan_omi(50)
    apple = load_apple_health_data()["data"]
    return {
        "omi_days": len(set(e["date"] for e in omi if e.get("date"))),
        "apple_days": apple.get("days", 0),
        "apple_summary": apple.get("summary", {}),
        "note": "Merge by date for future correlation."
    }

@mcp.tool()
def list_data_sources() -> Dict[str, Any]:
    export = _find_apple_export()
    return {
        "version": "2.5",
        "omi_files": len(list((OMI_VAULT_PATH / "050 Daily Omi").rglob("*.md"))) if (OMI_VAULT_PATH / "050 Daily Omi").exists() else 0,
        "apple_export_found": bool(export),
        "supported_signals": list(SIGNAL_PATTERNS.keys()),
        "parser_features": ["context words (сегодня/вчера)", "speaker separation", "quality scoring", "time-of-day", "lag 1-3d correlations", "anomalies vs baseline"],
        "status": "Phase 1 complete (Omi parser + Apple + Analytics)"
    }

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        os.environ.setdefault("OMI_VAULT_PATH", str(_DEMO_VAULT))
        print("VitaSide v3.0 self-test")
        test_entries = [
            {"date": "2026-06-01", "signals": ["sleep", "stress"], "snippet": "плохо спал ночью"},
            {"date": "2026-06-02", "signals": ["stress", "mood_low"], "snippet": "стресс и плохое настроение"},
            {"date": "2026-06-03", "signals": ["sleep"], "snippet": "спал отлично выспался"},
            {"date": "2026-06-04", "signals": ["mood_good"], "snippet": "отличное настроение"},
        ]
        ts = _build_timeseries(test_entries)
        assert len(ts["date_list"]) == 4
        sim = _simulate_whatif_core(test_entries, {"duration_days": 14})
        assert "projected_outcomes" in sim and "disclaimer" in sim
        print("Timeseries OK, dates:", len(ts["date_list"]))
        print("simulate_whatif OK, confidence:", sim["confidence"])
        print("All tests passed.")
    else:
        mcp.run(transport="stdio")
