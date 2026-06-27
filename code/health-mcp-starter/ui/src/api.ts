export type Insight = {
  rank?: number;
  headline: string;
  detail: string;
  evidence_date?: string;
  evidence_quote?: string;
  action?: string;
  why_not_llm?: string;
};

export type Briefing = {
  one_liner?: string;
  top_insights?: Insight[];
  days_analyzed?: number;
  files_scanned?: number;
  data_footprint?: {
    days_analyzed?: number;
    files_scanned?: number;
    overlap_days?: number;
    data_mode?: string;
  };
  vs_generic_llm?: string[];
  vs_llm_note?: string;
  disclaimer?: string;
  manual_context?: UserContextSummary;
  local_narrative?: { narrative?: string; evidence_map?: unknown[] };
};

export type TimelineEntry = {
  date: string;
  signals: string[];
  sleep_quality?: string;
  snippet?: string;
  quality?: number;
  time_of_day?: string;
};

export type Timeline = {
  count: number;
  entries: TimelineEntry[];
  disclaimer?: string;
};

export type Sidecar = {
  name?: string;
  issuer?: string;
  expires_at?: string;
  expired?: boolean;
  revoked?: boolean;
  allowed_scopes?: { path: string; permissions: string[] }[];
  tools?: string[];
  audit?: { entries?: number; tools_used?: Record<string, number> };
};

export type ConditionPack = {
  id: string;
  name: string;
  description: string;
};

export type ConditionReport = {
  condition_id: string;
  condition_name: string;
  days_analyzed: number;
  track_items: { id: string; label: string; days_with_signal: number; frequency: number }[];
  metrics: { id: string; value: number | string | null; unit?: string; note?: string }[];
  citations?: { date: string; signal: string; excerpt: string }[];
  doctor_focus?: string[];
  disclaimer?: string;
};

export type Questions = {
  count: number;
  questions: { question: string; evidence?: string; why?: string }[];
  manual_context?: UserContextSummary;
};

export type UserContextProfile = {
  display_name?: string;
  age?: string;
  timezone?: string;
  main_goal?: string;
  doctor_notes?: string;
  source?: "records" | "manual" | string;
};

export type ContextItem = {
  id?: string;
  name?: string;
  title?: string;
  status?: string;
  dose?: string;
  schedule?: string;
  target?: string;
  notes?: string;
  source?: "records" | "manual" | string;
  confidence?: number;
  evidence_date?: string;
  evidence_excerpt?: string;
  mentions?: number;
};

export type ManualLog = {
  id?: string;
  date?: string;
  type?: string;
  text: string;
  severity?: string;
  tags?: string[];
  source?: "records" | "manual" | string;
  confidence?: number;
};

export type UserContext = {
  profile: UserContextProfile;
  conditions: ContextItem[];
  medications: ContextItem[];
  goals: ContextItem[];
  manual_logs: ManualLog[];
  updated_at?: string;
};

export type UserContextSummary = {
  display_name?: string;
  main_goal?: string;
  conditions_count: number;
  medications_count: number;
  goals_count: number;
  manual_logs_count: number;
  recent_logs: ManualLog[];
  updated_at?: string;
};

export type UserContextResponse = {
  context: UserContext;
  summary: UserContextSummary;
};

export type ContextSuggestions = {
  raw: Partial<UserContext> & { profile?: UserContextProfile; stats?: Record<string, unknown> };
  pending: {
    profile?: UserContextProfile;
    conditions: ContextItem[];
    medications: ContextItem[];
    goals: ContextItem[];
    manual_logs: ManualLog[];
    stats?: Record<string, unknown>;
  };
};

export type NextStep = {
  id: string;
  priority: number;
  title: string;
  detail: string;
  action_label: string;
  tab: string;
  kind?: string;
  evidence_date?: string;
  evidence_quote?: string;
};

export type NextStepsResponse = {
  steps: NextStep[];
  context_summary: UserContextSummary;
  pending_suggestions: number;
  days_analyzed: number;
};

export type DataSourceStatus =
  | "connected"
  | "active"
  | "enabled"
  | "available"
  | "demo_fallback"
  | "demo"
  | "sparse"
  | "disabled"
  | "missing"
  | "empty"
  | "default"
  | "explicit_empty"
  | "scope_blocked"
  | "unknown";

