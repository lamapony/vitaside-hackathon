"""Seed demo manual logs when local context is empty (for journal / headache demo)."""
from __future__ import annotations

import datetime

from user_context import load_context, save_context

DEMO_MANUAL_LOGS = [
    {
        "type": "headache",
        "text": "Headache 7/10, pulsing since morning. Took ibuprofen.",
        "severity": 7,
    },
    {
        "type": "headache",
        "text": "Migraine after a sleepless night, dark room and rest.",
        "severity": 8,
    },
    {
        "type": "note",
        "text": "Deadline yesterday — headache again today.",
        "severity": 5,
    },
    {
        "type": "medication",
        "text": "Sumatriptan 50mg — relief after 40 minutes.",
        "severity": 4,
    },
]


def seed_demo_manual_logs_if_empty(days_ago: tuple = (2, 5, 9, 14)) -> bool:
    """Return True if logs were seeded."""
    ctx = load_context()
    if ctx.get("manual_logs"):
        return False
    today = datetime.date.today()
    logs = []
    for i, template in enumerate(DEMO_MANUAL_LOGS):
        row = dict(template)
        offset = days_ago[i] if i < len(days_ago) else (i + 1) * 3
        row["date"] = (today - datetime.timedelta(days=offset)).isoformat()
        logs.append(row)
    ctx["manual_logs"] = logs
    ctx.setdefault("profile", {})["main_goal"] = "Reduce migraine days and spot triggers"
    save_context(ctx)
    return True


if __name__ == "__main__":
    if seed_demo_manual_logs_if_empty():
        print("Seeded demo manual logs (local-data/user_context.json)")
    else:
        print("Manual logs already present — skipped")
