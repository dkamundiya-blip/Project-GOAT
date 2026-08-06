"""
Project GOAT v0.9 — Dedicated Unit Tests for Master Governance Engine Facade
"""

import pytest

from goat.governance.core.enums import EdgeStatus, GovernanceDecisionOutcome
from goat.governance.engine import MasterGovernanceEngine
from goat.governance.persistence.sqlite import GovernancePersistenceContext


@pytest.fixture
def memory_context():
    ctx = GovernancePersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.fixture
def master_engine(memory_context):
    return MasterGovernanceEngine(persistence_context=memory_context)


@pytest.mark.parametrize("idx", range(1, 10))
def test_master_engine_evaluate_governance(master_engine: MasterGovernanceEngine, idx: int):
    hyp_id = f"HYP_{idx:016X}"

    cand = master_engine.register_edge_candidate(
        title=f"Governance Edge #{idx}",
        hypothesis_id=hyp_id,
        evaluation_id=f"STE_{idx:016X}",
        experiment_id=f"EXP_{idx:016X}",
        validation_session_id=f"VSN_{idx:016X}",
        evidence_ids=[f"EVR_{idx:016X}"],
    )

    assert cand.edge_id.startswith("EDG_")

    gov_dec, pra, rta, audit = master_engine.evaluate_governance(
        edge_id=cand.edge_id,
        statistics_decision="SUPPORTED",
        live_validation_decision="PROMOTION_RECOMMENDED",
    )

    assert gov_dec.decision == GovernanceDecisionOutcome.PROMOTE
    assert pra.is_promotable is True
    assert rta.is_retirement_recommended is False
    assert audit.is_explainable is True
    assert audit.is_replayable is True

    updated_c = master_engine.get_candidate(cand.edge_id)
    assert updated_c is not None
    assert updated_c.status == EdgeStatus.APPROVED


def test_master_engine_report_generation(master_engine: MasterGovernanceEngine):
    cand = master_engine.register_edge_candidate(
        title="Report Edge",
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        evidence_ids=["EVR_1234567890ABCDEF"],
    )

    gov_dec, _, _, _ = master_engine.evaluate_governance(cand.edge_id)

    reports = master_engine.generate_reports(gov_dec.decision_id)
    assert "decision" in reports
    assert "executive" in reports
    assert "json" in reports
    assert "promotion" in reports
    assert "retirement" in reports
    assert "audit" in reports
    assert gov_dec.decision_id in reports["decision"]
