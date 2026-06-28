import { Loader2 } from "lucide-react";

export function Loading({ label = "Loading local patterns…" }: { label?: string }) {
  return (
    <div className="loading">
      <Loader2 className="animate-spin" size={20} style={{ marginRight: 8 }} />
      <span>{label}</span>
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="error-box" role="alert">
      <strong>Something needs attention</strong>
      <p>{message}</p>
    </div>
  );
}

const FRIENDLY_ENDPOINT: Record<string, string> = {
  briefing: "summary",
  timeline: "timeline",
  sidecar: "sidecar status",
  "condition-packs": "conditions",
  "user-context": "your context",
  questions: "visit questions",
  "next-steps": "next steps",
};

export function PartialErrorBanner({ endpoints }: { endpoints: string[] }) {
  if (!endpoints.length) return null;
  const labels = endpoints.map((e) => FRIENDLY_ENDPOINT[e] ?? e);
  return (
    <div className="error-box partial-error" role="status">
      <strong>Some data is unavailable</strong>
      <p>{labels.join(", ")}</p>
    </div>
  );
}
