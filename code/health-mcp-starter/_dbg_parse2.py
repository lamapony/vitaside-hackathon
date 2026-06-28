import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v", ROOT / "health-pattern-mcp.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

p = ROOT / "demo-data/vault/050 Daily Omi/Conversations/2026/03/2026-03-30.md"
content = p.read_text()
transcript_lines = re.findall(r"\*\*([^*]+)\*\*\s*\[(\d+):(\d+)\]:\s*(.+)", content)
spoken = " ".join([s[3] for s in transcript_lines])
full_text = spoken.lower()
signals = []
for sig, cfg in m.SIGNAL_PATTERNS.items():
    if re.findall(cfg["keywords"], full_text, re.I):
        signals.append(sig)
print("signals", signals)
print("date", re.search(r"date: (.+)", content))