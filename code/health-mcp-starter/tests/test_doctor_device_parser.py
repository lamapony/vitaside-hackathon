"""VIT-63: doctor_device export parsers (CSV / JSON / Apple Health XML)."""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_parse_doctor_device_csv_wide(tmp_path: Path):
    import multi_source_collector as msc

    csv_path = tmp_path / "export.csv"
    csv_path.write_text(
        "date,resting_hr,spo2,steps\n"
        "2026-06-27,61,97.1,8100\n"
        "2026-06-28,62,97.4,8420\n",
        encoding="utf-8",
    )
    events = msc.parse_doctor_device_export(csv_path)
    assert len(events) == 6
    assert all(e.source == "doctor_device" for e in events)
    metrics = {e.metric for e in events}
    assert metrics == {"resting_hr", "spo2", "steps"}


def test_parse_doctor_device_csv_long(tmp_path: Path):
    import multi_source_collector as msc

    csv_path = tmp_path / "long.csv"
    csv_path.write_text(
        "timestamp,metric,value,unit\n"
        "2026-06-28T08:00:00Z,hrv_sdnn,48,ms\n"
        "2026-06-28T09:00:00Z,sleep_efficiency,0.88,ratio\n",
        encoding="utf-8",
    )
    events = msc.parse_doctor_device_export(csv_path)
    assert len(events) == 2
    assert events[0].metric == "hrv_sdnn"
    assert events[1].metric == "sleep_efficiency"


def test_parse_doctor_device_json(tmp_path: Path):
    import multi_source_collector as msc

    json_path = tmp_path / "device.json"
    json_path.write_text(
        '{"events":[{"metric":"resting_hr","value":63,"unit":"bpm","date":"2026-06-28"}]}',
        encoding="utf-8",
    )
    events = msc.parse_doctor_device_export(json_path)
    assert len(events) == 1
    assert events[0].value == 63


def test_parse_doctor_device_apple_xml(tmp_path: Path):
    import multi_source_collector as msc

    xml_path = tmp_path / "export.xml"
    xml_path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
          <Record type="HKQuantityTypeIdentifierHeartRate" value="72" startDate="2026-06-28 10:00:00 +0000"/>
          <Record type="HKQuantityTypeIdentifierStepCount" value="5000" startDate="2026-06-28 11:00:00 +0000"/>
        </HealthData>""",
        encoding="utf-8",
    )
    events = msc.parse_doctor_device_export(xml_path)
    assert len(events) == 2
    assert {e.metric for e in events} == {"resting_hr", "steps"}


def test_collect_doctor_device_prefers_export_over_simulation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import multi_source_collector as msc

    csv_path = tmp_path / "export.csv"
    csv_path.write_text("date,steps\n2026-06-28,9000\n", encoding="utf-8")
    monkeypatch.setenv("VITASIDE_DEVICE_WINDOW_ACTIVE", "1")

    events = msc.collect_doctor_device(export_path=csv_path, simulated=True)
    assert len(events) == 1
    assert events[0].metric == "steps"
    assert events[0].value == 9000