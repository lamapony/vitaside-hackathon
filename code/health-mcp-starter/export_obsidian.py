"""Export VitaSide summary as Obsidian-friendly markdown."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List


def build_obsidian_note(
    analysis: Dict[str, Any],
    questions: Dict[str, Any],
    whatif: Dict[str, Any],
    anonymized: bool = False,
) -> str:
    today = datetime.date.today().isoformat()
    lines = [
        "---",
        f"date: {today}",
        "tags: [vitaside, health-patterns, doctor-prep]",
        "source: vitaside-mcp",
        "---",
        "",
        f"# VitaSide Visit Prep — {today}",
        "",
        f"> {analysis.get('disclaimer', 'Patterns only — not a diagnosis.')}",
        "",
        "## Summary",
        f"- Days analyzed: **{analysis.get('unique_dates', 0)}**",
        f"- Files: **{analysis.get('files_scanned', 0)}**",
        "",
        "## Top patterns",
    ]
    for c in analysis.get("temporal_correlations", [])[:5]:
        lines.append(
            f"- **{c.get('cause')} → {c.get('effect')}** (lag {c.get('lag')}d, "
            f"lift {c.get('lift_ratio')}, conf {c.get('confidence')})"
        )
        cites = c.get("citations") or []
        if cites:
            lines.append(f"  - > {cites[0].get('date')}: {cites[0].get('excerpt', '')[:120]}")

    lines += ["", "## Questions for doctor"]
    for q in questions.get("questions", []):
        lines.append(f"- [ ] **{q.get('topic')}**: {q.get('question')}")

    if whatif.get("projected_outcomes"):
        lines += ["", "## What-if note"]
        for p in whatif["projected_outcomes"]:
            lines.append(f"- {p.get('signal')}: {p.get('change_percent')}% ({p.get('direction')})")

    lines += ["", "## Links", "- [[VitaSide]]", ""]
    return "\n".join(lines)
