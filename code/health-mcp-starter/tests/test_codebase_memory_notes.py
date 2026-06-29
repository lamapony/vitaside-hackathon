"""VIT-68: codebase-memory-mcp hook + obsidian_notes multi-source lane."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def demo_vault() -> Path:
    return ROOT / "demo-data" / "vault"


def test_resolve_project_explicit_env(monkeypatch: pytest.MonkeyPatch):
    import codebase_memory_client as cmc

    monkeypatch.setenv("VITASIDE_CODEBASE_MEMORY_PROJECT", "my-vault-project")
    assert cmc.resolve_project_for_vault(Path("/any/path")) == "my-vault-project"


def test_collect_obsidian_notes_fallback_demo_vault(demo_vault: Path, monkeypatch: pytest.MonkeyPatch):
    import multi_source_collector as msc

    monkeypatch.setenv("OMI_VAULT_PATH", str(demo_vault))
    monkeypatch.setenv("VITASIDE_DISABLE_CODEBASE_MEMORY", "1")

    events, lane = msc.collect_obsidian_notes(demo_vault, use_codebase_memory=False)
    assert lane["backend"] == "obsidian_io"
    assert lane["status"] == "ok"
    assert events
    assert events[0].source == "obsidian_notes"


def test_build_multi_source_snapshot_includes_obsidian_lane(demo_vault: Path, monkeypatch: pytest.MonkeyPatch):
    import multi_source_collector as msc

    monkeypatch.setenv("OMI_VAULT_PATH", str(demo_vault))
    monkeypatch.setenv("VITASIDE_DISABLE_CODEBASE_MEMORY", "1")
    snap = msc.build_multi_source_snapshot(demo_vault, {}, data_mode="demo")
    assert "obsidian_notes" in snap["lanes"]
    assert snap["lanes"]["obsidian_notes"]["event_count"] >= 1
    assert snap["event_count_by_source"].get("obsidian_notes", 0) >= 1


def test_search_health_note_hits_uses_mocked_mcporter(demo_vault: Path):
    import codebase_memory_client as cmc

    fake_projects = {
        "projects": [{"name": "demo-proj", "root_path": str(demo_vault.resolve())}],
    }
    fake_search = {
        "total": 1,
        "results": [
            {
                "name": "Visit-Prep",
                "file_path": "03-Visits/Visit-Prep-2026-06-28-GP.md",
                "label": "File",
            }
        ],
        "has_more": False,
    }

    with patch.object(cmc, "_mcporter_call", side_effect=[fake_projects, fake_search, fake_search]):
        out = cmc.search_health_note_hits(demo_vault, queries=["sleep"], max_hits=3)
    assert out["status"] == "ok"
    assert out["project"] == "demo-proj"
    assert len(out["hits"]) >= 1