"""Minimal FHIR R4 bundle for PGHD handoff — binned summaries, not raw transcripts."""
from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional


def _uid() -> str:
    return str(uuid.uuid4())


def _observation(
    code: str,
    display: str,
    value: Any,
    effective: str,
    system: str = "http://loinc.org",
) -> Dict[str, Any]:
    res: Dict[str, Any] = {
        "resourceType": "Observation",
        "id": _uid(),
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "activity",
                "display": "Activity",
            }]
        }],
        "code": {"coding": [{"system": system, "code": code, "display": display}]},
        "effectiveDateTime": effective,
    }
    if isinstance(value, (int, float)):
        res["valueQuantity"] = {"value": value, "unit": "1", "system": "http://unitsofmeasure.org", "code": "1"}
    else:
        res["valueString"] = str(value)
    return res


def build_fhir_bundle(
    clinical_summary: Dict[str, Any],
    patient_ref: str = "Patient/vitaside-local",
    anonymize: bool = False,
) -> Dict[str, Any]:
    """PGHD bundle: Patient stub, weekly-binned Observations, DocumentReference summary."""
    today = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    patient_id = _uid()
    patient = {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {"tag": [{"system": "https://vitaside.local", "code": "local-first"}]},
        "identifier": [{"system": "https://vitaside.local/patient", "value": "local-user"}],
    }
    if anonymize:
        patient.pop("identifier", None)

    entries: List[Dict[str, Any]] = [{"fullUrl": f"urn:uuid:{patient_id}", "resource": patient}]

    for trend in clinical_summary.get("trends") or []:
        obs = _observation(
            code="vitaside-signal-trend",
            display=f"Signal trend: {trend.get('label')}",
            value=f"recent={trend.get('recent_14d')} prior={trend.get('prior_14d')} delta={trend.get('delta')}",
            effective=today,
            system="https://vitaside.local/codes",
        )
        entries.append({"fullUrl": f"urn:uuid:{obs['id']}", "resource": obs})

    for i, pat in enumerate(clinical_summary.get("top_patterns") or []):
        cite = pat.get("citation") or {}
        excerpt = (cite.get("excerpt") or "")[:120]
        if anonymize:
            excerpt = "[redacted]"
        obs = _observation(
            code="vitaside-pattern",
            display=f"{pat.get('cause')}->{pat.get('effect')}",
            value=f"lag={pat.get('lag_days')}d lift={pat.get('lift')} excerpt={excerpt}",
            effective=cite.get("date") or today,
            system="https://vitaside.local/codes",
        )
        entries.append({"fullUrl": f"urn:uuid:{obs['id']}", "resource": obs})

    doc_id = _uid()
    doc_ref = {
        "resourceType": "DocumentReference",
        "id": doc_id,
        "status": "current",
        "type": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "11506-3",
                "display": "Progress note",
            }]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "date": today,
        "description": clinical_summary.get("headline", "VitaSide clinical summary"),
        "content": [{
            "attachment": {
                "contentType": "application/json",
                "title": "VitaSide clinical summary (binned)",
                "data": None,
            }
        }],
        "meta": {
            "tag": [{"system": "https://vitaside.local", "code": "pghd-binned"}],
        },
    }
    entries.append({"fullUrl": f"urn:uuid:{doc_id}", "resource": doc_ref})

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": today,
        "entry": entries,
        "meta": {
            "tag": [
                {"system": "https://vitaside.local", "code": "vitaside-fhir-v1"},
                {"system": "https://vitaside.local", "code": "no-raw-transcripts"},
            ],
        },
        "policy": {
            "binning": "weekly_trends_and_top_patterns_only",
            "entry_count": len(entries),
            "anonymized": anonymize,
        },
    }
