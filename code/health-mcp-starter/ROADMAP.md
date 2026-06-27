# VitaCo Health MCP — ROADMAP

## Статус: Phase 1 Complete ✅

### Phase 0 — MVP (Omi Only) ✅
- [x] База: MCP сервер на FastMCP
- [x] Парсинг Omi .md файлов (фронтматтер + текст)
- [x] Сигналы: sleep, stress, mood_low, mood_good, symptom, food
- [x] Co-occurrence анализ по датам
- [x] generate_doctor_report
- [x] list_data_sources
- [x] _is_safe_path безопасность

### Phase 1 — Apple Health Integration ✅ (COMPLETED 2026-06-27)
- [x] **Parser:** Apple Health export.xml (XML/ETree stream-parse)
- [x] **Metrics parsed:** heart_rate (incl resting/walking), hrv_sdnn, steps, distance, flights, exercise_minutes, energy (basal/active), blood_pressure (sys/dia), spo2, weight, bmi, body_fat, respiratory_rate, sleep (core/deep/REM), audio exposure
- [x] **Symptoms parsed:** 40+ types (headache, fatigue, back_pain, dizziness, nausea, mood_changes, etc.)
- [x] **Activity Summaries:** Move/Exercise/Stand rings
- [x] **Clinical Records:** metadata (allergies, immunizations, results)
- [x] **Demo data generator:** 30 days realistic distributions
- [x] **Tool: `load_apple_health_data`** — загрузка export.xml или демо
- [x] **Tool: `analyze_apple_patterns`** — корреляции:
  - HR + HRV тренды и интерпретация
  - Sleep duration patterns + anomalies (<6h)
  - Steps/activity + low activity days
  - SpO2 averages + low readings
  - Cross-correlation: sleep → next-day HRV
  - Blood pressure averages
  - Trends over time (first vs last third)
- [x] **Tool: `combine_omi_and_apple`** — комбинация Omi + Apple по датам:
  - Omi "сон" жалоба + Apple sleep data confirmation/mismatch
  - Omi "стресс" + Apple elevated HR correlation
- [x] **Doctor report updated:** включён Apple Health анализ
- [x] **README updated** — полная документация Apple Health
- [x] **ROADMAP created**
- [x] **Tested with mcporter** — все 8 инструментов работают

### Phase 2 — SMART Analysis (NEXT)
- [ ] Более умный парсинг Omi транскриптов (время, контекст)
- [ ] Lag-корреляции: сон сегодня → настроение/HRV завтра
- [ ] Еженедельные/ежемесячные агрегации
- [ ] Выявление трендов по периодам

### Phase 3 — Export & Visualization
- [ ] PDF экспорт для врача
- [ ] Obsidian note generation с встроенными данными
- [ ] Визуализация: графики sleep/HRV/steps

### Phase 4 — Integration & Automation
- [ ] Автоматический импорт Apple Health по расписанию
- [ ] Обнаружение новых export.xml
- [ ] Сравнение периодов (baseline vs current)

## Apple Health XML Format Reference

Apple Health export создаётся через:
`Settings > Privacy > Health > Export All Health Data`

Формат:
```xml
<HealthData locale="en_RU">
  <ExportDate value="2024-01-15 12:00:00 +0300"/>
  <Me .../>
  <Record type="HKQuantityTypeIdentifierHeartRate"
          sourceName="Apple Watch"
          unit="count/min"
          value="72"
          startDate="2024-01-15 10:30:00 +0300"
          endDate="2024-01-15 10:30:00 +0300"
          creationDate="..."/>
  <ActivitySummary dateComponents="2024-01-15"
                   activeEnergyBurned="423.5"
                   activeEnergyBurnedGoal="600"
                   appleExerciseTime="32"
                   appleExerciseTimeGoal="30"
                   appleStandHours="11"
                   appleStandHoursGoal="12"/>
  <ClinicalRecord type="AllergyRecord" identifier="..." sourceName="..."/>
</HealthData>
```

Файл может быть 100+ MB для многолетних данных. Используется ElementTree (in-memory до ~500MB) — для больших файлов рассмотреть SAX/iterparse в будущем.
