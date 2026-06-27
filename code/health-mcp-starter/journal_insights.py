"""
Multi-journal view: Omi voice notes + manual quick logs + condition packs.

Minimal product promise:
- list what diaries you have and their stats
- per-journal summaries
- headache-specific trigger correlations with citations
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Callable, Dict, List, Optional, Set

HEADACHE_SIGNALS = frozenset({"headache", "symptom_pain", "migraine_day"})
HEADACHE_TEXT = re.compile(
    r"\b(мигрен|головн[а-я]*\s*бол|болит\s+голова|headache|migraine|пульсиру)\b",
    re.I,
)

TRIGGER_SIGNALS = ["stress", "sleep", "caffeine_alcohol", "mood_low", "exercise"]
TRIGGER_LABELS = {
    "stress": "stress",
    "sleep": "poor sleep / sleep mention",
    "caffeine_alcohol": "caffeine or alcohol",
    "mood_low": "low mood",
    "exercise": "exercise",
}


def is_headache_day(entry: Dict[str, Any], pack_headache_sigs: Optional[Set[str]] = None) -> bool:
    sigs = set(entry.get("signals", []))
    pack_sigs = set(entry.get("pack_signals", []))
    if pack_headache_sigs and (pack_sigs & pack_headache_sigs):
        return True
    if "headache" in pack_sigs:
        return True
    if "symptom_pain" in sigs and HEADACHE_TEXT.search(_entry_text(entry)):
        return True
    if HEADACHE_TEXT.search(_entry_text(entry)):
        return True
    return False


def _entry_text(entry: Dict[str, Any]) -> str:
    parts = [entry.get("snippet", "")]
    for ex_list in (entry.get("excerpts") or {}).values():
        for ex in ex_list:
            parts.append(ex.get("text", ""))
    return " ".join(parts)


def manual_logs_to_entries(
    logs: List[Dict[str, Any]],
    match_signals: Callable[[str], List[str]],
) -> List[Dict[str, Any]]:
    """Turn dashboard quick logs into parseable daily entries."""
    entries: List[Dict[str, Any]] = []
    for log in logs:
        text = (log.get("text") or "").strip()
        if not text:
            continue
        date = log.get("date") or ""
        if not date:
            continue
        log_type = (log.get("type") or "note").lower()
        signals = list(match_signals(text))
        if log_type in ("headache", "migraine", "pain") and "symptom_pain" not in signals:
            signals.append("symptom_pain")
        if log.get("severity") and int(log.get("severity") or 0) >= 7:
            if "symptom_pain" not in signals:
                signals.append("symptom_pain")
        entries.append({
            "date": date,
            "signals": signals,
            "snippet": text[:300],
            "excerpts": {s: [{"text": text, "speaker": "You"}] for s in signals[:3]},
            "sleep_quality": "unknown",
            "journal_id": "manual_log",
            "source": "manual_log",
            "log_type": log_type,
        })
    return entries


def merge_entries_by_date(*sources: List[Dict]) -> List[Dict]:
    """Merge multiple entry streams — same date unions signals, keeps both snippets."""
    by_date: Dict[str, Dict] = {}
    for entries in sources:
        for e in entries:
            d = e.get("date")
            if not d:
                continue
            if d not in by_date:
                by_date[d] = {**e, "signals": list(e.get("signals", [])), "sources": [e.get("journal_id", e.get("source", "omi"))]}
                continue
            row = by_date[d]
            row["signals"] = sorted(set(row.get("signals", [])) | set(e.get("signals", [])))
            if e.get("pack_signals"):
                row["pack_signals"] = sorted(set(row.get("pack_signals", [])) | set(e.get("pack_signals", [])))
            row.setdefault("sources", [])
            src = e.get("journal_id", e.get("source", "omi"))
            if src not in row["sources"]:
                row["sources"].append(src)
            if len(e.get("snippet", "")) > len(row.get("snippet", "")):
                row["snippet"] = e["snippet"]
            for sig, exs in (e.get("excerpts") or {}).items():
                row.setdefault("excerpts", {})
                row["excerpts"].setdefault(sig, []).extend(exs[:1])
    return sorted(by_date.values(), key=lambda x: x["date"])


JOURNAL_DEFS = [
    {
        "id": "omi_voice",
        "label": "Omi voice diary",
        "label_ru": "Голосовой дневник Omi",
        "description": "Daily conversations exported to Obsidian",
        "source_types": ["omi"],
    },
    {
        "id": "manual_log",
        "label": "Quick manual logs",
        "label_ru": "Быстрые записи в приложении",
        "description": "Headache scores, meds, one-line notes you enter locally",
        "source_types": ["manual_log"],
    },
    {
        "id": "combined",
        "label": "Combined timeline",
        "label_ru": "Объединённая лента",
        "description": "Omi + manual logs merged by date for correlations",
        "source_types": ["omi", "manual_log"],
    },
    {
        "id": "headache",
        "label": "Headache / migraine journal",
        "label_ru": "Дневник головной боли",
        "description": "Episodes, meds, and trigger patterns",
        "source_types": ["omi", "manual_log"],
        "condition_pack": "migraine",
    },
]


def journal_stats(entries: List[Dict], journal_id: str) -> Dict[str, Any]:
    if journal_id == "combined":
        pool = entries
    elif journal_id == "omi_voice":
        pool = [e for e in entries if e.get("journal_id", "omi") != "manual_log" and e.get("source") != "manual_log"]
    elif journal_id == "manual_log":
        pool = [e for e in entries if e.get("source") == "manual_log" or e.get("journal_id") == "manual_log"]
    elif journal_id == "headache":
        pool = [e for e in entries if is_headache_day(e)]
    else:
        pool = entries

    dates = sorted({e["date"] for e in pool if e.get("date")})
    sig_counter: Counter = Counter()
    for e in pool:
        for s in e.get("signals", []):
            sig_counter[s] += 1

    return {
        "days": len(dates),
        "entries": len(pool),
        "date_range": [dates[0], dates[-1]] if dates else [],
        "top_signals": [{"signal": s, "count": c} for s, c in sig_counter.most_common(6)],
    }


def list_journals(omi_entries: List[Dict], manual_entries: List[Dict], combined: List[Dict]) -> Dict[str, Any]:
    journals = []
    pools = {
        "omi_voice": omi_entries,
        "manual_log": manual_entries,
        "combined": combined,
        "headache": [e for e in combined if is_headache_day(e)],
    }
    for jdef in JOURNAL_DEFS:
        jid = jdef["id"]
        stats = journal_stats(combined if jid in ("combined", "headache") else pools.get(jid, []), jid)
        journals.append({**jdef, "stats": stats, "status": "active" if stats["days"] > 0 else "empty"})
    return {
        "journals": journals,
        "combined_days": len({e["date"] for e in combined if e.get("date")}),
        "manual_log_days": len({e["date"] for e in manual_entries if e.get("date")}),
        "omi_days": len({e["date"] for e in omi_entries if e.get("date")}),
    }


def _headache_dates(entries: List[Dict]) -> Set[str]:
    return {e["date"] for e in entries if e.get("date") and is_headache_day(e)}


def _signal_on_date(by_date: Dict[str, Dict], date: str, signal: str) -> bool:
    e = by_date.get(date, {})
    return signal in e.get("signals", [])


def _cite(entry: Optional[Dict], signal: str = "symptom_pain") -> Dict[str, str]:
    if not entry:
        return {"date": "", "excerpt": ""}
    ex = (entry.get("excerpts", {}).get(signal) or [{}])[0]
    return {"date": entry.get("date", ""), "excerpt": ex.get("text", entry.get("snippet", ""))[:200]}


def headache_trigger_correlations(
    entries: List[Dict],
    max_lag: int = 2,
) -> Dict[str, Any]:
    """
    What tends to appear 1–2 days BEFORE headache days in YOUR journals.
    """
    by_date = {e["date"]: e for e in entries if e.get("date")}
    dates = sorted(by_date.keys())
    headache_days = _headache_dates(entries)
    n_headache = len(headache_days)

    if n_headache < 2:
        return {
            "headache_days": n_headache,
            "note": "Need at least 2 headache days in your journals for trigger patterns",
            "triggers": [],
            "episodes": [],
        }

    triggers: List[Dict[str, Any]] = []
    for trigger in TRIGGER_SIGNALS:
        hits = 0
        examples: List[Dict[str, str]] = []
        for hd in sorted(headache_days):
            try:
                idx = dates.index(hd)
            except ValueError:
                continue
            for lag in range(1, max_lag + 1):
                if idx - lag < 0:
                    continue
                prior_d = dates[idx - lag]
                if _signal_on_date(by_date, prior_d, trigger):
                    hits += 1
                    if len(examples) < 3:
                        examples.append({
                            "headache_date": hd,
                            "trigger_date": prior_d,
                            "lag_days": lag,
                            **_cite(by_date.get(hd)),
                        })
                    break

        rate = hits / n_headache if n_headache else 0
        base = sum(1 for d in dates if _signal_on_date(by_date, d, trigger)) / max(len(dates), 1)
        lift = rate / base if base > 0 else 0
        if hits >= 1 and (lift >= 1.2 or hits >= 2):
            triggers.append({
                "trigger": trigger,
                "label": TRIGGER_LABELS.get(trigger, trigger),
                "headache_days_with_trigger": hits,
                "headache_days_total": n_headache,
                "rate_before_headache": round(rate, 3),
                "baseline_rate": round(base, 3),
                "lift": round(lift, 2),
                "typical_lag_days": "1–2",
                "examples": examples,
                "action": f"On days before headaches, {TRIGGER_LABELS.get(trigger, trigger)} appeared {hits}/{n_headache} times — worth tracking.",
            })

    triggers.sort(key=lambda x: (x["lift"], x["headache_days_with_trigger"]), reverse=True)

    episodes = []
    for hd in sorted(headache_days)[-8:]:
        e = by_date[hd]
        prior = []
        try:
            idx = dates.index(hd)
            for lag in range(1, 3):
                if idx - lag >= 0:
                    pd = dates[idx - lag]
                    prior_sigs = [t for t in TRIGGER_SIGNALS if _signal_on_date(by_date, pd, t)]
                    if prior_sigs:
                        prior.append({"date": pd, "signals": prior_sigs, "lag": lag})
        except ValueError:
            pass
        episodes.append({
            "date": hd,
            "excerpt": _cite(e)["excerpt"],
            "sources": e.get("sources", [e.get("source", "omi")]),
            "preceding": prior,
        })

    top = triggers[0] if triggers else None
    summary = (
        f"{n_headache} headache days in your journals. "
        f"Strongest preceding pattern: {top['label']} ({top['lift']}× vs baseline, {top['headache_days_with_trigger']}/{n_headache} episodes)."
        if top
        else f"{n_headache} headache days logged — add more notes to surface triggers."
    )

    return {
        "headache_days": n_headache,
        "days_analyzed": len(dates),
        "summary": summary,
        "triggers": triggers[:8],
        "recent_episodes": episodes[-5:],
        "disclaimer": "Trigger patterns for self-awareness — not a diagnosis.",
    }


def journal_digest(entries: List[Dict], journal_id: str, headache_report: Optional[Dict] = None) -> Dict[str, Any]:
    stats = journal_stats(entries, journal_id)
    digest: Dict[str, Any] = {
        "journal_id": journal_id,
        "stats": stats,
        "highlights": [],
    }
    if journal_id == "headache" and headache_report:
        digest["headache"] = headache_report
        for t in (headache_report.get("triggers") or [])[:2]:
            ex = (t.get("examples") or [{}])[0]
            digest["highlights"].append({
                "headline": f"Before headaches: {t['label']} ({t['lift']}×)",
                "detail": t.get("action", ""),
                "evidence_date": ex.get("headache_date", ""),
                "evidence_quote": ex.get("excerpt", "")[:140],
            })
    elif stats.get("top_signals"):
        top = stats["top_signals"][0]
        digest["highlights"].append({
            "headline": f"Most logged: {top['signal'].replace('_', ' ')}",
            "detail": f"{top['count']} days in this journal over {stats['days']} days.",
            "evidence_date": stats.get("date_range", ["", ""])[-1],
            "evidence_quote": "",
        })
    return digest
