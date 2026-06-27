"""Deeper analytics: p-values, weekly rollups, period comparison."""
from __future__ import annotations

import datetime
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

try:
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def apply_fdr(correlations: List[Dict]) -> List[Dict]:
    """Benjamini–Hochberg q-values on exploratory p-values."""
    indexed = [(i, c) for i, c in enumerate(correlations) if c.get("p_value") is not None]
    if not indexed:
        return correlations
    m = len(indexed)
    sorted_rows = sorted(indexed, key=lambda x: x[1]["p_value"])
    q_assign: Dict[int, float] = {}
    prev_q = 1.0
    for rank, (idx, row) in enumerate(reversed(sorted_rows), start=1):
        p = row["p_value"]
        q = min(prev_q, p * m / (m - rank + 1))
        q_assign[idx] = round(q, 4)
        prev_q = q
    out = []
    for i, c in enumerate(correlations):
        row = dict(c)
        if i in q_assign:
            row["q_value"] = q_assign[i]
        out.append(row)
    return out


def add_pvalues(correlations: List[Dict], n_days: int) -> List[Dict]:
    if not HAS_SCIPY or n_days < 14:
        return correlations
    out = []
    for c in correlations:
        row = dict(c)
        # approximate: prob vs base rate binomial test
        prob = c.get("probability", 0.5)
        base = prob / max(c.get("lift_ratio", 1), 0.01)
        trials = max(int(n_days * 0.3), 5)
        successes = int(prob * trials)
        try:
            pval = sp_stats.binomtest(successes, trials, min(base, 0.99)).pvalue
            row["p_value"] = round(float(pval), 4)
            row["statistically_note"] = "exploratory" if pval > 0.05 else " notable"
        except Exception:
            row["p_value"] = None
        out.append(row)
    return out


def weekly_summary(entries: List[Dict]) -> Dict[str, Any]:
    by_week: Dict[str, Counter] = defaultdict(Counter)
    for e in entries:
        d = e.get("date")
        if not d:
            continue
        try:
            dt = datetime.date.fromisoformat(d)
            week = dt.isocalendar()
            key = f"{week.year}-W{week.week:02d}"
        except ValueError:
            continue
        for s in e.get("signals", []):
            by_week[key][s] += 1

    weeks = sorted(by_week.keys())[-8:]
    return {
        "weeks": [
            {"week": w, "signals": dict(by_week[w]), "total_signal_hits": sum(by_week[w].values())}
            for w in weeks
        ],
        "week_count": len(weeks),
    }


def compare_periods(entries: List[Dict], recent_days: int = 14) -> Dict[str, Any]:
    by_date: Dict[str, List[str]] = {}
    for e in entries:
        d = e.get("date")
        if d:
            by_date[d] = e.get("signals", [])

    dates = sorted(by_date.keys())
    if len(dates) < recent_days * 2:
        return {"note": "Need more days for period comparison", "recent_days": 0}

    recent = set(dates[-recent_days:])
    prior = set(dates[-recent_days * 2 : -recent_days])

    def freq(days_set):
        c = Counter()
        for d in days_set:
            for s in by_date.get(d, []):
                c[s] += 1
        n = len(days_set) or 1
        return {k: round(v / n, 3) for k, v in c.items()}

    f_recent = freq(recent)
    f_prior = freq(prior)
    deltas = []
    all_sigs = set(f_recent) | set(f_prior)
    for s in all_sigs:
        delta = f_recent.get(s, 0) - f_prior.get(s, 0)
        if abs(delta) >= 0.05:
            deltas.append({"signal": s, "recent_freq": f_recent.get(s, 0),
                           "prior_freq": f_prior.get(s, 0), "delta": round(delta, 3)})

    deltas.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return {
        "recent_days": recent_days,
        "recent_range": [min(recent), max(recent)],
        "prior_range": [min(prior), max(prior)],
        "deltas": deltas[:10],
    }
