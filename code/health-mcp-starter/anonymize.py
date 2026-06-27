"""Strip identifying info from excerpts for sharing."""
from __future__ import annotations

import re
from typing import Any, Dict, List


_SPEAKER_RE = re.compile(r"\*\*[^*]+\*\*")
_NAME_LIKE = re.compile(r"\b([A-ZА-Я][a-zа-я]{2,})\b")


def anonymize_text(text: str) -> str:
    t = _SPEAKER_RE.sub("**[speaker]**", text)
    t = _NAME_LIKE.sub("[name]", t)
    return t


def anonymize_citations(citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for c in citations:
        row = dict(c)
        if "excerpt" in row:
            row["excerpt"] = anonymize_text(str(row["excerpt"]))
        out.append(row)
    return out
