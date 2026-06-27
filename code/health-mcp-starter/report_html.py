"""Self-contained HTML timeline report for VitaSide."""
from __future__ import annotations

import datetime
import html
import json
from typing import Any, Dict, List


SIGNAL_COLORS = {
    "sleep": "#6366f1",
    "stress": "#ef4444",
    "mood_low": "#f97316",
    "mood_good": "#22c55e",
    "exercise": "#06b6d4",
    "caffeine_alcohol": "#a855f7",
    "symptom_pain": "#ec4899",
    "social": "#14b8a6",
}


def _esc(s: Any) -> str:
    return html.escape(str(s))


def _timeline_rows(entries: List[Dict[str, Any]], max_days: int = 60) -> str:
    by_date: Dict[str, Dict] = {}
    for e in entries:
        d = e.get("date")
        if d:
            by_date[d] = e
    dates = sorted(by_date.keys())[-max_days:]
    rows = []
    for d in dates:
        e = by_date[d]
        chips = "".join(
            f'<span class="chip" style="background:{SIGNAL_COLORS.get(s, "#64748b")}">{_esc(s)}</span>'
            for s in e.get("signals", [])
        )
        sq = e.get("sleep_quality", "unknown")
        sq_badge = f'<span class="sq sq-{sq}">{_esc(sq)} sleep</span>' if sq != "unknown" else ""
        excerpt = _esc(e.get("snippet", "")[:180])
        rows.append(
            f'<div class="day-row"><div class="day-date">{_esc(d)}</div>'
            f'<div class="day-body">{sq_badge}{chips}<p class="excerpt">{excerpt}</p></div></div>'
        )
    return "\n".join(rows) or "<p>No timeline data.</p>"


def _pattern_cards(correlations: List[Dict[str, Any]]) -> str:
    cards = []
    for c in correlations[:6]:
        cites = c.get("citations", [])
        cite_html = "".join(
            f'<blockquote><small>{_esc(x.get("date", ""))}</small> {_esc(x.get("excerpt", "")[:160])}</blockquote>'
            for x in cites[:2]
        )
        cards.append(
            f'<div class="card">'
            f'<h4>{_esc(c.get("cause"))} → {_esc(c.get("effect"))} <span class="lag">lag {_esc(c.get("lag"))}d</span></h4>'
            f'<p>lift <strong>{_esc(c.get("lift_ratio"))}</strong> · '
            f'confidence <strong>{_esc(c.get("confidence", "?"))}</strong></p>'
            f'{cite_html or "<p><em>No citations</em></p>"}'
            f'</div>'
        )
    return "\n".join(cards) or "<p>No strong correlations yet.</p>"


def generate_html_report(
    analysis: Dict[str, Any],
    apple: Dict[str, Any],
    entries: List[Dict[str, Any]],
    whatif: Dict[str, Any] | None = None,
    audit: Dict[str, Any] | None = None,
    disclaimer: str = "",
) -> str:
    today = datetime.date.today().isoformat()
    whatif = whatif or {}
    audit = audit or {}
    projected = whatif.get("projected_outcomes", [])
    whatif_html = "".join(
        f'<li><strong>{_esc(p.get("signal"))}</strong>: {_esc(p.get("change_percent"))}% '
        f'({_esc(p.get("direction"))})</li>'
        for p in projected
    ) or "<li>No projection run.</li>"

    audit_html = (
        f'<p>Audit entries: <strong>{audit.get("entries", 0)}</strong> · '
        f'Files touched: <strong>{audit.get("unique_files", 0)}</strong></p>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>VitaSide Report — {today}</title>
<style>
  :root {{ font-family: system-ui, -apple-system, sans-serif; color: #0f172a; background: #f8fafc; }}
  body {{ max-width: 960px; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 1.75rem; margin-bottom: 0.25rem; }}
  .sub {{ color: #64748b; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 24px; }}
  .stat {{ background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .stat b {{ display: block; font-size: 1.5rem; }}
  section {{ background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .day-row {{ display: flex; gap: 12px; border-bottom: 1px solid #e2e8f0; padding: 10px 0; }}
  .day-date {{ width: 100px; font-size: 0.85rem; color: #475569; flex-shrink: 0; }}
  .chip {{ display: inline-block; color: #fff; font-size: 0.7rem; padding: 2px 8px; border-radius: 999px; margin: 2px; }}
  .sq {{ font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; margin-right: 6px; }}
  .sq-poor {{ background: #fee2e2; color: #991b1b; }}
  .sq-good {{ background: #dcfce7; color: #166534; }}
  .excerpt {{ font-size: 0.85rem; color: #334155; margin: 6px 0 0; }}
  .card {{ border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
  .lag {{ color: #64748b; font-weight: normal; font-size: 0.85rem; }}
  blockquote {{ margin: 8px 0 0; padding-left: 12px; border-left: 3px solid #cbd5e1; font-size: 0.85rem; color: #475569; }}
  .disclaimer {{ background: #fffbeb; border: 1px solid #fde68a; padding: 12px; border-radius: 8px; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>VitaSide Health Pattern Report</h1>
<p class="sub">Generated {today} · Omi {analysis.get("files_scanned", 0)} files · Apple {apple.get("source", "?")}</p>

<div class="grid">
  <div class="stat"><b>{analysis.get("unique_dates", 0)}</b> days</div>
  <div class="stat"><b>{len(analysis.get("temporal_correlations", []))}</b> correlations</div>
  <div class="stat"><b>{whatif.get("confidence", "—")}</b> what-if conf.</div>
  <div class="stat"><b>{audit.get("entries", 0)}</b> audit events</div>
</div>

<section><h2>Timeline</h2>{_timeline_rows(entries)}</section>
<section><h2>Top Patterns</h2>{_pattern_cards(analysis.get("temporal_correlations", []))}</section>
<section><h2>What-If Projection</h2><ul>{whatif_html}</ul>
<p><small>{_esc(whatif.get("based_on", {}).get("method", ""))}</small></p></section>
<section><h2>Audit</h2>{audit_html}</section>
<section class="disclaimer"><strong>Disclaimer:</strong> {_esc(disclaimer)}</section>
</body>
</html>"""
