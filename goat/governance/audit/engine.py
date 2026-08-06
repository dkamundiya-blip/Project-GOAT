"""
Project GOAT v0.9 — Governance Audit Engine
"""

from datetime import datetime, timezone

from goat.governance.core.canonical import compute_governance_audit_id
from goat.governance.core.models import EdgeCandidate, GovernanceAudit, GovernanceDecision


class GovernanceAuditEngine:
    """Governance Audit Engine for verifying that every governance decision is fully explainable,

    replayable, and linked to the complete evidence chain.
    """

    def __init__(self) -> None:
        self._audits: dict[str, GovernanceAudit] = {}

    def audit_decision(
        self,
        candidate: EdgeCandidate,
        decision: GovernanceDecision,
        operator: str = "AUDIT_ENGINE",
        timestamp: str | None = None,
    ) -> GovernanceAudit:
        """Audit governance decision and verify complete traceability back to scientific pipeline artifacts."""
        is_explainable = bool(decision.rationale and len(decision.rationale) >= 10)
        is_replayable = bool(
            candidate.hypothesis_id.startswith("HYP_")
            and candidate.experiment_id.startswith("EXP_")
            and candidate.evaluation_id.startswith("STE_")
            and candidate.validation_session_id.startswith("VSN_")
        )

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        aud_id, canonical_hash = compute_governance_audit_id(
            decision_id=decision.decision_id,
            action=decision.decision.value,
            timestamp=now_str,
            operator=operator,
        )

        audit = GovernanceAudit(
            audit_id=aud_id,
            decision_id=decision.decision_id,
            edge_id=candidate.edge_id,
            hypothesis_id=candidate.hypothesis_id,
            evidence_ids=candidate.evidence_ids,
            experiment_id=candidate.experiment_id,
            evaluation_id=candidate.evaluation_id,
            validation_session_id=candidate.validation_session_id,
            is_explainable=is_explainable,
            is_replayable=is_replayable,
            operator=operator,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        self._audits[aud_id] = audit
        return audit

    def get_audit(self, audit_id: str) -> GovernanceAudit | None:
        """Retrieve audit record by ID."""
        return self._audits.get(audit_id)
