"""Export VitaSide summary as Obsidian-friendly markdown."""
from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

# KG-ENTITY-REGISTRY: pp-01 — cited in visit packet template (VIT-26)
PP01_PAIN_POINT_CITATION: Dict[str, str] = {
    "entity_id": "pp-01",
    "source": "pain_point",
    "title": "Peak-end symptom recall",
    "excerpt": (
        "Retrospective recall skews toward recent peaks; prospective capture and "
        "longitudinal summaries improve what you bring to a short visit."
    ),
    "vault_link": "01-Pain-Points/PP-01-peak-end-symptom-recall",
}


def build_obsidian_note(
    analysis: Dict[str, Any],
    questions: Dict[str, Any],
    whatif: Dict[str, Any],
    anonymized: bool = False,
    *,
    entity_id: Optional[str] = None,
    personal_baselines: Optional[Dict[str, Any]] = None,
) -> str:
    today = datetime.date.today().isoformat()
    eid = entity_id or f"vp-{today.replace('-', '')}-gp"
    lines = [
        "---",
        f"date: {today}",
        f"entity_id: {eid}",
        "type: VisitPacket",
        "tags: [vitaside, health-patterns, doctor-prep, visit-packet]",
        "source: vitaside-mcp",
        f"pain_points: [pp-01]",
        "---",
        "",
        f"# VitaSide Visit Prep — {today}",
        "",
        f"> {analysis.get('disclaimer', 'Patterns only — not a diagnosis.')}",
        "",
        "## Why this packet",
        f"- Addresses [[{PP01_PAIN_POINT_CITATION['vault_link']}]] ({PP01_PAIN_POINT_CITATION['entity_id']}): "
        f"{PP01_PAIN_POINT_CITATION['excerpt']}",
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

    if personal_baselines and personal_baselines.get("metrics"):
        lines += ["", "## Personal baselines (local SQLite)"]
        lines.append(f"- Window end: **{personal_baselines.get('end_day', 'n/a')}**")
        for key, windows in list(personal_baselines.get("metrics", {}).items())[:4]:
            w14 = (windows or {}).get("14") or {}
            if w14.get("n"):
                lines.append(
                    f"- `{key}`: 14d mean {w14.get('mean')} (n={w14.get('n')}, trend {w14.get('trend')})"
                )

    lines += ["", "## Links", "- [[VitaSide]]", f"- entity_id: `{eid}`", ""]
    return "\n".join(lines)
