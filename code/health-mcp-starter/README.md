# Health Patterns MCP Server — v2 (Apple Health)

MCP server for Hermes (or Cursor). Analyzes Omi notes + Apple Health data locally.

## Quick start (without Hermes)

```bash
# List available tools
npx mcporter list --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py"

# Omi analysis
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" analyze_lifestyle_patterns --timeout 30000

# Apple Health (demo data if export.xml is missing)
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" load_apple_health_data --timeout 30000
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" analyze_apple_patterns --timeout 30000
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" combine_omi_and_apple --timeout 30000

# Full doctor report
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" generate_doctor_report --timeout 30000
```

## Local Dashboard UI

```bash
./setup.sh          # creates .venv and installs requirements
./serve-ui.sh       # uses .venv/bin/python when present
```

Opens the local dashboard at `http://127.0.0.1:5173`: top insights with citations,
manual profile/context, timeline, condition packs (`migraine` / `bipolar`), and
doctor handoff. API runs locally on `http://127.0.0.1:8787`; raw Omi/Apple data
is never sent to the network.

Manual context is stored locally in `local-data/user_context.json`:
- profile and current focus goal;
- conditions you want to track;
- medications and schedule;
- quick logs like “headache 7/10, took ibuprofen”.

**Auto-fill:** the *My context* tab suggests meds/conditions/goals from Omi notes.
*Apply to empty fields* fills blanks only; manual edits are tagged `manual` and are not overwritten.

**Home:** the main tab shows *Focus this week* — concrete next steps.

`Generate bundle` also writes `out/vitaside-user-context-*.md` for your visit.

## Hermes (persistent)

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  health_patterns:
    command: /opt/anaconda3/bin/python3
    args:
      - /path/to/vitaside-hackathon/code/health-mcp-starter/health-pattern-mcp.py
    env:
      OMI_VAULT_PATH: "/Users/YOUR_USERNAME/Documents/Obsidian Vault"
    timeout: 180
```

Then restart Hermes — tools appear as `mcp_health_patterns_*`.

## Tools

### Omi
| Tool | Description |
|---|---|
| `analyze_lifestyle_patterns` | Parse Omi notes: sleep, stress, mood, symptoms |
| `find_correlation` | Date-aligned signal co-occurrence |
| `generate_doctor_report` | Doctor handoff report (Omi + Apple) |
| `list_data_sources` | What the server can see |
| `get_clinical_summary` | One-page clinical summary |
| `run_n1_compare` | N-of-1 exposure vs control days |
| `export_fhir_bundle` | PGHD FHIR bundle (binned) |

### Apple Health
| Tool | Description |
|---|---|
| `load_apple_health_data` | Load export.xml or demo data |
| `analyze_apple_patterns` | HRV, sleep, steps, SpO2 trends |
| `combine_omi_and_apple` | Merge Omi + Apple by date |

## Apple Health export

1. iPhone: Settings → Privacy → Health → Export All Health Data
2. Copy `apple_health_export` to one of:
   - `~/Documents/Obsidian Vault/Apple Health/`
   - `~/Downloads/apple_health_export/`
   - `~/Desktop/apple_health_export/`
   - `~/Documents/apple_health_export/`

### Parsed from export.xml

**Quantitative (HKQuantityTypeIdentifier*):** heart rate, HRV, steps, sleep stages, SpO2, and more.

**Symptoms (HKCategoryTypeIdentifier*):** 40+ types including headache, fatigue, mood changes.

**Activity summaries:** Move / Exercise / Stand rings.

**Clinical records:** allergies, immunizations (metadata).

Parsing is scoped-path only — no network.

### No export.xml?

Demo mode returns ~30 days of representative sample data (HR ~72±8, sleep ~7±1.2h, steps 3k–15k).

## Roadmap

See `ROADMAP.md` for the full map.

## Architecture

```
health-pattern-mcp.py
├── Omi parser → signals: sleep, stress, mood, symptom, …
├── Apple Health parser → export.xml + demo generator
├── Scientific layer → correlations, baselines, N-of-1, FHIR
├── MCP tools + sidecar manifest (scoped read, audit, TTL)
└── api_server.py → local dashboard UI
```

**Not a medical device.** Patterns for self-awareness and visit prep only.

## Multi-Source Data Collection

Supports data beyond Omi:
- Obsidian notes / codebase-memory indexed hits
- Hermes / agent conversations (proactive lane during device window)
- Wearables (Apple Health export.xml)
- **Doctor-prescribed physical device** (temporary collection window)
- **Frame glasses** (vision lifestyle capture via `frame/` + `~/vitaside/data/`)

See `multi_source_collector.py` for normalization to `HealthEvent` with citations.

Proactive mode: agent calls `monitor_device_window` during the doctor's device period.

## Frame Glasses Integration

Hardware capture lives in repo root `frame/` (BLE via frame-sdk). Events land in `~/vitaside/data/lifestyle_events.jsonl` or repo `data/` for demo. The dashboard shows a Frame panel via `/api/frame-glasses`.
