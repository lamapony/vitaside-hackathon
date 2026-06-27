# UI Dashboard Agent

> Full spec: `plan/UI-AGENT-PROMPT.md` — read it first.  
> **Own:** `code/health-mcp-starter/ui/**` only. Touch `api_server.py` only for missing routes (already complete).

## Current state 🟡
- 4 tabs exist: Dashboard, Timeline, Condition, DoctorHandoff
- `./serve-ui.sh` works
- **Missing for Wave 2:**

## Wave 1 — Finish acceptance (P0)
From `UI-AGENT-PROMPT.md` checklist — verify each, fix gaps:
- [ ] Evidence quote visible on insight cards
- [ ] Timeline ≥30 days + signal filter
- [ ] Sidecar expiry on Dashboard
- [ ] Doctor bundle export + link to `out/*.html`
- [ ] README "Local Dashboard" section

## Wave 2 — New tabs (P1)

### Tab: **Data Sources** (`pages/DataSources.tsx`)
- `GET /api/data-sources`
- Show `sources[]`: id, label_ru, status (chip: connected/demo_fallback/disabled)
- Expand: `setup_steps_ru`, `stats`, `provides`
- Summary strip: `summary.connected_sources` vs `needs_setup`

### Tab: **Smart** (`pages/Smart.tsx`) OR section on Dashboard
- `GET /api/smart` → `attention_now[]`, `weekday_effects[]`, `personal_baselines`
- `GET /api/narrative?locale=ru` → narrative block + evidence_map
- Highlight attention items with evidence_quote

### Optional: collapsible **How analysis works**
- `GET /api/analysis-mechanics` → pipeline steps 1–11

## API types
Extend `ui/src/api.ts` with DataSources, SmartAnalysis, Narrative types.

## Design
Teal tokens from `docs/index.html`. Status chips:
- connected = green, demo_fallback = amber, disabled = gray

## Verify
```bash
cd code/health-mcp-starter
./serve-ui.sh
cd ui && npm run build
python3 test_mvp.py  # must still pass — don't break backend
```

## Report to conductor
Screenshots description, unchecked acceptance items, API gaps.
