# QA / Hardening Agent

## Role
Prove the demo won't break on stage. Fix **tests and scripts**, not product logic (unless bug).

## Verify matrix

| Check | Command | Pass criteria |
|-------|---------|---------------|
| MVP | `python3 test_mvp.py` | ALL PASSED |
| Demo full | `./run-demo-full.sh --hardening` | 3/3 |
| Demo quick | `./run-demo.sh` | no errors |
| UI build | `cd ui && npm run build` | dist/ |
| UI serve | `./serve-ui.sh` (30s) | dashboard loads |
| Scope | grep audit.log | scoped reads logged |
| mcporter | `./test-mcporter.sh` | optional if npx ok |

## Deliverable
Create/update `plan/QA-REPORT.md`:
- Pass/fail table
- Gaps vs `plan/UI-AGENT-PROMPT.md` acceptance
- P0 bugs for conductor to assign

## Allowed fixes
- Test assertions
- `run-demo-full.sh` flakiness
- Missing deps in `requirements.txt`

## Not allowed without conductor
- Refactor `health-pattern-mcp.py`
- Change API response shapes

## Report format
```
## QA Run YYYY-MM-DD
### Passed (N)
### Failed (N) — owner lane
### Recommended Wave 2 assignments
```
