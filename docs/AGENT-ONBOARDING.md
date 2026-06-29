# VitaSide — подключение агента (MCP)

Инструкция для оператора, который хочет **подцепить своего агента** (Cursor, Hermes, Claude Desktop, любой MCP-хост) к VitaSide, или **дать ссылку** коллеге / врачу / другому разработчику.

---

## Две ссылки — два сценария

| Кому | Что отправить | Зачем |
|------|---------------|--------|
| **Врач / reviewer / демо без установки** | https://lamapony.github.io/vitaside-hackathon/ | Полный React-дашборд с sample data: timeline, doctor handoff, sidecar, citations |
| **Разработчик / agent operator** | Этот репозиторий + раздел «5 минут до MCP» ниже | Локальный MCP sidecar на **своих** данных |

GitHub Pages **не** даёт агенту доступ к MCP — только наглядный UI. Для агента нужен локальный (или self-hosted) stdio MCP сервер.

---

## 5 минут до MCP

```bash
git clone https://github.com/lamapony/vitaside-hackathon.git
cd vitaside-hackathon/code/health-mcp-starter
./install.sh                    # venv + demo vault + sidecar
source .venv/bin/activate
python test_mvp.py              # sanity check
```

Свои данные (Obsidian / Omi vault):

```bash
export OMI_VAULT_PATH="$HOME/Documents/Obsidian Vault"
./issue-sidecar.sh sleep-stress-sidecar
./write-mcp-config.sh sidecars/sleep-stress-sidecar/manifest.yaml mcp-config.local.json
```

Файл `mcp-config.local.json` — **gitignored**, пути только локальные.

---

## Cursor

1. **Settings → MCP** (или `.cursor/mcp.json` в проекте)
2. Вставить содержимое `mcp-config.local.json` в `mcpServers`
3. Перезапустить MCP / Cursor

Минимальный пример (замените пути):

```json
{
  "mcpServers": {
    "vitaside-sleep-stress-sidecar": {
      "command": "/path/to/vitaside-hackathon/code/health-mcp-starter/.venv/bin/python",
      "args": [
        "/path/to/vitaside-hackathon/code/health-mcp-starter/health-pattern-mcp.py"
      ],
      "env": {
        "VITASIDE_MANIFEST": "/path/to/.../sidecars/sleep-stress-sidecar/manifest.yaml",
        "OMI_VAULT_PATH": "/Users/YOU/Documents/Obsidian Vault"
      }
    }
  }
}
```

Проверка без UI:

```bash
npx mcporter list --stdio ".venv/bin/python health-pattern-mcp.py"
npx mcporter call --stdio ".venv/bin/python health-pattern-mcp.py" get_actionable_briefing
```

---

## Hermes

В `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  vitaside_health:
    command: /path/to/vitaside-hackathon/code/health-mcp-starter/.venv/bin/python
    args:
      - /path/to/vitaside-hackathon/code/health-mcp-starter/health-pattern-mcp.py
    env:
      VITASIDE_MANIFEST: /path/to/.../sidecars/sleep-stress-sidecar/manifest.yaml
      OMI_VAULT_PATH: /Users/YOU/Documents/Obsidian Vault
    timeout: 180
```

Инструменты в чате: `mcp_vitaside_health_*` (префикс зависит от имени сервера).

YAML для copy-paste: `./scripts/print-hermes-profile-yaml.sh sleep-stress-sidecar`

---

## Claude Desktop / другие MCP-хосты

Тот же JSON, что для Cursor — ключ `mcpServers`, transport **stdio**, один процесс Python на сервер.

---

## Второй сервер (optional): second-brain read

Read-only доступ к Obsidian + MemPalace — **отдельный** процесс:

```json
{
  "mcpServers": {
    "vitaside-second-brain": {
      "command": "python3",
      "args": ["/path/to/.../mcp-servers/vitaside-second-brain/server.py"],
      "env": {
        "OMI_VAULT_PATH": "/Users/YOU/Documents/Obsidian Vault",
        "VITASIDE_MANIFEST": "/path/to/.../sidecars/sleep-stress-sidecar/manifest.yaml"
      }
    }
  }
}
```

Tools: `obsidian_search`, `obsidian_read_note`, `mempalace_query`.  
Подробнее: `code/health-mcp-starter/mcp-servers/vitaside-second-brain/README.md`

---

## Sidecar manifest — что это и зачем агенту

Перед каждым чтением данных MCP проверяет **manifest** (YAML):

- **allowed_scopes** — какие папки vault можно читать
- **tools** — whitelist инструментов
- **ttl** — срок действия sidecar
- **audit.log** — метаданные доступа (без сырого текста заметок в логе по умолчанию)

Выдать / обновить:

