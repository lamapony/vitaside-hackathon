#!/usr/bin/env python3
"""Collaboration demo — sharp narrative, no raw JSON dumps."""
import os
from pathlib import Path

ROOT = Path(__file__).parent
os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
bundle = ROOT / "sidecars/sleep-stress-sidecar/manifest.yaml"
if bundle.exists():
    os.environ.setdefault("VITASIDE_MANIFEST", str(bundle))

import importlib.util
spec = importlib.util.spec_from_file_location("vita", ROOT / "health-pattern-mcp.py")
vita = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vita)


def main():
    result = vita._collaborative_insight_core(vita.DEFAULT_HOST_CONTEXT)
    top = result.get("evidence", {}).get("top_correlation", {})
    print("=" * 60)
    print("COLLABORATION — why two agents beat one LLM")
    print("=" * 60)
    print()
    print("Hermes (main):  5 life events — flights, deadlines (calendar context)")
    print(f"Sidecar:        {top.get('cause', '?')}→{top.get('effect', '?')} lag {top.get('lag', '?')}d, lift {top.get('lift_ratio', '?')}×")
    cite = (top.get("citations") or [{}])[0]
    if cite.get("excerpt"):
        print(f"                📎 {cite.get('date')}: \"{cite['excerpt'][:70]}…\"")
    print()
    print("Combined insight (only possible with both):")
    print(f"  {result['collaborative_insight']}")
    print()
    print(f"Confidence: {result['confidence']}")
    print(vita.DISCLAIMER)
    print("=" * 60)


if __name__ == "__main__":
    main()
