# Parser quality slice (VIT-47 / PP-05)

**Issue:** VIT-47  
**Depends:** VIT-42 ✅, G1 (VIT-29) ✅  
**Pain card:** `vault/01-Pain-Points/PP-05-noisy-subjective-logs.md`

## What shipped

| Piece | Path |
|-------|------|
| Confidence heuristics | `omi_parser_quality.py` |
| Parse + cite wiring | `health-pattern-mcp.py` (`_parse_omi_file`, `_cite_for_entry`, `_enrich_correlations`) |
| Insight gating copy | `actionable_insights.py` (`low_quality_evidence`, `high_confidence_insight`) |
| Timeline API + UI | `api_server.py` `/api/timeline`, `ui/src/pages/Timeline.tsx` |
| Messy note fixtures | `fixtures/omi_messy/*.md` |
| CLI assessor | `scripts/assess_parser_quality.py` |
| Tests | `tests/test_omi_parser_quality.py` |

## Thresholds

- `LOW_QUALITY_THRESHOLD` = **0.45** — UI warning + exploratory insight flag
- `HIGH_CONFIDENCE_INSIGHT_THRESHOLD` = **0.55** — correlation confidence after parser blend

Statistical correlation confidence is multiplied by parser provenance via `blend_statistical_confidence()`.

## VERIFY

```bash
cd code/health-mcp-starter
pytest tests/test_omi_parser_quality.py -q
pytest tests/ -q
python3 scripts/assess_parser_quality.py fixtures/omi_messy --warn-low
python3 scripts/assess_parser_quality.py demo-data/vault/050\ Daily\ Omi/Conversations/2026/03/2026-03-30.md
```

- Messy corpus: clean fixture scores higher than vague-yesterday fixture
- Demo 90-day vault: ≥3 parseable markdown files; sample day `parser_confidence` ≥ 0.5
- Citations include `parser_confidence` / `low_quality_excerpt`

## Operator notes

- Timeline shows **Parser confidence %** and PP-05 warning when `low_quality_excerpt`
- Briefing insights append exploratory warning when citation provenance is noisy
- No raw vault paths committed — fixtures are synthetic only