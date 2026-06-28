"""VIT-24 sidecar-core: TTL, revoke, scoped paths, tool allowlist."""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sidecar_protocol as sp


def _write_manifest(path: Path, payload: dict) -> None:
    try:
        import yaml

        path.write_text(yaml.dump(payload, sort_keys=False), encoding="utf-8")
    except ImportError:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@pytest.fixture()
def vault_scope() -> Path:
    return ROOT / "demo-data" / "vault" / "050 Daily Omi"


@pytest.fixture()
def expired_manifest(tmp_path: Path, vault_scope: Path) -> Path:
    manifest = tmp_path / "expired.yaml"
    issued = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    _write_manifest(
        manifest,
        {
            "name": "expired-sidecar",
            "issuer": "test@local",
            "ttl": "7d",
            "issued_at": issued.isoformat().replace("+00:00", "Z"),
            "allowed_scopes": [{"path": str(vault_scope), "permissions": ["read"]}],
            "tools": ["analyze_lifestyle_patterns", "get_sidecar_status"],
        },
    )
    return manifest


@pytest.fixture()
def active_manifest(tmp_path: Path, vault_scope: Path) -> Path:
    manifest = tmp_path / "active.yaml"
    issued = datetime.datetime.now(datetime.timezone.utc)
    _write_manifest(
        manifest,
        {
            "name": "active-sidecar",
            "issuer": "test@local",
            "ttl": "30d",
            "issued_at": issued.isoformat().replace("+00:00", "Z"),
            "allowed_scopes": [{"path": str(vault_scope), "permissions": ["read"]}],
            "tools": ["analyze_lifestyle_patterns", "get_sidecar_status"],
        },
    )
    return manifest


def test_ttl_expiry_anchored_to_issued_at(expired_manifest: Path):
    m = sp.load_manifest(expired_manifest)
    exp = datetime.datetime.fromisoformat(m["_expires_at"].replace("Z", "+00:00"))
    issued = sp.parse_issued_at(m["issued_at"])
    assert exp == issued + datetime.timedelta(days=7)
    assert sp.is_expired(m)


def test_revoke_blocks_access(active_manifest: Path):
    sp.revoke_manifest(active_manifest)
    m2 = sp.load_manifest(active_manifest)
    assert sp.is_revoked(m2)
    with pytest.raises(RuntimeError, match="revoked"):
        sp.assert_sidecar_active(m2)


def test_expired_manifest_fail_closed(expired_manifest: Path):
    m = sp.load_manifest(expired_manifest)
    with pytest.raises(RuntimeError, match="expired"):
        sp.assert_sidecar_active(m)


def test_scoped_path_allows_and_denies(active_manifest: Path, vault_scope: Path):
    m = sp.load_manifest(active_manifest)
    assert sp.check_scope(m, vault_scope / "note.md")
    outside = ROOT / "demo-data" / "vault" / "outside.md"
    assert not sp.check_scope(m, outside)


def test_tool_allowlist_denies_unknown_tool(active_manifest: Path):
    m = sp.load_manifest(active_manifest)
    sp.assert_sidecar_active(m, tool="get_sidecar_status")
    with pytest.raises(RuntimeError, match="not allowed"):
        sp.assert_sidecar_active(m, tool="export_fhir_bundle")


def test_mcp_scan_rejects_expired_manifest(expired_manifest: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VITASIDE_MANIFEST", str(expired_manifest))
    monkeypatch.setenv("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))

    import importlib.util

    spec = importlib.util.spec_from_file_location("vita_sidecar_test", ROOT / "health-pattern-mcp.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._MANIFEST = None
    with pytest.raises(RuntimeError, match="expired"):
        mod.analyze_lifestyle_patterns()