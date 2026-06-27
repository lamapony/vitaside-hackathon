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
    brief: Dict[str, Any] | None = None,
    clinical: Dict[str, Any] | None = None,
) -> str:
    today = datetime.date.today().isoformat()
    brief = brief or {}
    clinical = clinical or {}
    one_liner = clinical.get("headline") or brief.get("one_liner", "")
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

    problem_rows = "".join(f"<li>{_e(p)}</li>" for p in clinical.get("problem_list") or []) or "<li>Not entered in VitaSide context</li>"
    med_rows = "".join(f"<li>{_e(m)}</li>" for m in clinical.get("medications") or []) or "<li>None entered</li>"
    trend_rows = "".join(
        f"<tr><td>{_e(t.get('label'))}</td><td>{_e(t.get('recent_14d'))}</td>"
        f"<td>{_e(t.get('prior_14d'))}</td><td>{_e(t.get('delta'))}</td>"
        f"<td>{_e(t.get('direction'))}</td></tr>"
        for t in (clinical.get("trends") or [])
    )
    flag_rows = "".join(f"<li>{_e(f)}</li>" for f in clinical.get("flags_for_review") or [])
    q_rows = "".join(f"<li>{_e(q)}</li>" for q in clinical.get("visit_questions") or [])

    return f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"/>
<title>VitaSide Doctor View — {today}</title>
<style>
body{{font-family:Georgia,serif;max-width:720px;margin:40px auto;padding:0 20px;color:#1a1a1a}}
h1{{font-size:1.4rem;border-bottom:2px solid #2563eb;padding-bottom:8px}}
.meta{{color:#666;font-size:.9rem}}
.one-liner{{font-weight:600;color:#1e40af;margin:12px 0}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:.85rem}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#f1f5f9}}
.disclaimer{{background:#fef3c7;padding:12px;border-radius:6px;font-size:.85rem;margin-top:24px}}
@media print{{body{{margin:0}} .section{{break-inside:avoid}}}}
.section{{margin:24px 0}}
</style></head><body>
<h1>Patient Pattern Summary (Doctor View)</h1>
<p class="meta">Generated {today} · {analysis.get('unique_dates',0)} days analyzed · 
<strong>Not a diagnosis</strong></p>
{f'<p class="one-liner"><strong>Headline:</strong> {_e(one_liner)}</p>' if one_liner else ''}

<div class="section"><h2>Problem list &amp; medications (patient-entered)</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
<div><h3>Conditions</h3><ul>{problem_rows}</ul></div>
<div><h3>Medications</h3><ul>{med_rows}</ul></div>
</div></div>

<div class="section"><h2>14-day trends vs prior 14 days</h2>
<table><tr><th>Signal</th><th>Recent</th><th>Prior</th><th>Delta</th><th>Trend</th></tr>
{trend_rows or '<tr><td colspan="5">Need ≥28 days for period comparison</td></tr>'}
</table></div>

<div class="section"><h2>Key Cross-Day Patterns</h2>
<table><tr><th>Pattern</th><th>Lag</th><th>Lift</th><th>Conf.</th><th>Example note</th></tr>
{pattern_rows or '<tr><td colspan="5">No patterns</td></tr>'}
</table></div>

<div class="section"><h2>Omi + Wearable Alignment</h2><ul>{merge_rows}</ul>
<p class="meta">Overlap days: {merge.get('overlap_days', 0)}</p></div>

<div class="section"><h2>What-If (patient scenario)</h2><ul>{whatif_rows}</ul>
<p class="meta">Confidence: {whatif.get('confidence', '—')}</p></div>

{f'<div class="section"><h2>Flags for review</h2><ul>{flag_rows}</ul></div>' if flag_rows else ''}
{f'<div class="section"><h2>Suggested visit questions</h2><ul>{q_rows}</ul></div>' if q_rows else ''}

<div class="disclaimer">{_e(disclaimer)}</div>
</body></html>"""
