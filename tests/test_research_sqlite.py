"""
Project GOAT v0.9 — Dedicated Unit Tests for SQLite Persistence Repositories
"""

import pytest

from goat.research.core.canonical import (
    compute_approval_id,
    compute_hypothesis_id,
    compute_revision_id,
    compute_summary_id,
    compute_validation_id,
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
from goat.research.persistence.sqlite import ResearchPersistenceContext


@pytest.fixture
def persistence_ctx():
    ctx = ResearchPersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.mark.parametrize("idx", range(1, 15))
def test_hypothesis_repository_roundtrip(persistence_ctx: ResearchPersistenceContext, idx: int):
    hyp_id, canonical_hash = compute_hypothesis_id(
        title=f"SQLite Hyp #{idx}",
        null_hypothesis=f"H0: Null hypothesis statement #{idx}",
        alternative_hypothesis=f"H1: Alternative hypothesis statement #{idx}",
        author=f"AUTHOR_{idx}",
    )

    hyp = ScientificHypothesis(
        hypothesis_id=hyp_id,
        title=f"SQLite Hyp #{idx}",
        research_question=f"Question #{idx}?",
        null_hypothesis=f"H0: Null hypothesis statement #{idx}",
        alternative_hypothesis=f"H1: Alternative hypothesis statement #{idx}",
        expected_behaviour=f"Behaviour #{idx}",
        independent_variables=[f"var_{idx}"],
        dependent_variables=["ret"],
        assumptions=["Normal dist"],
        risk_statement="Tail risk statement.",
        success_criteria=["p < 0.01"],
        failure_criteria=["p >= 0.05"],
        author=f"AUTHOR_{idx}",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        status=HypothesisStatus.DRAFT,
        priority=HypothesisPriority.NORMAL,
        evidence_level=EvidenceLevel.L0,
        revision_number=1,
        tags=[f"tag_{idx}"],
        metadata={"idx": idx},
        canonical_hash=canonical_hash,
    )

    persistence_ctx.hypotheses.save(hyp)
    fetched = persistence_ctx.hypotheses.get_by_id(hyp_id)

    assert fetched is not None
    assert fetched.hypothesis_id == hyp.hypothesis_id
    assert fetched.title == hyp.title
    assert fetched.canonical_hash == hyp.canonical_hash
    assert fetched.tags == hyp.tags
    assert fetched.metadata == hyp.metadata


@pytest.mark.parametrize("rev_idx", range(1, 10))
def test_revision_repository_roundtrip(persistence_ctx: ResearchPersistenceContext, rev_idx: int):
    hyp_id, _ = compute_hypothesis_id(
        title="Rev Hyp Title",
        null_hypothesis="H0: Null statement",
        alternative_hypothesis="H1: Alt statement",
    )
    hyp = ScientificHypothesis(
        hypothesis_id=hyp_id,
        title="Rev Hyp Title",
        research_question="Question?",
        null_hypothesis="H0: Null statement",
        alternative_hypothesis="H1: Alt statement",
        expected_behaviour="Expected behaviour statement",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
    )
    persistence_ctx.hypotheses.save(hyp)

    rev_id, rev_hash = compute_revision_id(
        hypothesis_id=hyp_id,
        revision_number=rev_idx,
        previous_hash="PREV",
        timestamp="2026-08-04T12:00:00Z",
    )
    rev = HypothesisRevision(
        revision_id=rev_id,
        hypothesis_id=hyp_id,
        revision_number=rev_idx,
        previous_hash="PREV",
        change_summary=f"Revision #{rev_idx}",
        author="DEV",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=rev_hash,
    )

    persistence_ctx.revisions.save(rev)
    revs = persistence_ctx.revisions.get_by_hypothesis_id(hyp_id)

    assert len(revs) == 1
    assert revs[0].revision_id == rev_id
    assert revs[0].revision_number == rev_idx


def test_cascade_delete_integrity(persistence_ctx: ResearchPersistenceContext):
    hyp_id, _ = compute_hypothesis_id(
        title="Cascade Hyp Title",
        null_hypothesis="H0: Null statement",
        alternative_hypothesis="H1: Alt statement",
    )
    hyp = ScientificHypothesis(
        hypothesis_id=hyp_id,
        title="Cascade Hyp Title",
        research_question="Question?",
        null_hypothesis="H0: Null statement",
        alternative_hypothesis="H1: Alt statement",
        expected_behaviour="Expected behaviour statement",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
    )
    persistence_ctx.hypotheses.save(hyp)

    rev_id, rev_hash = compute_revision_id(hypothesis_id=hyp_id, revision_number=1)
    rev = HypothesisRevision(
        revision_id=rev_id,
        hypothesis_id=hyp_id,
        revision_number=1,
        change_summary="Initial",
        author="DEV",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=rev_hash,
    )
    persistence_ctx.revisions.save(rev)

    # Delete hypothesis
    persistence_ctx.hypotheses.delete_by_id(hyp_id)

    assert persistence_ctx.hypotheses.get_by_id(hyp_id) is None
    assert len(persistence_ctx.revisions.get_by_hypothesis_id(hyp_id)) == 0
