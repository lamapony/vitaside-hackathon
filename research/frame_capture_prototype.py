#!/usr/bin/env python3
"""
VitaSide Frame Glasses Periodic Capture Prototype

Uses the Brilliant Labs Frame SDK (frame-sdk) to periodically capture photos
from the glasses camera over Bluetooth.

Cable is for POWER/CHARGING only. Data connection is Bluetooth.

Setup:
1. pip install frame-sdk
2. Power the glasses via your USB-C cable (or dock).
3. Get the pairing code displayed on the glasses (usually 2 digits).
4. Run this script and enter the code when prompted.

For VitaSide:
- Replace the "save and log" section with your local vision model call
  (caption + embeddings) + insert into your health pattern store.
- Add consent / pause controls.
- Run as a background sidecar (systemd, launchd, or Python process).

Example integration point:
    photo_bytes = await capture_photo(...)
    metadata = await your_vision.analyze(photo_bytes)  # caption, tags, etc.
    vitaside_store.add_lifestyle_event(timestamp, metadata)
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path

from frame_sdk import Frame
from frame_sdk.camera import Quality, AutofocusType

# === CONFIG (tune for your use case) ===
CAPTURE_INTERVAL_SECONDS = 120  # every 2 minutes — adjust!
OUTPUT_DIR = Path.home() / "vitaside_frame_captures"
QUALITY = Quality.MEDIUM
RESOLUTION = 512
AUTOFOCUS_SECONDS = 2
# ======================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def capture_and_save(f: Frame, index: int) -> str:
    """Capture one photo and save it with timestamp + index."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = OUTPUT_DIR / f"frame_{timestamp}_{index:04d}.jpg"

    try:
        await f.camera.save_photo(
            str(filename),
            autofocus_seconds=AUTOFOCUS_SECONDS,
            quality=QUALITY,
            resolution=RESOLUTION,
            autofocus_type=AutofocusType.CENTER_WEIGHTED,
        )
        print(f"[{timestamp}] Saved: {filename}")
        return str(filename)
    except Exception as e:
        print(f"Capture failed: {e}")
        return ""


async def main():
    print("=== VitaSide Frame Capture ===")
    print("Cable = power only. Bluetooth for data.")
    print(f"Photos will be saved to: {OUTPUT_DIR}")
    print(f"Interval: {CAPTURE_INTERVAL_SECONDS} seconds\n")

    pairing_code = input("Enter pairing code shown on Frame (or leave empty for any): ").strip().upper() or None

    photo_index = 0

    try:
        async with Frame(address=pairing_code) as f:
            print(f"Connected. Battery: {await f.get_battery_level()}%")

            # Optional: show something on the glasses so patient knows it's active
            await f.display.show_text("VitaSide recording...", align="MIDDLE_CENTER")

            while True:
                photo_path = await capture_and_save(f, photo_index)
                photo_index += 1

                battery = await f.get_battery_level()
                print(f"Battery: {battery}% | Next capture in {CAPTURE_INTERVAL_SECONDS}s...")

                # === Vitaside integration hook ===
                # if photo_path:
                #     photo_bytes = open(photo_path, "rb").read()
                #     analysis = await your_local_vision.analyze(photo_bytes)
                #     await vitaside_db.record_lifestyle_event(
                #         timestamp=datetime.now(),
                #         source="frame",
                #         caption=analysis.caption,
                #         tags=analysis.tags,
                #         # embeddings etc.
                #     )
                # =================================

                if battery < 15:
                    print("Low battery — consider stopping or charging.")
                    # Optionally: await f.display.show_text("Low battery", ...)

                await asyncio.sleep(CAPTURE_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Capture session ended.")


if __name__ == "__main__":
    asyncio.run(main())
