import { NextStep } from "../api";
import type { TabId } from "./Sidebar";
import { ArrowRight } from "lucide-react";

type Props = {
  steps: NextStep[];
  onNavigate: (tab: TabId) => void;
};

const KIND_LABEL: Record<string, string> = {
  setup: "Setup",
  insight: "Observation",
  track: "Track",
  visit: "Visit prep",
  review: "Review",
  pattern: "Pattern",
  analysis: "Analysis"
};

function kindLabel(kind?: string): string {
  const k = kind ?? "review";
  return KIND_LABEL[k] ?? k.charAt(0).toUpperCase() + k.slice(1);
}

export function NextStepsPanel({ steps, onNavigate }: Props) {
  if (!steps.length) return null;

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Next steps</p>
          <div className="card-title">Focus this week</div>
        </div>
      </div>

      <div className="next-step-list">
        {steps.map((step, index) => (
          <div key={step.id} className="next-step-card">
            <div className="next-step-row">
              <div className="step-index">{index + 1}</div>
              <div className="next-step-content">
                <div className="next-step-heading">
                  <span className="pill">{kindLabel(step.kind)}</span>
                  <strong>{step.title}</strong>
                </div>
                <div style={{ color: "var(--ink-2)", fontSize: 14, lineHeight: 1.45 }}>{step.detail}</div>
                {step.evidence_quote && (
                  <div className="evidence" style={{ marginTop: 8, fontSize: 13 }}>
                    {step.evidence_quote}
                  </div>
                )}
                <button
                  type="button"
                  onClick={() => onNavigate(step.tab as TabId)}
                  className="action-link"
                >
                  {step.action_label} <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
