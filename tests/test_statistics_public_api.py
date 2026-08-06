"""
Project GOAT v0.9 — Comprehensive Statistics Public API & Canonical Hash Integrity Tests
"""

import pytest

import goat.statistics as statistics
from goat.statistics import (
    ConfidenceAssessment,
    ConfidenceAssessmentEngine,
    ConfidenceRepository,
    DecisionRepository,
    EvaluationConfidence,
    EvaluationDecision,
    EvaluationStatus,
    EvaluationSummary,
    ExpectancyAssessment,
    ExpectancyAssessmentEngine,
    ExpectancyRepository,
    MasterStatisticalEngine,
    ScientificDecision,
    SignificanceAssessment,
    SignificanceAssessmentEngine,
    SignificanceRepository,
    StatisticalEvaluation,
    StatisticalEvaluationEngine,
    StatisticalPersistenceContext,
    StatisticalRepository,
    SummaryRepository,
    compute_canonical_sha256,
    compute_confidence_id,
    compute_decision_id,
    compute_expectancy_id,
    compute_significance_id,
    compute_statistical_evaluation_id,
    compute_summary_id,
    generate_confidence_report,
    generate_executive_report,
    generate_expectancy_report,
    generate_json_report,
    generate_significance_report,
    generate_statistical_report,
    init_statistics_db,
    serialize_canonical_json,
)


def test_public_api_exports():
    expected_exports = [
        "ConfidenceAssessment",
        "ConfidenceAssessmentEngine",
        "ConfidenceRepository",
        "DecisionRepository",
        "EvaluationConfidence",
        "EvaluationDecision",
        "EvaluationStatus",
        "EvaluationSummary",
        "ExpectancyAssessment",
        "ExpectancyAssessmentEngine",
        "ExpectancyRepository",
        "MasterStatisticalEngine",
        "ScientificDecision",
        "SignificanceAssessment",
        "SignificanceAssessmentEngine",
        "SignificanceRepository",
        "StatisticalEvaluation",
        "StatisticalEvaluationEngine",
        "StatisticalPersistenceContext",
        "StatisticalRepository",
        "SummaryRepository",
        "compute_canonical_sha256",
        "compute_confidence_id",
        "compute_decision_id",
        "compute_expectancy_id",
        "compute_significance_id",
        "compute_statistical_evaluation_id",
        "compute_summary_id",
        "generate_confidence_report",
        "generate_executive_report",
        "generate_expectancy_report",
        "generate_json_report",
        "generate_significance_report",
        "generate_statistical_report",
        "init_statistics_db",
        "serialize_canonical_json",
    ]

    for export_name in expected_exports:
        assert hasattr(statistics, export_name)
        assert export_name in statistics.__all__

    assert len(statistics.__all__) == len(expected_exports)


@pytest.mark.parametrize("i", range(1, 1201))
def test_evaluation_id_determinism_large(i: int):
    exp_id = f"EXP_{i:016X}"
    hyp_id = f"HYP_{i:016X}"

    id1, hash1 = compute_statistical_evaluation_id(experiment_id=exp_id, hypothesis_id=hyp_id)
    id2, hash2 = compute_statistical_evaluation_id(experiment_id=exp_id, hypothesis_id=hyp_id)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("STE_")
    assert len(id1) == 20
    assert len(hash1) == 64


@pytest.mark.parametrize("c", range(1, 1201))
def test_confidence_id_determinism_large(c: int):
    ste_id = f"STE_{c:016X}"

    id1, hash1 = compute_confidence_id(evaluation_id=ste_id, confidence_level=0.95, margin_of_error=0.01 * c)
    id2, hash2 = compute_confidence_id(evaluation_id=ste_id, confidence_level=0.95, margin_of_error=0.01 * c)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("CON_")
    assert len(id1) == 20


@pytest.mark.parametrize("s", range(1, 1201))
def test_significance_id_determinism_large(s: int):
    ste_id = f"STE_{s:016X}"

    id1, hash1 = compute_significance_id(evaluation_id=ste_id, p_value=0.001 * s, test_statistic=2.5)
    id2, hash2 = compute_significance_id(evaluation_id=ste_id, p_value=0.001 * s, test_statistic=2.5)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SIG_")
    assert len(id1) == 20


@pytest.mark.parametrize("e", range(1, 1201))
def test_expectancy_id_determinism_large(e: int):
    ste_id = f"STE_{e:016X}"

    id1, hash1 = compute_expectancy_id(evaluation_id=ste_id, expected_value=0.1 * e, sample_size=100)
    id2, hash2 = compute_expectancy_id(evaluation_id=ste_id, expected_value=0.1 * e, sample_size=100)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EXP_")
    assert len(id1) == 20


@pytest.mark.parametrize("d", range(1, 1201))
def test_decision_id_determinism_large(d: int):
    ste_id = f"STE_{d:016X}"
    hyp_id = f"HYP_{d:016X}"

    id1, hash1 = compute_decision_id(evaluation_id=ste_id, decision="SUPPORTED", hypothesis_id=hyp_id)
    id2, hash2 = compute_decision_id(evaluation_id=ste_id, decision="SUPPORTED", hypothesis_id=hyp_id)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EVD_")
    assert len(id1) == 20


@pytest.mark.parametrize("u", range(1, 1201))
def test_summary_id_determinism_large(u: int):
    ts = f"2026-08-04T12:{u % 60:02d}:00Z"

    id1, hash1 = compute_summary_id(total_evaluations=u, total_decisions=u, timestamp=ts)
    id2, hash2 = compute_summary_id(total_evaluations=u, total_decisions=u, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SUM_")
    assert len(id1) == 20
