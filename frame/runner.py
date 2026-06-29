#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from frame.capture import FrameCapture

async def main():
    print("VitaSide Frame Periodic Runner (VERY_HIGH + 720px defaults)")
    cap = FrameCapture()
    f = await cap.wait_and_connect(max_wait_minutes=10)
    if not f:
        print("No connection. Press pinhole button and retry.")
        return
    try:
        interval = 120
        print(f"Periodic capture every {interval}s. Ctrl+C to stop.")
        while True:
            await cap.capture(f)
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        await cap.disconnect(f)

if __name__ == "__main__":
    asyncio.run(main())
