#!/usr/bin/env python3
"""
Integrated VitaSide Frame Runner.
Background collection + analysis + storage.
Run after activation.

Usage:
  python3 ~/vitaside/frame/integrated_runner.py           # real glasses (waits for BT)
  python3 ~/vitaside/frame/integrated_runner.py --simulate   # use existing captures for demo
"""
import asyncio
import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from frame.capture import FrameCapture
from vitaside.profile import PatientProfile
from vitaside.analyzer import analyze_lifestyle
from vitaside.storage import LocalStore

async def main(simulate: bool = False):
    print("=== VitaSide Integrated Frame Runner ===")
    print("Background lifestyle data collection for doctor insights.")

    # Load profile
    config_dir = Path("~/vitaside/config").expanduser()
    profile = PatientProfile.load(config_dir / "patient_profile.json")
    if not profile:
        print("No profile. Run: python3 ~/vitaside/vitaside/activation.py")
        return
    profile_dict = profile.to_dict()

    store = LocalStore()
    cap = FrameCapture(output_dir="~/vitaside_frame_captures")

    print(f"Patient: {profile.name}. Goals: {profile.goals}")
    print("Starting collection. Press pinhole on glasses when needed.")

    if simulate:
        print("[SIMULATE MODE] Using existing local captures instead of real glasses.")
        captures_dir = Path("~/vitaside_frame_captures").expanduser()
        jpgs = sorted(captures_dir.glob("*.jpg"))[:5]
        for jpg in jpgs:
            print(f"[SIM] Processing {jpg.name}")
            event = analyze_lifestyle(jpg, profile_dict)
            store.add_event(event)
            patterns = store.compute_patterns()
            print(f"[Analysis] Tags: {event['lifestyle_tags']}")
            print(f"[Patterns] Top: {patterns.get('top_tags')}")
        print("[SIMULATE] Done. Run dashboard to view.")
        summary = store.export_for_doctor()
        print(f"Doctor summary: {summary}")
        return

    f = await cap.wait_and_connect(max_wait_minutes=10)
    if not f:
        print("Could not connect to glasses.")
        return

    try:
        interval = 120  # 2 min for demo; real: 15-60 min
        while True:
            img_path = await cap.capture(f)
            if img_path:
                event = analyze_lifestyle(img_path, profile_dict)
                store.add_event(event)
                patterns = store.compute_patterns()
                print(f"[Analysis] Tags: {event['lifestyle_tags']}")
                print(f"[Patterns] Top: {patterns.get('top_tags')}")
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        print("Stopping collection. Summary exported.")
        summary = store.export_for_doctor()
        print(f"Doctor summary: {summary}")
    finally:
        await cap.disconnect(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true", help="Use existing jpgs for demo (no glasses needed)")
    args = parser.parse_args()
    asyncio.run(main(simulate=args.simulate))
