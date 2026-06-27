"""Doctor-facing report view — highlights only, no raw dump."""
from __future__ import annotations

import datetime
import html
from typing import Any, Dict, List


def _e(s: Any) -> str:
    return html.escape(str(s))


def generate_doctor_view(
    analysis: Dict[str, Any],
    merge: Dict[str, Any],
    whatif: Dict[str, Any],
    disclaimer: str,
) -> str:
    today = datetime.date.today().isoformat()
    patterns = analysis.get("temporal_correlations", [])[:4]
    pattern_rows = "".join(
        f"<tr><td>{_e(c.get('cause'))}→{_e(c.get('effect'))}</td>"
        f"<td>{_e(c.get('lag'))}d</td><td>{_e(c.get('lift_ratio'))}</td>"
        f"<td>{_e(c.get('confidence'))}</td>"
        f"<td><small>{_e((c.get('citations') or [{}])[0].get('excerpt', '')[:100])}</small></td></tr>"
        for c in patterns
    )
    merge_rows = "".join(
        f"<li><strong>{_e(i.get('pattern'))}</strong>: {_e(i.get('description'))} ({_e(i.get('count'))} days)</li>"
        for i in merge.get("merged_insights", [])
    ) or "<li>No Omi↔Apple overlap insights yet.</li>"
    whatif_rows = "".join(
        f"<li>{_e(p.get('signal'))}: {_e(p.get('change_percent'))}% {_e(p.get('direction'))}</li>"
        for p in whatif.get("projected_outcomes", [])
    ) or "<li>Run what-if simulation for projections.</li>"

    return f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"/>
<title>VitaSide Doctor View — {today}</title>
<style>
body{{font-family:Georgia,serif;max-width:720px;margin:40px auto;padding:0 20px;color:#1a1a1a}}
h1{{font-size:1.4rem;border-bottom:2px solid #2563eb;padding-bottom:8px}}
.meta{{color:#666;font-size:.9rem}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:.85rem}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#f1f5f9}}
.disclaimer{{background:#fef3c7;padding:12px;border-radius:6px;font-size:.85rem;margin-top:24px}}
@media print{{body{{margin:0}} .section{{break-inside:avoid}}}}
.section{{margin:24px 0}}
</style></head><body>
<h1>Patient Pattern Summary (Doctor View)</h1>
<p class="meta">Generated {today} · {analysis.get('unique_dates',0)} days · 
<strong>Not a diagnosis</strong> — patterns for visit discussion</p>

<div class="section"><h2>Key Cross-Day Patterns</h2>
<table><tr><th>Pattern</th><th>Lag</th><th>Lift</th><th>Conf.</th><th>Example note</th></tr>
{pattern_rows or '<tr><td colspan="5">No patterns</td></tr>'}
</table></div>

<div class="section"><h2>Omi + Wearable Alignment</h2><ul>{merge_rows}</ul>
<p class="meta">Overlap days: {merge.get('overlap_days', 0)}</p></div>

<div class="section"><h2>What-If (patient scenario)</h2><ul>{whatif_rows}</ul>
<p class="meta">Confidence: {whatif.get('confidence', '—')}</p></div>

<div class="disclaimer">{_e(disclaimer)}</div>
</body></html>"""
