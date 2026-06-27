#!/usr/bin/env python3
"""
VitaSide demo-data generator.

Creates a realistic ~90-day Omi-style vault with PLANTED, explainable correlations so
the live demo (analyze + simulate_whatif + report) always has rich, convincing data.

Planted ground-truth (so what-if simulations have something real to find):
  - late caffeine (evening)            -> poor sleep same night
  - poor sleep                         -> stress + low mood the NEXT day (lag 1)
  - exercise                           -> good mood same day, better sleep that night
  - high stress streak                 -> symptom_pain (headache) within 1-2 days

Output goes to ./demo-data/<vault>/050 Daily Omi/Conversations/<year>/<month>/<file>.md
Point the MCP server at it with OMI_VAULT_PATH=.../demo-data/<vault>

This is clearly synthetic DEMO data. No real personal information.
"""
import os
import random
import datetime
from pathlib import Path

SEED = 42
DAYS = 90
OUT_VAULT = Path(__file__).parent / "demo-data" / "vault"

# Russian-language note fragments per signal (match the server's SIGNAL_PATTERNS regexes)
FRAGMENTS = {
    "sleep_poor": [
        "Опять плохо спал ночью, проснулся разбитый.",
        "Бессонница, ворочался до трёх, почти не выспался.",
        "Ночные пробуждения, сон рваный, устал из-за сна.",
    ],
    "sleep_good": [
        "Спал отлично, проснулся бодрым.",
        "Хороший крепкий сон, выспался наконец.",
    ],
    "stress": [
        "На работе сильный стресс, весь день на нервах.",
        "Тревога и напряжение, переживаю из-за дедлайна.",
        "Опять перегруз, чувствую как выгораю.",
    ],
    "mood_low": [
        "Настроение плохое, какая-то тоска и апатия.",
        "Грустно и тяжело, день прошёл уныло.",
        "Чувствую себя разбитым и опустошённым.",
    ],
    "mood_good": [
        "Сегодня отличное настроение, всё классно и бодро.",
        "Радостно, прилив энергии, вдохновлён.",
    ],
    "symptom_pain": [
        "С утра болит голова, мигрень не проходит.",
        "Головная боль пульсирует уже второй день, слабость.",
    ],
    "exercise": [
        "Утром пробежка, потом лёгкая зарядка.",
        "Сходил на тренировку, хорошая прогулка вечером.",
    ],
    "caffeine_late": [
        "Вечером выпил кофе перед сном, зря наверное.",
        "Поздний эспрессо, опять кофеин на ночь.",
    ],
    "social": [
        "Встретился с друзьями, хороший разговор.",
    ],
    # Condition-pack demo phrases (bipolar / migraine tracking)
    "migraine_episode": [
        "Пульсирующая мигрень с утра, выпил ибупрофен.",
        "Головная боль не проходит, принял суматриптан.",
        "Мигрень, тошнота, лёг в тёмную комнату.",
    ],
    "bipolar_med": [
        "Принял литий утром как обычно.",
        "Выпил лекарство, всё по расписанию.",
    ],
    "bipolar_elevated": [
        "Мало спал но бодр — три часа сна и полон энергии.",
        "Прилив сил, не могу уснуть от идей, на взводе.",
    ],
    "bipolar_irritable": [
        "Раздражительность на мелочи, срываюсь на всех.",
    ],
}


def pick(rng, key):
    return rng.choice(FRAGMENTS[key])


def build_day_signals(rng, day_idx, history):
    """Return (fragments, time, planted_flags) for a day, honoring planted correlations."""
    frags = []
    flags = {"caffeine_late": False, "sleep_poor": False, "exercise": False,
             "stress": False, "mood_low": False}

    # Base: exercise ~40% of days
    if rng.random() < 0.4:
        frags.append(pick(rng, "exercise"))
        flags["exercise"] = True

    # Late caffeine ~35% of days
    if rng.random() < 0.35:
        frags.append(pick(rng, "caffeine_late"))
        flags["caffeine_late"] = True

    # Sleep quality depends on caffeine + exercise
    p_poor = 0.25
    if flags["caffeine_late"]:
        p_poor += 0.45
    if flags["exercise"]:
        p_poor -= 0.15
    p_poor = max(0.05, min(0.9, p_poor))
    if rng.random() < p_poor:
        frags.append(pick(rng, "sleep_poor"))
        flags["sleep_poor"] = True
    else:
        frags.append(pick(rng, "sleep_good"))

    # Yesterday's poor sleep -> today's stress + low mood (lag 1)
    prev = history[-1] if history else None
    stress_boost = 0.4 if (prev and prev.get("sleep_poor")) else 0.12
    if rng.random() < stress_boost:
        frags.append(pick(rng, "stress"))
        flags["stress"] = True

    mood_low_boost = 0.45 if (prev and prev.get("sleep_poor")) else 0.1
    if flags["exercise"]:
        mood_low_boost -= 0.2
    if rng.random() < max(0.03, mood_low_boost):
        frags.append(pick(rng, "mood_low"))
        flags["mood_low"] = True
    elif flags["exercise"] and rng.random() < 0.5:
        frags.append(pick(rng, "mood_good"))

    # Stress streak (2 days) -> headache / migraine
    prev_stress = prev and prev.get("stress")
    if flags["stress"] and prev_stress:
        if rng.random() < 0.72:
            frags.append(pick(rng, "symptom_pain"))
        if rng.random() < 0.35:
            frags.append(pick(rng, "migraine_episode"))
    elif flags["stress"] and rng.random() < 0.08:
        frags.append(pick(rng, "symptom_pain"))
    if rng.random() < 0.2:
        frags.append(pick(rng, "social"))

    # Standalone migraine / headache days (~12% for journal demo)
    if rng.random() < 0.12:
        frags.append(pick(rng, "migraine_episode"))
    if rng.random() < 0.12:
        frags.append(pick(rng, "bipolar_med"))
    if rng.random() < 0.06:
        frags.append(pick(rng, "bipolar_elevated"))
    if rng.random() < 0.05:
        frags.append(pick(rng, "bipolar_irritable"))

    return frags, flags


def main():
    rng = random.Random(SEED)
    today = datetime.date.today()
    start = today - datetime.timedelta(days=DAYS - 1)
    history = []
    written = 0

    for i in range(DAYS):
        d = start + datetime.timedelta(days=i)
        frags, flags = build_day_signals(rng, i, history)
        history.append(flags)
        if not frags:
            continue

        hour = rng.choice([8, 9, 13, 19, 21, 22])
        minute = rng.randint(0, 59)
        speaker = "Me"
        body_lines = []
        for j, f in enumerate(frags):
            mm = j * 2
            ss = rng.randint(0, 59)
            body_lines.append(f"**{speaker}** [{mm:02d}:{ss:02d}]: {f}")

        content = (
            f"---\n"
            f"date: {d.isoformat()}\n"
            f"time: {hour:02d}:{minute:02d}\n"
            f"source: omi-demo\n"
            f"---\n\n"
            f"# Daily conversation {d.isoformat()}\n\n"
            + "\n".join(body_lines)
            + "\n"
        )

        out_dir = OUT_VAULT / "050 Daily Omi" / "Conversations" / f"{d.year}" / f"{d.month:02d}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{d.isoformat()}.md").write_text(content, encoding="utf-8")
        written += 1

    print(f"Generated {written} demo Omi notes over {DAYS} days at:")
    print(f"  {OUT_VAULT}")
    print(f"\nUse it:\n  OMI_VAULT_PATH=\"{OUT_VAULT}\" python3 health-pattern-mcp.py")


if __name__ == "__main__":
    main()
