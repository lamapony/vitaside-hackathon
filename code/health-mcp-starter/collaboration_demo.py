#!/usr/bin/env python3
"""VitaSide collaboration demo — thin CLI over MCP core."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent
os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
bundle = ROOT / "sidecars" / "sleep-stress-sidecar" / "manifest.yaml"
if bundle.exists():
    os.environ.setdefault("VITASIDE_MANIFEST", str(bundle))

import importlib.util
spec = importlib.util.spec_from_file_location("vita", ROOT / "health-pattern-mcp.py")
vita = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vita)


def main():
    result = vita._collaborative_insight_core(vita.DEFAULT_HOST_CONTEXT)
    result["disclaimer"] = vita.DISCLAIMER
    print("=" * 60)
    print("VITASIDE COLLABORATION DEMO")
    print("=" * 60)
    print()
    print("🧠 MAIN AGENT knows:", len(vita.DEFAULT_HOST_CONTEXT["events"]), "life events (travel + deadlines)")
    print("🔬 SIDECAR knows:", result["evidence"].get("top_correlation", {}))
    print()
    print("✨ COMBINED:")
    print("  ", result["collaborative_insight"])
    print()
    print(f"   Confidence: {result['confidence']}")
    print(f"   {result['disclaimer']}")
    print("=" * 60)
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
