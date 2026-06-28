"""VIT-26/VIT-28: canonical build_visit_packet + health_check."""
from __future__ import annotations

import importlib.util
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def mcp_mod():
    os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
    os.environ.setdefault(
        "VITASIDE_MANIFEST",
        str(ROOT / "sidecars" / "sleep-stress-sidecar" / "manifest.yaml"),
    )
    spec = importlib.util.spec_from_file_location("vita_mcp", ROOT / "health-pattern-mcp.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_build_visit_packet_has_gates(mcp_mod):
    pkt = mcp_mod.build_visit_packet(formats=["markdown"])
    assert pkt.get("questions_count", 0) >= 1
    assert pkt.get("disclaimer")
    assert len(pkt.get("summary_md", "")) > 50
    assert "confidence" in pkt
    assert pkt.get("entity_id", "").startswith("vp-")
    assert pkt.get("pain_point_citations")
    assert pkt["pain_point_citations"][0].get("entity_id") == "pp-01"
    baselines = pkt.get("personal_baselines") or {}
    assert baselines.get("storage") == "sqlite_local"
    visit_md = (pkt.get("outputs") or {}).get("visit_packet_md", "")
    assert "03-Visits" in visit_md or "Visits" in visit_md
    assert Path(visit_md).exists()


def test_build_visit_packet_e2e_offline_under_60s(mcp_mod, monkeypatch):
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("HTTPS_PROXY", raising=False)
    t0 = time.monotonic()
    pkt = mcp_mod.build_visit_packet(formats=["markdown", "obsidian"])
    elapsed = time.monotonic() - t0
    assert elapsed < 60.0, f"E2E took {elapsed:.1f}s"
    assert pkt.get("citations")
    assert any(c.get("entity_id") == "pp-01" for c in pkt["citations"])


def test_health_check_liveness(mcp_mod):
    hc = mcp_mod.health_check(include_sources=False)
    assert hc.get("expired") is False
    assert hc.get("name")