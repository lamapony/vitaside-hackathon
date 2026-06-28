"""Visit markdown → print-optimized HTML with mandatory audit footer (VIT-43)."""
from __future__ import annotations

import datetime
import html
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _esc(s: Any) -> str:
    return html.escape(str(s))


def _markdown_to_body_html(md: str) -> str:
    """Minimal markdown → HTML for visit notes (headings, lists, bold)."""
    lines = md.splitlines()
    out: List[str] = []
    in_ul = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            continue
        if stripped.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h3>{_esc(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2>{_esc(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h1>{_esc(stripped[2:])}</h1>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            text = stripped[2:]
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
            out.append(f"<li>{_esc(text) if '<strong>' not in text else text}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            out.append(f"<p>{_esc(text) if '<strong>' not in text else text}</p>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out) or "<p><em>Empty visit note</em></p>"


def render_audit_footer(
    *,
    disclaimer: str,
    confidence: float,
    data_scopes: List[str],
    audit_summary: Dict[str, Any],
    entity_id: str = "",
    generated_at: Optional[str] = None,
) -> str:
    generated_at = generated_at or datetime.date.today().isoformat()
    events = audit_summary.get("recent_events") or audit_summary.get("events") or []
    event_lines = ""
    if isinstance(events, list) and events:
        event_lines = "<ul>" + "".join(
            f"<li><code>{_esc(e.get('tool', e.get('event', '?')))}</code></li>"
            for e in events[:5]
            if isinstance(e, dict)
        ) + "</ul>"
    else:
        event_lines = (
            f"<p>Audit entries: <strong>{_esc(audit_summary.get('entries', 0))}</strong> · "
            f"Files touched: <strong>{_esc(audit_summary.get('unique_files', 0))}</strong></p>"
        )
    scope_list = "".join(f"<li>{_esc(s)}</li>" for s in data_scopes) or "<li>manifest allowed_scopes</li>"
    return f"""
<footer class="handoff-footer" id="vitaside-audit-footer">
  <h2>Data scope &amp; provenance</h2>
  <ul class="scope-list">{scope_list}</ul>
  <p>Packet confidence: <strong>{_esc(round(confidence, 2))}</strong>
     · Entity: <code>{_esc(entity_id or 'n/a')}</code>
     · Generated: {_esc(generated_at)}</p>
  <h3>Audit summary (local)</h3>
  {event_lines}
  <div class="disclaimer">{_esc(disclaimer)}</div>
</footer>
"""


def wrap_print_html(
    body_html: str,
    footer_html: str,
    title: str = "VitaSide Doctor Handoff",
) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{_esc(title)}</title>
<style>
body {{ font-family: Georgia, serif; max-width: 720px; margin: 24px auto; padding: 0 16px; color: #111; }}
h1 {{ font-size: 1.35rem; border-bottom: 2px solid #2563eb; padding-bottom: 6px; }}
.handoff-footer {{ margin-top: 32px; padding-top: 16px; border-top: 2px solid #cbd5e1; font-size: 0.85rem; }}
.handoff-footer .disclaimer {{ background: #fef3c7; padding: 12px; border-radius: 6px; margin-top: 12px; }}
.scope-list {{ margin: 8px 0; }}
@media print {{
  body {{ margin: 0; max-width: none; }}
  .handoff-footer {{ break-inside: avoid; page-break-inside: avoid; }}
  h2, h3 {{ break-after: avoid; }}
}}
</style>
</head>
<body>
<main class="handoff-body">
{body_html}
</main>
{footer_html}
</body>
</html>"""


def export_print_bundle_from_markdown(
    visit_md: str,
    *,
    disclaimer: str,
    confidence: float,
    data_scopes: List[str],
    audit_summary: Dict[str, Any],
    entity_id: str = "",
    out_dir: Path,
    basename: str = "doctor-handoff-print",
) -> Dict[str, Any]:
    """Write print HTML from visit markdown; returns paths + footer fingerprint."""
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    body = _markdown_to_body_html(visit_md)
    footer = render_audit_footer(
        disclaimer=disclaimer,
        confidence=confidence,
        data_scopes=data_scopes,
        audit_summary=audit_summary,
        entity_id=entity_id,
        generated_at=today,
    )
    full = wrap_print_html(body, footer, title=f"VitaSide Doctor Handoff — {today}")
    out_path = out_dir / f"{basename}-{today}.html"
    out_path.write_text(full, encoding="utf-8")
    return {
        "print_html": str(out_path),
        "footer_marker": "vitaside-audit-footer",
        "confidence": confidence,
        "entity_id": entity_id,
    }