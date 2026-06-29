# VitaSide + Brilliant Labs Frame Glasses Integration

**Goal**: Patient wears Frame glasses (powered via USB-C cable or dock). Camera periodically captures photos of daily activities. Local processing generates lifestyle insights for the doctor (kitchen time, outdoor activity, routines etc.). Everything local-first and privacy-respecting.

## Current Status (from repo analysis)
- GitHub: https://github.com/brilliantlabsAR/
- Key repo: frame-sdk-python
- **Connection**: Bluetooth LE only (no data over USB cable). Cable is for charging/power only.
- SDK: `pip install frame-sdk`
- Camera API: excellent — `take_photo()` returns JPEG bytes, `save_photo()` saves file. Supports autofocus, quality, resolution, pan.
- Pairing: Glasses show 2-digit code (or use full BT address). Use `async with Frame(address="XX") as f:`

## Architecture for VitaSide

1. **Frame Connector** (this sidecar / script)
   - Uses frame-sdk over BT.
   - Periodic or event-driven capture.
   - Saves images + metadata locally.

2. **Capture Policy**
   - Configurable interval (e.g. every 60-300s).
   - Respect battery (monitor `f.get_battery_level()`).
   - Patient controls: pause button, consent.

3. **Local Vision & Analysis**
   - On each photo: run local model (Ollama/Moondream/Llava, Apple ML, etc.).
   - Output: caption ("preparing food in kitchen", "walking outside"), tags, embeddings.
   - Do **not** send raw images to cloud by default.

4. **VitaSide Data Layer**
   - Feed structured events into existing health pattern / self-observation store.
   - Aggregate: time distribution, routines, anomalies.
   - Doctor view: insights + optional consented photo review.
   - Use existing privacy contracts / data minimization.

5. **Deployment Options**
   - Dev: Mac + cable for power + BT.
   - Patient: Phone (port to Flutter SDK if needed) or dedicated low-power sidecar running Python.
   - Or run the capture on a small always-on device near patient.

## Quick Start (Dev)

```bash
pip install frame-sdk
```

Power the glasses via the cable you have.

Get the pairing code (it should appear on the glasses display — tap or follow hardware instructions).

Run the example script (see vitaside-frame-capture.py).

## Next Steps / TODO

- [ ] Get pairing code from glasses while powered.
- [ ] Test basic connect + one photo capture.
- [ ] Implement periodic capture loop + local storage.
- [ ] Add local vision step (integrate your preferred model).
- [ ] Wire into VitaSide data model.
- [ ] Battery / power management + patient UX (display status on glasses?).
- [ ] Mobile path if needed (there are noa-*/flutter SDKs in the org).

## References
- SDK README + examples: cloned in analysis
- Official docs: https://docs.brilliant.xyz/frame/frame-sdk/
- Hardware: charging via USB-C cradle.
- Camera params: quality (VERY_LOW..VERY_HIGH), autofocus_seconds, resolution (100-720), autofocus_type.

This fits VitaSide perfectly for passive, consented, local lifestyle observation.
