"""
Project GOAT v0.6 — Canonical Serialization & Presentation Rendering

Provides deterministic JSON serialization primitives and Markdown report presentation rendering.
"""

from __future__ import annotations

import json
import math
from typing import Any

from goat.research.edge.canonical import canonical_json
from goat.research.edge.reporting.exceptions import ReportBuildError
from goat.research.edge.reporting.models import ValidationReport


def _verify_no_nan_inf(obj: Any) -> None:
    """Recursively check that no float in obj is NaN or Infinity."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ReportBuildError("Report JSON serialization rejected invalid float value (NaN or Infinity)")
    elif isinstance(obj, dict):
        for v in obj.values():
            _verify_no_nan_inf(v)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _verify_no_nan_inf(item)


def serialize_report_to_json(report: ValidationReport) -> str:
    """Serialize ValidationReport to canonical, deterministic UTF-8 JSON string."""
    dict_repr = report.model_dump(mode="json")
    _verify_no_nan_inf(dict_repr)
    return json.dumps(dict_repr, indent=2, sort_keys=True, ensure_ascii=False)


def render_report_markdown(report: ValidationReport) -> str:
    """Render human-readable Markdown report document from ValidationReport."""
    lines = [
        "# Project GOAT v0.6 — Scientific Edge Validation Report",
        "",
        f"**Report ID**               : `{report.report_id}`",
        f"**Validation Run ID**       : `{report.validation_run_id}`",
        f"**Generated At (UTC)**      : `{report.generated_at_utc}`",
        f"**Overall Decision**        : **{report.validation_summary.overall_decision}**",
        f"**Lifecycle State**         : `{report.validation_summary.lifecycle_state}`",
        f"**Highest Completed Stage** : `{report.validation_summary.highest_completed_stage}`",
        "",
        "## Candidate Edge Identity",
        "",
        f"- **Edge ID**                  : `{report.edge_identity.edge_id}`",
        f"- **Proposition Name**         : {report.edge_identity.proposition_name}",
        f"- **Causal Primitive**         : `{report.edge_identity.causal_primitive}`",
        f"- **Target Feature**           : `{report.edge_identity.target_feature}`",
        f"- **Economic Rationale**       : `{report.edge_identity.economic_rationale_category}`",
        "",
        "## Hypothesis & Parameterization",
        "",
        f"- **Hypothesis Version**       : `{report.hypothesis_identity.hypothesis_version}`",
        f"- **Forward Outcome Metric**   : `{report.hypothesis_identity.forward_outcome_metric}`",
        f"- **Forward Horizon**          : {report.hypothesis_identity.forward_horizon} bars",
        "",
        "## Validation Policy Specification",
        "",
        f"- **Policy Hash**              : `{report.policy_specification.policy_hash}`",
        f"- **Policy ID**                : `{report.policy_specification.policy_id}`",
        f"- **Multiplicity Strategy**    : `{report.policy_specification.multiplicity_strategy}`",
        f"- **Meta-Analysis Method**     : `{report.policy_specification.meta_analysis_method}`",
        f"- **Stage A Alpha / Threshold** : `{report.policy_specification.stage_a_alpha}` / `{report.policy_specification.stage_a_effect_min}`",
        "",
        "## Data Provenance",
        "",
        f"- **Dataset Fingerprint**      : `{report.data_provenance.dataset_fingerprint}`",
        f"- **Candidate Target Scope**   : `{report.data_provenance.candidate_target_scope}`",
        f"- **Context Universe ID**      : `{report.data_provenance.context_universe_id or 'N/A'}`",
        "",
        "## Stage Execution Summary",
        "",
    ]

    for stg in report.stage_results:
        status_icon = "✓ PASS" if stg.decision == "PASS" else f"✗ {stg.decision}"
        lines.append(f"### Stage {stg.stage} — {status_icon}")
        lines.append(f"- **Decision**       : `{stg.decision}`")
        lines.append(f"- **Reason Code**    : `{stg.reason_code}`")
        if stg.explanation:
            lines.append(f"- **Explanation**    : {stg.explanation}")
        lines.append(f"- **Evidence Count** : {stg.evidence_count}")
        lines.append("")

    if report.confirmatory_audit:
        lines.extend([
            "## Confirmatory Holdout Audit",
            "",
            f"- **Audit ID**                 : `{report.confirmatory_audit.audit_id}`",
            f"- **Holdout Partition**        : `{report.confirmatory_audit.holdout_partition_identity}`",
            "",
        ])

    lines.extend([
        "## Cryptographic Integrity & Audit Trail",
        "",
        f"- **Evidence Record Count**    : {report.integrity.evidence_count}",
        f"- **Report Content Hash**     : `{report.integrity.report_content_hash}`",
        f"- **Verification Status**     : **{report.integrity.verification_status}**",
        "",
    ])

    return "\n".join(lines)
