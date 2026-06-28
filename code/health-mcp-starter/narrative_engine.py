"""
Local cite-grounded narrative — smart without cloud.

Weaves personal baselines, correlations, and attention signals into
doctor-visit-ready prose. Every sentence maps to structured evidence.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

SIGNAL_RU = {
    "sleep": "сон",
    "stress": "стресс",
    "mood_low": "сниженное настроение",
    "mood_good": "хорошее настроение",
    "exercise": "физическая активность",
    "symptom_pain": "боль/усталость",
    "symptom_cold_flu": "простуда",
    "caffeine_alcohol": "кофеин/алкоголь",
    "social": "общение",
}


def _sig_ru(sig: str) -> str:
    return SIGNAL_RU.get(sig, sig.replace("_", " "))


def build_local_narrative(
    briefing: Dict[str, Any],
    smart: Optional[Dict[str, Any]] = None,
    locale: str = "en",
) -> Dict[str, Any]:
    """
    Produce a structured narrative from local data only.
    Returns narrative text + evidence map for UI / Azure fallback.
    """
    insights = briefing.get("top_insights") or []
    footprint = briefing.get("data_footprint") or {}
    days = footprint.get("days_analyzed", 0)
    files = footprint.get("files_scanned", 0)

    evidence_map: List[Dict[str, str]] = []
    paragraphs: List[str] = []

    if locale.startswith("ru"):
        intro = (
            f"За {days} дней и {files} записей Omi видны **ваши** паттерны — "
            "не усреднённые советы из интернета."
        )
    else:
        intro = (
            f"Across {days} days and {files} Omi files, these are **your** patterns — "
            "not generic internet wellness advice."
        )
    paragraphs.append(intro)

    # Top correlation insight
    if insights:
        top = insights[0]
        if locale.startswith("ru"):
            p = (
                f"Главная связь: {top.get('headline', '')}. "
                f"{top.get('detail', '')}"
            )
            if top.get("evidence_quote"):
                p += f" Цитата от {top.get('evidence_date')}: «{top.get('evidence_quote')[:100]}»."
        else:
            p = f"Top link: {top.get('headline', '')}. {top.get('detail', '')}"
            if top.get("evidence_quote"):
                p += f" Quote from {top.get('evidence_date')}: \"{top.get('evidence_quote')[:100]}\"."
        paragraphs.append(p)
        evidence_map.append({
            "claim": top.get("headline", ""),
            "source": "temporal_correlation",
            "date": top.get("evidence_date", ""),
            "excerpt": top.get("evidence_quote", "")[:120],
        })

    if smart:
        attention = smart.get("attention_now") or []
        if attention:
            att = attention[0]
            if locale.startswith("ru"):
                p = f"⚠️ Сейчас: {att.get('headline', '')}. {att.get('detail', '')}"
                if att.get("evidence_quote"):
                    p += f" ({att.get('evidence_date')}: «{att.get('evidence_quote')[:80]}»)"
            else:
                p = f"⚠️ Now: {att.get('headline', '')}. {att.get('detail', '')}"
            paragraphs.append(p)
            evidence_map.append({
                "claim": att.get("headline", ""),
                "source": "attention_now",
                "date": att.get("evidence_date", ""),
                "excerpt": att.get("evidence_quote", "")[:120],
            })

        weekday = smart.get("weekday_effects") or []
        if weekday:
            w = weekday[0]
            if locale.startswith("ru"):
                p = (
                    f"По дням недели: {_sig_ru(w['signal'])} чаще по {w['weekday_name_ru']} "
                    f"({w['lift']:.1f}× от вашей средней частоты)."
                )
            else:
                p = (
                    f"Weekday pattern: {w['signal']} spikes on {w['weekday_name']}s "
                    f"({w['lift']:.1f}× your average)."
                )
            paragraphs.append(p)
            evidence_map.append({
                "claim": f"weekday_{w['signal']}_{w['weekday_name']}",
                "source": "weekday_effect",
                "date": (w.get("example_dates") or [""])[0],
                "excerpt": "",
            })

        baselines = smart.get("personal_baselines", {}).get("signals", {})
        rising = [s for s, b in baselines.items() if b.get("trend") == "rising"]
        if rising:
            sig = rising[0]
            bl = baselines[sig]
            if locale.startswith("ru"):
                p = (
                    f"Тренд: {_sig_ru(sig)} растёт в вашей истории "
                    f"(средняя частота {bl['mean_freq']:.0%}, личный диапазон "
                    f"{bl['band_low']:.0%}–{bl['band_high']:.0%})."
                )
            else:
                p = (
                    f"Trend: {sig} is rising in your history "
                    f"(mean {bl['mean_freq']:.0%}, personal band {bl['band_low']:.0%}–{bl['band_high']:.0%})."
                )
            paragraphs.append(p)
            evidence_map.append({
                "claim": f"rising_{sig}",
                "source": "personal_baseline",
                "date": "",
                "excerpt": "",
            })

        wearable = smart.get("wearable_bands") or {}
        if wearable.get("recent_alerts"):
            alert = wearable["recent_alerts"][0]
            if locale.startswith("ru"):
                p = (
                    f"Apple Health: {alert['metric']} за неделю ({alert['recent_mean']}) "
                    f"ниже вашего личного среднего ({alert['personal_mean']})."
                )
            else:
                p = (
                    f"Apple Health: {alert['metric']} this week ({alert['recent_mean']}) "
                    f"below your personal average ({alert['personal_mean']})."
                )
            paragraphs.append(p)
            evidence_map.append({
                "claim": f"wearable_{alert['metric']}",
                "source": "wearable_band",
                "date": "",
                "excerpt": "",
            })

    # Action line from briefing
    if insights and insights[0].get("action"):
        if locale.startswith("ru"):
            paragraphs.append(f"→ Действие: {insights[0]['action']}")
        else:
            paragraphs.append(f"→ Action: {insights[0]['action']}")

    narrative = "\n\n".join(paragraphs)
    return {
        "source": "local_narrative_engine",
        "narrative": narrative,
        "evidence_map": evidence_map,
        "locale": locale,
        "disclaimer": (
            "Паттерны для самонаблюдения — не диагноз. Каждое утверждение привязано к вашим данным."
            if locale.startswith("ru")
            else "Patterns for self-awareness — not diagnosis. Every claim is tied to your data."
        ),
    }
