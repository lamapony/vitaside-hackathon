# Merge checklist — `vitaside/trunk-release` → `main`

**Issue:** VIT-59 (PR draft) · **Gate:** VIT-57 G2 (human) · **VERIFY:** VIT-58

Agents must **not** complete this checklist autonomously. CEO / Dima record G2 on Paperclip before merge.

---

## Before opening PR

- [ ] Compare branch is `vitaside/trunk-release` (includes VIT-41/45 beyond `vitaside/second-brain-read`)
- [ ] Working tree clean — no accidental UI/WIP unless explicitly in scope
- [ ] `git log main..vitaside/trunk-release --oneline` reviewed
- [ ] Push compare branch to `origin` if using GitHub

## VERIFY (attach logs to PR)

```bash
cd "$(git rev-parse --show-toplevel)"
source .venv/bin/activate
make ci
```

- [ ] pytest green (incl. sidecar, longitudinal, visit packet, second-brain)
- [ ] `test-mcporter.sh` — 17 passed
- [ ] `test-mcporter-expired.sh` — fail-closed PASS
- [ ] `python test_mvp.py` — ALL MVP CHECKS PASSED
- [ ] VIT-58 Paperclip issue marked `done` with same commands + timestamps

## Security / privacy

- [ ] No real `OMI_VAULT_PATH`, usernames, or PHI in committed files
- [ ] `mcp-config.local.json` and sidecar secrets remain gitignored
- [ ] Diff reviewed for hardcoded founder paths

## Documentation

- [ ] Vault PR draft: `VitaSide-Research/08-Planning/VIT-59-trunk-merge-pr-draft.md`
- [ ] BUILD rollup: `VitaSide-Research/08-Planning/build-ship-scorecard.md`
- [ ] Real-vault demo refs: VIT-53 transcript, VIT-57 stats + `08-Planning/VIT-57-hackathon-demo-script.sh`

## Human gates

- [ ] **G2 (VIT-57):** explicit trunk merge approval
- [ ] **G1 (VIT-29):** if policy requires SPEC assumptions before public `main` — confirm with CEO

## After merge (CEO)

- [ ] Optional annotated tag `0.2.0-productization` on merged SHA
- [ ] Record branch disposition in VIT-57 comment
- [ ] Retain or delete `vitaside/*` branches per CEO decision

---

Epic policy: `VitaSide-Research/08-Planning/implementation-epic-VIT-23.md` § Merge to `main`.