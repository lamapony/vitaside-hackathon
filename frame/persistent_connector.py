#!/usr/bin/env python3
"""
Persistent Frame connector for VitaSide.
Run this, then press the pinhole button (while on cable or after).
It will keep scanning and try to connect as soon as a device appears.
"""

import asyncio
from datetime import datetime
from pathlib import Path

from frame_sdk import Frame
from frame_sdk.camera import Quality, AutofocusType
from bleak import BleakScanner

OUTPUT_DIR = Path.home() / "vitaside_frame_captures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SERVICE_UUID = "7a230001-5475-a6a4-654c-8431f6ad49c4"

async def try_capture(f):
    try:
        bat = await f.get_battery_level()
        print(f"[CONNECTED] Battery: {bat}%")

        try:
            await f.display.show_text("VitaSide\nConnected", align="MIDDLE_CENTER")
        except:
            pass

        photo = await f.camera.take_photo(autofocus_seconds=2, quality=Quality.MEDIUM, resolution=512)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        jpg = OUTPUT_DIR / f"frame_{ts}.jpg"
        jpg.write_bytes(photo)
        print(f"[SUCCESS] Photo saved: {jpg} ({len(photo)} bytes)")
        return True
    except Exception as e:
        print(f"[CAPTURE ERROR] {e}")
        return False

async def main():
    print("=== Persistent Frame Scanner ===")
    print("Run this script.")
    print("Then press/hold the pinhole button on the glasses (on cable).")
    print("Script will auto-detect and connect when it advertises.\n")

    while True:
        try:
            devices = await BleakScanner.discover(timeout=5, return_adv=True)
            for dev, adv in devices.values():
                if SERVICE_UUID in (adv.service_uuids or []):
                    print(f"[FOUND] {dev.name or dev.address} RSSI={adv.rssi} at {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Try connect multiple times quickly
                    for i in range(5):
                        try:
                            async with Frame() as f:
                                if await try_capture(f):
                                    print("✅ Success! You can now use the runner.")
                                    return
                        except Exception as e:
                            print(f"  Connect attempt {i+1} failed: {e}")
                            await asyncio.sleep(0.5)
                    
                    print("Device disappeared or failed to connect. Waiting for next advertisement...")
            
            await asyncio.sleep(1)
        except Exception as e:
            print(f"[SCAN ERROR] {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
