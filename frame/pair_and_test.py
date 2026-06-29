#!/usr/bin/env python3
"""
Frame + VitaSide test - follows official pairing procedure exactly.

INSTRUCTIONS FOR YOU (Dima):
1. Glasses connected to your cable (charger).
2. Take a needle or sim-card tool.
3. Press and HOLD the pinhole button on the glasses for full 3 seconds.
4. (Best) Unplug the cable after.
5. Run this script: python3 /tmp/frame_vitaside_test.py
6. It will keep scanning. Tap the glasses if needed to wake.

The display being off on charger is normal per your report and docs.
The pinhole button forces pairing / advertising mode.
"""

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
    print("=" * 60)
    print("VitaSide Frame Test - OFFICIAL PAIRING FLOW")
    print("=" * 60)
    print()
    print("DO THIS FIRST (while glasses are on the cable):")
    print("  - Use needle to HOLD the pinhole pairing button for 3 seconds.")
    print("  - Then unplug the cable if possible.")
    print("  - The glasses should now be advertising.")
    print()
    print("This script will scan repeatedly. Keep it running.")
    print("If display wakes or shows code after button, great.")
    print()

    for attempt in range(1, 8):
        print(f"\n[Scan attempt {attempt}]")
        devices = await BleakScanner.discover(timeout=7, return_adv=True)
        frames = [(d, adv.rssi) for d, adv in devices.values() 
                  if SERVICE_UUID in (adv.service_uuids or [])]
        frames.sort(key=lambda x: x[1], reverse=True)

        if frames:
            print(f"  SUCCESS: {len(frames)} Frame device(s) advertising!")
            for dev, rssi in frames:
                print(f"    {dev.name or dev.address} (RSSI {rssi})")

            print("\n[CONNECT] Trying Frame() ...")
            try:
                async with Frame() as f:
                    bat = await f.get_battery_level()
                    print(f"[CONNECTED] Battery = {bat}%")

                    try:
                        await f.display.show_text("VitaSide\nOK", align="MIDDLE_CENTER")
                        print("[DISPLAY] Sent text to glasses")
                    except Exception as de:
                        print(f"[DISPLAY] (expected if still on charger): {de}")

                    print("[CAPTURE] Taking photo...")
                    photo = await f.camera.take_photo(
                        autofocus_seconds=2, 
                        quality=Quality.MEDIUM, 
                        resolution=512
                    )
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    jpg = OUTPUT_DIR / f"frame_{ts}.jpg"
                    jpg.write_bytes(photo)

                    meta = {"ts": datetime.now().isoformat(), "battery": bat, "path": str(jpg)}
                    (OUTPUT_DIR / f"frame_{ts}.json").write_text(json.dumps(meta, indent=2))

                    print(f"\n[SAVED] {jpg} ({len(photo)} bytes)")
                    print("✅ Connection works! We can now do periodic capture for VitaSide.")
                    return
            except Exception as e:
                print(f"  Connect failed: {e}")
        else:
            print("  No Frame devices yet. (Hold pinhole 3s again if needed)")

        await asyncio.sleep(3)

    print("\nNo luck after several attempts.")
    print("Try:")
    print("  - Hold pinhole 3s on charger, then remove cable, then run again.")
    print("  - Tap the glasses after the button press.")
    print("  - Check: system_profiler SPBluetoothDataType")

if __name__ == "__main__":
    asyncio.run(main())
