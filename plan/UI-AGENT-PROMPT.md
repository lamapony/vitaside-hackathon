# Agent Prompt: VitaSide Local Dashboard UI

Copy everything below the line into a new agent chat.

---

## Role

You are the **UI agent** for **VitaSide** — a local-first health pattern intelligence sidecar (hackathon project). Your job is to build a **local web dashboard** that makes existing backend value visible without replacing Hermes/MCP.

**Repo root:** workspace root (`vitaside-hackathon/`) — use relative paths, never hardcode user home directories.

**Backend (DO NOT rewrite):** `code/health-mcp-starter/`
- MCP server: `health-pattern-mcp.py`
- HTML reports (static): `report_html.py`, `report_doctor.py` → `out/vitaside-report-*.html`
- Condition packs: `condition_tracking.py`, `condition_packs/*.yaml`
- Azure contract (other agent): `azure_contract.py`, `azure_boost.py` — wire UI buttons only, do not implement Azure

**Landing page design reference:** `docs/index.html` (teal/mint palette, Inter, clean medical-adjacent — match this aesthetic)

---

## Do we need UI? Yes — but scoped

| Need UI for | Skip |
|-------------|------|
| Weekly briefing at a glance | Full patient portal / auth system |
| Timeline + citations (the moat vs ChatGPT) | Replacing Hermes chat |
| Condition pack view (migraine / bipolar) | Diagnosis UI, risk scores |
| Doctor handoff preview + export buttons | Storing health data in cloud |
| Sidecar status (TTL, audit summary) | Mobile native app |

**Principle:** UI is a **local viewer + action panel** on top of Python analysis. All raw data stays on disk; UI reads via a thin local API or pre-generated JSON.

---

## Architecture (required)

```
code/health-mcp-starter/
├── ui/                          # YOU CREATE
│   ├── package.json             # Vite + React (or vanilla if faster)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx    # top insights + vs-LLM
│   │   │   ├── Timeline.tsx     # signal chips by day
│   │   │   ├── Condition.tsx    # active condition pack
│   │   │   └── DoctorHandoff.tsx
│   │   └── components/
│   └── vite.config.ts           # proxy → API
├── api_server.py                # YOU CREATE — thin FastAPI wrapper
└── serve-ui.sh                  # YOU CREATE — one command demo
```

### `api_server.py` (FastAPI, port 8787)

Import functions from `health-pattern-mcp.py` via `importlib` (same pattern as `test_mvp.py` / `demo_briefing.py`). **Do not duplicate** parsing logic.

**Endpoints (minimum):**

| Method | Path | Maps to |
|--------|------|---------|
| GET | `/api/health` | `{ ok, version }` |
| GET | `/api/briefing` | `get_actionable_briefing()` |
| GET | `/api/timeline` | scan + entries by date (or extend briefing) |
| GET | `/api/condition/{id}` | `track_condition(id, 90)` |
| GET | `/api/condition-packs` | `list_condition_packs()` |
| GET | `/api/sidecar` | `get_sidecar_status()` |
| POST | `/api/export-bundle` | `export_visit_bundle()` → return file paths |
| GET | `/api/data-sources` | `list_data_sources()` — catalog + live connection status |
| GET | `/api/analysis-mechanics` | `get_analysis_mechanics()` — pipeline steps + tool→resource map |
| GET | `/api/narrative` | `get_local_narrative(locale)` |
| POST | `/api/azure/enhance` | `azure_enhance_insight(user_consent=True)` — show consent modal first |

Set env before import:
```python
os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data/vault"))
os.environ.setdefault("VITASIDE_MANIFEST", str(ROOT / "sidecars/sleep-stress-sidecar/manifest.yaml"))
```

CORS: allow `localhost:5173` (Vite dev).

### Data contract

UI consumes **JSON already shaped** by MCP tools. Example briefing insight:
```json
{
  "headline": "Sleep issues → Stress about 1 day(s) later",
  "detail": "...",
  "evidence_date": "2026-04-02",
  "evidence_quote": "Тревога и напряжение...",
  "action": "Track whether reducing sleep issues...",
  "why_not_llm": "Grounded in 90 files / 84 days..."
}
```

Render `evidence_quote` prominently — this is the product moat.

---

## Screens (MVP — 4 views, one app)

### 1. Dashboard (home)
- Hero: "Your patterns, not generic advice"
- Top 3 insights as cards: headline, detail, **dated citation block**
- Small "Why not ChatGPT?" strip from `why_not_llm`
- Quick stats: days analyzed, files scanned, sidecar name + expiry
- CTA: "Prepare doctor visit" → Doctor Handoff tab

