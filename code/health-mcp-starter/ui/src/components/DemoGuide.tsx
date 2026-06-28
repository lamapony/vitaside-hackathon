/* VitaSide — DemoGuide.
 *
 * A dismissible "Judges' quick tour" panel shown on the Home page (and
 * re-openable via the "Demo tour" link in the sidebar). It tells judges exactly
 * what to look at and links to each key feature, so the demo is self-documenting
 * whether judges click through the deployed demo URL or watch the live pitch.
 */
import { useEffect, useState } from "react";
import type { TabId } from "./Sidebar";
import { ArrowRight, X, MapPin } from "lucide-react";

const DISMISS_KEY = "vitaside_demo_guide_dismissed";
const OPEN_EVENT = "vitaside:open-demo-guide";

type Step = {
  n: number;
  tab?: TabId;
  title: string;
  look: string;
};

const STEPS: Step[] = [
  {
    n: 1,
    title: "This page — grounded insight",
    look: "Hero shows a real pattern (\"Stress → sleep…\") with a dated citation from your notes — not a guess. The \"Why not ChatGPT?\" card = source-cited, not generated.",
  },
  {
    n: 2,
    tab: "capture",
    title: "Add data — docs & voice",
    look: "Upload a health doc; VitaSide extracts dated signals locally. Or dictate a voice note (mic). Nothing is uploaded.",
  },
  {
    n: 3,
    tab: "timeline",
    title: "Timeline — 90-day signals",
    look: "Calendar heatmap of signals + a weekly frequency trend chart. Click a day for the cited excerpt.",
  },
  {
    n: 4,
    tab: "smart",
    title: "Smart view — N-of-1 analysis",
    look: "Personal baselines (your bands, not population averages), lag correlations, and a plain-language narrative with an evidence map.",
  },
  {
    n: 5,
    tab: "doctor",
    title: "Doctor handoff — visit packet",
    look: "Cited questions + clinical summary. \"Print / Save as PDF\" produces a clinician handoff. \"Preview what is sent\" shows the Azure data-minimization contract.",
  },
  {
    n: 6,
    tab: "sidecar",
    title: "Sidecar & audit — the differentiator",
    look: "Local-only, manifest-gated, TTL-scoped, revocable. Every read is logged as metadata (audit tail) — no raw notes, no cloud by default.",
  },
];

type Props = {
  onNavigate: (tab: TabId) => void;
};

export function DemoGuide({ onNavigate }: Props) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    try {
      if (localStorage.getItem(DISMISS_KEY) !== "1") setShow(true);
    } catch {
      setShow(true);
    }
    const handler = () => {
      try { localStorage.removeItem(DISMISS_KEY); } catch { /* ignore */ }
      setShow(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
    };
    window.addEventListener(OPEN_EVENT, handler);
    return () => window.removeEventListener(OPEN_EVENT, handler);
  }, []);

  if (!show) return null;

  function dismiss() {
    try { localStorage.setItem(DISMISS_KEY, "1"); } catch { /* ignore */ }
    setShow(false);
  }

  return (
    <div className="demo-guide" role="region" aria-label="Judges' quick tour">
      <div className="demo-guide-head">
        <div>
          <p className="eyebrow"><MapPin size={12} style={{ verticalAlign: -2, marginRight: 4 }} />Judges' quick tour</p>
          <h2>What to look at</h2>
        </div>
        <button type="button" className="demo-guide-close" onClick={dismiss} aria-label="Dismiss tour">
          <X size={16} /> Dismiss
        </button>
      </div>
      <p className="demo-guide-intro">
        VitaSide is a local-first health pattern intelligence sidecar. Here are the six things worth
        seeing — open each in order.
      </p>
      <ol className="demo-guide-steps">
        {STEPS.map((step) => (
          <li className="demo-guide-step" key={step.n}>
            <span className="demo-guide-num">{step.n}</span>
            <div className="demo-guide-body">
              <strong>{step.title}</strong>
              <p>{step.look}</p>
              {step.tab && (
                <button type="button" className="action-link" onClick={() => onNavigate(step.tab as TabId)}>
                  Open <ArrowRight size={13} />
                </button>
              )}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

export function openDemoGuide() {
  window.dispatchEvent(new Event(OPEN_EVENT));
}
