#!/usr/bin/env python3
"""Operator check: real OMI_VAULT_PATH + manifest scopes (VIT-42). Redacted stdout only."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sidecar_protocol import allowed_roots, check_scope, load_manifest  # noqa: E402


def _redact_path(p: Path) -> str:
    home = Path.home()
    try:
        rel = p.resolve().relative_to(home)
        return f"~/{rel}"
    except ValueError:
        return "<vault>"


def validate_scopes(manifest: dict, vault: Path) -> dict:
    roots = allowed_roots(manifest)
    scope_report = []
    md_in_scope = 0
    for root in roots:
        exists = root.is_dir()
        scope_report.append({"path_redacted": _redact_path(root), "exists": exists})
        if exists:
            for f in root.rglob("*.md"):
                if check_scope(manifest, f):
                    md_in_scope += 1
    return {
        "scope_dirs": scope_report,
        "scoped_markdown_count": md_in_scope,
        "manifest_name": manifest.get("name"),
        "manifest_loaded": manifest.get("_loaded"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="VIT-42 founder vault wiring check")
    parser.add_argument(
        "--packet",
        action="store_true",
        help="Also run build_visit_packet (offline; may write scoped visit note)",
    )
    args = parser.parse_args()

    explicit = os.environ.get("OMI_VAULT_PATH", "").strip()
    if not explicit:
        print("FAIL: set OMI_VAULT_PATH to your Obsidian vault root (not demo default)")
        return 1

    vault = Path(os.path.expanduser(explicit)).resolve()
    demo = (ROOT / "demo-data" / "vault").resolve()
    if vault == demo:
        print("FAIL: OMI_VAULT_PATH points at demo-data; use your real vault for founder wiring")
        return 1
    if not vault.is_dir():
        print(f"FAIL: vault directory missing ({_redact_path(vault)})")
        return 1

    manifest_path = os.environ.get("VITASIDE_MANIFEST", "")
    manifest = load_manifest(Path(manifest_path) if manifest_path else None)
    report = validate_scopes(manifest, vault)
    report["vault_redacted"] = _redact_path(vault)
    report["user_context_exists"] = (ROOT / "local-data" / "user_context.json").is_file()

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["scoped_markdown_count"] < 1:
        print("FAIL: 0 markdown files under manifest allowed_scopes")
        return 1

    if args.packet:
        os.environ.setdefault("VITASIDE_MANIFEST", manifest.get("_manifest_path", ""))
        import importlib.util

        spec = importlib.util.spec_from_file_location("hpmcp", ROOT / "health-pattern-mcp.py")
        if spec is None or spec.loader is None:
            print("FAIL: could not load health-pattern-mcp.py")
            return 1
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        pkt = mod.build_visit_packet(formats=["markdown"])
        summary = {
            "questions_count": pkt.get("questions_count"),
            "confidence": pkt.get("confidence"),
            "summary_chars": len(pkt.get("summary_md") or ""),
            "disclaimer_present": bool(pkt.get("disclaimer")),
        }
        print(json.dumps({"build_visit_packet": summary}, indent=2))

    print("OK: founder vault wiring check passed (redacted log above)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())