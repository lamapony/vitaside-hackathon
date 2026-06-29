from __future__ import annotations
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from frame_sdk import Frame
from frame_sdk.camera import Quality, AutofocusType
from bleak import BleakScanner

SERVICE_UUID = "7a230001-5475-a6a4-654c-8431f6ad49c4"

class FrameCapture:
    """Robust Frame capture for VitaSide.
    Uses best observed settings to reduce artifacts: VERY_HIGH quality, 720 res.
    """

    def __init__(self, output_dir: str = "~/vitaside_frame_captures"):
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.default_quality = Quality.VERY_HIGH
        self.default_resolution = 720
        self.default_af_seconds = 4
        self.default_af_type = AutofocusType.CENTER_WEIGHTED
        self.default_pan = 0

    async def wait_and_connect(self, max_wait_minutes: float = 5) -> Optional[Frame]:
        print("[Frame] Waiting for device advertisement (press pinhole if needed)...")
        deadline = asyncio.get_event_loop().time() + (max_wait_minutes * 60)
        while asyncio.get_event_loop().time() < deadline:
            devices = await BleakScanner.discover(timeout=4, return_adv=True)
            for dev, adv in devices.values():
                if SERVICE_UUID in (adv.service_uuids or []):
                    print(f"[Frame] Found {dev.name or dev.address} RSSI={adv.rssi}")
                    for _ in range(6):
                        try:
                            f = Frame()
                            await f.__aenter__()
                            bat = await f.get_battery_level()
                            print(f"[Frame] Connected! Battery {bat}%")
                            return f
                        except Exception as e:
                            await asyncio.sleep(0.3)
            await asyncio.sleep(1)
        return None

    async def capture(self, f: Frame, **overrides) -> Optional[Path]:
        try:
            params = {
                "autofocus_seconds": overrides.get("autofocus_seconds", self.default_af_seconds),
                "quality": overrides.get("quality", self.default_quality),
                "resolution": overrides.get("resolution", self.default_resolution),
                "autofocus_type": overrides.get("autofocus_type", self.default_af_type),
                "pan": overrides.get("pan", self.default_pan),
            }
            photo = await f.camera.take_photo(**params)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = self.output_dir / f"frame_{ts}.jpg"
            path.write_bytes(photo)

            bat = await f.get_battery_level()
            meta = {
                "timestamp": datetime.now().isoformat(),
                "battery_percent": bat,
                "image_path": str(path),
                "size_bytes": len(photo),
                "params": {k: str(v) for k,v in params.items()}
            }
            (path.with_suffix(".json")).write_text(json.dumps(meta, indent=2))

            print(f"[Frame] Captured {path.name} ({len(photo)}B, bat {bat}%, res={params['resolution']})")
            return path
        except Exception as e:
            print(f"[Frame] Capture error: {e}")
            return None

    async def disconnect(self, f: Optional[Frame]):
        if f:
            try:
                await f.__aexit__(None, None, None)
            except:
                pass
