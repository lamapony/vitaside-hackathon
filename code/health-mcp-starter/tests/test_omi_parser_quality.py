"""VIT-47: Omi / journal parser quality (PP-05)."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from omi_parser_quality import LOW_QUALITY_THRESHOLD  # noqa: F401 — threshold documented in slice doc

MESSY = ROOT / "fixtures" / "omi_messy"
DEMO_OMI = ROOT / "demo-data" / "vault" / "050 Daily Omi"


@pytest.fixture(scope="module")
def mcp_mod():
    os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
    spec = importlib.util.spec_from_file_location("vita_mcp", ROOT / "health-pattern-mcp.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_messy_corpus_scores(mcp_mod):
    clean = mcp_mod._parse_omi_file(MESSY / "structured_clean.md")
    vague = mcp_mod._parse_omi_file(MESSY / "vague_yesterday.md")
    bleed = mcp_mod._parse_omi_file(MESSY / "speaker_bleed_short.md")
    filename = mcp_mod._parse_omi_file(MESSY / "2026-02-14-filename-date.md")

    assert clean and vague and bleed and filename
    assert clean["parser_confidence"] > vague["parser_confidence"]
    assert "relative_day_words" in vague.get("quality_warnings", []) or vague.get("low_quality_excerpt")
    assert bleed.get("parser_confidence") is not None
    assert filename.get("quality_warnings") and "date_from_filename_only" in filename["quality_warnings"]


def test_citations_carry_parser_confidence(mcp_mod):
    entries = [
        mcp_mod._parse_omi_file(MESSY / "structured_clean.md"),
        mcp_mod._parse_omi_file(MESSY / "vague_yesterday.md"),
    ]
    entries = [e for e in entries if e]
    temporal = [
        {
            "cause": "stress",
            "effect": "sleep",
            "lag": 1,
            "example_dates": [entries[0]["date"], entries[1]["date"]],
        }
    ]
    enriched = mcp_mod._enrich_correlations(entries, temporal)
    cite = enriched[0]["citations"][0]
    assert "parser_confidence" in cite
    assert enriched[0]["confidence"] <= mcp_mod._confidence_from_samples(2)


def test_demo_vault_regression(mcp_mod):
    demo_dir = DEMO_OMI
    assert demo_dir.is_dir()
    parsed = sum(1 for p in demo_dir.rglob("*.md") if mcp_mod._parse_omi_file(p))
    assert parsed >= 3
    sample = next(p for p in demo_dir.rglob("*.md") if mcp_mod._parse_omi_file(p))
    row = mcp_mod._parse_omi_file(sample)
    assert row and row.get("parser_confidence") is not None