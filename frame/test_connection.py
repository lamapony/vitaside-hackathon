#!/usr/bin/env python3
"""Non-interactive Frame test (no input()). Run after you manually wake the glasses."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from frame_sdk import Frame
from frame_sdk.camera import Quality, AutofocusType
from bleak import BleakScanner

OUTPUT_DIR = Path.home() / "vitaside_frame_captures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SERVICE_UUID = "7a230001-5475-a6a4-654c-8431f6ad49c4"

async def main():
    print("=== VitaSide Frame Test (non-interactive) ===")
    print("Wake glasses FIRST (tap the arm, make sure display shows pairing code).")
    print("Then run this script.\n")

    print("[SCAN] 6s scan for Frame service...")
    devices = await BleakScanner.discover(timeout=6, return_adv=True)
    frames = []
    for d, adv in devices.values():
        if SERVICE_UUID in (adv.service_uuids or []):
            frames.append((d, adv.rssi))
    frames.sort(key=lambda x: x[1], reverse=True)

    print(f"[SCAN] Found {len(frames)} Frame device(s)")
    for dev, rssi in frames:
        print(f"  {dev.name or dev.address} RSSI={rssi}")

    if not frames:
        print("No advertising Frame found. Wake it and re-run.")
        return

    print("[CONNECT] Frame() ...")
    try:
        async with Frame() as f:
            bat = await f.get_battery_level()
            print(f"[CONNECTED] Battery {bat}%")

            try:
                await f.display.show_text("VitaSide", align="MIDDLE_CENTER")
            except: pass

            print("[CAPTURE] ...")
            photo = await f.camera.take_photo(autofocus_seconds=2, quality=Quality.MEDIUM, resolution=512)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            p = OUTPUT_DIR / f"frame_{ts}.jpg"
            p.write_bytes(photo)
            print(f"[SAVED] {p} ({len(photo)} bytes)")

            print("✅ Basic capture works. Ready for full integration.")
    except Exception as e:
        print(f"[FAIL] {e}")

if __name__ == "__main__":
    asyncio.run(main())
