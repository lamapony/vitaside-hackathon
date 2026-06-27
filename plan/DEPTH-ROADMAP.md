# VitaSide — Depth Roadmap (post-MVP)

> MVP закрыт (`docs/MVP-1.0.md`). Ниже — рост **вглубь**, не вширь.
> Правило: каждая фаза приносит пользу тебе или 2–3 реальным пользователям.

---

## Phase D1 — Real Data Loop (2–4 weeks)

**Goal:** Перестать жить только на demo vault.

- [ ] Подключить реальный Omi vault (`OMI_VAULT_PATH`)
- [ ] Импорт Apple Health export (Settings → Health → Export)
- [ ] Еженедельный ритуал: `./run-demo.sh` → прочитать отчёт → 1 инсайт в Obsidian
- [ ] Метрика: ≥2 полезных инсайта/неделю из **своих** данных

**Tech:**
- [x] Daily Omi↔Apple merge (`apple_merge.py`)
- [ ] SAX/iterparse для больших export.xml (>100MB)
- [ ] Obsidian note export из `generate_doctor_report`

---

## Phase D2 — Doctor Handoff (1–2 months)

**Goal:** Пациент → один файл → врач понимает за 3 минуты.

- [x] Doctor view HTML (`report_doctor.py`)
- [ ] PDF export (weasyprint или browser print)
- [ ] One-pager: «Questions to ask your doctor» auto-generated
- [ ] Anonymization mode (strip names from excerpts)

**Metric:** 1 врач посмотрел отчёт и сказал «удобнее сырых экспортов».

---

## Phase D3 — Sidecar Ecosystem (2–3 months)

**Goal:** Не один sidecar, а протокол.

- [x] Template: sleep-stress-sidecar
- [x] Template: recovery-sidecar
- [ ] Sidecar registry (`sidecars/registry.yaml`)
- [ ] Parallel sidecars (sleep + metabolic) без конфликта scopes
- [ ] Version pinning + revoke в manifest

---

## Phase D4 — Smarter Analysis (when data volume justifies)

**Only after D1 has 60+ real days.**

- [ ] Proper p-values on lag correlations (scipy)
- [ ] Personal baseline bands (not global thresholds)
- [ ] Seasonal / weekday effects
- [ ] Optional LLM layer for narrative (MCP sampling) — **always cite sources**

**Not now:** ML diagnosis, risk scores, government/regulatory path.

---

## Phase D5 — Agent Native (Hermes production)

- [ ] Live Hermes delegation (not script simulation)
- [ ] Sidecar requests context: `needs_context: {calendar}`
- [ ] Patient-controlled revoke from chat
- [ ] Push audit summary to user on sidecar expiry

---

## Architecture (target)

```
┌─────────────┐     manifest      ┌──────────────────┐
│   Doctor    │ ───────────────►  │  Sidecar Bundle  │
└─────────────┘                   │  manifest.yaml   │
                                  │  MCP server      │
┌─────────────┐    MCP stdio      └────────┬─────────┘
│   Hermes    │ ◄──────────────────────────┘
│  (host)     │   tools + collaborative_insight
└──────┬──────┘
       │ scoped read
       ▼
┌─────────────┐   merge    ┌─────────────┐
│  Omi vault  │ ◄───────► │ Apple daily │
└─────────────┘           └─────────────┘
       │
       ▼
 analyze → whatif → patient HTML + doctor view → audit.log
```

---

## Next 3 actions (this week)

1. `./setup.sh` + прогнать на **demo**, потом переключить `OMI_VAULT_PATH` на реальный vault
2. Экспортировать Apple Health → положить в `~/Downloads/apple_health_export/`
3. Отправить `out/vitaside-doctor-*.html` себе / одному врачу для feedback
