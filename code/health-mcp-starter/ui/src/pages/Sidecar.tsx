/* VitaSide — Sidecar & audit page.
 *
 * Surfaces the manifest-gated, local-only, audited differentiator that the
 * runbook demo checklist asks for ("Show manifest, local-only, no network" +
 * "Show audit.log tail"). Pure frontend: reads the /api/sidecar payload the
 * app already loads (works in live and demo mode). No backend dependency.
 */
import type { Sidecar } from "../api";
import { ShieldCheck, Lock, ScrollText, FileText, Activity } from "lucide-react";

type Props = { sidecar?: Sidecar };

function StatusBadge({ sidecar }: { sidecar: Sidecar }) {
  if (sidecar.revoked) {
    return <span className="status-chip status-blocked">Revoked</span>;
  }
  if (sidecar.expired) {
    return <span className="status-chip status-warning">Expired</span>;
  }
  return <span className="status-chip status-connected">Active</span>;
}

export function SidecarPage({ sidecar }: Props) {
  if (!sidecar) {
    return (
      <section className="page-grid">
        <div className="soft-card">
          <p className="meta">Loading sidecar status…</p>
        </div>
      </section>
    );
  }

  const scopes = sidecar.allowed_scopes ?? [];
  const tools = sidecar.tools ?? [];
  const audit = sidecar.audit;
  const toolsUsed = audit?.tools_used ?? {};
  const toolEntries = Object.entries(toolsUsed).sort((a, b) => b[1] - a[1]);

  return (
    <section className="page-grid fade-in">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Local-only · manifest-gated · audited</p>
          <h1>Sidecar &amp; audit</h1>
        </div>
        <p>
          The VitaSide sidecar runs as a scoped, temporary MCP tool server. Every read is manifest-checked and
          logged as metadata. No outbound network by default.
        </p>
      </div>

      <div className="summary-strip">
        <div className="summary-item">
          <span>Status</span>
          <strong>{sidecar.revoked ? "Revoked" : sidecar.expired ? "Expired" : "Active"}</strong>
          <small>{sidecar.name ?? "—"}</small>
        </div>
        <div className="summary-item">
          <span>Tools allowed</span>
          <strong>{tools.length}</strong>
          <small>manifest allowlist</small>
        </div>
        <div className="summary-item">
          <span>Scoped paths</span>
          <strong>{scopes.length}</strong>
          <small>read under manifest only</small>
        </div>
        <div className="summary-item">
          <span>Audit entries</span>
          <strong>{audit?.entries ?? 0}</strong>
          <small>metadata only</small>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Manifest</p>
            <div className="card-title">Sidecar manifest</div>
          </div>
          <ShieldCheck size={18} />
        </div>
        <div className="stats-row" style={{ marginBottom: 16 }}>
          <div className="stat-card">
            <span>Issuer</span>
            <strong>{sidecar.issuer ?? "—"}</strong>
          </div>
          <div className="stat-card">
            <span>Expires at</span>
            <strong>{sidecar.expires_at ? sidecar.expires_at.slice(0, 10) : "—"}</strong>
          </div>
          <div className="stat-card">
            <span>State</span>
            <strong><StatusBadge sidecar={sidecar} /></strong>
          </div>
        </div>
        <div className="meta" style={{ marginBottom: 12 }}>
          <Lock size={13} style={{ verticalAlign: -2, marginRight: 6 }} />
          No outbound network by default. Cloud LLM is opt-in, gated by a data-minimization contract.
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Allowed scopes</p>
            <div className="card-title">Where the sidecar may read</div>
          </div>
          <FileText size={18} />
        </div>
        {scopes.length === 0 && <div className="meta">No scopes declared.</div>}
        {scopes.map((scope, i) => (
          <div key={`${scope.path}-${i}`} className="trend-row" style={{ marginBottom: 8 }}>
            <div className="trend-label">
              <strong style={{ fontFamily: "ui-monospace, Menlo, monospace", fontSize: 13 }}>{scope.path}</strong>
            </div>
            <div className="trend-values">
              {(scope.permissions ?? []).map((p) => (
                <span key={p} className="chip chip-muted">{p}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Tool allowlist</p>
            <div className="card-title">Tools the manifest permits</div>
          </div>
          <Activity size={18} />
        </div>
        <div className="chips">
          {tools.map((tool) => (
            <span key={tool} className="chip chip-muted">{tool}</span>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Audit activity</p>
            <div className="card-title">Tool usage (metadata only — no raw note text)</div>
          </div>
          <ScrollText size={18} />
        </div>
        {toolEntries.length === 0 && <div className="meta">No tool usage recorded yet.</div>}
        {toolEntries.length > 0 && (
          <div className="trend-list">
            {toolEntries.map(([tool, count]) => (
              <div key={tool} className="trend-row">
                <div className="trend-label">
                  <strong>{tool}</strong>
                </div>
                <div className="trend-values">
                  <span className="trend-delta">{count} call{count === 1 ? "" : "s"}</span>
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="meta" style={{ marginTop: 12 }}>
          Audit log records paths and counts only — never raw note text. Azure ops log fingerprints only.
        </div>
      </div>

      <div className="disclaimer">
        Quality gates on every analysis output: confidence, dated citations, and disclaimer. The sidecar is
        temporary (TTL-scoped) and revocable. This page shows metadata for trust review, not personal health data.
      </div>
    </section>
  );
}
