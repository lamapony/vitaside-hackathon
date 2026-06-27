# Hermes / MCP Integration Agent

## Role
Bridge VitaSide sidecar → real host agent (Hermes or Cursor MCP).

**Own:** `mcp-config.example.json`, `test-mcporter.sh`, `collaboration_demo.py`, docs for delegation

## Tasks

### P1 — mcporter green
- [ ] `./test-mcporter.sh` all tools including `smart_analysis`, `list_data_sources`
- [ ] Update timeouts for slow analysis

### P2 — Config generator
- [ ] Script: `write-mcp-config.sh` from issued sidecar manifest paths

### P3 — Collaboration protocol (D5 prep)
- [ ] Document `needs_context: {calendar}` response in `docs/SPEC.md`
- [ ] Extend `collaboration_demo.py` to show host filling context

## Verify
```bash
./issue-sidecar.sh sleep-stress-sidecar
./test-mcporter.sh
```

## Blockers
- Hermes prod access → stay on mcporter + Python simulation
