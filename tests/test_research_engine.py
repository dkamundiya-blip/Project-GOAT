"""
Project GOAT v0.9 — Dedicated Unit Tests for Scientific Research Engine Facade
"""

import pytest

from goat.research.core.enums import HypothesisStatus
from goat.research.engine import ScientificResearchEngine
from goat.research.persistence.sqlite import ResearchPersistenceContext


@pytest.fixture
def memory_context():
    ctx = ResearchPersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.fixture
def research_engine(memory_context):
    return ScientificResearchEngine(persistence_context=memory_context)


@pytest.mark.parametrize("idx", range(1, 10))
def test_engine_register_and_persist(research_engine: ScientificResearchEngine, idx: int):
    title = f"Engine Test Title #{idx}"
    hyp, val = research_engine.register_hypothesis(
        title=title,
        research_question=f"Does question #{idx} work?",
        null_hypothesis=f"H0 #{idx}",
        alternative_hypothesis=f"H1 #{idx}",
        expected_behaviour=f"Behaviour #{idx}",
        success_criteria=["p < 0.01"],
    )

    assert hyp.title == title
    assert val.is_valid is True
    assert research_engine.persistence is not None

    fetched = research_engine.persistence.hypotheses.get_by_id(hyp.hypothesis_id)
    assert fetched is not None
    assert fetched.hypothesis_id == hyp.hypothesis_id


@pytest.mark.parametrize("status", [HypothesisStatus.APPROVED, HypothesisStatus.REJECTED, HypothesisStatus.RETIRED])
def test_engine_status_workflow(research_engine: ScientificResearchEngine, status: HypothesisStatus):
    hyp, _ = research_engine.register_hypothesis(
        title="Workflow Target Title",
        research_question="Workflow question?",
        null_hypothesis="H0 Workflow",
        alternative_hypothesis="H1 Workflow",
        expected_behaviour="Behaviour Workflow",
        success_criteria=["p < 0.01"],
    )

    if status == HypothesisStatus.APPROVED:
        updated_hyp, app = research_engine.approve_hypothesis(hyp.hypothesis_id, approver="BOARD_MEMBER")
    elif status == HypothesisStatus.REJECTED:
        updated_hyp, app = research_engine.reject_hypothesis(hyp.hypothesis_id, reviewer="REVIEWER_A")
    else:
        updated_hyp, app = research_engine.retire_hypothesis(hyp.hypothesis_id, reviewer="REVIEWER_B")

    assert updated_hyp.status == status
    assert app.status == status
    assert research_engine.get_hypothesis(hyp.hypothesis_id).status == status


def test_engine_report_generation(research_engine: ScientificResearchEngine):
    hyp, _ = research_engine.register_hypothesis(
        title="Report Target Title",
        research_question="Report question?",
        null_hypothesis="H0 Report",
        alternative_hypothesis="H1 Report",
        expected_behaviour="Behaviour Report",
        success_criteria=["p < 0.01"],
    )

    reports = research_engine.generate_reports(hyp.hypothesis_id)
    assert "markdown" in reports
    assert "json" in reports
    assert "executive" in reports
    assert hyp.title in reports["markdown"]
