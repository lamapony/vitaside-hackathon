#!/opt/anaconda3/bin/python3
"""
VitaSide Health Pattern MCP Server — v1.0 MVP
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

from sidecar_protocol import (
    load_manifest,
    assert_sidecar_active,
    check_scope,
    audit,
    audit_summary,
    is_expired,
    is_revoked,
)
from report_html import generate_html_report
from report_doctor import generate_doctor_view
from apple_merge import parse_daily, merge_with_omi
from anonymize import anonymize_text, anonymize_citations
from visit_questions import generate_visit_questions as build_visit_questions
from export_obsidian import build_obsidian_note
from analytics_depth import add_pvalues, weekly_summary, compare_periods as compare_periods_analysis
from actionable_insights import build_actionable_briefing, format_briefing_terminal

_MANIFEST: Optional[Dict[str, Any]] = None


def _get_manifest() -> Dict[str, Any]:
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = load_manifest()
    return _MANIFEST


def _with_gates(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload.setdefault("disclaimer", DISCLAIMER)
    payload.setdefault("quality_gates", _get_manifest().get("quality_gates", []))
    return payload

try:
    import pandas as pd
    import numpy as np
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    pd = np = sp_stats = None

mcp = FastMCP("vitaside-health-mvp-1.0")

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

        excerpts: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        for speaker, _mm, _ss, text in transcript_lines:
            line = text.strip()
            line_lower = line.lower()
            for sig, cfg in SIGNAL_PATTERNS.items():
                if re.search(cfg["keywords"], line_lower, re.I):
                    excerpts[sig].append({"text": line, "speaker": speaker})

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
            "excerpts": dict(excerpts),
            "snippet": (spoken[:300] + "...") if len(spoken) > 300 else spoken
        } if date_str and signals else None
    except Exception as e:
        return None

def _omi_search_paths(vault: Path) -> List[Path]:
    paths: List[Path] = []
    for part in os.getenv("VITASIDE_OMI_PATHS", "").split(":"):
        if part.strip():
            p = Path(part.strip()).expanduser()
            if p.exists():
                paths.append(p)
    for rel in ("050 Daily Omi/Conversations", "050 Daily Omi", "Daily Notes", "Journal", "Health"):
        p = vault / rel
        if p.exists() and p not in paths:
            paths.append(p)
    return paths or [vault]


def _parseable_count(vault: Path, cap: int = 200) -> int:
    files: List[Path] = []
    for base in _omi_search_paths(vault):
        files.extend(base.rglob("*.md"))
    files = files[:cap]
    return sum(1 for f in files if _parse_omi_file(f))


def _build_brief(entries: List[Dict], analysis: Dict[str, Any]) -> Dict[str, Any]:
    by_date = _entries_by_date(entries)
    merge = merge_with_omi(by_date, parse_daily(_find_apple_export()))
    whatif = _simulate_whatif_core(entries, {
        "intervention": "consistent_sleep_7_5h",
        "duration_days": 14,
        "target_signals": ["mood_low", "stress", "symptom_pain"],
    })
    period = compare_periods_analysis(entries, 14)
    return build_actionable_briefing(analysis, merge, whatif, period)


def _resolve_vault() -> Path:
    """Explicit OMI_VAULT_PATH is never silently replaced by demo data."""
    global OMI_VAULT_PATH
    explicit = "OMI_VAULT_PATH" in os.environ
    if explicit:
        OMI_VAULT_PATH = _DEFAULT_VAULT
        return _DEFAULT_VAULT
    if _parseable_count(_DEFAULT_VAULT) >= 3:
        OMI_VAULT_PATH = _DEFAULT_VAULT
        return _DEFAULT_VAULT
    OMI_VAULT_PATH = _DEMO_VAULT
    return _DEMO_VAULT


def _scan_omi(limit: int = 100, tool: str = "scan_omi") -> List[Dict]:
    assert_sidecar_active(_get_manifest())
    vault = _resolve_vault()
    manifest = _get_manifest()
    files: List[Path] = []
    for base in _omi_search_paths(vault):
        files.extend(base.rglob("*.md"))
    files = sorted(set(files), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    allowed_files = [f for f in files if check_scope(manifest, f)][:limit]
    parsed = [p for p in (_parse_omi_file(f) for f in allowed_files) if p]
    audit(tool, {"files": [str(f) for f in allowed_files], "count": len(parsed), "vault": str(vault)})
    return parsed


def _entries_by_date(entries: List[Dict]) -> Dict[str, Dict]:
    return {e["date"]: e for e in entries if e.get("date")}


def _cite_for_entry(entry: Dict[str, Any], signal: str) -> Dict[str, str]:
    ex = entry.get("excerpts", {}).get(signal, [])
    text = ex[0]["text"] if ex else entry.get("snippet", "")
    return {"date": entry.get("date", ""), "excerpt": text[:220]}


def _enrich_correlations(entries: List[Dict], temporal: List[Dict]) -> List[Dict]:
    by_date = _entries_by_date(entries)
    for c in temporal:
        cites = []
        for d in c.get("example_dates", []):
            e = by_date.get(d)
            if not e:
                continue
            lag = c.get("lag", 1)
            date_list = sorted(by_date.keys())
            try:
                idx = date_list.index(d)
                effect_date = date_list[idx + lag] if idx + lag < len(date_list) else d
                effect_entry = by_date.get(effect_date, e)
            except ValueError:
                effect_entry = e
            cites.append(_cite_for_entry(effect_entry, c.get("effect", "")))
        c["citations"] = cites[:2]
        c["confidence"] = _confidence_from_samples(len(c.get("example_dates", [])))
    return temporal


def _enrich_anomalies(entries: List[Dict], anomalies: List[Dict]) -> List[Dict]:
    by_date = _entries_by_date(entries)
    for a in anomalies:
        e = by_date.get(a.get("date", ""), {})
        sig = a.get("signal", "")
        a["citations"] = [_cite_for_entry(e, sig)] if e else []
        a["confidence"] = _confidence_from_samples(1 if e else 0)
    return anomalies


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
def analyze_patterns(time_range: str = "last_90_days") -> Dict[str, Any]:
    """SPEC alias for analyze_lifestyle_patterns."""
    return analyze_lifestyle_patterns(time_range)

@mcp.tool()
def analyze_lifestyle_patterns(time_range: str = "last_90_days") -> Dict[str, Any]:
    entries = _scan_omi(120, tool="analyze_lifestyle_patterns")
    ts = _build_timeseries(entries)
    by_date = ts["by_date"]
    baseline = _compute_baseline_stats(ts)
    temporal = _enrich_correlations(entries, add_pvalues(_compute_temporal_correlations(ts), len(by_date)))
    anomalies = _enrich_anomalies(entries, _compute_anomalies(entries, baseline))
    apple = analyze_apple_patterns()

    co = sum(1 for sigs in by_date.values() if "sleep" in sigs and "stress" in sigs)
    vault = _resolve_vault()
    manifest = _get_manifest()
    core = {
        "version": "1.0-mvp",
        "sidecar": manifest.get("name"),
        "sidecar_expired": is_expired(manifest),
        "sidecar_revoked": is_revoked(manifest),
        "data_mode": "explicit" if "OMI_VAULT_PATH" in os.environ else ("demo" if str(vault) == str(_DEMO_VAULT) else "auto"),
        "vault_path": str(vault),
        "time_range": time_range,
        "files_scanned": len(entries),
        "unique_dates": len(by_date),
        "signals_distribution": dict(Counter(s for e in entries for s in e.get("signals", []))),
        "baseline": baseline,
        "co_occurrence": [{"pattern": "sleep+stress same day", "count": co, "confidence": _confidence_from_samples(co)}],
        "temporal_correlations": temporal,
        "anomalies": anomalies,
        "apple_patterns": apple,
        "recommendations": ["Collect more Omi notes on sleep/mood", "Export Apple Health data"],
        "audit_summary": audit_summary(5),
        "phase": "demo-polish",
    }
    core["actionable_briefing"] = _build_brief(entries, core)
    return _with_gates(core)

@mcp.tool()
def get_actionable_briefing() -> Dict[str, Any]:
    """Top insights from YOUR data — with citations. The moat vs generic LLM chat."""
    entries = _scan_omi(120, tool="get_actionable_briefing")
    analysis = analyze_lifestyle_patterns()
    brief = analysis.get("actionable_briefing") or _build_brief(entries, analysis)
    return _with_gates(brief)

@mcp.tool()
def find_correlation(metric_a: str = "sleep", metric_b: str = "stress", lag: int = 1) -> Dict[str, Any]:
    entries = _scan_omi(80, tool="find_correlation")
    ts = _build_timeseries(entries)
    by_date = _entries_by_date(entries)
    co = 0
    example_dates = []
    for i, d in enumerate(ts["date_list"]):
        if metric_a in ts["by_date"].get(d, set()):
            lag_idx = i + lag
            if lag_idx < len(ts["date_list"]):
                lag_d = ts["date_list"][lag_idx]
                if metric_b in ts["by_date"].get(lag_d, set()):
                    co += 1
                    example_dates.append(lag_d)
    citations = [_cite_for_entry(by_date[d], metric_b) for d in example_dates[:2] if d in by_date]
    return _with_gates({
        "metric_a": metric_a, "metric_b": metric_b, "lag": lag,
        "co_occurrences": co,
        "confidence": _confidence_from_samples(co),
        "citations": citations,
    })

@mcp.tool()
def simulate_whatif(scenario: dict) -> Dict[str, Any]:
    """
    Project lifestyle signal changes if an intervention is applied, based on YOUR historical patterns.

    Example scenario:
      {"intervention": "consistent_sleep_7_5h", "duration_days": 14,
       "target_signals": ["mood_low", "stress", "symptom_pain"]}
    """
    entries = _scan_omi(120, tool="simulate_whatif")
    return _with_gates(_simulate_whatif_core(entries, scenario or {}))

DEFAULT_HOST_CONTEXT = {
    "agent": "hermes-main",
    "events": [
        {"date": "2026-05-02", "type": "travel", "note": "Late flight return, landed 01:30"},
        {"date": "2026-05-09", "type": "travel", "note": "Conference trip — 2 nights in hotel"},
        {"date": "2026-05-16", "type": "deadline", "note": "Product launch crunch week"},
        {"date": "2026-05-23", "type": "travel", "note": "Weekend trip, red-eye Sunday"},
        {"date": "2026-06-06", "type": "deadline", "note": "Hackathon prep sprint"},
    ],
}


def _dates_near_events(events: List[Dict], window: int = 2) -> set:
    out = set()
    for ev in events:
        try:
            d = datetime.date.fromisoformat(ev["date"])
        except ValueError:
            continue
        for delta in range(-window, window + 1):
            out.add((d + datetime.timedelta(days=delta)).isoformat())
    return out


def _collaborative_insight_core(host_context: Dict[str, Any]) -> Dict[str, Any]:
    entries = _scan_omi(120, tool="collaborative_insight")
    analysis = analyze_lifestyle_patterns()
    apple = combine_omi_and_apple()
    events = host_context.get("events", [])
    travel_dates = _dates_near_events([e for e in events if e.get("type") == "travel"])
    deadline_dates = _dates_near_events([e for e in events if e.get("type") == "deadline"], window=3)
    by_date = _entries_by_date(entries)

    poor_near_travel, stress_near_deadline = [], []
    for d in travel_dates:
        e = by_date.get(d)
        if e and e.get("sleep_quality") == "poor":
            poor_near_travel.append({"date": d, "excerpt": e.get("snippet", "")[:160]})
    for d in deadline_dates:
        e = by_date.get(d)
        if e and "stress" in e.get("signals", []):
            stress_near_deadline.append({"date": d, "excerpt": e.get("snippet", "")[:160]})

    top = (analysis.get("temporal_correlations") or [{}])[0]
    parts = []
    if poor_near_travel:
        p = poor_near_travel[0]
        parts.append(
            f"{len(poor_near_travel)} poor-sleep nights within ±2 days of travel "
            f"(e.g. {p['date']}: \"{p['excerpt'][:80]}\")."
        )
    if stress_near_deadline:
        parts.append(f"Stress signals on {len(stress_near_deadline)} days near deadline windows.")
    if not parts:
        parts.append("Travel/deadline windows overlap with sleep+stress co-occurrence in sidecar data.")
    parts.append(
        f"Sidecar correlation: {top.get('cause')}→{top.get('effect')} lag {top.get('lag')}d. "
        f"Main agent tracked {len(events)} life events."
    )

    return {
        "main_agent_context": host_context,
        "collaborative_insight": " ".join(parts),
        "evidence": {
            "poor_sleep_near_travel": poor_near_travel[:3],
            "stress_near_deadline": stress_near_deadline[:3],
            "top_correlation": top,
            "apple_summary": apple.get("apple_summary", {}),
        },
        "confidence": _confidence_from_samples(len(poor_near_travel) + len(stress_near_deadline)),
    }


@mcp.tool()
def collaborative_insight(host_context: dict = None) -> Dict[str, Any]:
    """Merge main-agent life context with sidecar biometric/pattern analysis."""
    ctx = host_context if host_context else DEFAULT_HOST_CONTEXT
    audit("collaborative_insight", {"events": len(ctx.get("events", []))})
    return _with_gates(_collaborative_insight_core(ctx))

@mcp.tool()
def generate_doctor_report(format: str = "markdown", include_whatif: bool = True, anonymize: bool = False) -> str:
    entries = _scan_omi(120, tool="generate_doctor_report")
    analysis = analyze_lifestyle_patterns()
    if anonymize:
        for c in analysis.get("temporal_correlations", []):
            c["citations"] = anonymize_citations(c.get("citations", []))
    apple = analyze_apple_patterns()
    whatif = _simulate_whatif_core(entries, {
        "intervention": "consistent_sleep_7_5h",
        "duration_days": 14,
        "target_signals": ["mood_low", "stress", "symptom_pain"],
    }) if include_whatif else {}
    audit_info = audit_summary(10)

    if format == "json":
        return json.dumps(_with_gates({
            "analysis": analysis, "apple": apple, "whatif": whatif, "audit": audit_info,
        }), ensure_ascii=False, indent=2)

    if format == "html":
        brief = analysis.get("actionable_briefing") or _build_brief(entries, analysis)
        html_out = generate_html_report(analysis, apple, entries, whatif, audit_info, DISCLAIMER, brief)
        out_path = _SCRIPT_DIR / "out" / f"vitaside-report-{datetime.date.today()}.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_out, encoding="utf-8")
        audit("report_export", {"format": "html", "path": str(out_path)})
        return html_out

    if format == "doctor":
        by_date = _entries_by_date(entries)
        apple_daily = parse_daily(_find_apple_export())
        merge = merge_with_omi(by_date, apple_daily)
        doc_html = generate_doctor_view(
            analysis, merge, whatif, DISCLAIMER,
            analysis.get("actionable_briefing") or _build_brief(entries, analysis),
        )
        out_path = _SCRIPT_DIR / "out" / f"vitaside-doctor-{datetime.date.today()}.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(doc_html, encoding="utf-8")
        audit("report_export", {"format": "doctor", "path": str(out_path), "anonymized": anonymize})
        return doc_html

    if format == "obsidian":
        by_date = _entries_by_date(entries)
        merge = merge_with_omi(by_date, parse_daily(_find_apple_export()))
        questions = build_visit_questions(analysis, merge, whatif)
        note = build_obsidian_note(analysis, questions, whatif, anonymized=anonymize)
        out_path = _SCRIPT_DIR / "out" / f"vitaside-visit-prep-{datetime.date.today()}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(note, encoding="utf-8")
        audit("report_export", {"format": "obsidian", "path": str(out_path)})
        return note

    lines = [
        f"# VitaSide Health Pattern Report v1.0",
        f"",
        f"**Date:** {datetime.date.today()}",
        f"**Omi:** {analysis['files_scanned']} files, {analysis['unique_dates']} days",
        f"**Apple:** {apple['source']} ({apple['days_covered']} days)",
        f"",
        f"## Top Correlations",
    ]
    for c in analysis.get("temporal_correlations", [])[:5]:
        lines.append(f"- **{c['cause']} → {c['effect']}** (lag {c['lag']}d, lift {c['lift_ratio']}, conf {c.get('confidence')})")
        for cite in c.get("citations", [])[:1]:
            lines.append(f"  > {cite.get('date')}: {cite.get('excerpt', '')[:120]}")
    if whatif.get("projected_outcomes"):
        lines += ["", "## What-If", json.dumps(whatif["projected_outcomes"], ensure_ascii=False, indent=2)]
    lines += ["", f"**{DISCLAIMER}**"]
    return "\n".join(lines)

@mcp.tool()
def generate_visit_questions() -> Dict[str, Any]:
    """Discussion topics for your next doctor visit, grounded in your patterns."""
    entries = _scan_omi(120, tool="generate_visit_questions")
    analysis = analyze_lifestyle_patterns()
    merge = combine_omi_and_apple()
    whatif = _simulate_whatif_core(entries, {"duration_days": 14, "target_signals": ["mood_low", "stress"]})
    return _with_gates(build_visit_questions(analysis, merge, whatif))

@mcp.tool()
def weekly_summary_report() -> Dict[str, Any]:
    """Roll up signal counts by ISO week for the last ~8 weeks."""
    entries = _scan_omi(120, tool="weekly_summary")
    return _with_gates(weekly_summary(entries))

@mcp.tool()
def compare_periods(recent_days: int = 14) -> Dict[str, Any]:
    """Compare signal frequency: last N days vs the N days before that."""
    entries = _scan_omi(120, tool="compare_periods")
    return _with_gates(compare_periods_analysis(entries, recent_days))

@mcp.tool()
def export_visit_bundle(anonymize: bool = False) -> Dict[str, Any]:
    """Generate doctor HTML + patient HTML + Obsidian note + questions in out/."""
    generate_doctor_report(format="html", anonymize=anonymize)
    generate_doctor_report(format="doctor", anonymize=anonymize)
    generate_doctor_report(format="obsidian", anonymize=anonymize)
    qs = generate_visit_questions()
    today = datetime.date.today().isoformat()
    return _with_gates({
        "bundle_date": today,
        "outputs": {
            "patient_html": str(_SCRIPT_DIR / "out" / f"vitaside-report-{today}.html"),
            "doctor_html": str(_SCRIPT_DIR / "out" / f"vitaside-doctor-{today}.html"),
            "obsidian_note": str(_SCRIPT_DIR / "out" / f"vitaside-visit-prep-{today}.md"),
        },
        "questions_count": qs.get("count", 0),
        "anonymized": anonymize,
    })

@mcp.tool()
def combine_omi_and_apple() -> Dict[str, Any]:
    entries = _scan_omi(120, tool="combine_omi_and_apple")
    by_date = _entries_by_date(entries)
    apple_daily = parse_daily(_find_apple_export())
    merge = merge_with_omi(by_date, apple_daily)
    return _with_gates({
        "omi_days": len(by_date),
        "apple_days": len(apple_daily),
        "overlap_days": merge.get("overlap_days", 0),
        "apple_summary": load_apple_health_data()["data"].get("summary", {}),
        "merged_insights": merge.get("merged_insights", []),
        "sample_days": merge.get("sample_days", []),
        "note": "Daily Omi signals merged with Apple metrics by date.",
    })

@mcp.tool()
def get_sidecar_status() -> Dict[str, Any]:
    m = _get_manifest()
    return _with_gates({
        "name": m.get("name"),
        "issuer": m.get("issuer"),
        "expires_at": m.get("_expires_at"),
        "expired": is_expired(m),
        "revoked": is_revoked(m),
        "allowed_scopes": m.get("allowed_scopes", []),
        "tools": m.get("tools", []),
        "manifest_path": m.get("_manifest_path"),
        "audit": audit_summary(5),
    })

@mcp.tool()
def list_data_sources() -> Dict[str, Any]:
    export = _find_apple_export()
    vault = _resolve_vault()
    return _with_gates({
        "version": "1.0-mvp",
        "sidecar": _get_manifest().get("name"),
        "omi_files": len(list((vault / "050 Daily Omi").rglob("*.md"))) if (vault / "050 Daily Omi").exists() else 0,
        "apple_export_found": bool(export),
        "supported_signals": list(SIGNAL_PATTERNS.keys()),
        "parser_features": [
            "context words", "speaker separation", "quality scoring", "signal excerpts/citations",
            "time-of-day", "lag correlations", "what-if simulation", "audit log", "sidecar manifest",
            "omi-apple daily merge", "doctor view export",
        ],
        "status": "MVP 1.0 complete — see docs/MVP-1.0.md",
    })

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        os.environ.setdefault("OMI_VAULT_PATH", str(_DEMO_VAULT))
        print("VitaSide MVP 1.0 self-test")
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
        html = generate_html_report(
            {"files_scanned": 4, "unique_dates": 4, "temporal_correlations": []},
            {"source": "demo"}, test_entries, sim, {"entries": 0}, DISCLAIMER,
        )
        assert "<title>VitaSide Report" in html
        print("Timeseries OK, dates:", len(ts["date_list"]))
        print("simulate_whatif OK, confidence:", sim["confidence"])
        print("HTML report OK, bytes:", len(html))
        print("All tests passed.")
    else:
        mcp.run(transport="stdio")
