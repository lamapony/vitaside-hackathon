"""VIT-43: doctor handoff print export + golden footer markers."""
from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from doctor_handoff_export import (  # noqa: E402
    export_print_bundle_from_markdown,
    render_audit_footer,
    wrap_print_html,
)


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


DEMO_MD = """# Visit prep (demo)

## Patterns
- **sleep → mood_low** lag 1d

## Questions
- Ask about sleep hygiene
"""


def _norm_html(s: str) -> str:
    s = re.sub(r"Generated: \d{4}-\d{2}-\d{2}", "Generated: YYYY-MM-DD", s)
    s = re.sub(r"doctor-handoff-print-\d{4}-\d{2}-\d{2}", "doctor-handoff-print-YYYY-MM-DD", s)
    return s


def test_footer_has_mandatory_fields(tmp_path):
    footer = render_audit_footer(
        disclaimer="Not medical advice.",
        confidence=0.82,
        data_scopes=["demo-data/vault/050 Daily Omi"],
        audit_summary={"entries": 3, "unique_files": 2},
        entity_id="vp-demo-1",
        generated_at="2026-01-15",
    )
    assert "vitaside-audit-footer" in footer
    assert "Data scope" in footer
    assert "0.82" in footer
    assert "Not medical advice" in footer
    assert "vp-demo-1" in footer


def test_golden_print_html_footer_markers(tmp_path):
    out = export_print_bundle_from_markdown(
        DEMO_MD,
        disclaimer="Demo disclaimer for print.",
        confidence=0.75,
        data_scopes=["scope-a", "scope-b"],
        audit_summary={"entries": 5, "unique_files": 1},
        entity_id="vp-golden",
        out_dir=tmp_path,
        basename="doctor-handoff-print",
    )
    html = Path(out["print_html"]).read_text(encoding="utf-8")
    assert "@media print" in html
    markers = "\n".join(
        [
            "FOOTER_ID=vitaside-audit-footer",
            "HAS_SCOPE=scope-a",
            "HAS_CONFIDENCE=0.75",
            "HAS_ENTITY=vp-golden",
            "HAS_DISCLAIMER=Demo disclaimer",
            "HAS_PRINT_MEDIA=@media print",
        ]
    )
    golden_path = ROOT / "fixtures" / "doctor_handoff_print_markers.txt"
    assert golden_path.read_text(encoding="utf-8").strip() == markers.strip()


def test_export_doctor_handoff_print_tool_demo(mcp_mod, tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_mod, "_SCRIPT_DIR", tmp_path)
    result = mcp_mod.export_doctor_handoff_print()
    assert result.get("footer_marker") == "vitaside-audit-footer"
    print_path = (result.get("outputs") or {}).get("print_html")
    assert print_path and Path(print_path).is_file()
    body = Path(print_path).read_text(encoding="utf-8")
    assert "vitaside-audit-footer" in body
    assert result.get("confidence") is not None