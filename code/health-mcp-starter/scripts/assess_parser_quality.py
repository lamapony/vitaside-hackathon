#!/usr/bin/env python3
"""CLI: assess parser confidence for Omi/journal markdown files (VIT-47)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_mcp():
    spec = importlib.util.spec_from_file_location("vita_mcp", ROOT / "health-pattern-mcp.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assess Omi/journal parser quality")
    parser.add_argument("paths", nargs="+", help="Markdown files or directories")
    parser.add_argument("--json", action="store_true", help="JSON lines output")
    parser.add_argument("--warn-low", action="store_true", help="Exit 1 if any file below threshold")
    args = parser.parse_args(argv)

    mcp = _load_mcp()
    rows = []
    for raw in args.paths:
        path = Path(raw)
        files = list(path.rglob("*.md")) if path.is_dir() else [path]
        for f in sorted(files):
            parsed = mcp._parse_omi_file(f)
            row = {
                "path": str(f),
                "parsed": bool(parsed),
                "parser_confidence": parsed.get("parser_confidence") if parsed else None,
                "quality_warnings": parsed.get("quality_warnings") if parsed else [],
                "low_quality_excerpt": parsed.get("low_quality_excerpt") if parsed else None,
            }
            rows.append(row)
            if args.json:
                print(json.dumps(row, ensure_ascii=False))
            else:
                flag = "LOW" if row.get("low_quality_excerpt") else "ok"
                print(f"{flag:4} {row['parser_confidence']}  {f}")

    if args.warn_low and any(r.get("low_quality_excerpt") for r in rows if r["parsed"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())