import { useEffect, useState } from "react";
import {
  ContextItem,
  ContextSuggestions,
  ManualLog,
  UserContext,
  UserContextProfile,
  UserContextResponse,
  getJson,
  postJson
} from "../api";

type Props = {
  context?: UserContext;
  onContextChange: (context: UserContext) => void;
  onSuggestionsApplied?: () => void;
};

type Section = "profile" | "conditions" | "medications" | "goals" | "logs";

const blankProfile: UserContextProfile = {
  display_name: "",
  age: "",
  timezone: "",
  main_goal: "",
  doctor_notes: ""
};

function sourceLabel(s?: string): string {
  if (s === "records") return "Auto-detected";
  if (s === "manual") return "Manual entry";
  return s ?? "Manual entry";
}

function titleCase(s?: string): string {
  if (!s) return "";
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function MyContext({ context, onContextChange, onSuggestionsApplied }: Props) {
  const [section, setSection] = useState<Section>("profile");
  const [profile, setProfile] = useState<UserContextProfile>(context?.profile ?? blankProfile);
  const [conditions, setConditions] = useState<ContextItem[]>(context?.conditions ?? []);
  const [medications, setMedications] = useState<ContextItem[]>(context?.medications ?? []);
  const [goals, setGoals] = useState<ContextItem[]>(context?.goals ?? []);
  const [log, setLog] = useState<ManualLog>({ type: "symptom", text: "", severity: "", tags: [] });
  const [suggestions, setSuggestions] = useState<ContextSuggestions | null>(null);
  const [saved, setSaved] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setProfile(context?.profile ?? blankProfile);
    setConditions(context?.conditions ?? []);
    setMedications(context?.medications ?? []);
    setGoals(context?.goals ?? []);
  }, [context]);

  useEffect(() => {
    getJson<ContextSuggestions>("/api/context-suggestions").then(setSuggestions).catch(() => setSuggestions(null));
  }, [context]);

  const pending = suggestions?.pending;
  const pendingCount =
    (pending?.conditions.length ?? 0) +
    (pending?.medications.length ?? 0) +
    (pending?.goals.length ?? 0) +
    (pending?.manual_logs.length ?? 0) +
    (pending?.profile?.main_goal ? 1 : 0);

  async function applySuggestions(mode: "fill_empty" | "refresh_auto" = "fill_empty") {
    setBusy(true);
    try {
      const result = await postJson<{ context: UserContext }>("/api/context-suggestions/apply", { mode });
      onContextChange(result.context);
      onSuggestionsApplied?.();
      setSaved(mode === "fill_empty" ? "Suggestions applied to empty fields." : "Auto-detected fields refreshed.");
      const fresh = await getJson<ContextSuggestions>("/api/context-suggestions");
      setSuggestions(fresh);
    } finally {
      setBusy(false);
    }
  }

  async function saveProfile() {
    const response = await put<UserContextResponse>("/api/user-context/profile", { profile });
    onContextChange(response.context);
    setSaved("Profile saved.");
  }

  async function saveList(kind: "conditions" | "medications" | "goals", items: ContextItem[]) {
    const response = await put<UserContextResponse>(`/api/user-context/${kind}`, { items });
    onContextChange(response.context);
    setSaved("Saved.");
  }

  async function addLog() {
    if (!log.text.trim()) return;
    const response = await postJson<UserContextResponse>("/api/manual-logs", {
      ...log,
      tags: Array.isArray(log.tags) ? log.tags : []
    });
    onContextChange(response.context);
    setLog({ type: "symptom", text: "", severity: "", tags: [] });
    setSaved("Log added.");
  }

  return (
    <section className="context-page">
      <header className="page-header">
        <div>
          <p className="eyebrow">My context</p>
          <h1>Your health profile</h1>
          <p className="lede">Auto-filled from notes where possible. Edit anything — manual changes always win.</p>
        </div>
      </header>

      {pendingCount > 0 && (
        <div className="suggestions-banner">
          <div>
            <strong>{pendingCount} suggestions from your records</strong>
            <p>Medications, conditions, goals and recent note excerpts detected locally.</p>
          </div>
          <div className="button-row">
            <button className="primary" disabled={busy} onClick={() => applySuggestions("fill_empty")}>
              Apply to empty fields
            </button>
            <button className="secondary" disabled={busy} onClick={() => applySuggestions("refresh_auto")}>
              Refresh auto fields
            </button>
          </div>
        </div>
      )}

      {pendingCount > 0 && (
        <div className="suggestion-preview-grid">
          <SuggestionGroup title="Conditions" items={pending?.conditions ?? []} nameKey="name" />
          <SuggestionGroup title="Medications" items={pending?.medications ?? []} nameKey="name" />
          <SuggestionGroup title="Goals" items={pending?.goals ?? []} nameKey="title" />
        </div>
      )}

      <div className="section-tabs">
        {([
          ["profile", "Profile"],
          ["conditions", "Conditions"],
          ["medications", "Medications"],
          ["goals", "Goals"],
          ["logs", "Logs"]
        ] as [Section, string][]).map(([id, label]) => (
          <button key={id} className={section === id ? "section-tab active" : "section-tab"} onClick={() => setSection(id)}>
            {label}
          </button>
        ))}
      </div>

      {section === "profile" && (
        <div className="soft-card form-card">
          <div className="form-grid">
            <Field label="Name" value={profile.display_name} onChange={(v) => setProfile({ ...profile, display_name: v })} />
            <Field label="Age" value={profile.age} onChange={(v) => setProfile({ ...profile, age: v })} />
            <Field label="Timezone" value={profile.timezone} onChange={(v) => setProfile({ ...profile, timezone: v })} />
            <Area label="Main goal" value={profile.main_goal ?? ""} onChange={(v) => setProfile({ ...profile, main_goal: v })} placeholder="Reduce migraine days; stabilize sleep; prepare psych visit" />
            <Area label="Notes for doctor" value={profile.doctor_notes ?? ""} onChange={(v) => setProfile({ ...profile, doctor_notes: v })} placeholder="Things you forget to mention" />
          </div>
          <SourceHint source={profile.source as string | undefined} />
          <button className="primary" onClick={saveProfile}>Save profile</button>
        </div>
      )}

      {section === "conditions" && (
        <ListEditor title="Conditions to monitor" items={conditions} setItems={setConditions} fields={[["name", "Condition"], ["status", "Status"], ["notes", "Notes"]]} onSave={() => saveList("conditions", conditions)} />
      )}

      {section === "medications" && (
        <ListEditor title="Medications" items={medications} setItems={setMedications} fields={[["name", "Medication"], ["dose", "Dose"], ["schedule", "Schedule"], ["notes", "Notes"]]} onSave={() => saveList("medications", medications)} />
      )}

      {section === "goals" && (
        <ListEditor title="Goals & visit questions" items={goals} setItems={setGoals} fields={[["title", "Goal"], ["target", "Target"], ["notes", "Notes"]]} onSave={() => saveList("goals", goals)} />
      )}

      {section === "logs" && (
        <div className="context-grid logs-grid">
          <div className="soft-card form-card">
            <h2>Quick log</h2>
            <div className="form-grid">
              <label className="field">
                Type
                <select value={log.type ?? "note"} onChange={(e) => setLog({ ...log, type: e.target.value })}>
                  <option value="symptom">Symptom</option>
                  <option value="medication">Medication</option>
                  <option value="mood">Mood</option>
                  <option value="sleep">Sleep</option>
                  <option value="trigger">Trigger</option>
                  <option value="note">Note</option>
                </select>
              </label>
              <Field label="Severity" value={log.severity} onChange={(v) => setLog({ ...log, severity: v })} placeholder="0-10" />
              <Area label="What happened?" value={log.text} onChange={(v) => setLog({ ...log, text: v })} placeholder="Headache 7/10, took ibuprofen after poor sleep" />
            </div>
            <button className="primary" onClick={addLog}>Add log</button>
          </div>
          <div className="soft-card">
            <h2>Recent logs</h2>
            <div className="manual-log-list">
              {(context?.manual_logs ?? []).slice(0, 10).map((item) => (
                <article className="manual-log" key={item.id ?? item.text}>
                  <div className="log-head">
                    <strong>{item.date} · {titleCase(item.type)}</strong>
                    <span className={`source-tag ${item.source === "records" ? "auto" : "manual"}`}>{sourceLabel(item.source)}</span>
                  </div>
                  <p>{item.text}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      )}

      {saved && <p className="save-toast">{saved}</p>}
    </section>
  );
}

function SuggestionGroup({ title, items, nameKey }: { title: string; items: ContextItem[]; nameKey: keyof ContextItem }) {
  if (!items.length) return null;
  return (
    <div className="suggestion-group">
      <h3>{title}</h3>
      {items.slice(0, 4).map((item) => (
        <div className="suggestion-item" key={item.id ?? String(item[nameKey])}>
          <strong>{String(item[nameKey] ?? "")}</strong>
          {item.notes && <span>{item.notes}</span>}
          {item.evidence_excerpt && <blockquote>{item.evidence_excerpt}</blockquote>}
        </div>
      ))}
    </div>
  );
}

function ListEditor({
  title,
  items,
  setItems,
  fields,
  onSave
}: {
  title: string;
  items: ContextItem[];
  setItems: (items: ContextItem[]) => void;
  fields: [keyof ContextItem, string][];
  onSave: () => void;
}) {
  return (
    <div className="soft-card form-card">
      <h2>{title}</h2>
      <div className="editable-list">
        {items.map((item, index) => (
          <div className="editable-row" key={item.id ?? index}>
            {fields.map(([key, label]) => (
              <Field key={String(key)} label={label} value={String(item[key] ?? "")} onChange={(v) => {
                const next = [...items];
                next[index] = { ...next[index], [key]: v, source: "manual" };
                setItems(next);
              }} />
            ))}
            <span className={`source-tag ${item.source === "records" ? "auto" : "manual"}`}>{sourceLabel(item.source)}</span>
            <button className="secondary" onClick={() => setItems(items.filter((_, i) => i !== index))}>Remove</button>
          </div>
        ))}
      </div>
      <div className="button-row">
        <button className="secondary" onClick={() => setItems([...items, { source: "manual" }])}>Add row</button>
        <button className="primary" onClick={onSave}>Save</button>
      </div>
    </div>
  );
}

function Field({ label, value, placeholder, onChange }: { label: string; value?: string; placeholder?: string; onChange: (v: string) => void }) {
  return (
    <label className="field">
      {label}
      <input value={value ?? ""} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />
    </label>
  );
}

function Area({ label, value, placeholder, onChange }: { label: string; value: string; placeholder?: string; onChange: (v: string) => void }) {
  return (
    <label className="field field-wide">
      {label}
      <textarea value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />
    </label>
  );
}

function SourceHint({ source }: { source?: string }) {
  if (!source) return null;
  return <p className="source-hint">Main goal source: <strong>{sourceLabel(source)}</strong></p>;
}

async function put<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!response.ok) throw new Error(`${response.status}`);
  return response.json();
}
