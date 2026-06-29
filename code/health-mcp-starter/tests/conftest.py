import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_DEMO_VAULT = ROOT / "demo-data" / "vault"
os.environ["OMI_VAULT_PATH"] = str(_DEMO_VAULT)
os.environ.setdefault(
    "VITASIDE_MANIFEST",
    str(ROOT / "sidecars" / "sleep-stress-sidecar" / "manifest.yaml"),
)
