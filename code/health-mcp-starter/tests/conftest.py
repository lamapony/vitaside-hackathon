import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_DEMO_VAULT = ROOT / "demo-data" / "vault"
os.environ["OMI_VAULT_PATH"] = str(_DEMO_VAULT)
os.environ.setdefault(
    "VITASIDE_MANIFEST",
    str(ROOT / "sidecars" / "sleep-stress-sidecar" / "manifest.yaml"),
)


@pytest.fixture(scope="session", autouse=True)
def _ensure_demo_vault():
    if not (_DEMO_VAULT / "050 Daily Omi" / "Conversations").exists():
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "gen_demo_data.py")], cwd=ROOT, check=True)
    visit_dir = _DEMO_VAULT / "03-Visits"
    visit_dir.mkdir(parents=True, exist_ok=True)
    visit_file = visit_dir / "Visit-Prep-2026-06-28-GP.md"
    if not visit_file.exists():
        visit_file.write_text(
            """---
VisitPacket: demo
condition: migraine
generated: 2026-06-28
---

# Visit prep (demo fixture)

## Patterns
- sleep → mood_low (lag 1d)

## Questions
- Ask about sleep hygiene
""",
            encoding="utf-8",
        )