export type DataSource = {
  id: string;
  label: string;
  label_ru: string;
  type?: string;
  privacy?: string;
  status: DataSourceStatus | string;
  provides?: string[];
  consumed_by?: string[];
  setup_steps?: string[];
  setup_steps_ru?: string[];
  stats?: Record<string, unknown>;
  resolved_path?: string | null;
  env?: Record<string, string>;
};

export type DataSourcesSummary = {
  connected_sources: string[];
  needs_setup: string[];
  primary_source?: string;
  optional_enrichment?: string[];
};

export type DataSourcesQuickSetup = {
  demo?: string[];
  real_omi?: string[];
  real_apple?: string[];
};

export type DataSourcesResponse = {
  summary: DataSourcesSummary;
  sources: DataSource[];
  quick_setup?: DataSourcesQuickSetup;
  supported_signals?: string[];
  sidecar?: string;
  parser_features?: string[];
};

export type AttentionItem = {
  priority?: number;
  headline: string;
  detail: string;
  evidence_date?: string;
  evidence_quote?: string;
  action?: string;
};

export type WeekdayEffect = {
  signal: string;
  weekday: number;
  weekday_name: string;
  weekday_name_ru?: string;
  weekday_freq: number;
  overall_freq: number;
  lift: number;
  occurrences?: number;
  example_dates?: string[];
};

export type PersonalBaselineSignal = {
  mean_freq: number;
  std_freq?: number;
  band_low: number;
  band_high: number;
  p25?: number;
  p75?: number;
  trend?: string;
  sample_windows?: number;
};

export type PersonalBaselines = {
  days_analyzed?: number;
  signals: Record<string, PersonalBaselineSignal>;
};

export type SmartAnalysis = {
  attention_now?: AttentionItem[];
  weekday_effects?: WeekdayEffect[];
  personal_baselines?: PersonalBaselines;
  summary?: {
    baseline_signals?: number;
    weekday_patterns?: number;
    recent_anomalies?: number;
    attention_items?: number;
    wearable_bands_available?: boolean;
  };
};

export type NarrativeEvidence = {
  claim: string;
  source: string;
  date?: string;
  excerpt?: string;
};

export type Narrative = {
  source?: string;
  narrative: string;
  evidence_map?: NarrativeEvidence[];
  locale?: string;
  disclaimer?: string;
};

export type ClinicalTrend = {
  signal?: string;
  label?: string;
  direction?: "up" | "down" | "stable" | string;
  delta_14d?: number;
  delta_90d?: number;
  recent_freq?: number;
  prior_freq?: number;
  period?: string;
  detail?: string;
};

export type ClinicalSummary = {
  headline?: string;
  trends?: ClinicalTrend[];
  days_analyzed?: number;
  disclaimer?: string;
};

export type N1Compare = {
  method?: string;
  exposure_signal?: string;
  outcome_signal?: string;
  window_days?: number;
  headline?: string;
  summary?: string;
  interpretation?: string;
  exposure_weeks?: number;
  control_weeks?: number;
  exposure_days?: number;
  control_days?: number;
  exposure_outcome_rate?: number;
  control_outcome_rate?: number;
  lift?: number;
  lift_ratio?: number;
  risk_difference?: number;
  ci_low?: number;
  ci_high?: number;
  ci_95?: { low?: number | null; high?: number | null };
  p_value?: number | null;
  confidence?: string;
  example?: { date?: string; excerpt?: string };
  note?: string;
  disclaimer?: string;
};

export const DEMO_SIGNALS = ["stress", "mood_low", "sleep", "symptom_pain"] as const;

export type DemoSignal = (typeof DEMO_SIGNALS)[number];

export function signalLabel(signal: string): string {
  const labels: Record<string, string> = {
    stress: "Stress",
    mood_low: "Low mood",
    sleep: "Sleep signal",
    symptom_pain: "Pain / symptom"
  };
  return labels[signal] ?? signal.replace(/_/g, " ");
}

export async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  const data = await response.json();
  if (data?.error) {
    throw new Error(data.message || data.error);
  }
  return data as T;
}

export async function postJson<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  const data = await response.json();
  if (data?.error) {
    throw new Error(data.message || data.error);
  }
  return data as T;
}
