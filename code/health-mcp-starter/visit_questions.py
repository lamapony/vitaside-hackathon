"""Auto-generate questions for a doctor visit from pattern analysis."""
from __future__ import annotations

from typing import Any, Dict, List


def generate_visit_questions(
    analysis: Dict[str, Any],
    merge: Dict[str, Any],
    whatif: Dict[str, Any],
) -> Dict[str, Any]:
    questions: List[Dict[str, str]] = []

    for c in analysis.get("temporal_correlations", [])[:3]:
        questions.append({
            "topic": f"{c.get('cause')} → {c.get('effect')}",
            "question": (
                f"I noticed in my notes that when I report '{c.get('cause')}', "
                f"'{c.get('effect')}' often appears {c.get('lag')} day(s) later "
                f"(confidence {c.get('confidence')}). Could lifestyle factors explain this?"
            ),
            "evidence": (c.get("citations") or [{}])[0].get("excerpt", "")[:160],
        })

    for ins in merge.get("merged_insights", [])[:2]:
        questions.append({
            "topic": ins.get("pattern", "wearable"),
            "question": (
                f"My voice notes and wearable data show: {ins.get('description')} "
                f"({ins.get('count')} days). Is this worth tracking clinically?"
            ),
            "evidence": "",
        })

    for p in whatif.get("projected_outcomes", [])[:1]:
        questions.append({
            "topic": "sleep intervention",
            "question": (
                f"If I improve sleep consistently, my data suggests {p.get('signal')} "
                f"might change by ~{abs(p.get('change_percent', 0))}%. "
                "Does that align with what you'd expect for me?"
            ),
            "evidence": whatif.get("based_on", {}).get("method", ""),
        })

    if not questions:
        questions.append({
            "topic": "general",
            "question": "I'd like to review lifestyle patterns from my tracked notes before our visit.",
            "evidence": "",
        })

    return {
        "questions": questions,
        "count": len(questions),
        "disclaimer": "Suggested discussion topics — not medical advice.",
    }
