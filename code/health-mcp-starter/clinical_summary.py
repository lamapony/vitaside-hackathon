"""One-page clinical summary — trends, context, patterns, visit questions."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional


def _trend_row(label: str, recent: float, prior: float, unit: str = "freq/day") -> Dict[str, Any]:
    delta = round(recent - prior, 3)
    direction = "up" if delta > 0.02 else "down" if delta < -0.02 else "stable"
    return {
        "label": label,
        "recent_14d": recent,
        "prior_14d": prior,
        "delta": delta,
        "direction": direction,
        "unit": unit,
    }


def build_clinical_summary(
    analysis: Dict[str, Any],
    period_compare: Dict[str, Any],
    smart: Optional[Dict[str, Any]],
    user_context: Optional[Dict[str, Any]],
    visit_questions: Optional[Dict[str, Any]],
    merge: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Structured 3-minute doctor handoff payload."""
    today = datetime.date.today().isoformat()
    smart = smart or analysis.get("smart_analysis") or {}
    ctx = user_context or {}
    profile = ctx.get("profile", {}) if isinstance(ctx.get("profile"), dict) else {}
    questions = visit_questions or {}

    top_patterns = (analysis.get("temporal_correlations") or [])[:3]
    deltas = period_compare.get("deltas") or []
    trends: List[Dict[str, Any]] = []
    for d in deltas[:5]:
        trends.append(
            _trend_row(
                d.get("signal", "?"),
                d.get("recent_freq", 0),
                d.get("prior_freq", 0),
            )
        )

    conditions = ctx.get("conditions") or []
    medications = ctx.get("medications") or []
    problem_list = [c.get("name", "") for c in conditions if c.get("name")][:5]

    flags: List[str] = []
    attention = smart.get("attention_now") or []
    for item in attention[:3]:
        flags.append(item.get("reason") or item.get("signal") or str(item))
    for p in top_patterns:
        if p.get("q_value", 1) < 0.1 or p.get("p_value", 1) < 0.05:
            flags.append(f"Pattern {p.get('cause')}→{p.get('effect')} (lag {p.get('lag')}d)")

    headline_parts = []
    if analysis.get("unique_dates"):
        headline_parts.append(f"{analysis['unique_dates']} days of self-tracking")
    if problem_list:
        headline_parts.append(f"focus: {', '.join(problem_list[:2])}")
    elif profile.get("main_goal"):
        headline_parts.append(f"goal: {profile.get('main_goal')}")
    if top_patterns:
        t0 = top_patterns[0]
        headline_parts.append(f"top pattern {t0.get('cause')}→{t0.get('effect')}")

    return {
        "generated_at": today,
        "headline": " · ".join(headline_parts) or "Personal health pattern summary",
        "problem_list": problem_list,
        "medications": [m.get("name", "") for m in medications if m.get("name")][:8],
        "trends": trends,
        "top_patterns": [
            {
                "cause": p.get("cause"),
                "effect": p.get("effect"),
                "lag_days": p.get("lag"),
                "lift": p.get("lift_ratio"),
                "confidence": p.get("confidence"),
                "p_value": p.get("p_value"),
                "q_value": p.get("q_value"),
                "citation": (p.get("citations") or [{}])[0],
            }
            for p in top_patterns
        ],
        "wearable_alignment": (merge or {}).get("merged_insights", [])[:3],
        "flags_for_review": flags[:5],
        "visit_questions": (questions.get("questions") or [])[:6],
        "days_analyzed": analysis.get("unique_dates", 0),
        "overlap_days": (merge or {}).get("overlap_days", 0),
        "disclaimer": analysis.get("disclaimer", ""),
    }
