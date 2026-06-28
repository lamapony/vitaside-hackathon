"""VIT-25 sqlite-longitudinal: migration, baselines, scope."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import longitudinal_store as ls
import sidecar_protocol as sp


@pytest.fixture()
def vault_scope() -> Path:
    return ROOT / "demo-data" / "vault" / "050 Daily Omi"


def _write_manifest(path: Path, payload: dict) -> None:
    try:
        import yaml

        path.write_text(yaml.dump(payload, sort_keys=False), encoding="utf-8")
    except ImportError:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@pytest.fixture()
def scoped_manifest(tmp_path: Path, vault_scope: Path) -> Path:
    manifest = tmp_path / "scoped.yaml"
    _write_manifest(
        manifest,
        {
            "name": "longitudinal-test",
            "issuer": "test@local",
            "ttl": "30d",
            "allowed_scopes": [{"path": str(vault_scope), "permissions": ["read", "write"]}],
            "tools": ["get_personal_baselines", "smart_analysis"],
        },
    )
    return manifest


def test_migration_idempotent(scoped_manifest: Path, monkeypatch):
    db = ROOT / "demo-data" / "vault" / "050 Daily Omi" / ".vitaside" / "test-longitudinal.db"
    monkeypatch.setenv("VITASIDE_MANIFEST", str(scoped_manifest))
    monkeypatch.setenv("VITASIDE_LONGITUDINAL_DB", str(db))
    if db.exists():
        db.unlink()
    conn = ls.connect(db, sp.load_manifest(scoped_manifest))
    ls.migrate(conn)
    tables1 = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    ls.migrate(conn)
    tables2 = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert tables1 == tables2
    assert "daily_metric" in tables1
    assert "schema_migrations" in tables1


def test_fixture_baselines_windows(tmp_path: Path, scoped_manifest: Path, monkeypatch):
    db = tmp_path / "scoped" / "longitudinal.db"
    db.parent.mkdir(parents=True)
    # parent is tmp — must be under vault scope via env path inside vault
    vault_db = ROOT / "demo-data" / "vault" / "050 Daily Omi" / ".vitaside" / "fixture-test.db"
    monkeypatch.setenv("VITASIDE_MANIFEST", str(scoped_manifest))
    monkeypatch.setenv("VITASIDE_LONGITUDINAL_DB", str(vault_db))
    if vault_db.exists():
        vault_db.unlink()

    fixture = ROOT / "fixtures" / "longitudinal_metrics.json"
    payload = ls.get_personal_baselines_payload(
        entries=[],
        manifest=sp.load_manifest(scoped_manifest),
        metric_keys=["resting_hr", "sleep_hours"],
        fixture_path=fixture,
    )
    assert payload["citations"]
    assert "7" in payload["metrics"]["resting_hr"]
    assert payload["metrics"]["resting_hr"]["7"]["n"] == 7
    assert payload["metrics"]["resting_hr"]["14"]["mean"] is not None
    assert payload["windows"] == [7, 14, 30]


def test_db_path_outside_scope_rejected(tmp_path: Path, scoped_manifest: Path, monkeypatch):
    outside = tmp_path / "outside.db"
    monkeypatch.setenv("VITASIDE_MANIFEST", str(scoped_manifest))
    monkeypatch.setenv("VITASIDE_LONGITUDINAL_DB", str(outside))
    with pytest.raises(RuntimeError, match="outside manifest scope"):
        ls.resolve_db_path(sp.load_manifest(scoped_manifest))