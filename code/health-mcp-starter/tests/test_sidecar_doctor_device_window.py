"""VIT-65: manifest doctor_device + collection_window TTL in sidecar_protocol."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import sidecar_protocol as sp


def test_collection_window_ttl_computed_on_load(tmp_path: Path):
    manifest_path = tmp_path / "manifest.yaml"
    started = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest_path.write_text(
        f"""
name: test-sidecar
ttl: 30d
issued_at: "{started}"
collection_window:
  enabled: true
  ttl: 7d
  started_at: "{started}"
doctor_device:
  enabled: true
  export_paths:
    - "{{{{vault}}}}/exports/device.csv"
""",
        encoding="utf-8",
    )
    m = sp.load_manifest(manifest_path)
    window = m["collection_window"]
    assert window["expires_at"]
    exp = sp._parse_instant(window["expires_at"])
    start = sp._parse_instant(started)
    assert exp - start == timedelta(days=7)
    assert sp.collection_window_active(m)


def test_doctor_device_export_candidates_uses_manifest_vault_placeholder(tmp_path: Path):
    vault = tmp_path / "vault"
    export = vault / "exports" / "device.csv"
    export.parent.mkdir(parents=True)
    export.write_text("metric,value\nhr,60\n", encoding="utf-8")
    manifest = {
        "doctor_device": {
            "enabled": True,
            "export_paths": ["{{vault}}/exports/device.csv"],
        }
    }
    paths = sp.doctor_device_export_candidates(vault, manifest)
    assert export in paths
    assert sp.doctor_device_export_candidates(vault, manifest)[0] == paths[0]