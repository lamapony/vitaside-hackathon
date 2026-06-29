from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

@dataclass
class CaptureConfig:
    interval_seconds: int = 120
    quality: str = "MEDIUM"
    resolution: int = 512
    autofocus_seconds: int = 2
    output_dir: str = "~/vitaside_frame_captures"

@dataclass
class BluetoothConfig:
    pairing_code: str = ""

@dataclass
class ProcessingConfig:
    enabled: bool = True
    min_battery_percent: int = 15

@dataclass
class FrameConfig:
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    bluetooth: BluetoothConfig = field(default_factory=BluetoothConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    patient_consent: bool = True

    @classmethod
    def load(cls, path: str | Path = "~/vitaside/config/frame.yaml") -> "FrameConfig":
        path = Path(path).expanduser()
        if not path.exists():
            # fallback to example
            example = Path(__file__).parent.parent / "config" / "frame.example.yaml"
            if example.exists():
                path = example
            else:
                return cls()

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        capture = CaptureConfig(**data.get("capture", {}))
        bt = BluetoothConfig(**data.get("bluetooth", {}))
        proc = ProcessingConfig(**data.get("processing", {}))

        return cls(
            capture=capture,
            bluetooth=bt,
            processing=proc,
            patient_consent=data.get("patient", {}).get("consent", True),
        )

    def get_output_dir(self) -> Path:
        return Path(self.capture.output_dir).expanduser()