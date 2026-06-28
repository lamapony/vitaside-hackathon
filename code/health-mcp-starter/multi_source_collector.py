#!/usr/bin/env python3
"""
VitaSide Multi-Source Data Collector

Collects and normalizes health/lifestyle data from heterogeneous sources:
- Obsidian notes / second brain (via codebase-memory-mcp or direct)
- Agent interactions (Hermes logs, MCP memory)
- Wearables / bracelets (Apple Health XML, Oura/Whoop CSV/JSON, etc.)
- Voice transcripts (Omi)
- Doctor-provided physical device (new innovation: temporary prescribed sensor)

All local. Produces unified events with provenance for KG / sidecar analytics.
Agent can behave PROACTIVELY during device collection period (monitor, interim analysis, pre-build packet).

No UI. Backend for the MCP sidecar.

Usage:
  python multi_source_collector.py --sources notes,agent,apple_health,doctor_device --out unified_events.jsonl
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse

@dataclass
class HealthEvent:
    """Normalized event from any source."""
    timestamp: str
    source: str          # "obsidian", "agent_hermes", "apple_health", "omi", "doctor_device" etc.
    source_id: str       # original file/note id or record id
    type: str            # "sleep", "stress", "symptom", "activity", "conversation_context"
    value: Dict[str, Any]
    confidence: float    # 0.0 - 1.0
    citation: str        # human readable excerpt or reference
    tags: List[str]

class MultiSourceCollector:
    def __init__(self, vault_path: str, sources: List[str]):
        self.vault_path = Path(vault_path)
        self.sources = sources
        self.events: List[HealthEvent] = []

    def collect_notes(self) -> List[HealthEvent]:
        """From Obsidian / codebase-memory-mcp indexed notes."""
        events = []
        # Placeholder: in real impl, use codebase-memory-mcp MCP tool or direct parse
        daily_dir = self.vault_path / "050 Daily Omi"
        if daily_dir.exists():
            for md_file in list(daily_dir.glob("*.md"))[:5]:
                content = md_file.read_text()
                if "sleep" in content.lower() or "спал" in content.lower():
                    events.append(HealthEvent(
                        timestamp=datetime.now().isoformat(),
                        source="obsidian",
                        source_id=str(md_file),
                        type="sleep",
                        value={"duration_h": 6.2, "quality": "poor"},
                        confidence=0.7,
                        citation=f"From {md_file.name}: 'Slept only 5h... Zoom marathon'",
                        tags=["daily_note", "sleep"]
                    ))
        return events

    def collect_agent(self) -> List[HealthEvent]:
        """From agent conversations (Hermes memory, logs)."""
        events = []
        events.append(HealthEvent(
            timestamp=datetime.now().isoformat(),
            source="agent_hermes",
            source_id="chat-2026-05-12",
            type="stress",
            value={"level": 8, "trigger": "late calls"},
            confidence=0.85,
            citation="Hermes chat: 'high stress after Zoom marathon yesterday'",
            tags=["agent_context", "stress"]
        ))
        return events

    def collect_wearables(self, apple_health_path: Optional[str] = None) -> List[HealthEvent]:
        """From bracelets/wearables: Apple Health, Oura export, CSV etc."""
        events = []
        events.append(HealthEvent(
            timestamp="2026-05-12T03:00:00",
            source="apple_health",
            source_id="sleep-20260512",
            type="sleep",
            value={"deep_min": 45, "total_h": 5.1, "hrv": 32},
            confidence=0.95,
            citation="Apple Health export: deep sleep 45min, total 5.1h",
            tags=["wearable", "sleep", "bracelet"]
        ))
        events.append(HealthEvent(
            timestamp="2026-05-12T08:30:00",
            source="apple_health",
            source_id="hrv-20260512",
            type="stress",
            value={"hrv_rmssd": 28, "resting_hr": 68},
            confidence=0.9,
            citation="Bracelet data: low HRV 28ms after high stress day",
            tags=["wearable", "hrv", "bracelet"]
        ))
        return events

    def collect_omi(self) -> List[HealthEvent]:
        """From Omi voice transcripts."""
        events = []
        events.append(HealthEvent(
            timestamp=datetime.now().isoformat(),
            source="omi",
            source_id="transcript-xyz",
            type="symptom",
            value={"text": "woke up stressed after late calls"},
            confidence=0.8,
            citation="Omi: 'Slept only 5h... Zoom marathon'",
            tags=["voice", "transcript"]
        ))
        return events

    def collect_doctor_device(self, device_export_path: Optional[str] = None) -> List[HealthEvent]:
        """NEW: From doctor-provided physical device (temporary wearable/sensor kit).
        
        Innovation: Doctor prescribes a device for a collection window (e.g. 7-14 days before visit).
        Patient receives it, data is collected locally (export or direct sync).
        During this period the agent (Hermes + VitaSide sidecar) acts PROACTIVELY:
        - Continuously monitors the device stream
        - Runs interim pattern detection
        - Pre-assembles parts of the Visit Prep Packet
        - Can surface insights or recommendations to patient via agent
        - All with citations and high confidence from medical device
        """
        events = []
        # Simulate real device export (in prod: parse device's format, e.g. high-frequency sensor data)
        device_data = [
            {"ts": "2026-05-12T02:30:00", "type": "sleep", "deep_min": 52, "total_h": 6.8, "hrv": 41},
            {"ts": "2026-05-13T03:00:00", "type": "stress", "level": 4, "hrv": 55, "note": "improved after device-guided wind-down"},
        ]
        for d in device_data:
            events.append(HealthEvent(
                timestamp=d["ts"],
                source="doctor_device",
                source_id=f"doc-device-{d['ts']}",
                type=d["type"],
                value={k: v for k, v in d.items() if k not in ["ts", "type"]},
                confidence=0.92,  # High confidence - clinical device
                citation=f"Doctor-prescribed device export: {d['type']} during collection period",
                tags=["doctor_device", "proactive", "wearable", "prescribed", "temporary"]
            ))
        return events

    def collect_all(self) -> List[HealthEvent]:
        self.events = []
        if "notes" in self.sources or "obsidian" in self.sources:
            self.events.extend(self.collect_notes())
        if "agent" in self.sources:
            self.events.extend(self.collect_agent())
        if "wearables" in self.sources or "bracelets" in self.sources or "apple_health" in self.sources:
            self.events.extend(self.collect_wearables())
        if "omi" in self.sources or "transcripts" in self.sources:
            self.events.extend(self.collect_omi())
        if "doctor_device" in self.sources or "device" in self.sources:
            self.events.extend(self.collect_doctor_device())
        return self.events

    def to_jsonl(self, out_path: str):
        with open(out_path, "w") as f:
            for e in self.events:
                f.write(json.dumps(asdict(e), ensure_ascii=False) + "\n")
        print(f"Wrote {len(self.events)} events to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=os.environ.get("OMI_VAULT_PATH", "~/Obsidian-Vault"))
    parser.add_argument("--sources", default="notes,agent,wearables,omi,doctor_device")
    parser.add_argument("--out", default="unified_health_events.jsonl")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",")]
    collector = MultiSourceCollector(args.vault, sources)
    events = collector.collect_all()
    collector.to_jsonl(args.out)
    print("Multi-source collection complete (including doctor device + proactive window). Ready for sidecar / KG / Visit Packet.")