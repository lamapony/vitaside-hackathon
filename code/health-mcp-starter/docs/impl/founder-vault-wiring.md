# Founder vault wiring (VIT-42)

**Issue:** VIT-42  
**Assignee:** Integration Engineer  
**Depends:** G3 (human `OMI_VAULT_PATH`), VIT-41 ✅  
**Policy:** G1 (VIT-29) ✅ — Paperclip closed VIT-42 after operator evidence + pytest.

## What this slice adds

| Piece | Path |
|-------|------|
| Env resolver | `scripts/vitaside_paths.sh`, `install.sh` |
| Manual context template | `docs/templates/user_context.example.json` |
| Local init (no PHI import) | `scripts/init_founder_context.sh` → `local-data/user_context.json` |
| Operator verify | `scripts/verify_founder_vault.py` |
| Checklist (vault) | `VitaSide-Research/05-Second-Brain/Operator-Checklist-Founder-Vault.md` |

Real Omi notes are **never** copied into git. `local-data/` stays gitignored.

## Operator flow (Dima machine)

```bash
cd code/health-mcp-starter
export OMI_VAULT_PATH="$HOME/Documents/<Your-Obsidian-Vault>"
./install.sh sleep-stress-sidecar    # re-issue manifest with resolved scopes
./scripts/init_founder_context.sh
./scripts/verify_founder_vault.py
./scripts/verify_founder_vault.py --packet   # optional: build_visit_packet smoke
```

Save **redacted** JSON from `verify_founder_vault.py` into the vault checklist (no file paths with patient text).

## Indexer verify (VIT-48, optional full-vault)

With real `OMI_VAULT_PATH` exported:

```bash
codebase-memory-mcp cli index_repository "{\"repo_path\":\"$OMI_VAULT_PATH\",\"project_name\":\"vitaside-founder-vault\"}"
PROJ="Users-dmitriibabinov-Library-CloudStorage-GoogleDrive-spbabinov-gmail.com-Obsidian-Backup-01-Personal-Obsidian-Vault"
codebase-memory-mcp cli index_status "{\"project\":\"$PROJ\"}"
```

Evidence template: `VitaSide-Research/08-Planning/VIT-48-integration-evidence.md`. Hackathon demo may use scoped sidecar reads while showing index `ready` proof (`VIT-57-indexed-vault-stats.md`).

## VERIFY (acceptance)

- [x] `OMI_VAULT_PATH` is explicit and not `demo-data/vault`
- [x] Manifest `allowed_scopes` directories exist under vault
- [x] `scoped_markdown_count` ≥ 1
- [x] `build_visit_packet` succeeds with `--packet` (offline)
- [x] `pytest tests/` still uses fixtures only (21 tests green)

_Close in Paperclip after **G1** (VIT-29) per phase-2 §2; operator evidence in vault checklist._

## pytest

```bash
pytest tests/test_founder_vault.py -q
pytest tests/ -q
```