### 2. Timeline
- Scrollable list by date (reuse visual language from `report_html.py` signal colors)
- Chips: sleep, stress, mood_low, etc.
- Excerpt per day (truncated)
- Optional: filter by signal

### 3. Condition (if pack active or picker)
- Dropdown: migraine | bipolar (from `list_condition_packs`)
- Track items with bar/frequency
- Metrics list + doctor_focus bullets
- Disclaimer footer (always visible)

### 4. Doctor Handoff
- Preview link to existing `out/vitaside-report-*.html` and doctor HTML (open in new tab)
- Button: "Generate bundle" → calls export API → shows paths + success
- List auto-generated visit questions (from `generate_visit_questions`)
- Toggle: anonymize (pass to export)
- **Placeholder** button: "Share with doctor (Azure)" — disabled with tooltip "Azure agent — coming soon" unless `get_azure_contract().azure_enabled`

---

## Design requirements

- Match `docs/index.html`: `--teal: #0f7c7c`, `--mint: #d7f1eb`, `--paper: #f7fbfa`
- Mobile-friendly (single column on narrow)
- Russian **and** English labels OK (demo data is Russian)
- Always show disclaimer: *"Patterns for self-awareness — not medical diagnosis"*
- No stock photos; typography + data viz only
- Accessibility: contrast, focus states, semantic headings

---

## Dev workflow

```bash
# Terminal 1 — API
cd code/health-mcp-starter
pip install fastapi uvicorn  # add to requirements-ui.txt or requirements.txt
python3 api_server.py      # :8787

# Terminal 2 — UI
cd code/health-mcp-starter/ui
npm install && npm run dev   # :5173, proxy /api → 8787

# One-command demo (you must create)
./serve-ui.sh                # starts both + opens browser
```

Demo data:
```bash
python3 gen_demo_data.py
OMI_VAULT_PATH=demo-data/vault ./issue-sidecar.sh sleep-stress-sidecar
```

---

## Integration rules

1. **Do not** commit secrets or call Azure without consent UI.
2. **Do not** modify `health-pattern-mcp.py` logic unless adding a tiny JSON helper is unavoidable — prefer `api_server.py`.
3. **Coordinate:** Azure share/enhance = button + consent modal only; live Azure is another agent's job.
4. **Coordinate:** Condition packs already exist — consume APIs, don't redefine YAML.
5. Add `requirements-ui.txt` or extend `requirements.txt` with `fastapi`, `uvicorn[standard]`.
6. Update `pitch/DEMO-SCRIPT.md` with one line: "Open `./serve-ui.sh` for dashboard demo".

---

## Acceptance criteria (must all pass)

- [ ] `./serve-ui.sh` opens dashboard with demo vault data
- [ ] Dashboard shows ≥1 insight with **visible date + quote**
- [ ] Timeline shows ≥30 days with signal chips
- [ ] Condition tab works for `migraine` and `bipolar`
- [ ] Doctor Handoff generates bundle and links to HTML in `out/`
- [ ] Sidecar expiry visible on Dashboard
- [ ] Works offline (no external CDN required for core demo — bundle assets)
- [ ] `python3 test_mvp.py` still passes (backend unchanged behavior)
- [ ] README section: "Local Dashboard" with 3-line quick start

---

## Out of scope (explicit)

- User login / multi-tenant
- Editing Omi notes from UI
- Real-time sync with Obsidian
- FHIR viewer
- Replacing terminal `./run-demo.sh` (keep both)

---

## Suggested stack

- **Frontend:** Vite + React + TypeScript (or Preact if speed-critical)
- **Styling:** CSS modules or Tailwind — match existing teal tokens
- **Charts (optional):** lightweight — CSS bars for weekly summary, no heavy chart lib unless needed
- **API:** FastAPI + uvicorn

If time-constrained: single-page **enhanced static** dashboard in `ui/index.html` + `api_server.py` is acceptable fallback, but prefer React for condition pack switching.

---

## First steps (order)

1. Read `demo_briefing.py`, `test_mvp.py`, `report_html.py`, `docs/index.html`
2. Create `api_server.py` with `/api/briefing` working
3. Scaffold Vite app, proxy, Dashboard with one insight card
4. Add Timeline, Condition, Doctor Handoff
5. `serve-ui.sh` + README + demo script note
6. Visual polish pass against `docs/index.html`

Report back with: screenshot description, `./serve-ui.sh` command, and any API gaps that required backend changes.
