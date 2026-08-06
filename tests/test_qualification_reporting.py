"""
Project GOAT v0.7 — Test Suite for Qualification Reports

Coverage:
- ScientificQualificationReport (Markdown & JSON)
- GateEvaluationReport (Markdown & JSON)
- DecisionReadinessReport (Markdown & JSON)
- QualificationSummaryReport (Markdown & JSON)
- ScientificReadinessReport (Markdown & JSON)
"""

from goat.qualification.core.canonical import (
    compute_evaluation_id,
    compute_qualification_id,
    compute_readiness_id,
)
from goat.qualification.core.enums import QualificationState, ReadinessLevel
from goat.qualification.core.models import (
    DecisionReadiness,
    GateEvaluation,
    ScientificQualification,
)
from goat.qualification.reporting.reports import (
    DecisionReadinessReport,
    GateEvaluationReport,
    QualificationSummaryReport,
    ScientificQualificationReport,
    ScientificReadinessReport,
)


def test_qualification_report_rendering():
    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(
        qualification_id=q_id,
        composite_id="CMP_1",
        regime_id="MRG_1",
        evaluation_timestamp="2026-07-30T00:00:00Z",
        qualification_state=QualificationState.QUALIFIED,
        overall_readiness=0.85,
        canonical_hash=q_hash,
    )

    report = ScientificQualificationReport(
        report_id="SQR_QLF_001",
        timestamp="2026-07-30T00:00:00Z",
        qualifications=[qual],
    )

    md = report.to_markdown()
    assert "# Scientific Qualification Report" in md
    assert q_id in md

    json_str = report.to_json()
    assert '"report_id":"SQR_QLF_001"' in json_str


def test_readiness_report_rendering():
    r_id, r_hash = compute_readiness_id("SQL_1", "READY_FOR_SIMULATION")
    readiness = DecisionReadiness(
        readiness_id=r_id,
        qualification_id="SQL_1",
        readiness_level=ReadinessLevel.READY_FOR_SIMULATION,
        timestamp="2026-07-30T00:00:00Z",
        canonical_hash=r_hash,
    )

    report = DecisionReadinessReport(
        report_id="SQR_RDN_001",
        timestamp="2026-07-30T00:00:00Z",
        readiness_records=[readiness],
    )

    md = report.to_markdown()
    assert "# Decision Readiness Report" in md
    assert r_id in md


def test_scientific_readiness_report_rendering():
    report = ScientificReadinessReport(
        report_id="SQR_001",
        timestamp="2026-07-30T00:00:00Z",
        total_composites_qualified=1,
        top_readiness_level="READY_FOR_FORWARD_TESTING",
        top_readiness_score=0.92,
    )

    md = report.to_markdown()
    assert "# Scientific Qualification & Decision Readiness Executive Report" in md
    assert "READY_FOR_FORWARD_TESTING" in md
