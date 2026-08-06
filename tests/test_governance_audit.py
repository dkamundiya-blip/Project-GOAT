"""
Project GOAT v0.9 — Dedicated Unit Tests for Governance Audit Engine
"""

import pytest

from goat.governance.audit.engine import GovernanceAuditEngine
from goat.governance.core.canonical import compute_edge_id, compute_governance_decision_id
from goat.governance.core.enums import GovernanceDecisionOutcome, GovernanceReason
from goat.governance.core.models import EdgeCandidate, GovernanceDecision


@pytest.fixture
def audit_engine():
    return GovernanceAuditEngine()


def test_audit_decision_success(audit_engine: GovernanceAuditEngine):
    edg_id, hash_val = compute_edge_id("HYP_1234567890ABCDEF", "Audit Edge")
    candidate = EdgeCandidate(
        edge_id=edg_id,
        title="Audit Edge",
        hypothesis_id="HYP_1234567890ABCDEF",
        evaluation_id="STE_1234567890ABCDEF",
        experiment_id="EXP_1234567890ABCDEF",
        validation_session_id="VSN_1234567890ABCDEF",
        evidence_ids=["EVR_1234567890ABCDEF"],
        created_timestamp="2026-08-04T12:00:00Z",
        canonical_hash=hash_val,
    )

    gov_id, gov_hash = compute_governance_decision_id(
        edge_id=edg_id,
        decision="PROMOTE",
        reason="LIVE_CONFIRMATION",
    )
    decision = GovernanceDecision(
        decision_id=gov_id,
        edge_id=edg_id,
        hypothesis_id="HYP_1234567890ABCDEF",
        decision=GovernanceDecisionOutcome.PROMOTE,
        reason=GovernanceReason.LIVE_CONFIRMATION,
        rationale="Detailed binding rationale statement for test audit.",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=gov_hash,
    )

    audit = audit_engine.audit_decision(candidate=candidate, decision=decision)

    assert audit.audit_id.startswith("AUD_")
    assert audit.decision_id == gov_id
    assert audit.is_explainable is True
    assert audit.is_replayable is True
    assert audit_engine.get_audit(audit.audit_id) is not None