```bash
./issue-sidecar.sh sleep-stress-sidecar      # sleep / stress / demo
./issue-sidecar.sh migraine-tracking-sidecar # condition pack
./issue-sidecar.sh azure-hybrid-sidecar      # optional Azure stub
./revoke-sidecar.sh sleep-stress-sidecar     # отзыв
```

Шаблон scope для «расшарить агенту только Omi»:

```yaml
allowed_scopes:
  - path: "/path/to/vault/050 Daily Omi"
    permissions: ["read"]
tools:
  - analyze_lifestyle_patterns
  - get_actionable_briefing
  - generate_doctor_report
  - list_data_sources
ttl: "30d"
```

Спека: `vault/04-Architecture/sidecar-manifest-standard.md`

---

## Что сказать агенту в промпте (copy-paste)

```text
You have VitaSide MCP tools for LOCAL lifestyle pattern analysis (not diagnosis).

Workflow:
1. list_data_sources — see what is connected (Omi vault, Apple Health, etc.)
2. get_actionable_briefing or analyze_lifestyle_patterns — patterns WITH citations
3. generate_doctor_report(format="doctor") — clinician-oriented summary
4. build_visit_packet — visit prep bundle

Rules:
- Always include disclaimer; never present as medical diagnosis
- Prefer tools over guessing; cite dated excerpts from tool output
- If collaborative_insight returns needs_context, pass host_context.events (travel/deadline) and retry
- For multi-source / device window: list_multi_sources, monitor_device_window

Demo without real vault: OMI_VAULT_PATH=.../demo-data/vault (bundled in repo).
```

---

## Host agent ↔ sidecar (контекст календаря)

Если sidecar просит контекст — см. `code/health-mcp-starter/docs/COLLABORATION.md`.

```json
{
  "host_context": {
    "agent": "my-agent",
    "events": [
      {"date": "2026-05-02", "type": "travel", "note": "Red-eye flight"},
      {"date": "2026-05-16", "type": "deadline", "note": "Launch week"}
    ]
  }
}
```

Tool: `collaborative_insight(host_context=...)`

---

## Шпаргалка инструментов (health-pattern-mcp)

| Tool | Когда вызывать |
|------|----------------|
| `health_check` | Liveness + sidecar TTL |
| `list_data_sources` | Что подключено, demo vs real |
| `get_actionable_briefing` | Top insights + citations для UI/чата |
| `analyze_lifestyle_patterns` | Полный анализ Omi + smart layer |
| `smart_analysis` | Baselines, correlations, weekday effects |
| `generate_doctor_report` | Markdown / HTML / doctor view |
| `build_visit_packet` | Visit prep + questions |
| `export_doctor_handoff_print` | Print-ready HTML с audit footer |
| `list_multi_sources` | Doctor device + wearables + Frame + notes lanes |
| `monitor_device_window` | Proactive monitoring during prescribed device window |
| `track_condition` / `condition_report` | migraine / bipolar packs |
| `collaborative_insight` | Host calendar + health merge |
| `get_sidecar_status` | Scopes, expiry, audit summary |

Полный список: `npx mcporter list --stdio "python health-pattern-mcp.py"`

---

## Локальный UI (опционально)

Агент работает через MCP; человек может смотреть тот же backend в браузере:

```bash
cd code/health-mcp-starter
./serve-ui.sh
# UI http://127.0.0.1:5173  API http://127.0.0.1:8787
```

---

## Что отправить в одном сообщении (шаблон)

**Врачу / reviewer:**

> Демо дашборда (без установки): https://lamapony.github.io/vitaside-hackathon/  
> В sidebar — «Demo tour». Doctor handoff → Print/PDF. Sample data, not your PHI.

**Agent operator:**

> Repo: https://github.com/lamapony/vitaside-hackathon  
> Onboarding: `docs/AGENT-ONBOARDING.md`  
> Quick: `cd code/health-mcp-starter && ./install.sh` → merge `mcp-config.local.json` into Cursor/Hermes MCP settings.

---

## Безопасность

- Не коммить `mcp-config.local.json`, реальные vault paths, `export.xml`, sidecar manifests с личными scope
- Sidecar **read-only** по design; TTL и revoke — `./revoke-sidecar.sh`
- Azure / skin photo / external — только с explicit `user_consent` в tool args
- **Not a medical device** — patterns for visit prep only

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Tool denied by manifest | `./issue-sidecar.sh ...` и добавь tool name в `tools:` |
| Sidecar expired | Re-issue sidecar or extend TTL |
| Empty analysis | Check `OMI_VAULT_PATH`, run `list_data_sources` |
| mcporter timeout | `--timeout 60000` or increase Hermes `timeout:` |
| Tests fail on clone | `python gen_demo_data.py` then `python test_mvp.py` |

Детали: [STATUS.md](../STATUS.md) · [RELEASE.md](../code/health-mcp-starter/docs/RELEASE.md)
