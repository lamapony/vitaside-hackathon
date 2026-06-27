# VitaSide — Rocket Plan (Gap-Driven Execution)

> Принцип: бьём строго по разрыву между обещаниями питча/демо и реальным кодом.
> Каждый спринт = демонстрируемый wow + acceptance criteria. Ничего «на будущее».

**North Star демо (что должно произойти на сцене за 6–8 минут):**
`issue → load → ask → analyze (с цитатами) → what-if → beautiful HTML timeline → export → audit`

**Позиционные рельсы (неизменны):** personal pattern intelligence для самонаблюдения и
подготовки к разговору с врачом. Никаких «диагнозов / сигналов риска». Дисклеймер везде.
Регуляторный риск адресуем открыто на слайде (turns weakness into trust).

---

## Состояние кода (база для плана)

| Компонент | Статус | Действие |
|---|---|---|
| Omi parser (контекст, спикеры, quality) | ✅ работает | оставить, добавить извлечение цитат |
| Apple Health XML | ⚠️ базовый (лимит 5000) | докрутить merge по датам |
| Temporal correlations + lift | ✅ работает | добавить confidence + цитаты |
| Anomalies / baseline | ⚠️ примитив | оставить для демо, не углублять |
| HTML report | ❌ заглушка (JSON dump) | **построить настоящий timeline** |
| `simulate_whatif` | ❌ нет | **написать (главный wow)** |
| Sidecar manifest + loader | ❌ нет | написать |
| `issue-sidecar.sh` | ❌ нет | написать |
| Audit log | ❌ нет | написать |
| Collaboration demo | ❌ нет | написать скрипт |
| Quality gates (confidence/cite/disclaimer) | ⚠️ частично | вшить во все tool-выводы |
| git | ❌ нет | `git init` сейчас |

---

## Критический путь (порядок = зависимости + wow/час)

### Sprint 0 — Foundation (30–45 мин)
- [ ] `git init`, `.gitignore` (`__pycache__`, `*.pyc`, экспорты данных), первый коммит
- [ ] `requirements.txt` (mcp, pandas, numpy, scipy) + `README` quick-start для судей
- [ ] Smoke-test: `python health-pattern-mcp.py --test` зелёный
- **Acceptance:** чистый репозиторий, сервер стартует, тест проходит.

### Sprint 1 — `simulate_whatif` (главный wow) (3–4 ч)
- [ ] Новый MCP-tool `simulate_whatif(scenario: dict)`
- [ ] Модель: историческое сравнение «похожих периодов» + дельты по сигналам
      (не ML — простая, объяснимая статистика на реальных данных)
- [ ] Выход: `projected_outcomes`, `based_on` (сколько похожих периодов), `confidence`, дисклеймер
- [ ] Пример сценария из демо: «сон 7.5ч 2 недели» → «−28% low-mood сигналов, ...»
- **Acceptance:** на реальном Omi-волте отдаёт осмысленный прогноз с confidence и обоснованием.

### Sprint 2 — Quality Gates + цитаты (2 ч)
- [ ] Парсер возвращает точные цитаты-excerpts с датами (не только `example_dates`)
- [ ] Каждый инсайт корреляции/аномалии: `confidence: 0–1` + 1–2 реальные цитаты
- [ ] Глобальный дисклеймер в каждом tool-выводе
- **Acceptance:** ни один инсайт без источника, confidence и дисклеймера (anti-hallucination).

### Sprint 3 — Beautiful HTML Timeline (3 ч) — визуальный гвоздь
- [ ] Настоящий HTML-отчёт: timeline-бары (сон/активность/настроение), аннотации событий Omi
- [ ] Топ-паттерны с цитатами и датами, what-if блок, audit-сводка
- [ ] Самодостаточный файл (inline CSS/JS, открывается в браузере одним кликом)
- **Acceptance:** `generate_doctor_report(format="html")` рендерит живой timeline, не JSON-дамп.

### Sprint 4 — Protocol + Issuance + Audit (2–3 ч)
- [ ] `manifest.yaml` (name, scopes, tools, ttl, issuer) + загрузчик со scope-enforcement
- [ ] `issue-sidecar.sh <name>` → генерит манифест + бандл, печатает «одну строку для конфига»
- [ ] `audit.log`: каждый доступ к файлам/данным логируется (timestamp, path, tool)
- [ ] TTL-проверка (sidecar «истекает»)
- **Acceptance:** `./issue-sidecar.sh sleep-stress` создаёт рабочий sidecar; audit.log заполняется.

### Sprint 5 — Collaboration Demo (1.5–2 ч)
- [ ] Python-скрипт: «main-агент знает контекст (поездки из заметок), sidecar — биометрию»,
      показываем объединённый инсайт, который ни один не даёт в одиночку
- [ ] Реальный merge Omi↔Apple по датам (заменить заглушку `combine_omi_and_apple`)
- **Acceptance:** скрипт выдаёт combined insight на реальных данных.

### Sprint 6 — Demo Hardening & Pitch (2–3 ч)
- [ ] `run-demo.sh` — one-command end-to-end (issue → analyze → whatif → html → export)
- [ ] Прогон демо 3× на реальных данных, замер времени (анализ < 30с)
- [ ] Слайды + обновить `pitch/DEMO-SCRIPT.md` под финальный флоу
- [ ] Backup: pre-recorded видео + скриншоты
- **Acceptance:** демо проходит end-to-end без ошибок 3 раза подряд.

---

## Таймлайн (48-часовой хакатон)

| Блок | Часы | Спринты |
|---|---|---|
| Старт | 0–1 | Sprint 0 |
| Ядро wow | 1–8 | Sprint 1, 2 |
| Визуал | 8–12 | Sprint 3 |
| Протокол | 12–16 | Sprint 4 |
| Коллаборация | 16–19 | Sprint 5 |
| Полировка/демо | 19–24 | Sprint 6 |
| Буфер/stretch | 24–48 | см. ниже |

## Приоритеты, если время горит
1. `simulate_whatif` (Sprint 1) — без него нет wow
2. HTML timeline (Sprint 3) — визуальная победа
3. Quality gates + цитаты (Sprint 2) — доверие
4. Issuance + audit (Sprint 4) — новизна протокола
> Коллаборацию (5) можно показать скриптом, не живым агентом, если поджимает.

## Риски и митигации
- **Шум данных → ложные корреляции:** показываем confidence + реальные цитаты, честно про «medium confidence».
- **Регуляторика:** слайд «почему это НЕ медизделие» — снимаем возражение до того, как его задали.
- **Живой агент упадёт:** backup-видео + скриптовая коллаборация.
- **Scope creep:** заморозка фич после Sprint 4; всё остальное — stretch.

## Stretch (только если ядро готово)
- Несколько типов sidecar параллельно
- Веб «doctor view»
- Живой Omi-сниппет голосом

## Что НЕ делаем
- Не углубляем аномалии/ML — демо это не оценит.
- Не добавляем новые источники данных.
- Не строим дашборды, пока HTML-отчёт не полезен.
- Не делаем медицинских claim'ов.

---
**Правило скорости:** каждый спринт заканчивается demoable-артефактом и коммитом.
Если слайс не виден на сцене — он ждёт stretch-фазы.
