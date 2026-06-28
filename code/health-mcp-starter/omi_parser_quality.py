"""
Omi / journal parser quality scoring (PP-05).

Heuristic confidence for noisy voice notes — gates citations and UI warnings.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

LOW_QUALITY_THRESHOLD = 0.45
HIGH_CONFIDENCE_INSIGHT_THRESHOLD = 0.55

VAGUE_CONTEXT = frozenset({"today", "yesterday", "tomorrow", "day-2", "day+2"})
EMOTIONAL_FILLER = re.compile(
    r"\b(ужасно|кошмар|не знаю|как-то|типа|блин|omg|literally|so tired of)\b",
    re.I,
)


def ui_quality_band(parser_confidence: float) -> int:
    """Map 0..1 parser confidence to Timeline UI scale 1 (worst) .. 5 (best)."""
    pc = max(0.0, min(1.0, parser_confidence))
    return max(1, min(5, int(round(pc * 4) + 1)))


def blend_statistical_confidence(statistical: float, parser_confidence: float) -> float:
    """Down-rank correlation confidence when excerpt provenance is noisy."""
    stat = max(0.0, min(0.99, statistical))
    pc = max(0.0, min(1.0, parser_confidence))
    return round(stat * (0.35 + 0.65 * pc), 2)


def assess_parse_quality(
    *,
    date_str: str,
    date_from_frontmatter: bool,
    transcript_line_count: int,
    speakers: List[str],
    context_words: List[str],
    signals_with_quality: List[Dict[str, Any]],
    spoken_chars: int,
    body_chars: int,
    full_text: str = "",
) -> Tuple[float, List[str]]:
    """
    Returns (parser_confidence 0..1, quality_warnings[]).
    """
    warnings: List[str] = []
    score = 0.42

    if date_from_frontmatter:
        score += 0.18
    else:
        warnings.append("date_from_filename_only")
        score -= 0.08

    if transcript_line_count >= 2:
        score += 0.12
    elif transcript_line_count == 0:
        warnings.append("no_transcript_structure")
        score -= 0.06

    if len(speakers) > 2:
        warnings.append("speaker_bleed")
        score -= 0.12
    elif len(speakers) == 1:
        score += 0.05

    vague = [w for w in context_words if w in VAGUE_CONTEXT]
    if vague and not date_from_frontmatter:
        warnings.append("vague_date_language")
        score -= 0.14
    elif vague:
        warnings.append("relative_day_words")
        score -= 0.05

    if signals_with_quality:
        avg_sig = sum(s.get("quality_score", 0) for s in signals_with_quality) / len(signals_with_quality)
        score += min(0.22, 0.08 * avg_sig)
    else:
        warnings.append("no_signal_quality")

    if spoken_chars < 40 and body_chars < 80:
        warnings.append("short_excerpt")
        score -= 0.1

    if full_text and assess_text_emotional_noise(full_text):
        warnings.append("emotional_filler")
        score -= 0.06

    score = max(0.05, min(0.98, score))
    if score < LOW_QUALITY_THRESHOLD:
        warnings.append("low_parser_confidence")

    # dedupe while preserving order
    seen = set()
    deduped: List[str] = []
    for w in warnings:
        if w not in seen:
            seen.add(w)
            deduped.append(w)
    return round(score, 3), deduped


def assess_from_entry(entry: Dict[str, Any]) -> float:
    return float(entry.get("parser_confidence", 0.75))


def assess_text_emotional_noise(text: str) -> bool:
    return bool(EMOTIONAL_FILLER.search(text or ""))