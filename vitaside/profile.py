from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import List, Dict

@dataclass
class PatientProfile:
    patient_id: str
    name: str
    age: int
    conditions: List[str]
    goals: List[str]  # e.g. ["improve nutrition", "increase activity"]
    doctor_notes: str = ""
    glasses_id: str = "Frame FF"  # from pairing

    def to_dict(self):
        return asdict(self)

    @classmethod
    def load(cls, path: Path):
        if path.exists():
            data = json.loads(path.read_text())
            return cls(**data)
        return None

def activate_profile(config_dir: Path = Path("~/vitaside/config").expanduser()) -> PatientProfile:
    """Interactive activation for patient who received glasses by mail."""
    config_dir.mkdir(parents=True, exist_ok=True)
    profile_path = config_dir / "patient_profile.json"

    print("=== VitaSide Activation (patient side) ===")
    print("You received glasses from doctor by mail.")
    print("Activate to start collecting lifestyle data for your doctor visit.")

    name = input("Your name: ").strip() or "Patient"
    age = int(input("Age: ") or 30)
    conditions = input("Conditions (comma sep, e.g. diabetes,anxiety): ").split(",")
    goals = input("Goals (comma sep, e.g. nutrition,activity,sleep): ").split(",")
    doctor_notes = input("Any notes for doctor (optional): ") or ""

    profile = PatientProfile(
        patient_id=f"patient_{name.lower().replace(' ', '_')}",
        name=name,
        age=age,
        conditions=[c.strip() for c in conditions if c.strip()],
        goals=[g.strip() for g in goals if g.strip()],
        doctor_notes=doctor_notes,
        glasses_id="Frame FF"  # update after pairing
    )

    profile_path.write_text(json.dumps(profile.to_dict(), indent=2))
    print(f"\n✅ Profile saved to {profile_path}")
    print("Glasses can now collect data in background.")
    print("Run the runner to start collection.")
    return profile
