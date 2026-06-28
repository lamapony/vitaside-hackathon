/* VitaSide — client-side document analysis.
 *
 * Lightweight, local extraction of dated signal observations from a pasted or
 * uploaded document (.txt/.md/.csv). Mirrors the backend signal vocabulary so a
 * manually added document can be previewed ("analyzed") in the browser without
 * sending it to the server. Privacy: parsing happens locally; nothing leaves the
 * device unless the user clicks "Add to notes" (posts a short summary to the
 * existing /api/manual-logs endpoint).
 */

export type ExtractedObservation = {
  date: string;
  signals: string[];
  excerpt: string;
};

export type DocumentAnalysis = {
  observations: ExtractedObservation[];
  signalCounts: { signal: string; label: string; count: number }[];
  datedEntries: number;
  undatedSignals: string[];
  totalSignals: number;
  chars: number;
};

export const SIGNAL_KEYWORDS: { signal: string; label: string; words: string[] }[] = [
  { signal: "stress", label: "Stress", words: ["stress", "stressed", "overwhelmed", "pressure", "tense", "anxious", "rushed", "deadline"] },
  { signal: "mood_low", label: "Low mood", words: ["sad", "low mood", "depressed", "down", "gloomy", "heavy", "hopeless", "blue", "crying"] },
  { signal: "mood_good", label: "Good mood", words: ["happy", "good mood", "energized", "inspired", "joy", "content", "grateful", "calm"] },
  { signal: "sleep", label: "Sleep", words: ["sleep", "insomnia", "tired", "fatigue", "awake", "restless", "woke", "exhausted", "nap"] },
  { signal: "symptom_pain", label: "Pain / symptom", words: ["pain", "ache", "sore", "cramp", "nausea", "dizzy", "fever"] },
  { signal: "headache", label: "Headache", words: ["headache", "migraine", "head pain", "tension headache"] },
  { signal: "medication", label: "Medication", words: ["ibuprofen", "sumatriptan", "med", "dose", "pill", "took", "lithium", "prescription"] },
];

const SIGNAL_LABELS: Record<string, string> = Object.fromEntries(
  SIGNAL_KEYWORDS.map((s) => [s.signal, s.label])
);

const DATE_PATTERNS: RegExp[] = [
  /(\d{4})-(\d{1,2})-(\d{1,2})/,
  /(\d{4})\/(\d{1,2})\/(\d{1,2})/,
  /(\d{1,2})\/(\d{1,2})\/(\d{4})/,
  /(\d{1,2})\.(\d{1,2})\.(\d{4})/,
];

function pad(n: number): string {
  return n < 10 ? `0${n}` : `${n}`;
}

function findDate(line: string): string | null {
  for (let i = 0; i < DATE_PATTERNS.length; i++) {
    const m = line.match(DATE_PATTERNS[i]);
    if (m) {
      let iso: string;
      if (i === 0 || i === 1) {
        iso = `${m[1]}-${pad(Number(m[2]))}-${pad(Number(m[3]))}`;
      } else if (i === 2) {
        iso = `${m[3]}-${pad(Number(m[1]))}-${pad(Number(m[2]))}`;
      } else {
        iso = `${m[3]}-${pad(Number(m[2]))}-${pad(Number(m[1]))}`;
      }
      if (iso.startsWith("20")) return iso;
    }
  }
  return null;
}

function signalsIn(text: string): string[] {
  const lower = text.toLowerCase();
  const found: string[] = [];
  for (const { signal, words } of SIGNAL_KEYWORDS) {
    if (words.some((w) => lower.includes(w)) && !found.includes(signal)) {
      found.push(signal);
    }
  }
  return found;
}

function truncate(s: string, max: number): string {
  const clean = s.replace(/\s+/g, " ").trim();
  return clean.length > max ? `${clean.slice(0, max)}…` : clean;
}

export function signalLabel(signal: string): string {
  return SIGNAL_LABELS[signal] ?? signal.replace(/_/g, " ");
}

export function analyzeDocument(text: string): DocumentAnalysis {
  const lines = text.split(/\r?\n/);
  const observations: ExtractedObservation[] = [];
  const counts: Record<string, number> = {};
  const undatedSignals: string[] = [];
  let datedEntries = 0;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const sigs = signalsIn(trimmed);
    if (sigs.length === 0) continue;
    const date = findDate(trimmed);
    sigs.forEach((s) => {
      counts[s] = (counts[s] ?? 0) + 1;
    });
    if (date) {
      datedEntries += 1;
      observations.push({ date, signals: sigs, excerpt: truncate(trimmed, 160) });
    } else {
      sigs.forEach((s) => {
        if (!undatedSignals.includes(s)) undatedSignals.push(s);
      });
      const last = observations[observations.length - 1];
      if (!last || last.date !== "undated") {
        observations.push({ date: "undated", signals: sigs, excerpt: truncate(trimmed, 160) });
      }
    }
  }

  observations.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));

  const signalCounts = Object.entries(counts)
    .map(([signal, count]) => ({ signal, label: signalLabel(signal), count }))
    .sort((a, b) => b.count - a.count);

  const totalSignals = Object.values(counts).reduce((a, b) => a + b, 0);

  return {
    observations: observations.slice(0, 50),
    signalCounts,
    datedEntries,
    undatedSignals,
    totalSignals,
    chars: text.length,
  };
}

export const SAMPLE_DOCUMENT = `2026-05-01  Long day at work, felt stressed and tense by evening. Slept badly.
2026-05-02  Woke at 4am, insomnia again. Low mood all morning, heavy and gloomy.
2026-05-05  Headache started around noon, tension-type. Took sumatriptan, eased by 3pm.
2026-05-08  Good gym session and an evening walk. Happy, energized, slept well.
2026-05-10  Deadline pressure, very anxious. Skipped lunch. Insomnia — tossed until 3am.
2026-05-12  Sad and heavy day, everything felt gloomy. No headache at least.
2026-05-15  Migraine returned, 7/10 pain. Took ibuprofen after poor sleep. Stressed about the week.
2026-05-18  Restful weekend. Calm, content. Slept 8 hours.
2026-05-22  Back-to-back meetings, overwhelmed. Headache in the afternoon.
2026-05-25  Inspired after a good conversation. Good mood, decent sleep.`;
