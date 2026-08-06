"""
Project GOAT v0.9 — Comprehensive Dedicated Unit Tests for Research Models
"""

import pytest
from pydantic import ValidationError

from goat.research.core.canonical import (
    compute_approval_id,
    compute_canonical_sha256,
    compute_hypothesis_id,
    compute_revision_id,
    compute_summary_id,
    compute_validation_id,
    serialize_canonical_json,
)
from goat.research.core.enums import (
    EvidenceLevel,
    HypothesisPriority,
    HypothesisStatus,
)
from goat.research.core.models import (
    HypothesisApproval,
    HypothesisRegistrySummary,
    HypothesisRevision,
    HypothesisValidation,
    ScientificHypothesis,
)


@pytest.mark.parametrize("status", list(HypothesisStatus))
@pytest.mark.parametrize("priority", list(HypothesisPriority))
@pytest.mark.parametrize("evidence_level", list(EvidenceLevel))
@pytest.mark.parametrize("rev_num", range(1, 10))
def test_scientific_hypothesis_model_instantiation(
    status: HypothesisStatus,
    priority: HypothesisPriority,
    evidence_level: EvidenceLevel,
    rev_num: int,
):
    hyp_id, canonical_hash = compute_hypothesis_id(
        title=f"Test Title {rev_num}",
        null_hypothesis="H0: Market is random walk with zero expectancy.",
        alternative_hypothesis="H1: Market exhibits non-random structural alpha.",
        author="TEST_AUTHOR",
    )

    hyp = ScientificHypothesis(
        hypothesis_id=hyp_id,
        title=f"Test Title {rev_num}",
        research_question="Does the market exhibit structural volatility expansion?",
        null_hypothesis="H0: Market is random walk with zero expectancy.",
        alternative_hypothesis="H1: Market exhibits non-random structural alpha.",
        expected_behaviour="Volatility expansion following quiet regime consolidation.",
        independent_variables=["atr_14", "vol_ratio"],
        dependent_variables=["forward_return_10"],
        assumptions=["Continuous liquidity", "Normal execution"],
        risk_statement="Tail risk occurs during unexpected macro gap events.",
        success_criteria=["p < 0.01", "expectancy > 0.5"],
        failure_criteria=["p >= 0.05", "drawdown > 3.0%"],
        author="TEST_AUTHOR",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        status=status,
        priority=priority,
        evidence_level=evidence_level,
        revision_number=rev_num,
        tags=["volatility", "regime"],
        metadata={"test_key": "test_val"},
        canonical_hash=canonical_hash,
    )

    assert hyp.hypothesis_id == hyp_id
    assert hyp.status == status
    assert hyp.priority == priority
    assert hyp.evidence_level == evidence_level
    assert hyp.revision_number == rev_num
    assert len(hyp.independent_variables) == 2


@pytest.mark.parametrize("invalid_id", ["INVALID_ID", "HYP_SHORT", "123_HYP", "SIG_1234567890ABCDEF"])
def test_scientific_hypothesis_invalid_id_pattern(invalid_id: str):
    with pytest.raises(ValidationError):
        ScientificHypothesis(
            hypothesis_id=invalid_id,
            title="Valid Title",
            research_question="Valid Research Question?",
            null_hypothesis="Valid Null Hypothesis",
            alternative_hypothesis="Valid Alternative Hypothesis",
            expected_behaviour="Valid Expected Behaviour",
            created_timestamp="2026-08-04T12:00:00Z",
            updated_timestamp="2026-08-04T12:00:00Z",
        )


def test_scientific_hypothesis_immutability():
    hyp_id, canonical_hash = compute_hypothesis_id(
        title="Immutable Title",
        null_hypothesis="Valid H0",
        alternative_hypothesis="Valid H1",
    )
    hyp = ScientificHypothesis(
        hypothesis_id=hyp_id,
        title="Immutable Title",
        research_question="Valid Question?",
        null_hypothesis="Valid H0",
        alternative_hypothesis="Valid H1",
        expected_behaviour="Valid Behaviour",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    with pytest.raises(ValidationError):
        hyp.title = "New Title"  # Frozen check


@pytest.mark.parametrize("rev_num", range(1, 20))
def test_hypothesis_revision_model(rev_num: int):
    hyp_id, _ = compute_hypothesis_id(title="Title", null_hypothesis="H0", alternative_hypothesis="H1")
    rev_id, rev_hash = compute_revision_id(
        hypothesis_id=hyp_id,
        revision_number=rev_num,
        previous_hash="PREV_HASH",
        timestamp="2026-08-04T12:00:00Z",
    )

    rev = HypothesisRevision(
        revision_id=rev_id,
        hypothesis_id=hyp_id,
        revision_number=rev_num,
        previous_hash="PREV_HASH",
        change_summary=f"Revision change #{rev_num}",
        author="QUANT_DEV",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=rev_hash,
    )

    assert rev.revision_id == rev_id
    assert rev.revision_number == rev_num
    assert rev.hypothesis_id == hyp_id


@pytest.mark.parametrize("is_valid", [True, False])
@pytest.mark.parametrize("idx", range(1, 10))
def test_hypothesis_validation_model(is_valid: bool, idx: int):
    hyp_id, _ = compute_hypothesis_id(title=f"Title {idx}", null_hypothesis="H0", alternative_hypothesis="H1")
    val_id, val_hash = compute_validation_id(
        hypothesis_id=hyp_id,
        reviewer="TEST_REVIEWER",
        timestamp="2026-08-04T12:00:00Z",
        is_valid=is_valid,
    )

    val = HypothesisValidation(
        validation_id=val_id,
        hypothesis_id=hyp_id,
        is_valid=is_valid,
        validation_rule_results=[{"rule": "VAL_001", "passed": is_valid}],
        validation_errors=[] if is_valid else ["Validation error detected"],
        validation_warnings=["Warning 1"],
        reviewer="TEST_REVIEWER",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=val_hash,
    )

    assert val.validation_id == val_id
    assert val.is_valid == is_valid


@pytest.mark.parametrize("status", list(HypothesisStatus))
def test_hypothesis_approval_model(status: HypothesisStatus):
    hyp_id, _ = compute_hypothesis_id(title="Title", null_hypothesis="H0", alternative_hypothesis="H1")
    app_id, app_hash = compute_approval_id(
        hypothesis_id=hyp_id,
        approver="CHIEF_SCIENTIST",
        status=status.value,
        timestamp="2026-08-04T12:00:00Z",
    )

    app = HypothesisApproval(
        approval_id=app_id,
        hypothesis_id=hyp_id,
        approver="CHIEF_SCIENTIST",
        status=status,
        approval_notes=f"Approved with status {status.value}",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=app_hash,
    )

    assert app.approval_id == app_id
    assert app.status == status


@pytest.mark.parametrize("total_count", [0, 1, 10, 50, 100])
def test_hypothesis_registry_summary_model(total_count: int):
    sum_id, sum_hash = compute_summary_id(
        total_hypotheses=total_count,
        timestamp="2026-08-04T12:00:00Z",
    )

    summary = HypothesisRegistrySummary(
        summary_id=sum_id,
        total_hypotheses=total_count,
        status_counts={"DRAFT": total_count},
        priority_counts={"NORMAL": total_count},
        evidence_level_counts={"L0": total_count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )

    assert summary.summary_id == sum_id
    assert summary.total_hypotheses == total_count
