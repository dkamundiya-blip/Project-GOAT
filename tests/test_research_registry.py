"""
Project GOAT v0.9 — Dedicated Unit Tests for Scientific Hypothesis Registry Engine
"""

import pytest

from goat.research.core.enums import (
    EvidenceLevel,
    HypothesisPriority,
    HypothesisStatus,
)
from goat.research.registry.engine import ScientificHypothesisRegistry


@pytest.fixture
def registry():
    return ScientificHypothesisRegistry()


@pytest.mark.parametrize("idx", range(1, 15))
def test_register_hypothesis_success(registry: ScientificHypothesisRegistry, idx: int):
    title = f"Hypothesis Title #{idx}"
    hyp, val = registry.register_hypothesis(
        title=title,
        research_question=f"Does factor #{idx} yield alpha?",
        null_hypothesis=f"H0: Factor #{idx} has zero expectancy.",
        alternative_hypothesis=f"H1: Factor #{idx} has positive expectancy.",
        expected_behaviour=f"Behaviour for factor #{idx}.",
        success_criteria=["p < 0.01"],
        failure_criteria=["p >= 0.05"],
        author=f"AUTHOR_{idx}",
        tags=[f"tag_{idx}", "test"],
    )

    assert hyp.hypothesis_id.startswith("HYP_")
    assert hyp.title == title
    assert hyp.status == HypothesisStatus.DRAFT
    assert val.is_valid is True
    assert registry.get_hypothesis(hyp.hypothesis_id) is not None


@pytest.mark.parametrize("status", list(HypothesisStatus))
def test_hypothesis_status_transitions(registry: ScientificHypothesisRegistry, status: HypothesisStatus):
    hyp, _ = registry.register_hypothesis(
        title="Transition Test Hypothesis",
        research_question="Status transition question?",
        null_hypothesis="H0: Random walk.",
        alternative_hypothesis="H1: Alpha pattern.",
        expected_behaviour="Expected behaviour.",
        success_criteria=["p < 0.01"],
    )

    updated_hyp, app = registry.transition_status(
        hypothesis_id=hyp.hypothesis_id,
        target_status=status,
        actor="CHIEF_SCIENTIST",
        notes=f"Transitioning to {status.value}",
    )

    assert updated_hyp.status == status
    assert app.status == status
    assert app.approver == "CHIEF_SCIENTIST"
    assert app.approval_id.startswith("HAP_")


@pytest.mark.parametrize("rev_count", range(1, 10))
def test_hypothesis_revision_updates(registry: ScientificHypothesisRegistry, rev_count: int):
    hyp, _ = registry.register_hypothesis(
        title="Base Hypothesis Title",
        research_question="Base Question?",
        null_hypothesis="H0: Base H0 Statement.",
        alternative_hypothesis="H1: Base H1 Statement.",
        expected_behaviour="Base Expected Behaviour.",
        success_criteria=["p < 0.01"],
    )

    for r in range(1, rev_count + 1):
        updated_hyp, rev = registry.update_hypothesis(
            hypothesis_id=hyp.hypothesis_id,
            change_summary=f"Applying revision update #{r}",
            author=f"AUTHOR_REV_{r}",
            title=f"Base Hypothesis Title (Rev {r+1})",
        )
        assert updated_hyp.revision_number == r + 1
        assert rev.revision_number == r + 1
        assert rev.revision_id.startswith("REV_")

    history = registry.get_revision_history(hyp.hypothesis_id)
    assert len(history) == rev_count + 1  # 1 initial + rev_count updates


@pytest.mark.parametrize("search_status", [HypothesisStatus.DRAFT, HypothesisStatus.APPROVED, HypothesisStatus.REJECTED])
@pytest.mark.parametrize("priority", [HypothesisPriority.NORMAL, HypothesisPriority.HIGH])
def test_search_registry_filtering(
    registry: ScientificHypothesisRegistry,
    search_status: HypothesisStatus,
    priority: HypothesisPriority,
):
    registry.register_hypothesis(
        title="Search Target Alpha",
        research_question="Question Alpha?",
        null_hypothesis="H0: Alpha random.",
        alternative_hypothesis="H1: Alpha edge.",
        expected_behaviour="Behaviour Alpha.",
        success_criteria=["p < 0.01"],
        priority=priority,
    )

    results = registry.search_registry(query="Alpha", priority=priority)
    assert len(results) >= 1
    assert any("Alpha" in h.title for h in results)


def test_registry_summary_generation(registry: ScientificHypothesisRegistry):
    for i in range(5):
        registry.register_hypothesis(
            title=f"Summary Test Title #{i}",
            research_question=f"Question #{i}?",
            null_hypothesis=f"H0 #{i}",
            alternative_hypothesis=f"H1 #{i}",
            expected_behaviour=f"Behaviour #{i}",
            success_criteria=["p < 0.01"],
        )

    summary = registry.generate_summary()
    assert summary.summary_id.startswith("HRS_")
    assert summary.total_hypotheses == 5
    assert summary.status_counts["DRAFT"] == 5
