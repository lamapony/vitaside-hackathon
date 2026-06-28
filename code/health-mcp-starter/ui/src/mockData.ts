/* VitaSide — demo / offline mock data layer.
 *
 * Realistic, deterministic sample data that mirrors the local API shapes in
 * api.ts. Used by demoTransport.ts so the dashboard always renders — even when
 * the Python sidecar / API server is not running (hackathon-demo reliability).
 *
 * Narrative (aligned with the hackathon runbook):
 *  - stress → poor sleep (lag ~1 day)
 *  - headaches cluster Tue/Wed
 *  - low mood tracks poor sleep
 *  - confidence ~0.6, every claim cited to a dated excerpt, disclaimer on every output
 */
import type {
  Briefing,
  Timeline,
  TimelineEntry,
  Sidecar,
  ConditionPack,
  ConditionReport,
  Questions,
  UserContext,
  UserContextResponse,
  UserContextSummary,
  ContextSuggestions,
  NextStepsResponse,
  NextStep,
  DataSourcesResponse,
  SmartAnalysis,
  Narrative,
  ClinicalSummary,
  N1Compare,
} from "./api";

export const DISCLAIMER =
  "Personal lifestyle patterns only — not a medical diagnosis. Always discuss these observations with a qualified clinician.";

const CONFIDENCE_NOTE = "Confidence is moderate (N-of-1, 90 days). Treat as a hypothesis to discuss, not a conclusion.";

/* ---------- deterministic helpers ---------- */

function daysAgo(n: number): string {
  const d = new Date();
  d.setUTCDate(d.getUTCDate() - n);
  return d.toISOString().slice(0, 10);
}

