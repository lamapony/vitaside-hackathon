import { useState } from "react";
import { DataSource, DataSourceStatus, DataSourcesResponse } from "../api";

type Props = {
  data?: DataSourcesResponse;
};

const VAULT_NOT_READY = new Set<DataSourceStatus>(["explicit_empty", "scope_blocked"]);

export function DataSources({ data }: Props) {
  const summary = data?.summary;
  const sources = data?.sources ?? [];
  const primary = summary?.primary_source;
  const vaultNotReady =
    primary && VAULT_NOT_READY.has(primary as DataSourceStatus) ? primary : undefined;
  const omiSource = sources.find((source) => source.id === "omi_vault");

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Local data catalog</p>
          <h1>Data sources</h1>
        </div>
        <p>Where VitaSide reads your health signals — all processing stays on this machine.</p>
      </div>

      {vaultNotReady && (
        <VaultNotReadyBanner
          reason={vaultNotReady as "explicit_empty" | "scope_blocked"}
          quickSetup={data?.quick_setup?.real_omi}
          omiSource={omiSource}
        />
      )}

      {summary && (
        <div className="summary-strip">
          <div className="summary-item">
            <span>Connected</span>
            <strong>{summary.connected_sources.length}</strong>
            <small>{summary.connected_sources.join(", ") || "none"}</small>
          </div>
          <div className="summary-item">
            <span>Needs setup</span>
            <strong>{summary.needs_setup.length}</strong>
            <small>{summary.needs_setup.join(", ") || "all ready"}</small>
          </div>
          {primary && (
            <div className="summary-item">
              <span>Primary</span>
              <strong>{primarySourceLabel(primary)}</strong>
            </div>
          )}
        </div>
      )}

      <div className="source-list">
        {sources.map((source) => (
          <SourceCard key={source.id} source={source} />
        ))}
        {!sources.length && (
          <div className="soft-card">
            <p className="empty">No data sources returned from the API.</p>
          </div>
        )}
      </div>
    </section>
  );
}

function SourceCard({ source }: { source: DataSource }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <article className="source-card soft-card">
      <div className="source-header">
        <div>
          <p className="eyebrow">{source.id}</p>
          <h2>{source.label}</h2>
          {source.description && source.description !== source.label && (
            <p className="source-subtitle">{source.description}</p>
          )}
        </div>
        <StatusChip status={source.status} />
      </div>

      {source.provides && source.provides.length > 0 && (
        <div className="chips">
          {source.provides.slice(0, 4).map((item) => (
            <span className="chip chip-muted" key={item}>
              {truncate(item, 48)}
            </span>
          ))}
          {source.provides.length > 4 && (
            <span className="chip chip-muted">+{source.provides.length - 4} more</span>
          )}
        </div>
      )}

      <button
        className="secondary expand-toggle"
        onClick={() => setExpanded((value) => !value)}
        aria-expanded={expanded}
      >
        {expanded ? "Hide details" : "Show setup & stats"}
      </button>

      {expanded && (
        <div className="source-details">
          {(source.setup_steps ?? source.setup_steps_ru)?.length ? (
            <div>
              <h3>Setup steps</h3>
              <ol className="setup-steps">
                {(source.setup_steps ?? source.setup_steps_ru ?? []).map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </div>
          ) : null}

          {source.stats && Object.keys(source.stats).length > 0 && (
            <div>
              <h3>Stats</h3>
              <dl className="stats-dl">
                {Object.entries(source.stats).map(([key, value]) => (
                  <div key={key}>
                    <dt>{key}</dt>
                    <dd>{formatStatValue(value)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {source.provides && source.provides.length > 0 && (
            <div>
              <h3>Provides</h3>
              <ul className="provides-list">
                {source.provides.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {source.resolved_path && (
            <p className="resolved-path">
              Path: <code>{source.resolved_path}</code>
            </p>
          )}
        </div>
      )}
    </article>
  );
}

function VaultNotReadyBanner({
  reason,
  quickSetup,
  omiSource,
}: {
  reason: "explicit_empty" | "scope_blocked";
  quickSetup?: string[];
  omiSource?: DataSource;
}) {
  const isEmpty = reason === "explicit_empty";
  const title = isEmpty
    ? "Omi vault not ready — no notes found"
    : "Omi vault not ready — sidecar scope blocks parsing";
  const detail = isEmpty
    ? "VitaSide is pointed at a real vault path, but no markdown notes were discovered. Insights stay empty until Omi exports land in the expected folders."
    : "Notes exist in your vault, but the active sidecar manifest does not grant parse access. Re-issue the sidecar or widen allowed scopes.";
  const steps =
    quickSetup?.length ? quickSetup : (omiSource?.setup_steps ?? omiSource?.setup_steps_ru ?? []);

  return (
    <div className={`vault-not-ready-banner ${isEmpty ? "vault-empty" : "vault-blocked"}`}>
      <div>
        <strong>{title}</strong>
        <p>{detail}</p>
        {omiSource?.resolved_path && (
          <p className="vault-path">
            Vault path: <code>{omiSource.resolved_path}</code>
          </p>
        )}
      </div>
      {steps.length > 0 && (
        <div>
          <p className="eyebrow">Quick setup</p>
          <ol className="setup-steps">
            {steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

function StatusChip({ status }: { status: string }) {
  const cls = statusClass(status);
  const label = statusLabel(status);
  return <span className={`status-chip ${cls}`}>{label}</span>;
}

function statusLabel(status: string): string {
  switch (status) {
    case "explicit_empty":
      return "Vault empty";
    case "scope_blocked":
      return "Scope blocked";
    case "demo_fallback":
      return "Demo fallback";
    default:
      return status.replace(/_/g, " ");
  }
}

function primarySourceLabel(id: string): string {
  switch (id) {
    case "explicit_empty":
      return "Vault empty";
    case "scope_blocked":
      return "Scope blocked";
    case "demo_fallback":
      return "Demo data";
    case "omi_vault":
      return "Omi vault";
    default:
      return id.replace(/_/g, " ");
  }
}

function statusClass(status: string) {
  if (["connected", "active", "enabled", "available"].includes(status)) return "status-connected";
  if (status === "explicit_empty") return "status-warning";
  if (status === "scope_blocked") return "status-blocked";
  if (["demo_fallback", "demo", "sparse", "default"].includes(status)) return "status-demo";
  if (["disabled", "missing", "empty", "unknown"].includes(status)) return "status-disabled";
  return "status-demo";
}

function truncate(text: string, max: number) {
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

function formatStatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
