"""Auto-generate doctor visit questions from YOUR cited patterns."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from actionable_insights import _label


def generate_visit_questions(
    analysis: Dict[str, Any],
    merge: Dict[str, Any],
    whatif: Dict[str, Any],
    smart: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    questions: List[Dict[str, str]] = []
    days = analysis.get("unique_dates", 0)

    for c in analysis.get("temporal_correlations", [])[:3]:
        cause, effect = _label(c.get("cause", "")), _label(c.get("effect", ""))
        cite = (c.get("citations") or [{}])[0]
        ex = cite.get("excerpt", "")[:100]
        date = cite.get("date", "")
        questions.append({
            "topic": f"{cause} → {effect}",
            "question": (
                f"Across {days} days of my notes, {effect} showed up {c.get('lag')} day(s) after {cause} "
                f"in {len(c.get('example_dates', []))}+ chains (lift {c.get('lift_ratio')}×). "
                f"On {date} I wrote about this — could we explore lifestyle links?"
            ),
            "evidence": ex,
            "evidence_date": date,
        })

    for ins in merge.get("merged_insights", [])[:2]:
        questions.append({
            "topic": "voice + wearable",
            "question": (
                f"My Omi notes and Apple data agree on {ins.get('count')} days: {ins.get('description')}. "
                "Should we use both sources at follow-ups?"
            ),
            "evidence": f"{merge.get('overlap_days', 0)} overlapping days analyzed",
            "evidence_date": "",
        })

    for p in whatif.get("projected_outcomes", [])[:1]:
        based = whatif.get("based_on", {})
        questions.append({
            "topic": "sleep experiment",
            "question": (
                f"If I stabilize sleep, my own history suggests {_label(p.get('signal', ''))} "
                f"could shift ~{abs(p.get('change_percent', 0)):.0f}% "
                f"(based on {based.get('good_sleep_nights', 0)} good vs {based.get('poor_sleep_nights', 0)} poor nights). "
                "Is a 2-week sleep focus reasonable to try?"
            ),
            "evidence": (whatif.get("sources") or [{}])[0].get("excerpt", "")[:120],
            "evidence_date": (whatif.get("sources") or [{}])[0].get("cause_date", ""),
        })

    if not questions:
        questions.append({
            "topic": "tracking",
            "question": f"I've been logging {days} days — can we review patterns together?",
            "evidence": "",
            "evidence_date": "",
        })

    if smart:
        for att in (smart.get("attention_now") or [])[:2]:
            questions.append({
                "topic": "personal baseline",
                "question": (
                    f"My recent data shows: {att.get('headline', '')}. "
                    f"{att.get('detail', '')} Is this worth monitoring?"
                ),
                "evidence": (att.get("evidence_quote") or "")[:100],
                "evidence_date": att.get("evidence_date", ""),
            })
        for w in (smart.get("weekday_effects") or [])[:1]:
            questions.append({
                "topic": "weekday pattern",
                "question": (
                    f"I notice {_label(w['signal'])} more on {w['weekday_name']}s "
                    f"({w['lift']:.1f}× my average). Could weekday rhythm affect this?"
                ),
                "evidence": f"{w['occurrences']} {w['weekday_name']} occurrences",
                "evidence_date": (w.get("example_dates") or [""])[0],
            })

    return {
        "questions": questions,
        "count": len(questions),
        "disclaimer": "Discussion topics from your data — not medical advice.",
    }
