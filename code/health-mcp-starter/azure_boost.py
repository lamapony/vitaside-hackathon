"""
Azure boost layer — stub + provider hook for the Azure integration agent.

Set VITASIDE_AZURE_MODE=live and configure endpoints to enable real calls.
Default mode: stub (local fallback, no network).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from azure_contract import (
    CONTRACT_VERSION,
    azure_enabled,
    build_payload,
    contract_info,
    validate_outbound,
)
from narrative_engine import build_local_narrative

AZURE_MODE = os.getenv("VITASIDE_AZURE_MODE", "stub").lower()
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
SHARE_URL = os.getenv("AZURE_FUNCTION_SHARE_URL", "").rstrip("/")


def is_live() -> bool:
    return AZURE_MODE == "live"


def azure_status(manifest: Dict[str, Any]) -> Dict[str, Any]:
    return {
        **contract_info(manifest),
        "mode": AZURE_MODE,
        "live_configured": {
            "openai": bool(OPENAI_ENDPOINT and OPENAI_DEPLOYMENT),
            "share_function": bool(SHARE_URL),
        },
        "implementation_module": "azure_boost.py",
        "stub_note": "Second agent implements _call_openai / _call_share_function for live mode.",
    }


def _stub_enhance(payload: Dict[str, Any]) -> Dict[str, Any]:
    ins = payload.get("local_summary", {}).get("top_insights") or []
    smart = payload.get("local_summary", {}).get("smart_analysis")
    briefing = {"top_insights": ins, "data_footprint": payload.get("local_summary", {}).get("data_footprint", {})}
    locale = payload.get("request", {}).get("locale", "en")
    if smart or ins:
        narr = build_local_narrative(briefing, smart, locale)
        return {
            "source": "local_narrative_engine",
            "contract_version": CONTRACT_VERSION,
            "narrative": narr["narrative"],
            "structured": {"insights_used": len(ins), "evidence_map": narr.get("evidence_map", [])},
            "disclaimer": narr.get("disclaimer", "Stub — enable VITASIDE_AZURE_MODE=live for Azure OpenAI."),
        }
    lines = [
        "Локальный черновик (Azure OpenAI не подключён).",
        "На основе ваших агрегированных паттернов:",
    ]
    for i in ins[:3]:
        lines.append(f"• {i.get('headline', '')}: {i.get('detail', '')[:200]}")
    cond = payload.get("local_summary", {}).get("condition_tracking")
    if cond:
        lines.append(f"• Пак «{cond.get('condition_name')}»: {cond.get('days_analyzed')} дней в выборке.")
    return {
        "source": "local_stub",
        "contract_version": CONTRACT_VERSION,
        "narrative": "\n".join(lines),
        "structured": {"insights_used": len(ins), "condition_id": (cond or {}).get("condition_id")},
        "disclaimer": "Stub response — enable VITASIDE_AZURE_MODE=live for Azure OpenAI.",
    }


def _call_openai(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Live Azure OpenAI — implement / extend by Azure integration agent."""
    if not (OPENAI_ENDPOINT and OPENAI_DEPLOYMENT and OPENAI_API_KEY):
        raise RuntimeError("Azure OpenAI not configured (AZURE_OPENAI_ENDPOINT, DEPLOYMENT, API_KEY)")

    url = f"{OPENAI_ENDPOINT}/openai/deployments/{OPENAI_DEPLOYMENT}/chat/completions?api-version=2024-02-15-preview"
    system = (
        "You enrich personal health PATTERN summaries for doctor visit prep. "
        "Never diagnose. Use only the JSON aggregates provided. Respond in the user's locale."
    )
    body = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "api-key": OPENAI_API_KEY},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    text = data["choices"][0]["message"]["content"]
    return {
        "source": "azure_openai",
        "contract_version": CONTRACT_VERSION,
        "narrative": text,
        "structured": None,
        "disclaimer": "Azure OpenAI enrichment — patterns only, not medical advice.",
    }


