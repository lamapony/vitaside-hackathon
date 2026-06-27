# Health Patterns MCP Server — v2 (Apple Health)

Подключается к Hermes как MCP сервер. Анализирует Omi записи + Apple Health данные.

## Быстрый старт (тест без Hermes)

```bash
# Посмотреть доступные инструменты (8 инструментов)
npx mcporter list --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py"

# Omi анализ
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" analyze_lifestyle_patterns --timeout 30000

# Apple Health (демо-данные если export.xml не найден)
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" load_apple_health_data --timeout 30000
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" analyze_apple_patterns --timeout 30000
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" combine_omi_and_apple --timeout 30000

# Полный отчёт
npx mcporter call --stdio "/opt/anaconda3/bin/python3 $(pwd)/health-pattern-mcp.py" generate_doctor_report --timeout 30000
```

## Подключение к Hermes (постоянно)

Добавь в `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  health_patterns:
    command: /opt/anaconda3/bin/python3
    args:
      - /Users/dmitriibabinov/Documents/Aviato/04-research/health-mcp-starter/health-pattern-mcp.py
    env:
      OMI_VAULT_PATH: "/Users/dmitriibabinov/Documents/Obsidian Vault"
    timeout: 180
```

Затем:
- `hermes` (или перезапуск gateway)
- Инструменты появятся как `mcp_health_patterns_*`

## Инструменты (8 total)

### Omi Tools (original)
| Инструмент | Описание |
|---|---|
| `analyze_lifestyle_patterns` | Анализ Omi записей: сигналы (sleep, stress, mood, symptoms, food) |
| `find_correlation` | Простая корреляция совпадений по датам |
| `generate_doctor_report` | Генерация отчёта для врача (Omi + Apple Health) |
| `list_data_sources` | Показывает что видит сервер |

### Apple Health Tools (NEW в v2)
| Инструмент | Описание |
|---|---|
| `load_apple_health_data` | Загружает export.xml или демо-данные |
| `analyze_apple_patterns` | Корреляции HRV, sleep, steps, SpO2, trends |
| `combine_omi_and_apple` | Объединение Omi + Apple по датам |

## Apple Health Export

### Как получить export.xml
1. iPhone: Настройки > Приватность > Здоровье > Экспорт данных здоровья
2. Скопируй папку `apple_health_export` в одно из:
   - `~/Documents/Obsidian Vault/Apple Health/`
   - `~/Downloads/apple_health_export/`
   - `~/Desktop/apple_health_export/`
   - `~/Documents/apple_health_export/`

### Что парсится из export.xml

**Количественные метрики (HKQuantityTypeIdentifier*):**
- heart_rate, resting_heart_rate, walking_heart_rate
- hrv_sdnn (вариабельность пульса)
- steps, distance, flights_climbed
- exercise_minutes, active_energy, basal_energy
- blood_pressure (systolic/diastolic)
- spo2 (сатурация)
- weight, bmi, body_fat, lean_body_mass
- respiratory_rate
- sleep (3 стадии: core/deep/REM)
- audio exposure (environmental/headphone)

**Симптомы (HKCategoryTypeIdentifier*): 40+ типов**
- headache, fatigue, back_pain, dizziness, nausea
- mood_changes, sleep_changes, appetite_changes
- chest_pain, shortness_of_breath, palpitations
- и другие

**Activity Summaries:** кольца активности (Move/Exercise/Stand)

**Clinical Records:** аллергии, прививки, результаты (metadata)

Парсинг безопасен: только scoped paths, без сети.

### Если export.xml нет
По умолчанию `use_demo_if_missing=True` — возвращает репрезентативные демо-данные на 30 дней с реалистичными распределениями (HR 72±8, sleep 7±1.2ч, steps 3000-15000).

## Дорожная карта

Текущий статус: **Phase 1 — Apple Health завершён**

См. ROADMAP.md для полной карты.

## Архитектура

```
health-pattern-mcp.py
├── Omi Parser (_parse_omi_file)
│   └── Сигналы: sleep, stress, mood, symptom, food
├── Apple Health Parser (_parse_apple_health_xml)
│   ├── Records (HKQuantityTypeIdentifier*)
│   ├── Activity Summaries
│   ├── Clinical Records
│   └── Demo data generator
├── MCP Tools (8)
│   ├── analyze_lifestyle_patterns, find_correlation
│   ├── load_apple_health_data, analyze_apple_patterns
│   ├── combine_omi_and_apple
│   ├── generate_doctor_report
│   └── list_data_sources
└── Безопасность: _is_safe_path (scoped paths only)
```

**Не медицинский инструмент.** Только паттерны для врача.
