"""
Actionable insights — the product moat vs generic LLM chat.

Every insight MUST cite a date + excerpt or a computed stat from the user's vault.
No generic wellness advice.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

SIGNAL_LABELS = {
    "sleep": "sleep issues",
    "stress": "stress",
    "mood_low": "low mood",
    "mood_good": "good mood",
    "exercise": "exercise",
    "caffeine_alcohol": "late caffeine/alcohol",
    "symptom_pain": "pain/fatigue",
    "social": "social activity",
}


def _label(sig: str) -> str:
    return SIGNAL_LABELS.get(sig, sig.replace("_", " "))


def build_actionable_briefing(
    analysis: Dict[str, Any],
    merge: Dict[str, Any],
    whatif: Dict[str, Any],
    period_compare: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    days = analysis.get("unique_dates", 0)
    files = analysis.get("files_scanned", 0)
    insights: List[Dict[str, Any]] = []

    for c in analysis.get("temporal_correlations", [])[:3]:
        cause, effect = c.get("cause", "?"), c.get("effect", "?")
        lag = c.get("lag", 1)
        cite = (c.get("citations") or [{}])[0]
        ex_dates = c.get("example_dates", [])
        insights.append({
            "rank": len(insights) + 1,
            "headline": f"{_label(cause).title()} → {_label(effect)} about {lag} day(s) later",
            "detail": (
                f"In {len(ex_dates)}+ dated note chains, {_label(effect)} followed {_label(cause)} "
                f"with {c.get('probability', 0)*100:.0f}% day-after rate (lift {c.get('lift_ratio')}×, confidence {c.get('confidence')})."
            ),
            "evidence_date": cite.get("date", ex_dates[0] if ex_dates else ""),
            "evidence_quote": (cite.get("excerpt") or "")[:140],
            "action": f"Track whether reducing {_label(cause)} changes {_label(effect)} next week.",
            "why_not_llm": f"Grounded in {files} files / {days} days — LLM has no access to your Omi vault.",
        })

    for ins in merge.get("merged_insights", [])[:2]:
        insights.append({
            "rank": len(insights) + 1,
            "headline": ins.get("description", "Wearable + voice note alignment"),
            "detail": f"Matched on {ins.get('count', 0)} days where Omi notes and Apple data overlap ({merge.get('overlap_days', 0)} overlap days total).",
            "evidence_date": "",
            "evidence_quote": "",
            "action": "Bring this alignment chart to your doctor — subjective vs objective on same dates.",
            "why_not_llm": "Cross-source merge on dates — ChatGPT cannot read your local Apple export + Omi files together.",
        })

    for p in whatif.get("projected_outcomes", [])[:1]:
        based = whatif.get("based_on", {})
        insights.append({
            "rank": len(insights) + 1,
            "headline": f"If sleep stabilizes: {_label(p.get('signal', ''))} may drop ~{abs(p.get('change_percent', 0)):.0f}%",
            "detail": (
                f"Based on {based.get('good_sleep_nights', 0)} good vs {based.get('poor_sleep_nights', 0)} poor sleep nights "
                f"in your history (confidence {whatif.get('confidence')})."
            ),
            "evidence_date": (whatif.get("sources") or [{}])[0].get("cause_date", ""),
            "evidence_quote": (whatif.get("sources") or [{}])[0].get("excerpt", "")[:140],
            "action": "Use as a discussion starter — not a prescription.",
            "why_not_llm": "Projection uses YOUR good/poor sleep periods — not population averages from training data.",
        })

    if period_compare and period_compare.get("deltas"):
        d = period_compare["deltas"][0]
        insights.append({
            "rank": len(insights) + 1,
            "headline": f"Recent weeks: { _label(d['signal'])} {'up' if d['delta'] > 0 else 'down'} vs prior period",
            "detail": f"Frequency {d['recent_freq']} now vs {d['prior_freq']} before (Δ{d['delta']:+.2f}/day).",
            "evidence_date": period_compare.get("recent_range", ["", ""])[0],
            "evidence_quote": "",
            "action": "Check if a life event explains the shift.",
            "why_not_llm": "Computed window comparison on your timeline — not a vague 'how have you been feeling'.",
        })

    one_liner = insights[0]["headline"] if insights else "Collect more daily notes to surface personal patterns."

    return {
        "one_liner": one_liner,
        "top_insights": insights[:5],
        "data_footprint": {
            "days_analyzed": days,
            "files_scanned": files,
            "overlap_days": merge.get("overlap_days", 0),
            "data_mode": analysis.get("data_mode", "unknown"),
        },
        "vs_generic_llm": [
            "Reads YOUR local Omi + Apple files — zero cloud upload",
            "Every pattern links to dated excerpts from your notes",
            "What-if uses YOUR good/bad sleep history — not internet averages",
            "Audit log proves exactly which files were read",
        ],
    }


def format_briefing_terminal(brief: Dict[str, Any]) -> str:
    lines = [
        "",
        "╔══════════════════════════════════════════════════════════╗",
        "║  VITASIDE — YOUR DATA, NOT GENERIC ADVICE                ║",
        "╚══════════════════════════════════════════════════════════╝",
        "",
        f"📌 {brief['one_liner']}",
        "",
    ]
    for ins in brief.get("top_insights", [])[:3]:
        lines.append(f"  {ins['rank']}. {ins['headline']}")
        lines.append(f"     {ins['detail']}")
        if ins.get("evidence_quote"):
            lines.append(f"     📎 {ins.get('evidence_date')}: \"{ins['evidence_quote'][:90]}…\"")
        lines.append(f"     → {ins['action']}")
        lines.append("")
    lines.append("  Why not just ask ChatGPT?")
    for v in brief.get("vs_generic_llm", []):
        lines.append(f"     • {v}")
    lines.append("")
    return "\n".join(lines)
