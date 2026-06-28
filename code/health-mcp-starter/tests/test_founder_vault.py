"""VIT-42: founder vault wiring helpers (fixture/demo only)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "verify_founder_vault.py"
TEMPLATE = ROOT / "docs/templates/user_context.example.json"


def test_user_context_template_is_valid_json():
    data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    assert "profile" in data
    assert "manual_logs" in data


def test_verify_founder_vault_fails_without_explicit_vault(monkeypatch):
    monkeypatch.delenv("OMI_VAULT_PATH", raising=False)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "OMI_VAULT_PATH" in proc.stdout + proc.stderr


def test_verify_founder_vault_rejects_demo_path(monkeypatch):
    demo = ROOT / "demo-data" / "vault"
    if not demo.is_dir():
        pytest.skip("demo-data not generated in this checkout")
    monkeypatch.setenv("OMI_VAULT_PATH", str(demo))
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "demo" in (proc.stdout + proc.stderr).lower()