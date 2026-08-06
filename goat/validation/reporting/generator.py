"""
Project GOAT v0.7 — Validation Report Generator

Generates deterministic validation reports, summaries, audit reports,
evidence reports, and statistics reports. Supports Markdown and JSON output.
"""

from __future__ import annotations

import json
from typing import Any

from goat.research.edge.canonical import compute_canonical_sha256
from goat.validation.core.run import ValidationRun
from goat.validation.decisions.models import ValidationDecision
from goat.validation.evidence.models import ValidationEvidence
from goat.validation.reporting.models import (
    ValidationAuditReport,
    ValidationEvidenceReport,
    ValidationReport,
    ValidationStatisticsReport,
    ValidationSummary,
)
from goat.validation.statistics.scores import ValidationScores


def generate_validation_report(
    run: ValidationRun,
    decision: ValidationDecision,
    scores: ValidationScores,
    evidence_summary: dict[str, Any],
    timestamp: str = "",
) -> ValidationReport:
    """Generate deterministic ValidationReport.

    Args:
        run: Completed ValidationRun.
        decision: Final ValidationDecision.
        scores: Computed ValidationScores.
        evidence_summary: Aggregated evidence summary.
        timestamp: Optional ISO 8601 timestamp.

    Returns:
        Immutable ValidationReport.
    """
    ts = timestamp or run.completion_timestamp or "2026-01-01T00:00:00Z"
    payload = {
        "hypothesis_id": run.hypothesis_id,
        "timestamp": ts,
        "validation_run_id": run.validation_id,
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"VRPT_{digest[:16].upper()}"

    overall = evidence_summary.get("overall", evidence_summary)

    return ValidationReport(
        report_id=report_id,
        validation_run_id=run.validation_id,
        hypothesis_id=run.hypothesis_id,
        timestamp=ts,
        decision_summary=decision.decision_type.value,
        overall_confidence=scores.overall_confidence,
        evidence_count=overall.get("total_count", 0),
        scores={
            "confidence_score": scores.confidence_score,
            "evidence_score": scores.evidence_score,
            "agreement_score": scores.agreement_score,
            "reproducibility_score": scores.reproducibility_score,
            "robustness_score": scores.robustness_score,
            "stability_score": scores.stability_score,
            "validation_score": scores.validation_score,
            "overall_confidence": scores.overall_confidence,
        },
        threshold_results=decision.threshold_results,
        reasoning=decision.reasoning,
    )


def generate_validation_summary(
    run: ValidationRun,
    decision: ValidationDecision,
    scores: ValidationScores,
    evidence_count: int,
    passed_count: int = 0,
    total_thresholds: int = 0,
) -> ValidationSummary:
    """Generate compact ValidationSummary."""
    return ValidationSummary(
        hypothesis_id=run.hypothesis_id,
        decision_type=decision.decision_type.value,
        overall_confidence=scores.overall_confidence,
        evidence_count=evidence_count,
        thresholds_passed=passed_count,
        total_thresholds=total_thresholds,
    )


def generate_audit_report(
    run: ValidationRun,
    audit_events: list[dict[str, Any]],
    timestamp: str = "",
) -> ValidationAuditReport:
    """Generate deterministic ValidationAuditReport."""
    ts = timestamp or "2026-01-01T00:00:00Z"
    payload = {"report_type": "audit", "timestamp": ts, "validation_run_id": run.validation_id}
    digest = compute_canonical_sha256(payload)
    report_id = f"VAUD_{digest[:16].upper()}"

    return ValidationAuditReport(
        report_id=report_id,
        validation_run_id=run.validation_id,
        timestamp=ts,
        audit_events=audit_events,
        integrity_status="clean",
    )


def generate_evidence_report(
    run: ValidationRun,
    evidence_list: list[ValidationEvidence],
    evidence_summary: dict[str, Any],
    timestamp: str = "",
) -> ValidationEvidenceReport:
    """Generate deterministic ValidationEvidenceReport."""
    ts = timestamp or "2026-01-01T00:00:00Z"
    payload = {"report_type": "evidence", "timestamp": ts, "validation_run_id": run.validation_id}
    digest = compute_canonical_sha256(payload)
    report_id = f"VEVR_{digest[:16].upper()}"

    overall = evidence_summary.get("overall", evidence_summary)
    breakdown = [
        {
            "evidence_id": e.evidence_id,
            "evidence_type": e.evidence_type,
            "confidence": e.confidence,
            "weight": e.weight,
            "supports_hypothesis": e.supports_hypothesis,
        }
        for e in evidence_list
    ]

    return ValidationEvidenceReport(
        report_id=report_id,
        validation_run_id=run.validation_id,
        timestamp=ts,
        evidence_summary=overall,
        evidence_breakdown=breakdown,
        total_evidence=overall.get("total_count", len(evidence_list)),
        supporting_evidence=overall.get("supporting_count", 0),
        contradicting_evidence=overall.get("contradicting_count", 0),
    )


def generate_statistics_report(
    run: ValidationRun,
    scores: ValidationScores,
    timestamp: str = "",
    weights: dict[str, float] | None = None,
) -> ValidationStatisticsReport:
    """Generate deterministic ValidationStatisticsReport."""
    ts = timestamp or "2026-01-01T00:00:00Z"
    payload = {"report_type": "statistics", "timestamp": ts, "validation_run_id": run.validation_id}
    digest = compute_canonical_sha256(payload)
    report_id = f"VSTR_{digest[:16].upper()}"

    default_weights = weights or {
        "confidence": 0.20,
        "evidence": 0.15,
        "agreement": 0.20,
        "reproducibility": 0.15,
        "robustness": 0.10,
        "stability": 0.10,
        "validation": 0.10,
    }

    return ValidationStatisticsReport(
        report_id=report_id,
        validation_run_id=run.validation_id,
        timestamp=ts,
        scores={
            "confidence_score": scores.confidence_score,
            "evidence_score": scores.evidence_score,
            "agreement_score": scores.agreement_score,
            "reproducibility_score": scores.reproducibility_score,
            "robustness_score": scores.robustness_score,
            "stability_score": scores.stability_score,
            "validation_score": scores.validation_score,
            "overall_confidence": scores.overall_confidence,
        },
        score_weights=default_weights,
    )


def render_validation_markdown(
    report: ValidationReport,
    decision: ValidationDecision,
) -> str:
    """Render a validation report as Markdown.

    Args:
        report: ValidationReport instance.
        decision: ValidationDecision instance.

    Returns:
        Markdown string.
    """
    lines = [
        f"# Validation Report — {report.report_id}",
        "",
        f"**Hypothesis ID**: {report.hypothesis_id}",
        f"**Validation Run ID**: {report.validation_run_id}",
        f"**Timestamp**: {report.timestamp}",
        "",
        "## Decision",
        "",
        f"**Outcome**: {report.decision_summary}",
        f"**Overall Confidence**: {report.overall_confidence:.4f}",
        f"**Reasoning**: {report.reasoning}",
        "",
        "## Scores",
        "",
        "| Score | Value |",
        "|-------|-------|",
    ]

    for name, value in sorted(report.scores.items()):
        lines.append(f"| {name} | {value:.6f} |")

    lines.extend([
        "",
        f"## Evidence Count: {report.evidence_count}",
        "",
        f"**Decision ID**: {decision.decision_id}",
        "",
    ])

    return "\n".join(lines)


def serialize_validation_to_json(
    report: ValidationReport,
    decision: ValidationDecision,
    scores: ValidationScores,
) -> dict[str, Any]:
    """Serialize validation results to a canonical JSON dictionary.

    Returns:
        Deterministically ordered dictionary.
    """
    return {
        "decision": json.loads(decision.model_dump_json()),
        "report": json.loads(report.model_dump_json()),
        "scores": json.loads(scores.model_dump_json()),
    }
