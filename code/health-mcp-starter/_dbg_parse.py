import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v", ROOT / "health-pattern-mcp.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

paths = [
    ROOT / "fixtures/omi_messy/vague_yesterday.md",
    ROOT / "fixtures/omi_messy/2026-02-14-filename-date.md",
    ROOT / "demo-data/vault/050 Daily Omi/Conversations/2026/03/2026-03-30.md",
]
for p in paths:
    try:
        r = m._parse_omi_file(p)
    except Exception as e:
        print(p.name, "EXC", e)
        continue
    print(p.name, "->", None if r is None else (r.get("signals"), r.get("parser_confidence")))