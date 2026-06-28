import re
from pathlib import Path
p = Path("demo-data/vault/050 Daily Omi/Conversations/2026/03/2026-03-30.md")
content = p.read_text()
fm = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
transcript = re.findall(r"\*\*([^*]+)\*\*\s*\[(\d+):(\d+)\]:\s*(.+)", content)
spoken = " ".join([s[3] for s in transcript])
full = spoken.lower()
stress = re.compile(r"\b(стресс|тревог[аи]?|anxious|stress[^o]|нерв[а-я]|пережива[юе]|паник[а-я]|волну[юя]|напряж[её]н|беспоко[ия]|адреналин|выгора[юе]|перегруз)\b", re.I)
print("transcript", len(transcript), spoken[:80])
for pat in ["sleep", "caffeine", "headache"]:
    print(pat, bool(re.search(r"caffeine|headache|sleep", full, re.I)))
print("stress word", re.findall(stress, full))