function hashStr(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function rnd(seed: number, n: number): number {
  return ((seed * 9301 + n * 49297) % 233280) / 233280;
}

const today = () => daysAgo(0);

/* ---------- timeline (90 days, deterministic patterns) ---------- */

function snippetFor(signals: string[], sleep: string): string {
  const parts: string[] = [];
  if (signals.includes("stress")) parts.push("Back-to-back meetings, felt wired and tense by evening.");
  if (sleep === "poor") parts.push("Slept badly — woke at 4am, couldn't get back to sleep.");
  else if (sleep === "fair") parts.push("Restless night, woke a couple of times.");
  if (signals.includes("symptom_pain")) parts.push("Headache built around midday, tension-type, lingered into the afternoon.");
  if (signals.includes("mood_low")) parts.push("Lower mood today, hard to get going.");
  if (parts.length === 0) parts.push("Quiet day, nothing notable to report.");
  return parts.join(" ");
}

function buildTimeline(): TimelineEntry[] {
  const entries: TimelineEntry[] = [];
  for (let i = 89; i >= 0; i--) {
    const date = daysAgo(i);
    const dow = new Date(date + "T00:00:00Z").getUTCDay(); // 0 Sun .. 6 Sat
    const isWeekday = dow >= 1 && dow <= 5;
    const seed = hashStr(date);
    const signals: string[] = [];
    let sleep: "good" | "fair" | "poor" = "good";

    if (isWeekday && rnd(seed, 1) < 0.55) {
      signals.push("stress");
      sleep = rnd(seed, 2) < 0.6 ? "poor" : "fair";
    } else if (!isWeekday && rnd(seed, 3) < 0.18) {
      signals.push("stress");
    }

    if ((dow === 2 || dow === 3) && rnd(seed, 4) < 0.5) {
      signals.push("symptom_pain");
    }
    if (sleep === "poor" && rnd(seed, 5) < 0.7) signals.push("mood_low");
    if (signals.length === 0 && rnd(seed, 6) < 0.25) sleep = "fair";

    const tod = rnd(seed, 7) < 0.5 ? "morning" : rnd(seed, 8) < 0.5 ? "evening" : "night";
    const quality = signals.includes("stress") ? 2 : signals.length ? 3 : 4;

    entries.push({
      date,
      signals: signals.length ? signals : ["sleep"],
      sleep_quality: sleep,
      snippet: snippetFor(signals, sleep),
      quality,
      time_of_day: tod,
    });
  }
  return entries; // ascending by date
}

const TIMELINE: TimelineEntry[] = buildTimeline();

function recentEntry(matcher: (e: TimelineEntry) => boolean): TimelineEntry {
  for (let i = TIMELINE.length - 1; i >= 0; i--) {
    if (matcher(TIMELINE[i])) return TIMELINE[i];
  }
  return TIMELINE[TIMELINE.length - 1];
}

/* ---------- user context (mutable so MyContext edits "stick" in demo) ---------- */

const MOCK_CONTEXT_BASE: UserContext = {
  profile: {
    display_name: "Alex",
    age: "34",
    timezone: "Europe/Berlin",
    main_goal: "Understand stress → sleep → headaches before my next visit",
    doctor_notes: "Next appointment Friday. Bring trends, not just today.",
    source: "manual",
  },
  conditions: [
    { id: "migraine", name: "Migraine / tension headaches", status: "active", source: "manual", confidence: 0.8, evidence_date: daysAgo(6) },
    { id: "insomnia", name: "Sleep difficulty", status: "active", source: "manual", confidence: 0.6 },
  ],
  medications: [
    { id: "sumatriptan", name: "Sumatriptan", dose: "50mg", schedule: "as needed", target: "migraine", source: "manual" },
  ],
  goals: [
    { id: "goal-sleep", title: "Protect sleep on high-stress weeks", source: "manual" },
    { id: "goal-headache", title: "Find what triggers mid-week headaches", source: "manual" },
  ],
  manual_logs: [
    { id: "log-1", date: daysAgo(1), type: "note", text: "Took sumatriptan at noon, headache eased by 3pm.", severity: "moderate", tags: ["migraine", "med"], source: "manual" },
    { id: "log-2", date: daysAgo(3), type: "flare", text: "Woke with headache, likely stress from deadline day.", severity: "moderate", tags: ["migraine", "stress"], source: "manual" },
    { id: "log-3", date: daysAgo(8), type: "note", text: "Slept 7h, felt decent. No headache.", severity: "", tags: ["sleep"], source: "manual" },
  ],
  updated_at: new Date().toISOString(),
};

let mutableContext: UserContext = JSON.parse(JSON.stringify(MOCK_CONTEXT_BASE));

function recomputeSummary(ctx: UserContext): UserContextSummary {
  return {
    display_name: ctx.profile?.display_name,
    main_goal: ctx.profile?.main_goal,
    conditions_count: ctx.conditions?.length ?? 0,
    medications_count: ctx.medications?.length ?? 0,
    goals_count: ctx.goals?.length ?? 0,
    manual_logs_count: ctx.manual_logs?.length ?? 0,
    recent_logs: (ctx.manual_logs ?? []).slice(0, 5),
    updated_at: ctx.updated_at,
  };
}

/* ---------- mock builders ---------- */

export function mockHealth() {
  return { ok: true, version: "1.0-demo", root: "(demo mode)", demo_vault: "(sample data)" };
}

export function mockBriefing(): Briefing {
  const stressDay = recentEntry((e) => e.signals.includes("stress"));
  const headacheDay = recentEntry((e) => e.signals.includes("symptom_pain"));
  const moodDay = recentEntry((e) => e.signals.includes("mood_low"));
  return {
    one_liner: "Stress is leaking into your sleep; headaches like Tuesdays and Wednesdays.",
    days_analyzed: 90,
    files_scanned: 142,
    data_footprint: { days_analyzed: 90, files_scanned: 142, overlap_days: 84, data_mode: "demo" },
    top_insights: [
      {
        rank: 1,
        headline: "High-stress days are followed by poorer sleep the next night",
        detail:
          "Across 90 days, sleep quality dropped on 68% of nights that followed a high-stress day, vs 31% otherwise. The lag is about one day.",
        evidence_date: stressDay.date,
        evidence_quote: stressDay.snippet,
        action: "Review your sleep on nights after stressful days — Timeline.",
        why_not_llm: "Grounded in 142 of your own notes with dated excerpts, not a population average.",
      },
      {
        rank: 2,
        headline: "Headaches cluster mid-week (Tue/Wed)",
        detail: "9 of 12 headache episodes in the window fell on Tuesday or Wednesday — a 2.4× lift versus other days.",
        evidence_date: headacheDay.date,
        evidence_quote: headacheDay.snippet,
        action: "Note morning context on Tue/Wed — Condition → Migraine.",
        why_not_llm: "Lift computed against your own baseline; every episode has a dated citation.",
      },
      {
        rank: 3,
        headline: "Low mood tracks poor sleep more than stress",
        detail: "Low-mood days overlapped poor-sleep days 74% of the time; the direct stress correlation was weaker.",
        evidence_date: moodDay.date,
        evidence_quote: moodDay.snippet,
        action: "Protect sleep before mood slips — Smart view.",
        why_not_llm: "Co-occurrence is from your observations, not a generic mental-health article.",
      },
    ],
    vs_generic_llm: [
      "Every claim cites a dated excerpt from your notes",
      "Personal N-of-1 baselines, not population averages",
      "No hallucinated advice — confidence + disclaimer on every output",
    ],
    vs_llm_note: "Generic LLMs guess. VitaSide shows the receipts.",
    disclaimer: DISCLAIMER,
    manual_context: recomputeSummary(mutableContext),
    local_narrative: {
      narrative:
        "Over the last 90 days your stress and sleep are coupled: busy weekdays tend to cost you the next night, and low mood follows poor sleep more closely than stress itself. Headaches, when they come, prefer Tuesdays and Wednesdays.",
      evidence_map: [
        { claim: "Stress precedes poor sleep", source: "your Omi notes", date: stressDay.date, excerpt: stressDay.snippet },
        { claim: "Headaches cluster Tue/Wed", source: "your Omi notes", date: headacheDay.date, excerpt: headacheDay.snippet },
      ],
    },
  };
}

export function mockTimeline(): Timeline {
  return { count: TIMELINE.length, entries: TIMELINE, disclaimer: DISCLAIMER };
}

export function mockSidecar(): Sidecar {
  const exp = new Date();
  exp.setUTCDate(exp.getUTCDate() + 60);
  return {
    name: "sleep-stress-sidecar",
    issuer: "vitaside-local",
    expires_at: exp.toISOString(),
    expired: false,
    revoked: false,
    allowed_scopes: [
      { path: "demo-data/vault/050 Daily Omi", permissions: ["read"] },
      { path: "demo-data/vault/050 Daily Omi/Visits", permissions: ["read", "write"] },
    ],
    tools: ["health_check", "list_data_sources", "list_patterns", "simulate_whatif", "build_visit_packet", "contract_preview"],
    audit: {
      entries: 128,
      tools_used: { analyze_lifestyle_patterns: 14, build_visit_packet: 3, list_data_sources: 8 },
    },
  };
}

const MOCK_PACKS: ConditionPack[] = [
  { id: "migraine", name: "Migraine / tension headaches", description: "Triggers, weekday patterns, med timing." },
  { id: "sleep", name: "Sleep difficulty", description: "Stress lag, sleep quality trends." },
  { id: "mood", name: "Low mood", description: "Co-occurrence with sleep and stress." },
];

export function mockConditionPacks() {
  return { packs: MOCK_PACKS };
}

export function mockUserContextResponse(): UserContextResponse {
  return { context: mutableContext, summary: recomputeSummary(mutableContext) };
}

export function mockQuestions(): Questions {
  return {
    count: 7,
    questions: [
      { question: "Could my Tuesday/Wednesday headaches be linked to my work schedule?", evidence: "9/12 episodes on Tue/Wed (2.4× lift)", why: "Mid-week cluster stands out from your baseline." },
      { question: "My sleep worsens after high-stress days — is that worth tracking preventively?", evidence: "68% of post-stress nights were poor vs 31% overall", why: "Lag correlation ~1 day." },
      { question: "Is the pattern of low mood following poor sleep consistent enough to address?", evidence: "74% overlap of low mood with poor sleep", why: "Stronger than the direct stress link." },
      { question: "Does sumatriptan still work as well for the mid-week episodes?", evidence: "Logged use on " + daysAgo(1), why: "Compare good vs bad response days." },
      { question: "Are there weeks where stress stays high for several days in a row?", evidence: "See Timeline heatmap", why: "Clustered stress may explain sleep debt." },
      { question: "Should I bring a 30-day trend summary instead of just today's complaints?", evidence: "PP-01: peak-end recall bias", why: "Visit packet counters recency bias." },
      { question: "Any pattern to when headaches do NOT happen despite stress?", evidence: "Compare non-headache stress days", why: "Protective factors are as useful as triggers." },
    ],
    manual_context: recomputeSummary(mutableContext),
  };
}

export function mockNextSteps(conditionId: string): NextStepsResponse {
  const steps: NextStep[] = [
    { id: "s1", priority: 1, title: "Prepare a doctor handoff packet", detail: "Turn 90 days into a cited, time-bounded summary for Friday's visit.", action_label: "Open Doctor handoff", tab: "doctor", kind: "visit", evidence_date: daysAgo(2), evidence_quote: "Headache built around midday, tension-type." },
    { id: "s2", priority: 2, title: "Review mid-week headache cluster", detail: "9/12 headaches fell on Tue/Wed — note morning context on those days.", action_label: "Open Condition", tab: "condition", kind: "pattern", evidence_date: daysAgo(3) },
    { id: "s3", priority: 3, title: "Confirm your profile and meds", detail: "A confirmed context sharpens every recommendation.", action_label: "Open My context", tab: "context", kind: "setup" },
    { id: "s4", priority: 4, title: "Explore stress → sleep lag", detail: "Sleep drops on 68% of nights after high-stress days.", action_label: "Open Smart view", tab: "smart", kind: "analysis", evidence_date: daysAgo(1) },
    { id: "s5", priority: 5, title: "Check data sources", detail: "Make sure Omi notes and Apple export are connected for richer patterns.", action_label: "Open Data sources", tab: "datasources", kind: "setup" },
  ];
  return {
    steps,
    context_summary: recomputeSummary(mutableContext),
    pending_suggestions: 3,
    days_analyzed: 90,
  };
  void conditionId;
}

export function mockCondition(id: string): ConditionReport {
  const name = MOCK_PACKS.find((p) => p.id === id)?.name ?? id;
  const painDays = TIMELINE.filter((e) => e.signals.includes("symptom_pain"));
  return {
    condition_id: id,
    condition_name: name,
    days_analyzed: 90,
    track_items: [
      { id: "episodes", label: "Headache episodes", days_with_signal: painDays.length, frequency: painDays.length / 90 },
      { id: "tue_wed", label: "Tue/Wed episodes", days_with_signal: 9, frequency: 9 / painDays.length },
      { id: "med_response", label: "Sumatriptan use", days_with_signal: 4, frequency: 4 / 90 },
    ],
    metrics: [
      { id: "avg_intensity", value: 6, unit: "/10", note: "self-reported" },
      { id: "duration_h", value: 4.5, unit: "h" },
      { id: "days_free", value: 78, unit: "days" },
    ],
    citations: painDays.slice(0, 5).map((e) => ({ date: e.date, signal: "symptom_pain", excerpt: e.snippet ?? "" })),
    doctor_focus: ["Mid-week clustering (Tue/Wed)", "Stress as a possible precursor", "Med timing and response"],
    disclaimer: DISCLAIMER,
  };
}

export function mockSmart(): SmartAnalysis {
  return {
    attention_now: [
      { priority: 1, headline: "Sleep deteriorating this week", detail: "3 of the last 4 nights were poor, following a stressful stretch.", evidence_date: daysAgo(1), evidence_quote: "Slept badly — woke at 4am." },
      { priority: 2, headline: "Headache frequency above baseline", detail: "2 episodes in the last 7 days vs a 90-day mean of ~1.3/week.", evidence_date: daysAgo(3) },
    ],
    weekday_effects: [
      { signal: "symptom_pain", weekday: 2, weekday_name: "Tuesday", weekday_freq: 0.5, overall_freq: 0.13, lift: 3.7, occurrences: 6, example_dates: [daysAgo(3), daysAgo(10)] },
      { signal: "symptom_pain", weekday: 3, weekday_name: "Wednesday", weekday_freq: 0.45, overall_freq: 0.13, lift: 3.3, occurrences: 3, example_dates: [daysAgo(17)] },
      { signal: "stress", weekday: 1, weekday_name: "Monday", weekday_freq: 0.6, overall_freq: 0.4, lift: 1.5, occurrences: 8 },
    ],
    personal_baselines: {
      days_analyzed: 90,
      signals: {
        stress: { mean_freq: 0.4, std_freq: 0.12, band_low: 0.28, band_high: 0.52, trend: "stable", sample_windows: 12 },
        sleep: { mean_freq: 0.34, std_freq: 0.1, band_low: 0.24, band_high: 0.44, trend: "slight_down", sample_windows: 12 },
        mood_low: { mean_freq: 0.22, std_freq: 0.09, band_low: 0.13, band_high: 0.31, trend: "stable", sample_windows: 12 },
        symptom_pain: { mean_freq: 0.13, std_freq: 0.06, band_low: 0.07, band_high: 0.19, trend: "up", sample_windows: 12 },
      },
    },
    summary: { baseline_signals: 4, weekday_patterns: 3, recent_anomalies: 2, attention_items: 2, wearable_bands_available: false },
  };
}

export function mockNarrative(): Narrative {
  const stressDay = recentEntry((e) => e.signals.includes("stress"));
  const headacheDay = recentEntry((e) => e.signals.includes("symptom_pain"));
  return {
    source: "local-narrative-engine (demo)",
    narrative:
      "Your last 90 days tell a small, consistent story: stress and sleep are coupled, low mood rides on the back of poor sleep, and your headaches prefer the middle of the week. None of this is a diagnosis — it is a set of hypotheses, each tied to a dated excerpt from your own notes, ready to discuss with your clinician.",
    evidence_map: [
      { claim: "Stress precedes poor sleep (~1 day lag)", source: "your Omi notes", date: stressDay.date, excerpt: stressDay.snippet },
      { claim: "Headaches cluster on Tue/Wed", source: "your Omi notes", date: headacheDay.date, excerpt: headacheDay.snippet },
    ],
    locale: "en",
    disclaimer: DISCLAIMER + " " + CONFIDENCE_NOTE,
  };
}

export function mockClinicalSummary(): ClinicalSummary {
  return {
    headline: "Stress→sleep coupling and a mid-week headache cluster are the strongest signals in the last 90 days.",
    trends: [
      { signal: "stress", label: "Stress", direction: "up", delta_14d: 0.12, delta_90d: 0.04, recent_freq: 0.48, prior_freq: 0.36, period: "14d vs prior", detail: "Slight uptick in the last two weeks." },
      { signal: "sleep_quality", label: "Sleep quality", direction: "down", delta_14d: -0.15, delta_90d: -0.06, recent_freq: 0.4, prior_freq: 0.3, period: "14d vs prior", detail: "More poor-sleep nights recently." },
      { signal: "symptom_pain", label: "Headache frequency", direction: "up", delta_14d: 0.2, delta_90d: 0.05, recent_freq: 0.2, prior_freq: 0.12, period: "14d vs prior", detail: "Above your 90-day baseline." },
      { signal: "mood_low", label: "Low mood", direction: "stable", delta_14d: 0.01, delta_90d: -0.02, recent_freq: 0.23, prior_freq: 0.22, period: "14d vs prior" },
    ],
    days_analyzed: 90,
    disclaimer: DISCLAIMER,
  };
}

export function mockDataSources(): DataSourcesResponse {
  return {
    summary: {
      connected_sources: ["omi_vault"],
      needs_setup: ["apple_export"],
      primary_source: "omi_vault",
      optional_enrichment: ["apple_export"],
    },
    sources: [
      {
        id: "omi_vault",
        label: "Omi vault (notes & journals)",
        label_ru: "Omi-хранилище",
        description: "Daily notes, symptom logs, visit notes.",
        privacy: "Local files only — read under manifest scope.",
        status: "demo",
        provides: ["stress", "sleep", "mood_low", "symptom_pain"],
        consumed_by: ["analyze_lifestyle_patterns", "build_visit_packet"],
        stats: { notes: 142, days: 90 },
        resolved_path: "demo-data/vault/050 Daily Omi",
      },
      {
        id: "apple_export",
        label: "Apple Health export",
        description: "Heart rate, sleep duration, step count.",
        privacy: "Optional. Parsed locally; never uploaded.",
        status: "available",
        provides: ["heart_rate", "sleep_duration", "steps"],
        setup_steps: ["Copy export.xml under ~/Downloads/apple_health_export/", "Restart the sidecar"],
      },
      {
        id: "manual_log",
        label: "Manual log",
        description: "Quick capture of symptoms and context.",
        privacy: "Local only.",
        status: "connected",
        provides: ["symptom_pain", "context"],
      },
    ],
    quick_setup: { demo: ["Run ./setup.sh to seed the demo vault"], real_omi: ["Set OMI_VAULT_PATH to your vault"], real_apple: ["Place export.xml under apple_health_export/"] },
    supported_signals: ["stress", "sleep", "mood_low", "symptom_pain", "heart_rate", "steps"],
    sidecar: "sleep-stress-sidecar",
  };
}

export function mockN1Compare(exposure: string, outcome: string, windowDays: number): N1Compare {
  const lift = 2.1;
  const expRate = 0.68;
  const ctrlRate = 0.32;
  return {
    method: "n-of-1 lagged co-occurrence",
    exposure_signal: exposure,
    outcome_signal: outcome,
    window_days: windowDays,
    headline: `${exposure.replace(/_/g, " ")} is followed by ${outcome.replace(/_/g, " ")} about twice as often as on control days.`,
    summary: `On days exposed to ${exposure}, ${outcome} occurred in ${Math.round(expRate * 100)}% of the ${windowDays}-day windows vs ${Math.round(ctrlRate * 100)}% on control days.`,
    interpretation: "This is a personal correlation, not causation. Confidence is moderate for an N-of-1 sample.",
    exposure_weeks: 18,
    control_weeks: 12,
    exposure_days: 38,
    control_days: 52,
    exposure_outcome_rate: expRate,
    control_outcome_rate: ctrlRate,
    lift,
    lift_ratio: lift,
    risk_difference: expRate - ctrlRate,
    ci_low: 1.2,
    ci_high: 3.4,
    ci_95: { low: 1.2, high: 3.4 },
    p_value: 0.04,
    q_value: 0.08,
    confidence: "moderate",
    example: { date: recentEntry((e) => e.signals.includes(exposure)).date, excerpt: recentEntry((e) => e.signals.includes(exposure)).snippet },
    note: CONFIDENCE_NOTE,
    disclaimer: DISCLAIMER,
  };
}

export function mockExportBundle(body?: unknown): unknown {
  const anonymize = (body as { anonymize?: boolean } | null | undefined)?.anonymize ?? false;
  const dateStr = today();
  return {
    visit_date: dateStr,
    questions_count: 7,
    anonymized: anonymize,
    confidence: 0.58,
    disclaimer: DISCLAIMER,
    outputs: {
      visit_packet_md: `out/vitaside-visit-prep-${dateStr}.md`,
      patient_html: `out/vitaside-report-${dateStr}.html`,
      doctor_html: `out/vitaside-doctor-${dateStr}.html`,
    },
    latest: {
      patient_html: `vitaside-report-${dateStr}.html`,
      doctor_html: `vitaside-doctor-${dateStr}.html`,
      user_context: `context-${dateStr}.md`,
    },
    personal_baselines: { stress: "0.40", sleep: "0.34", mood_low: "0.22", symptom_pain: "0.13" },
    citations: TIMELINE.slice(-8).map((e) => ({ date: e.date, source_path: `050 Daily Omi/${e.date}.md`, excerpt: e.snippet })),
    note: "Generated locally — no cloud. Open the files in out/.",
  };
}

export function mockAzureContract(): unknown {
  return { azure_enabled: false, mode: "stub (demo)", allowed_operations: [], contract_version: "1.0" };
}

export function mockPreviewAzure(): unknown {
  return {
    operation: "enhance_insight",
    payload: { summary: "stress→sleep lag, mid-week headaches", confidence: 0.58, signals: ["stress", "sleep", "symptom_pain"] },
    data_minimization: { payload_fingerprint: "sha256:demo-fingerprint-9c4f", forbidden_categories: ["free_text", "raw_transcripts", "names"] },
    note: "Preview only — nothing was sent. Raw notes never leave your machine.",
  };
}

export function mockAzureEnhance(): unknown {
  return { share_url: null, note: "Azure is disabled in demo mode. No outbound network.", anonymized: true };
}

export function mockSkinPhoto(): unknown {
  return {
    observations: [
      "Border appears slightly irregular on the lower edge.",
      "Two distinct shades of brown are visible.",
      "Diameter is moderate; no major asymmetry noted.",
    ],
    abcde_observations: { diameter_px: 420, asymmetry: "low", border_contrast: "moderate", distinct_colors: 2 },
    recommendation: "This is a description, not a diagnosis. If you notice changes, show it to a dermatologist.",
    disclaimer: "Not a diagnosis or risk score. For any skin concern, see a clinician.",
    external: null,
  };
}

export function mockContextSuggestions(): ContextSuggestions {
  return {
    raw: { profile: { main_goal: "Understand stress → sleep → headaches" }, stats: { notes: 142 } },
    pending: {
      profile: { main_goal: "Understand stress → sleep → headaches before my next visit" },
      conditions: [{ id: "migraine", name: "Migraine / tension headaches", source: "records", confidence: 0.8, evidence_date: daysAgo(6) }],
      medications: [{ id: "sumatriptan", name: "Sumatriptan", dose: "50mg", schedule: "as needed", source: "records", confidence: 0.7 }],
      goals: [{ id: "goal-sleep", title: "Protect sleep on high-stress weeks", source: "records" }],
      manual_logs: [],
      stats: { notes: 142 },
    },
  };
}

export function mockApplySuggestions(): unknown {
  return { applied: 3, skipped: 0, context: mutableContext, summary: recomputeSummary(mutableContext) };
}

/* ---------- write endpoints (mutate mutableContext so edits stick) ---------- */

function parseBody(body: BodyInit | null | undefined): Record<string, unknown> {
  if (!body) return {};
  try {
    if (typeof body === "string") return JSON.parse(body);
  } catch {
    /* ignore */
  }
  return {};
}

export function mockAddManualLog(body: BodyInit | null | undefined): UserContextResponse {
  const b = parseBody(body);
  const log = {
    id: "log-" + Date.now(),
    date: (b.date as string) || today(),
    type: (b.type as string) || "note",
    text: (b.text as string) || "",
    severity: (b.severity as string) || "",
    tags: (b.tags as string[]) || [],
    source: "manual" as const,
  };
  mutableContext = {
    ...mutableContext,
    manual_logs: [log, ...(mutableContext.manual_logs ?? [])].slice(0, 50),
    updated_at: new Date().toISOString(),
  };
  return { context: mutableContext, summary: recomputeSummary(mutableContext) };
}

export function mockPutUserContext(path: string, body: BodyInit | null | undefined): UserContextResponse {
  const b = parseBody(body);
  if (path === "/api/user-context") {
    mutableContext = { ...(b.context as UserContext), updated_at: new Date().toISOString() };
  } else if (path === "/api/user-context/profile") {
    mutableContext = { ...mutableContext, profile: { ...mutableContext.profile, ...(b.profile as Record<string, unknown>) }, updated_at: new Date().toISOString() };
  } else if (path.startsWith("/api/user-context/")) {
    const kind = path.split("/api/user-context/")[1] as "conditions" | "medications" | "goals";
    mutableContext = { ...mutableContext, [kind]: (b.items as typeof mutableContext[typeof kind]) ?? mutableContext[kind], updated_at: new Date().toISOString() };
  }
  return { context: mutableContext, summary: recomputeSummary(mutableContext) };
}

/* ---------- dispatcher ---------- */

export function mockFor(method: string, url: string, body?: BodyInit | null | undefined): unknown | undefined {
  try {
    const u = new URL(url, "http://localhost");
    const path = u.pathname;
    const q = u.searchParams;
    const m = method.toUpperCase();

    if (m === "GET") {
      switch (path) {
        case "/api/health": return mockHealth();
        case "/api/briefing": return mockBriefing();
        case "/api/timeline": return mockTimeline();
        case "/api/sidecar": return mockSidecar();
        case "/api/condition-packs": return mockConditionPacks();
        case "/api/user-context": return mockUserContextResponse();
        case "/api/questions": return mockQuestions();
        case "/api/next-steps": return mockNextSteps(q.get("condition_id") ?? "migraine");
        case "/api/smart": return mockSmart();
        case "/api/narrative": return mockNarrative();
        case "/api/clinical-summary": return mockClinicalSummary();
        case "/api/data-sources": return mockDataSources();
        case "/api/azure-contract": return mockAzureContract();
        case "/api/preview-azure": return mockPreviewAzure();
        case "/api/context-suggestions": return mockContextSuggestions();
        case "/api/n1-compare": return mockN1Compare(q.get("exposure_signal") ?? "stress", q.get("outcome_signal") ?? "mood_low", Number(q.get("window_days") ?? 2));
        case "/api/journals": return { journals: [{ id: "omi_voice", label: "Omi voice" }, { id: "manual_log", label: "Manual log" }] };
        case "/api/headache-insights": return { max_lag: 2, headaches: 12, top_triggers: [{ signal: "stress", lift: 2.1 }], disclaimer: DISCLAIMER };
      }
      if (path.startsWith("/api/condition/")) return mockCondition(decodeURIComponent(path.replace("/api/condition/", "")));
      if (path.startsWith("/api/journals/")) return { journal_id: path.split("/api/journals/")[1], entries: TIMELINE.slice(-7), disclaimer: DISCLAIMER };
    }

    if (m === "POST") {
      switch (path) {
        case "/api/export-bundle": return mockExportBundle(body);
        case "/api/azure/enhance": return mockAzureEnhance();
        case "/api/analyze-skin-photo": return mockSkinPhoto();
        case "/api/context-suggestions/apply": return mockApplySuggestions();
        case "/api/manual-logs": return mockAddManualLog(body);
      }
    }

    if (m === "PUT") {
      if (path === "/api/user-context" || path === "/api/user-context/profile" || path.startsWith("/api/user-context/")) {
        return mockPutUserContext(path, body);
      }
    }

    return undefined;
  } catch {
    return undefined;
  }
}
