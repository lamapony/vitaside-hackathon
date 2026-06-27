"""Actionable next-step recommendations for the dashboard."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_next_steps(
    briefing: Optional[Dict[str, Any]] = None,
    context_summary: Optional[Dict[str, Any]] = None,
    suggestions_pending: Optional[Dict[str, Any]] = None,
    condition: Optional[Dict[str, Any]] = None,
    questions_count: int = 0,
) -> List[Dict[str, Any]]:
    briefing = briefing or {}
    context_summary = context_summary or {}
    suggestions_pending = suggestions_pending or {}
    steps: List[Dict[str, Any]] = []

    pending_total = sum(len(suggestions_pending.get(k, [])) for k in ("conditions", "medications", "goals", "manual_logs"))
    if pending_total > 0 or suggestions_pending.get("profile"):
        steps.append({
            "id": "review_suggestions",
            "priority": 1,
            "title": "Review auto-detected context",
            "detail": f"{pending_total} items from your notes can pre-fill your profile, meds and goals.",
            "action_label": "Review suggestions",
            "tab": "context",
            "kind": "setup",
        })

    if not context_summary.get("main_goal"):
        steps.append({
            "id": "set_goal",
            "priority": 2,
            "title": "Set your current focus",
            "detail": "A clear goal helps VitaSide prioritize what to track this week.",
            "action_label": "Add goal",
            "tab": "context",
            "kind": "setup",
        })

    top = (briefing.get("top_insights") or [{}])[0]
    if top.get("action"):
        steps.append({
            "id": "follow_top_insight",
            "priority": 3,
            "title": "Try this for 7 days",
            "detail": top.get("action"),
            "evidence_date": top.get("evidence_date"),
            "evidence_quote": top.get("evidence_quote"),
            "action_label": "See insight",
            "tab": "dashboard",
            "kind": "insight",
        })

    if condition and condition.get("condition_id"):
        steps.append({
            "id": "condition_checkin",
            "priority": 4,
            "title": f"Check {condition.get('condition_name', 'condition pack')}",
            "detail": (condition.get("doctor_focus") or ["Review recent episodes and meds"])[0],
            "action_label": "Open condition view",
            "tab": "condition",
            "kind": "track",
        })

    if questions_count >= 1:
        steps.append({
            "id": "doctor_prep",
            "priority": 5,
            "title": "Prepare for your next visit",
            "detail": f"{questions_count} visit questions ready from your patterns.",
            "action_label": "Doctor handoff",
            "tab": "doctor",
            "kind": "visit",
        })
    else:
        steps.append({
            "id": "log_more",
            "priority": 6,
            "title": "Add a quick note today",
            "detail": "Even one sentence in My context improves next week's insights.",
            "action_label": "Quick log",
            "tab": "context",
            "kind": "track",
        })

    if (briefing.get("days_analyzed") or 0) >= 14:
        steps.append({
            "id": "timeline_review",
            "priority": 7,
            "title": "Scan your timeline",
            "detail": "Look for clusters — stress before headaches, poor sleep before low mood.",
            "action_label": "Open timeline",
            "tab": "timeline",
            "kind": "review",
        })

    steps.sort(key=lambda s: s["priority"])
    return steps[:5]
