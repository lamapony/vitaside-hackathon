"""VIT-27: second-brain read — scoped paths, audit, traversal denial."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "mcp-servers" / "vitaside-second-brain"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))

import sidecar_protocol as sp
from obsidian_io import obsidian_read_note, obsidian_search
from second_brain_scope import resolve_safe_path, vault_roots


@pytest.fixture()
def vault_root(monkeypatch: pytest.MonkeyPatch) -> Path:
    v = ROOT / "demo-data" / "vault"
    monkeypatch.setenv("OMI_VAULT_PATH", str(v))
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    return v


@pytest.fixture()
def audit_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    log = tmp_path / "audit.log"
    monkeypatch.setenv("VITASIDE_AUDIT_LOG", str(log))
    sp.AUDIT_LOG = log
    return log


def test_vault_fixture_has_notes(vault_root: Path):
    assert list(vault_root.rglob("*.md"))


def test_obsidian_search_returns_snippets(vault_root: Path, audit_file: Path):
    out = obsidian_search(str(vault_root), "sleep")
    assert out["count"] >= 1
    assert out["files"][0]["snippet"]
    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    assert any("second_brain_read" in l for l in lines)


def test_obsidian_read_note_frontmatter(vault_root: Path):
    visit = vault_root / "03-Visits" / "Visit-Prep-2026-06-28-GP.md"
    out = obsidian_read_note(str(visit), max_lines=50)
    assert "VisitPacket" in str(out.get("frontmatter", {}))
    assert "content" in out and len(out["content"]) > 20


def test_path_traversal_denied_and_audited(vault_root: Path, audit_file: Path):
    with pytest.raises(ValueError, match="outside allowed"):
        resolve_safe_path("/etc/passwd")
    rows = [json.loads(l) for l in audit_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert any(r.get("event") == "path_escape_denied" for r in rows)


def test_relative_escape_blocked(vault_root: Path, audit_file: Path):
    omi = vault_root / "050 Daily Omi"
    with pytest.raises(ValueError):
        resolve_safe_path("../../../etc/passwd", vault_hint=str(omi))
    assert audit_file.exists()


def test_scoped_manifest_limits_roots(tmp_path: Path, vault_root: Path, monkeypatch: pytest.MonkeyPatch):
    manifest = tmp_path / "scoped.yaml"
    manifest.write_text(
        f"name: test\nissuer: local\nttl: 30d\n"
        f"allowed_scopes:\n  - path: {vault_root / '050 Daily Omi'}\n    permissions: [read]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("VITASIDE_MANIFEST", str(manifest))
    monkeypatch.delenv("OMI_VAULT_PATH", raising=False)
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    roots = vault_roots()
    assert len(roots) == 1
    inside = vault_root / "050 Daily Omi" / "Conversations" / "2026" / "03" / "2026-03-30.md"
    resolve_safe_path(str(inside))
    outside = vault_root / "03-Visits" / "Visit-Prep-2026-06-28-GP.md"
    with pytest.raises(ValueError):
        resolve_safe_path(str(outside))