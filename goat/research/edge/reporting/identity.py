"""
Project GOAT v0.6 — Report Deterministic Identity Computation

Implements canonical RPT_<HEX16> identity computation according to SPEC.4 architecture.
"""

from __future__ import annotations

from typing import Sequence

from goat.research.edge.canonical import compute_canonical_sha256
from goat.research.edge.reporting.exceptions import ReportIdentityError


def compute_report_id(
    validation_run_id: str,
    edge_id: str,
    policy_hash: str,
    dataset_fingerprint: str,
    hypothesis_version: str,
    evidence_payload_hashes: Sequence[str],
    context_universe_id: str = "",
    audit_id: str = "",
    report_schema_version: int = 1,
) -> str:
    """Compute deterministic canonical report identity string: RPT_<HEX16>.

    Inputs participating in scientific report identity:
    - validation_run_id
    - edge_id
    - policy_hash
    - dataset_fingerprint
    - hypothesis_version
    - evidence_payload_hashes (sorted canonically)
    - context_universe_id
    - audit_id
    - report_schema_version

    Excluded fields:
    - generated_at_utc (provenance metadata only)
    """
    if not str(validation_run_id).strip():
        raise ReportIdentityError("validation_run_id must be a non-empty string")
    if not str(edge_id).strip():
        raise ReportIdentityError("edge_id must be a non-empty string")
    if not str(policy_hash).strip():
        raise ReportIdentityError("policy_hash must be a non-empty string")

    sorted_evp = sorted([str(h).strip() for h in evidence_payload_hashes if str(h).strip()])

    payload = {
        "audit_id": str(audit_id).strip(),
        "context_universe_id": str(context_universe_id).strip(),
        "dataset_fingerprint": str(dataset_fingerprint).strip(),
        "edge_id": str(edge_id).strip(),
        "evidence_payload_hashes": sorted_evp,
        "hypothesis_version": str(hypothesis_version).strip(),
        "policy_hash": str(policy_hash).strip(),
        "report_schema_version": int(report_schema_version),
        "validation_run_id": str(validation_run_id).strip(),
    }
    digest = compute_canonical_sha256(payload, length=16)
    return f"RPT_{digest.upper()}"
