"""
Personal intelligence layer — not population averages.

- Personal baseline bands (rolling window per signal)
- Weekday / weekend effects
- Anomalies vs YOUR history (not global thresholds)
- Attention-now: what's unusual in the last 7 days
- Wearable personal bands when Apple data exists
- Smarter correlation ranking (consistency + lift + recency)
"""
from __future__ import annotations

import datetime
import statistics
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_NAMES_RU = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


def _entries_by_date(entries: List[Dict]) -> Dict[str, Dict]:
    return {e["date"]: e for e in entries if e.get("date")}


def _dates_sorted(entries: List[Dict]) -> List[str]:
    return sorted({e["date"] for e in entries if e.get("date")})


def _weekday(date_str: str) -> int:
    return datetime.date.fromisoformat(date_str).weekday()


def _signal_days(entries: List[Dict], signal: str) -> Set[str]:
    return {e["date"] for e in entries if signal in e.get("signals", []) and e.get("date")}


def compute_personal_baselines(
    entries: List[Dict],
    window_days: int = 28,
    min_windows: int = 2,
) -> Dict[str, Any]:
    """
    Rolling personal frequency bands per signal.
    Returns mean, std, p25/p75, and trend (recent vs prior window).
    """
    dates = _dates_sorted(entries)
    if len(dates) < window_days:
        window_days = max(len(dates) // 2, 7)

    by_date = _entries_by_date(entries)
    all_signals: Set[str] = set()
    for e in entries:
        all_signals.update(e.get("signals", []))

    baselines: Dict[str, Dict[str, Any]] = {}
    for sig in sorted(all_signals):
        rolling_freqs: List[float] = []
        for start in range(0, max(len(dates) - window_days + 1, 1)):
            chunk = dates[start : start + window_days]
            if len(chunk) < 7:
                continue
            hits = sum(1 for d in chunk if sig in by_date.get(d, {}).get("signals", []))
            rolling_freqs.append(hits / len(chunk))

        if len(rolling_freqs) < min_windows:
            overall = len(_signal_days(entries, sig)) / max(len(dates), 1)
            baselines[sig] = {
                "mean_freq": round(overall, 3),
                "std_freq": 0.0,
                "band_low": round(max(0, overall - 0.08), 3),
                "band_high": round(min(1, overall + 0.08), 3),
                "p25": round(overall, 3),
                "p75": round(overall, 3),
                "trend": "insufficient_data",
                "sample_windows": len(rolling_freqs),
            }
            continue

        mean_f = statistics.mean(rolling_freqs)
        std_f = statistics.stdev(rolling_freqs) if len(rolling_freqs) > 1 else 0.05
        sorted_f = sorted(rolling_freqs)
        p25 = sorted_f[max(0, len(sorted_f) // 4 - 1)]
        p75 = sorted_f[min(len(sorted_f) - 1, 3 * len(sorted_f) // 4)]

        recent = statistics.mean(rolling_freqs[-2:]) if len(rolling_freqs) >= 2 else mean_f
        prior = statistics.mean(rolling_freqs[:-2]) if len(rolling_freqs) > 2 else mean_f
        if recent > prior * 1.15:
            trend = "rising"
        elif recent < prior * 0.85:
            trend = "falling"
        else:
            trend = "stable"

        baselines[sig] = {
            "mean_freq": round(mean_f, 3),
            "std_freq": round(std_f, 3),
            "band_low": round(max(0, mean_f - std_f), 3),
            "band_high": round(min(1, mean_f + std_f), 3),
            "p25": round(p25, 3),
            "p75": round(p75, 3),
            "trend": trend,
            "sample_windows": len(rolling_freqs),
        }

    return {
        "window_days": window_days,
        "days_analyzed": len(dates),
        "signals": baselines,
    }


def compute_weekday_effects(entries: List[Dict], min_lift: float = 1.25) -> List[Dict[str, Any]]:
    """Which weekdays spike which signals vs your overall average."""
    dates = _dates_sorted(entries)
    if len(dates) < 14:
        return []

    by_date = _entries_by_date(entries)
    all_signals: Set[str] = set()
    for e in entries:
        all_signals.update(e.get("signals", []))

    n_days = len(dates)
    effects: List[Dict[str, Any]] = []

    for sig in all_signals:
        overall = len(_signal_days(entries, sig)) / n_days
        if overall < 0.03:
            continue

        by_wd: Counter = Counter()
        wd_totals: Counter = Counter()
        for d in dates:
            wd = _weekday(d)
            wd_totals[wd] += 1
            if sig in by_date.get(d, {}).get("signals", []):
                by_wd[wd] += 1

        for wd in range(7):
            if wd_totals[wd] < 2:
                continue
            wd_freq = by_wd[wd] / wd_totals[wd]
            lift = wd_freq / overall if overall else 0
            if lift >= min_lift and by_wd[wd] >= 2:
                example_dates = [
                    d for d in dates
                    if _weekday(d) == wd and sig in by_date.get(d, {}).get("signals", [])
                ][:2]
                effects.append({
                    "signal": sig,
                    "weekday": wd,
                    "weekday_name": WEEKDAY_NAMES[wd],
                    "weekday_name_ru": WEEKDAY_NAMES_RU[wd],
                    "weekday_freq": round(wd_freq, 3),
                    "overall_freq": round(overall, 3),
                    "lift": round(lift, 2),
                    "occurrences": by_wd[wd],
                    "example_dates": example_dates,
                })

    effects.sort(key=lambda x: x["lift"], reverse=True)
    return effects[:8]


def compute_weekend_vs_weekday(entries: List[Dict]) -> List[Dict[str, Any]]:
    """Compare weekend (Sat/Sun) vs weekday signal rates."""
    by_date = _entries_by_date(entries)
    dates = _dates_sorted(entries)
    if len(dates) < 14:
        return []

    all_signals: Set[str] = set()
    for e in entries:
        all_signals.update(e.get("signals", []))

    results = []
    for sig in all_signals:
        wd_hits = wd_n = we_hits = we_n = 0
        for d in dates:
            is_weekend = _weekday(d) >= 5
            if is_weekend:
                we_n += 1
                if sig in by_date.get(d, {}).get("signals", []):
                    we_hits += 1
            else:
                wd_n += 1
                if sig in by_date.get(d, {}).get("signals", []):
                    wd_hits += 1

        if wd_n < 5 or we_n < 2:
            continue
        wd_rate = wd_hits / wd_n
        we_rate = we_hits / we_n
        if wd_rate < 0.02 and we_rate < 0.02:
            continue
        ratio = we_rate / wd_rate if wd_rate > 0 else (2.0 if we_rate > 0 else 1.0)
        if abs(ratio - 1.0) >= 0.25:
            results.append({
                "signal": sig,
                "weekday_rate": round(wd_rate, 3),
                "weekend_rate": round(we_rate, 3),
                "weekend_vs_weekday_ratio": round(ratio, 2),
                "interpretation": "higher_on_weekends" if ratio > 1.15 else "higher_on_weekdays",
            })

    results.sort(key=lambda x: abs(x["weekend_vs_weekday_ratio"] - 1), reverse=True)
    return results[:5]


def detect_personal_anomalies(
    entries: List[Dict],
    baselines: Dict[str, Any],
    recent_days: int = 7,
) -> List[Dict[str, Any]]:
    """Flag recent days where signal rate exceeds personal band (not global threshold)."""
    dates = _dates_sorted(entries)
    if len(dates) < recent_days + 7:
        return []

    by_date = _entries_by_date(entries)
    recent = dates[-recent_days:]
    prior = dates[-recent_days * 2 : -recent_days] if len(dates) >= recent_days * 2 else dates[:-recent_days]

    anomalies: List[Dict[str, Any]] = []
    sig_baselines = baselines.get("signals", {})

    for sig, bl in sig_baselines.items():
        recent_rate = sum(1 for d in recent if sig in by_date.get(d, {}).get("signals", [])) / len(recent)
        band_high = bl.get("band_high", bl.get("mean_freq", 0) + 0.1)
        band_low = bl.get("band_low", 0)

        if recent_rate > band_high and recent_rate > bl.get("mean_freq", 0) * 1.3:
            example = next(
                (d for d in reversed(recent) if sig in by_date.get(d, {}).get("signals", [])),
                recent[-1],
            )
            entry = by_date.get(example, {})
            ex = (entry.get("excerpts", {}).get(sig) or [{}])[0]
            excerpt = ex.get("text", entry.get("snippet", ""))[:160]
            anomalies.append({
                "signal": sig,
                "type": "above_personal_band",
                "recent_rate": round(recent_rate, 3),
                "personal_mean": bl.get("mean_freq"),
                "band_high": band_high,
                "date": example,
                "excerpt": excerpt,
                "severity": "high" if recent_rate > band_high * 1.5 else "moderate",
            })
        elif recent_rate < band_low and bl.get("mean_freq", 0) > 0.08:
            anomalies.append({
                "signal": sig,
                "type": "below_personal_band",
                "recent_rate": round(recent_rate, 3),
                "personal_mean": bl.get("mean_freq"),
                "band_low": band_low,
                "date": recent[-1],
                "excerpt": "",
                "severity": "moderate",
            })

    # Single-day spikes: signal on a day when it rarely appears for this person
    for d in recent:
        entry = by_date.get(d, {})
        for sig in entry.get("signals", []):
            bl = sig_baselines.get(sig, {})
            if bl.get("mean_freq", 1) < 0.12:
                continue
            # Check if this signal appeared on same weekday historically less often
            wd = _weekday(d)
            wd_dates = [x for x in dates if _weekday(x) == wd and x < d][-8:]
            if len(wd_dates) < 3:
                continue
            wd_rate = sum(1 for x in wd_dates if sig in by_date.get(x, {}).get("signals", [])) / len(wd_dates)
            if wd_rate < bl.get("mean_freq", 0) * 0.5:
                ex = (entry.get("excerpts", {}).get(sig) or [{}])[0]
                anomalies.append({
                    "signal": sig,
                    "type": "unusual_for_weekday",
                    "date": d,
                    "weekday_name": WEEKDAY_NAMES[wd],
                    "weekday_historical_rate": round(wd_rate, 3),
                    "personal_mean": bl.get("mean_freq"),
                    "excerpt": ex.get("text", entry.get("snippet", ""))[:160],
                    "severity": "moderate",
                })

    seen = set()
    deduped = []
    for a in anomalies:
        key = (a.get("signal"), a.get("type"), a.get("date"))
        if key not in seen:
            seen.add(key)
            deduped.append(a)

    deduped.sort(key=lambda x: (0 if x.get("severity") == "high" else 1, -x.get("recent_rate", 0)))
    return deduped[:10]


def rank_correlations_smarter(
    entries: List[Dict],
    correlations: List[Dict],
) -> List[Dict]:
    """Re-rank correlations by consistency, recency, and lift — not lift alone."""
    if not correlations:
        return []

    by_date = _entries_by_date(entries)
    dates = _dates_sorted(entries)
    date_set = set(dates)
    max_date = dates[-1] if dates else ""

    ranked = []
    for c in correlations:
        row = dict(c)
        cause, effect, lag = c.get("cause"), c.get("effect"), c.get("lag", 1)
        example_dates = c.get("example_dates", [])

        # Consistency: what fraction of cause-days lead to effect
        cause_days = [d for d in dates if cause in by_date.get(d, {}).get("signals", [])]
        hits = 0
        for i, d in enumerate(dates):
            if cause not in by_date.get(d, {}).get("signals", []):
                continue
            if i + lag < len(dates):
                lag_d = dates[i + lag]
                if effect in by_date.get(lag_d, {}).get("signals", []):
                    hits += 1
        consistency = hits / len(cause_days) if cause_days else 0

        # Recency: more recent examples score higher
        recency = 0.0
        if example_dates and max_date:
            try:
                latest = max(example_dates)
                days_ago = (datetime.date.fromisoformat(max_date) - datetime.date.fromisoformat(latest)).days
                recency = max(0, 1 - days_ago / 90)
            except ValueError:
                recency = 0.5

        lift = c.get("lift_ratio", 1)
        pval = c.get("p_value")
        sig_bonus = 0.15 if pval is not None and pval < 0.05 else 0

        composite = (
            0.35 * min(lift / 3, 1)
            + 0.30 * consistency
            + 0.20 * recency
            + 0.15 * c.get("confidence", 0.5)
            + sig_bonus
        )
        row["consistency"] = round(consistency, 3)
        row["recency_score"] = round(recency, 3)
        row["composite_score"] = round(composite, 3)
        row["cause_day_count"] = len(cause_days)
        ranked.append(row)

    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    return ranked


def wearable_personal_bands(apple_daily: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Personal bands for sleep/HRV/steps from Apple history."""
    if not apple_daily or len(apple_daily) < 14:
        return {"available": False, "note": "Need 14+ Apple days for personal wearable bands"}

    metrics: Dict[str, List[float]] = defaultdict(list)
    for row in apple_daily.values():
        for k in ("sleep_hours", "hrv_sdnn", "heart_rate_avg", "steps"):
            if k in row:
                metrics[k].append(float(row[k]))

    bands = {}
    for k, vals in metrics.items():
        if len(vals) < 10:
            continue
        mean_v = statistics.mean(vals)
        std_v = statistics.stdev(vals) if len(vals) > 1 else mean_v * 0.1
        sorted_v = sorted(vals)
        bands[k] = {
            "mean": round(mean_v, 2),
            "std": round(std_v, 2),
            "band_low": round(mean_v - std_v, 2),
            "band_high": round(mean_v + std_v, 2),
            "p25": round(sorted_v[len(sorted_v) // 4], 2),
            "p75": round(sorted_v[3 * len(sorted_v) // 4], 2),
            "samples": len(vals),
        }

    # Recent 7d vs personal band
    dates = sorted(apple_daily.keys())
    recent = dates[-7:]
    alerts = []
    for k, bl in bands.items():
        recent_vals = [apple_daily[d][k] for d in recent if k in apple_daily.get(d, {})]
        if not recent_vals:
            continue
        recent_mean = statistics.mean(recent_vals)
        if k == "sleep_hours" and recent_mean < bl["band_low"]:
            alerts.append({
                "metric": k,
                "type": "below_personal_band",
                "recent_mean": round(recent_mean, 2),
                "personal_mean": bl["mean"],
                "severity": "high" if recent_mean < bl["p25"] else "moderate",
            })
        elif k == "hrv_sdnn" and recent_mean < bl["band_low"]:
            alerts.append({
                "metric": k,
                "type": "below_personal_band",
                "recent_mean": round(recent_mean, 2),
                "personal_mean": bl["mean"],
                "severity": "moderate",
            })
        elif k == "heart_rate_avg" and recent_mean > bl["band_high"]:
            alerts.append({
                "metric": k,
                "type": "above_personal_band",
                "recent_mean": round(recent_mean, 2),
                "personal_mean": bl["mean"],
                "severity": "moderate",
            })

    return {
        "available": bool(bands),
        "metrics": bands,
        "recent_alerts": alerts,
        "days_analyzed": len(apple_daily),
    }


def build_attention_now(
    entries: List[Dict],
    baselines: Dict[str, Any],
    personal_anomalies: List[Dict],
    weekday_effects: List[Dict],
    wearable_bands: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Actionable 'what needs attention this week' — always with evidence."""
    attention: List[Dict[str, Any]] = []
    by_date = _entries_by_date(entries)
    dates = _dates_sorted(entries)
    today_wd = _weekday(dates[-1]) if dates else 0

    for a in personal_anomalies[:3]:
        if a.get("type") == "above_personal_band":
            attention.append({
                "priority": 1 if a.get("severity") == "high" else 2,
                "headline": f"Recent {a['signal'].replace('_', ' ')} above your personal norm",
                "detail": (
                    f"Last 7 days: {a['recent_rate']:.0%} vs your usual {a['personal_mean']:.0%} "
                    f"(personal band up to {a['band_high']:.0%})."
                ),
                "evidence_date": a.get("date", ""),
                "evidence_quote": (a.get("excerpt") or "")[:140],
                "action": "Compare with calendar — stress, travel, sleep changes this week?",
            })

    for w in weekday_effects[:2]:
        if w["weekday"] == today_wd and w["lift"] >= 1.4:
            d = w["example_dates"][0] if w.get("example_dates") else dates[-1]
            entry = by_date.get(d, {})
            ex = (entry.get("excerpts", {}).get(w["signal"]) or [{}])[0]
            attention.append({
                "priority": 2,
                "headline": f"{w['signal'].replace('_', ' ').title()} often spikes on {w['weekday_name']}s for you",
                "detail": (
                    f"On {w['weekday_name']}s this signal appears {w['lift']:.1f}× more often "
                    f"({w['weekday_freq']:.0%} vs overall {w['overall_freq']:.0%})."
                ),
                "evidence_date": d,
                "evidence_quote": ex.get("text", entry.get("snippet", ""))[:140],
                "action": f"Today is {w['weekday_name']} — plan lighter load or extra recovery if needed.",
            })

    if wearable_bands and wearable_bands.get("recent_alerts"):
        for alert in wearable_bands["recent_alerts"][:2]:
            metric_label = alert["metric"].replace("_", " ")
            attention.append({
                "priority": 1 if alert.get("severity") == "high" else 2,
                "headline": f"Apple {metric_label}: recent week below your personal band",
                "detail": (
                    f"7-day avg {alert['recent_mean']} vs your history mean {alert['personal_mean']} "
                    f"(personal baseline from {wearable_bands.get('days_analyzed', 0)} days)."
                ),
                "evidence_date": dates[-1] if dates else "",
                "evidence_quote": "",
                "action": "Cross-check with Omi notes on same dates — subjective vs objective.",
            })

    # Rising trends from baselines
    for sig, bl in baselines.get("signals", {}).items():
        if bl.get("trend") == "rising" and bl.get("mean_freq", 0) > 0.1:
            recent_dates = [d for d in dates[-14:] if sig in by_date.get(d, {}).get("signals", [])]
            if recent_dates:
                d = recent_dates[-1]
                entry = by_date[d]
                ex = (entry.get("excerpts", {}).get(sig) or [{}])[0]
                attention.append({
                    "priority": 3,
                    "headline": f"{sig.replace('_', ' ').title()} trending up in your history",
                    "detail": f"Rolling windows show rising frequency (current mean {bl['mean_freq']:.0%}).",
                    "evidence_date": d,
                    "evidence_quote": ex.get("text", entry.get("snippet", ""))[:140],
                    "action": "Worth noting at next check-in if the trend continues.",
                })
            break  # one trend alert max

    attention.sort(key=lambda x: x["priority"])
    return attention[:6]


def run_smart_analysis(
    entries: List[Dict],
    correlations: Optional[List[Dict]] = None,
    apple_daily: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, Any]:
    """Full smart analysis bundle for MCP / API / briefing."""
    baselines = compute_personal_baselines(entries)
    weekday_effects = compute_weekday_effects(entries)
    weekend_effects = compute_weekend_vs_weekday(entries)
    personal_anomalies = detect_personal_anomalies(entries, baselines)
    wearable_bands = wearable_personal_bands(apple_daily or {})

    smarter_corr = rank_correlations_smarter(entries, correlations or [])
    attention = build_attention_now(
        entries, baselines, personal_anomalies, weekday_effects, wearable_bands
    )

    return {
        "personal_baselines": baselines,
        "weekday_effects": weekday_effects,
        "weekend_vs_weekday": weekend_effects,
        "personal_anomalies": personal_anomalies,
        "wearable_bands": wearable_bands,
        "ranked_correlations": smarter_corr[:10],
        "attention_now": attention,
        "summary": {
            "baseline_signals": len(baselines.get("signals", {})),
            "weekday_patterns": len(weekday_effects),
            "recent_anomalies": len(personal_anomalies),
            "attention_items": len(attention),
            "wearable_bands_available": wearable_bands.get("available", False),
        },
    }
