"""
VitaSide ↔ Azure integration contract (v1.0).

Local MCP builds minimized payloads; Azure modules consume them.
Raw vault paths and full transcripts NEVER appear in outbound payloads.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
from typing import Any, Dict, List, Optional

from anonymize import anonymize_citations, anonymize_text

CONTRACT_VERSION = "1.0"

OPERATIONS = (
    "enhance_insight",   # Azure OpenAI: richer narrative from local stats
    "share_report",      # Azure Function + Blob: time-limited doctor link
    "embed_search",      # Azure AI Search: semantic retrieval (embeddings only)
    "fhir_export",       # Azure Health Data Services: FHIR bundle from report JSON
)

DEFAULT_MAX_EXCERPT = 140


def azure_enabled(manifest: Dict[str, Any]) -> bool:
    if manifest.get("enable_azure_boost") is True:
        return True
    return str(manifest.get("enable_azure_boost", "")).lower() in ("true", "1", "yes")


def allowed_operations(manifest: Dict[str, Any]) -> List[str]:
    cfg = manifest.get("azure") or {}
    ops = cfg.get("allowed_operations")
    if ops:
        return list(ops)
    if azure_enabled(manifest):
        return ["enhance_insight", "share_report"]
    return []


def _policy(manifest: Dict[str, Any]) -> Dict[str, Any]:
    cfg = (manifest.get("azure") or {}).get("data_policy") or {}
    return {
        "max_excerpt_chars": int(cfg.get("max_excerpt_chars", DEFAULT_MAX_EXCERPT)),
        "anonymize_by_default": bool(cfg.get("anonymize_by_default", True)),
        "include_signal_counts": bool(cfg.get("include_signal_counts", True)),
        "include_whatif": bool(cfg.get("include_whatif", True)),
    }


def _trim_excerpt(text: str, max_chars: int, anonymize: bool) -> str:
    t = (text or "")[:max_chars]
    return anonymize_text(t) if anonymize else t


def _sanitize_correlations(items: List[Dict], max_chars: int, anonymize: bool) -> List[Dict]:
    out = []
    for c in items[:5]:
        row = {
            "cause": c.get("cause"),
            "effect": c.get("effect"),
            "lag": c.get("lag"),
            "probability": c.get("probability"),
            "lift_ratio": c.get("lift_ratio"),
            "confidence": c.get("confidence"),
            "example_dates": (c.get("example_dates") or [])[:3],
        }
        cites = c.get("citations") or []
        if cites:
            cite = cites[0]
            row["sample_citation"] = {
                "date": cite.get("date"),
                "excerpt": _trim_excerpt(cite.get("excerpt", ""), max_chars, anonymize),
            }
        out.append(row)
    return out


def _sanitize_insights(items: List[Dict], max_chars: int, anonymize: bool) -> List[Dict]:
    out = []
    for ins in items[:5]:
        out.append({
            "rank": ins.get("rank"),
            "headline": ins.get("headline"),
            "detail": ins.get("detail"),
            "evidence_date": ins.get("evidence_date"),
            "evidence_quote": _trim_excerpt(ins.get("evidence_quote", ""), max_chars, anonymize),
            "action": ins.get("action"),
        })
    return out


def _sanitize_condition(data: Optional[Dict[str, Any]], max_chars: int, anonymize: bool) -> Optional[Dict[str, Any]]:
    if not data:
        return None
    cites = data.get("citations") or []
    if anonymize:
        cites = anonymize_citations(cites)
    return {
        "condition_id": data.get("condition_id"),
        "condition_name": data.get("condition_name"),
        "days_analyzed": data.get("days_analyzed"),
        "track_items": data.get("track_items", [])[:10],
        "metrics": data.get("metrics", [])[:10],
        "doctor_focus": data.get("doctor_focus", [])[:8],
        "citations": [
            {
                "date": c.get("date"),
                "signal": c.get("signal"),
                "excerpt": _trim_excerpt(c.get("excerpt", ""), max_chars, anonymize),
            }
            for c in cites[:5]
        ],
    }


def build_payload(
    operation: str,
    manifest: Dict[str, Any],
    *,
    analysis: Dict[str, Any],
    briefing: Optional[Dict[str, Any]] = None,
    condition: Optional[Dict[str, Any]] = None,
    whatif: Optional[Dict[str, Any]] = None,
    period_compare: Optional[Dict[str, Any]] = None,
    user_consent: bool = False,
    anonymize: bool = True,
    locale: str = "ru",
    prompt_hint: str = "",
) -> Dict[str, Any]:
    """Build a cloud-safe payload. Does NOT send anything — preview / handoff only."""
    if operation not in OPERATIONS:
        raise ValueError(f"Unknown operation: {operation}. Allowed: {OPERATIONS}")
    if operation not in allowed_operations(manifest) and azure_enabled(manifest):
        raise PermissionError(f"Operation '{operation}' not allowed in sidecar manifest")

    policy = _policy(manifest)
    max_ex = policy["max_excerpt_chars"]
    if policy["anonymize_by_default"] and anonymize is None:
        anonymize = True

    signal_counts = analysis.get("signal_counts") or analysis.get("signals") or {}
    if isinstance(signal_counts, dict):
        signal_counts = {k: v for k, v in signal_counts.items() if isinstance(v, (int, float))}

    local_summary: Dict[str, Any] = {
        "days_analyzed": analysis.get("unique_dates", 0),
        "files_scanned": analysis.get("files_scanned", 0),
        "signal_counts": signal_counts if policy["include_signal_counts"] else {},
        "temporal_correlations": _sanitize_correlations(
            analysis.get("temporal_correlations") or [], max_ex, anonymize
        ),
    }

    if briefing:
        local_summary["top_insights"] = _sanitize_insights(
            briefing.get("top_insights") or [], max_ex, anonymize
        )
        local_summary["vs_llm_note"] = briefing.get("vs_llm_note", "")

    if policy["include_whatif"] and whatif:
        local_summary["whatif"] = {
            "intervention": whatif.get("intervention"),
            "duration_days": whatif.get("duration_days"),
            "confidence": whatif.get("confidence"),
            "projected_outcomes": (whatif.get("projected_outcomes") or [])[:5],
            "disclaimer": whatif.get("disclaimer", ""),
        }

    if period_compare:
        local_summary["period_compare"] = {
            "recent_days": period_compare.get("recent_days"),
            "deltas": (period_compare.get("deltas") or period_compare.get("changes") or [])[:8],
        }

    cond = _sanitize_condition(condition, max_ex, anonymize)
    if cond:
        local_summary["condition_tracking"] = cond

    smart = analysis.get("smart_analysis")
    if smart:
        local_summary["smart_analysis"] = {
            "summary": smart.get("summary", {}),
            "attention_now": [
                {
                    "headline": a.get("headline"),
                    "detail": a.get("detail"),
                    "evidence_date": a.get("evidence_date"),
                    "evidence_quote": _trim_excerpt(a.get("evidence_quote", ""), max_ex, anonymize),
                }
                for a in (smart.get("attention_now") or [])[:4]
            ],
            "weekday_effects": (smart.get("weekday_effects") or [])[:4],
        }
        local_summary["data_footprint"] = {
            "days_analyzed": analysis.get("unique_dates", 0),
            "files_scanned": analysis.get("files_scanned", 0),
        }

    payload = {
        "contract_version": CONTRACT_VERSION,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sidecar": {
            "name": manifest.get("name"),
            "issuer": manifest.get("issuer"),
            "version": manifest.get("version"),
        },
        "consent": {
            "granted": bool(user_consent),
            "operation": operation,
            "locale": locale,
        },
        "data_minimization": {
            "raw_transcripts": False,
            "vault_paths": False,
            "anonymized": anonymize,
            "max_excerpt_chars": max_ex,
            "payload_fingerprint": "",
        },
        "local_summary": local_summary,
        "request": {
            "operation": operation,
            "locale": locale,
            "prompt_hint": (prompt_hint or "")[:500],
        },
    }
    payload["data_minimization"]["payload_fingerprint"] = payload_fingerprint(payload)
    return payload


def payload_fingerprint(payload: Dict[str, Any]) -> str:
    """Stable hash for audit logs (no PII in hash input beyond aggregates)."""
    clone = copy.deepcopy(payload)
    clone.pop("generated_at", None)
    clone.get("data_minimization", {}).pop("payload_fingerprint", None)
    raw = json.dumps(clone, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def validate_outbound(payload: Dict[str, Any]) -> List[str]:
    """Pre-flight checks before HTTP send. Returns list of violations (empty = OK)."""
    violations: List[str] = []
    if payload.get("contract_version") != CONTRACT_VERSION:
        violations.append("contract_version mismatch")
    if not payload.get("consent", {}).get("granted"):
        violations.append("consent not granted")
    blob = json.dumps(payload, ensure_ascii=False).lower()
    for forbidden in ("/users/", "omi_vault_path", "050 daily omi/conversations", ".md"):
        if forbidden in blob and forbidden != ".md":
            violations.append(f"forbidden token in payload: {forbidden}")
    ls = payload.get("local_summary", {})
    for c in ls.get("temporal_correlations", []):
        sc = c.get("sample_citation") or {}
        if sc.get("excerpt") and len(sc["excerpt"]) > DEFAULT_MAX_EXCERPT + 20:
            violations.append("excerpt too long in correlation")
    return violations


def contract_info(manifest: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "azure_enabled": azure_enabled(manifest),
        "allowed_operations": allowed_operations(manifest),
        "operations_doc": {
            "enhance_insight": "Azure OpenAI enriches local briefing (stats + short excerpts only)",
            "share_report": "Upload minimized report JSON to Azure Function → time-limited link",
            "embed_search": "Send embedding vectors + query id (no full note text by default)",
            "fhir_export": "Convert visit bundle JSON to FHIR DocumentReference + Observations",
        },
        "required_env_for_live": [
            "VITASIDE_AZURE_MODE=live",
            "AZURE_OPENAI_ENDPOINT (enhance_insight)",
            "AZURE_OPENAI_DEPLOYMENT (enhance_insight)",
            "AZURE_FUNCTION_SHARE_URL (share_report)",
        ],
        "manifest_flags": {
            "enable_azure_boost": True,
            "azure.allowed_operations": list(OPERATIONS),
            "azure.data_policy.max_excerpt_chars": DEFAULT_MAX_EXCERPT,
        },
        "docs": "docs/AZURE-CONTRACT.md",
    }
