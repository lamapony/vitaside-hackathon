# VitaSide Collaboration Protocol

Host agent (Hermes / Cursor) and sidecar MCP cooperate through tool calls and optional context handoff.

## Flow

```
Host                          Sidecar (MCP)
  |                                |
  |-- collaborative_insight() ---->|
  |<-- needs_context OR insight ---|
  |                                |
  |-- collaborative_insight(       |
  |     host_context={events}) --->|
  |<-- collaborative_insight ------|
```

## `needs_context` response (stub → production)

When the sidecar lacks calendar or life-event data, it may return a **request** instead of a full insight:

```json
{
  "needs_context": {
    "calendar": true,
    "reason": "Travel and deadline windows improve sleep/stress correlation accuracy"
  },
  "disclaimer": "..."
}
```

The host should gather context (calendar, task list, travel itinerary) and call `collaborative_insight` again with `host_context`.

## `host_context` shape

Pass as the MCP tool argument `host_context`:

```json
{
  "agent": "hermes-main",
  "events": [
    {"date": "2026-05-02", "type": "travel", "note": "Late flight return, landed 01:30"},
    {"date": "2026-05-16", "type": "deadline", "note": "Product launch crunch week"}
  ]
}
```

### Event fields

| Field  | Required | Values / notes                                      |
|--------|----------|-----------------------------------------------------|
| `date` | yes      | ISO date `YYYY-MM-DD`                               |
| `type` | yes      | `travel` \| `deadline` (extensible later)           |
| `note` | no       | Free text for host agent / user                     |

### Event types

- **`travel`** — flights, hotels, timezone changes, red-eyes. Sidecar checks ±2 days for poor sleep.
- **`deadline`** — crunch weeks, launches, exams. Sidecar checks ±3 days for stress signals.

Other types may be added; unknown types are ignored.

## Successful response

After context is supplied (or when demo `DEFAULT_HOST_CONTEXT` is used):

```json
{
  "main_agent_context": { "agent": "...", "events": [...] },
  "collaborative_insight": "N poor-sleep nights within ±2 days of travel ...",
  "evidence": {
    "poor_sleep_near_travel": [...],
    "stress_near_deadline": [...],
    "top_correlation": {...},
    "apple_summary": {...}
  },
  "confidence": 0.72,
  "disclaimer": "..."
}
```

## mcporter example

```bash
export VITASIDE_MANIFEST=./sidecars/sleep-stress-sidecar/manifest.yaml
export OMI_VAULT_PATH=./demo-data/vault

npx mcporter call --stdio "python3 health-pattern-mcp.py" collaborative_insight \
  --args '{"host_context":{"agent":"hermes","events":[{"date":"2026-05-02","type":"travel","note":"Red-eye"}]}}'
```

## Python simulation

```bash
python3 collaboration_demo.py
```

## Data source catalog

`list_data_sources` documents `host_context` as resource id `host_context`, consumed by `collaborative_insight`. See `data_sources.py`.

## Privacy

- Host passes only events the user approves; sidecar does not fetch calendar itself.
- Events are not persisted unless written to audit log metadata (event count only).