def enhance_insight(payload: Dict[str, Any]) -> Dict[str, Any]:
    violations = validate_outbound(payload)
    if violations:
        return {"error": "payload_validation_failed", "violations": violations}
    if payload.get("request", {}).get("operation") != "enhance_insight":
        return {"error": "wrong_operation", "expected": "enhance_insight"}

    if is_live() and OPENAI_ENDPOINT:
        try:
            return _call_openai(payload)
        except (urllib.error.URLError, RuntimeError, KeyError, json.JSONDecodeError) as e:
            return {"error": "azure_openai_failed", "message": str(e), "fallback": _stub_enhance(payload)}
    return _stub_enhance(payload)


def _stub_share(payload: Dict[str, Any]) -> Dict[str, Any]:
    fp = payload.get("data_minimization", {}).get("payload_fingerprint", "local")
    return {
        "source": "local_stub",
        "share_url": None,
        "expires_at": None,
        "upload_token_preview": f"stub-{fp}",
        "note": "Configure AZURE_FUNCTION_SHARE_URL + live mode to obtain a real link.",
    }


def _call_share_function(payload: Dict[str, Any], ttl_hours: int = 48) -> Dict[str, Any]:
    if not SHARE_URL:
        raise RuntimeError("AZURE_FUNCTION_SHARE_URL not set")
    body = {"payload": payload, "ttl_hours": ttl_hours}
    req = urllib.request.Request(
        SHARE_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def share_report(payload: Dict[str, Any], ttl_hours: int = 48) -> Dict[str, Any]:
    violations = validate_outbound(payload)
    if violations:
        return {"error": "payload_validation_failed", "violations": violations}
    if payload.get("request", {}).get("operation") != "share_report":
        return {"error": "wrong_operation", "expected": "share_report"}

    if is_live() and SHARE_URL:
        try:
            out = _call_share_function(payload, ttl_hours)
            out.setdefault("source", "azure_function")
            return out
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as e:
            return {"error": "share_upload_failed", "message": str(e), "fallback": _stub_share(payload)}
    return _stub_share(payload)


def require_azure(manifest: Dict[str, Any], operation: str) -> None:
    if not azure_enabled(manifest):
        raise RuntimeError(
            "Azure boost disabled. Issue azure-hybrid-sidecar or set enable_azure_boost: true in manifest."
        )
    allowed = contract_info(manifest)["allowed_operations"]
    if operation not in allowed:
        raise PermissionError(f"Operation '{operation}' not in manifest azure.allowed_operations")

def _stub_embed_search(payload):
    """Prototype stub for embed_search (Azure AI Search)."""
    return {
        "source": "local_stub",
        "contract_version": CONTRACT_VERSION,
        "search_results": [],
        "note": "Prototype: would send embeddings only to Azure AI Search. Configure for live.",
        "disclaimer": "Stub — enable live for real semantic search over consented embeddings.",
    }

def _stub_fhir_export(payload):
    """Prototype stub for fhir_export (Azure Health Data Services)."""
    cond = payload.get("local_summary", {}).get("condition_tracking") or {}
    return {
        "source": "local_stub",
        "contract_version": CONTRACT_VERSION,
        "fhir_resources": {
            "DocumentReference": {"status": "current", "type": "VitaSide visit bundle"},
            "Observations": [{"code": cond.get("condition_name", "health-patterns"), "value": "see local_summary"}],
        },
        "note": "Prototype: would convert minimized report to FHIR. Configure Azure Health Data Services for live.",
        "disclaimer": "Stub — patterns only, not medical records.",
    }

def embed_search(payload):
    violations = validate_outbound(payload)
    if violations:
        return {"error": "payload_validation_failed", "violations": violations}
    if payload.get("request", {}).get("operation") != "embed_search":
        return {"error": "wrong_operation", "expected": "embed_search"}
    return _stub_embed_search(payload)

def fhir_export(payload):
    violations = validate_outbound(payload)
    if violations:
        return {"error": "payload_validation_failed", "violations": violations}
    if payload.get("request", {}).get("operation") != "fhir_export":
        return {"error": "wrong_operation", "expected": "fhir_export"}
    return _stub_fhir_export(payload)

