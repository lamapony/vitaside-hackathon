"""N-of-1 style within-person comparison: exposure days vs non-exposure days."""
from __future__ import annotations

import datetime
import random
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

try:
    from scipy import stats as sp_stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def _entries_by_date(entries: List[Dict]) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for e in entries:
        d = e.get("date")
        if d:
            out[d] = e
    return out


def _outcome_on_date(by_date: Dict[str, Dict], date: str, outcome_signal: str, window_days: int) -> bool:
    try:
        base = datetime.date.fromisoformat(date)
    except ValueError:
        return False
    for offset in range(0, window_days + 1):
        d = (base + datetime.timedelta(days=offset)).isoformat()
        e = by_date.get(d)
        if e and outcome_signal in (e.get("signals") or []):
            return True
    return False


def run_n1_compare(
    entries: List[Dict],
    exposure_signal: str,
    outcome_signal: str,
    window_days: int = 2,
    bootstrap_n: int = 400,
) -> Dict[str, Any]:
    """
    Compare outcome rate after exposure days vs control days (no exposure that day).
    window_days: outcome counted within [0, window_days] after exposure day.
    """
    by_date = _entries_by_date(entries)
    dates = sorted(by_date.keys())
    if len(dates) < 14:
        return {
            "note": "Need at least 14 tracked days for N-of-1 compare",
            "exposure_signal": exposure_signal,
            "outcome_signal": outcome_signal,
            "window_days": window_days,
        }

    exposure_days: List[str] = []
    control_days: List[str] = []
    for d in dates:
        sigs = by_date[d].get("signals") or []
        if exposure_signal in sigs:
            exposure_days.append(d)
        else:
            control_days.append(d)

    if len(exposure_days) < 3 or len(control_days) < 3:
        return {
            "note": f"Insufficient exposure ({len(exposure_days)}) or control ({len(control_days)}) days",
            "exposure_signal": exposure_signal,
            "outcome_signal": outcome_signal,
            "exposure_days": len(exposure_days),
            "control_days": len(control_days),
        }

    exp_outcomes = sum(1 for d in exposure_days if _outcome_on_date(by_date, d, outcome_signal, window_days))
    ctrl_outcomes = sum(1 for d in control_days if _outcome_on_date(by_date, d, outcome_signal, window_days))

    exp_rate = exp_outcomes / len(exposure_days)
    ctrl_rate = ctrl_outcomes / len(control_days)
    lift = round(exp_rate / max(ctrl_rate, 0.01), 2)
    risk_diff = round(exp_rate - ctrl_rate, 3)

    p_value: Optional[float] = None
    if HAS_SCIPY:
        table = [[exp_outcomes, len(exposure_days) - exp_outcomes],
                 [ctrl_outcomes, len(control_days) - ctrl_outcomes]]
        try:
            _, p_value = sp_stats.fisher_exact(table)
            p_value = round(float(p_value), 4)
        except Exception:
            p_value = None

    ci_low, ci_high = _bootstrap_ci(
        exposure_days, control_days, by_date, outcome_signal, window_days, bootstrap_n
    )

    example_exposure = None
    for d in exposure_days:
        if _outcome_on_date(by_date, d, outcome_signal, window_days):
            e = by_date[d]
            example_exposure = {"date": d, "excerpt": (e.get("snippet") or "")[:160]}
            break

    interpretation = (
        f"After days with '{exposure_signal}', '{outcome_signal}' occurred within {window_days}d "
        f"on {exp_outcomes}/{len(exposure_days)} days ({exp_rate:.0%}) vs "
        f"{ctrl_outcomes}/{len(control_days)} control days ({ctrl_rate:.0%})."
    )

    return {
        "method": "n_of_1_exposure_vs_control",
        "exposure_signal": exposure_signal,
        "outcome_signal": outcome_signal,
        "window_days": window_days,
        "exposure_days": len(exposure_days),
        "control_days": len(control_days),
        "exposure_outcome_rate": round(exp_rate, 3),
        "control_outcome_rate": round(ctrl_rate, 3),
        "risk_difference": risk_diff,
        "lift_ratio": lift,
        "p_value": p_value,
        "ci_95": {"low": ci_low, "high": ci_high},
        "interpretation": interpretation,
        "example": example_exposure,
        "confidence": _confidence(len(exposure_days), len(control_days), p_value),
    }


def _bootstrap_ci(
    exposure_days: List[str],
    control_days: List[str],
    by_date: Dict[str, Dict],
    outcome_signal: str,
    window_days: int,
    n: int,
) -> Tuple[Optional[float], Optional[float]]:
    if len(exposure_days) < 3:
        return None, None
    rng = random.Random(42)
    diffs: List[float] = []
    for _ in range(n):
        exp_sample = [rng.choice(exposure_days) for _ in range(len(exposure_days))]
        ctrl_sample = [rng.choice(control_days) for _ in range(len(control_days))]
        er = sum(1 for d in exp_sample if _outcome_on_date(by_date, d, outcome_signal, window_days)) / len(exp_sample)
        cr = sum(1 for d in ctrl_sample if _outcome_on_date(by_date, d, outcome_signal, window_days)) / len(ctrl_sample)
        diffs.append(er - cr)
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs)) - 1]
    return round(lo, 3), round(hi, 3)


def _confidence(n_exp: int, n_ctrl: int, p_value: Optional[float]) -> str:
    if n_exp >= 10 and n_ctrl >= 20 and p_value is not None and p_value < 0.05:
        return "moderate"
    if n_exp >= 5 and n_ctrl >= 10:
        return "exploratory"
    return "low"
