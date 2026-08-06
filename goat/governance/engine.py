"""
Project GOAT v0.9 — Master Edge Promotion & Retirement Governance Engine Facade
"""

from datetime import datetime, timezone
from typing import Any

from goat.governance.audit.engine import GovernanceAuditEngine
from goat.governance.core.canonical import compute_edge_id, compute_summary_id
from goat.governance.core.enums import (
    EdgeStatus,
    GovernanceDecisionOutcome,
    GovernanceReason,
)
from goat.governance.core.models import (
    EdgeCandidate,
    GovernanceAudit,
    GovernanceDecision,
    GovernanceSummary,
    PromotionAssessment,
    RetirementAssessment,
)
from goat.governance.governance.engine import EdgeGovernanceEngine
from goat.governance.persistence.sqlite import GovernancePersistenceContext
from goat.governance.promotion.engine import EdgePromotionEngine
from goat.governance.reporting.reports import (
    generate_audit_report,
    generate_executive_report,
    generate_governance_decision_report,
    generate_json_report,
    generate_promotion_report,
    generate_retirement_report,
)
from goat.governance.retirement.engine import EdgeRetirementEngine


class MasterGovernanceEngine:
    """Master Facade Engine orchestrating edge promotion assessments, retirement evaluations,

    binding governance decision derivation, audit verification, reporting, and optional SQLite persistence.
    """

    def __init__(
        self,
        persistence_context: GovernancePersistenceContext | None = None,
        promotion_engine: EdgePromotionEngine | None = None,
        retirement_engine: EdgeRetirementEngine | None = None,
        governance_engine: EdgeGovernanceEngine | None = None,
        audit_engine: GovernanceAuditEngine | None = None,
    ) -> None:
        self._promotion_engine = promotion_engine or EdgePromotionEngine()
        self._retirement_engine = retirement_engine or EdgeRetirementEngine()
        self._governance_engine = governance_engine or EdgeGovernanceEngine(
            promotion_engine=self._promotion_engine,
            retirement_engine=self._retirement_engine,
        )
        self._audit_engine = audit_engine or GovernanceAuditEngine()
        self._persistence = persistence_context

        self._candidates: dict[str, EdgeCandidate] = {}

        # Sync existing database entities if persistence context provided
        if self._persistence:
            for cand in self._persistence.edges.list_all():
                self._candidates[cand.edge_id] = cand
            for pra in self._persistence.promotions.list_all():
                self._promotion_engine._assessments[pra.assessment_id] = pra
            for rta in self._persistence.retirements.list_all():
                self._retirement_engine._assessments[rta.assessment_id] = rta
            for gov in self._persistence.decisions.list_all():
                self._governance_engine._decisions[gov.decision_id] = gov

    @property
    def promotion_engine(self) -> EdgePromotionEngine:
        return self._promotion_engine

    @property
    def retirement_engine(self) -> EdgeRetirementEngine:
        return self._retirement_engine

    @property
    def governance_engine(self) -> EdgeGovernanceEngine:
        return self._governance_engine

    @property
    def audit_engine(self) -> GovernanceAuditEngine:
        return self._audit_engine

    @property
    def persistence(self) -> GovernancePersistenceContext | None:
        return self._persistence

    def register_edge_candidate(
        self,
        title: str,
        hypothesis_id: str,
        evaluation_id: str,
        experiment_id: str,
        validation_session_id: str,
        evidence_ids: list[str],
        status: EdgeStatus = EdgeStatus.CANDIDATE,
        author: str = "QUANT_RESEARCH",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EdgeCandidate:
        """Register a quantitative trading edge candidate for governance review."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        edge_id, canonical_hash = compute_edge_id(
            hypothesis_id=hypothesis_id,
            title=title,
            author=author,
        )

        candidate = EdgeCandidate(
            edge_id=edge_id,
            title=title.strip(),
            hypothesis_id=hypothesis_id.strip(),
            evaluation_id=evaluation_id.strip(),
            experiment_id=experiment_id.strip(),
            validation_session_id=validation_session_id.strip(),
            evidence_ids=evidence_ids or [],
            status=status,
            created_timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._candidates[edge_id] = candidate
        if self._persistence:
            self._persistence.edges.save(candidate)

        return candidate

    def get_candidate(self, edge_id: str) -> EdgeCandidate | None:
        """Retrieve edge candidate by ID."""
        return self._candidates.get(edge_id)

    def list_all_candidates(self) -> list[EdgeCandidate]:
        """List all candidates."""
        return sorted(self._candidates.values(), key=lambda c: c.created_timestamp)

    def evaluate_governance(
        self,
        edge_id: str,
        expectancy_degradation: float = 0.0,
        confidence_decline: float = 0.0,
        structural_shift: bool = False,
        amendment_001_violation: bool = False,
        hypothesis_valid: bool = True,
        evidence_valid: bool = True,
        experiment_valid: bool = True,
        statistics_decision: str = "SUPPORTED",
        live_validation_decision: str = "PROMOTION_RECOMMENDED",
        authorizer: str = "GOVERNANCE_BOARD",
        timestamp: str | None = None,
    ) -> tuple[GovernanceDecision, PromotionAssessment, RetirementAssessment, GovernanceAudit]:
        """Evaluate edge candidate and produce binding governance decision and audit trail."""
        candidate = self.get_candidate(edge_id)
        if not candidate:
            raise KeyError(f"Edge Candidate '{edge_id}' not found.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()

        pra = self._promotion_engine.evaluate_promotion(
            candidate=candidate,
            hypothesis_valid=hypothesis_valid,
            evidence_valid=evidence_valid,
            experiment_valid=experiment_valid,
            statistics_decision=statistics_decision,
            live_validation_decision=live_validation_decision,
            timestamp=now_str,
        )

        rta = self._retirement_engine.evaluate_retirement(
            candidate=candidate,
            expectancy_degradation=expectancy_degradation,
            confidence_decline=confidence_decline,
            structural_shift_detected=structural_shift,
            amendment_001_violation=amendment_001_violation,
            timestamp=now_str,
        )

        gov_decision = self._governance_engine.make_governance_decision(
            candidate=candidate,
            promotion_assessment=pra,
            retirement_assessment=rta,
            authorizer=authorizer,
            timestamp=now_str,
        )

        audit = self._audit_engine.audit_decision(
            candidate=candidate,
            decision=gov_decision,
            operator=authorizer,
            timestamp=now_str,
        )

        # Update candidate status based on decision
        new_status = EdgeStatus.CANDIDATE
        if gov_decision.decision == GovernanceDecisionOutcome.PROMOTE:
            new_status = EdgeStatus.APPROVED
        elif gov_decision.decision == GovernanceDecisionOutcome.RETIRE:
            new_status = EdgeStatus.RETIRED
        elif gov_decision.decision == GovernanceDecisionOutcome.PAUSE:
            new_status = EdgeStatus.PAUSED
        elif gov_decision.decision == GovernanceDecisionOutcome.RETURN_TO_RESEARCH:
            new_status = EdgeStatus.RESEARCH
        elif gov_decision.decision == GovernanceDecisionOutcome.RETAIN:
            new_status = EdgeStatus.VALIDATING

        updated_candidate = EdgeCandidate(
            edge_id=candidate.edge_id,
            title=candidate.title,
            hypothesis_id=candidate.hypothesis_id,
            evaluation_id=candidate.evaluation_id,
            experiment_id=candidate.experiment_id,
            validation_session_id=candidate.validation_session_id,
            evidence_ids=candidate.evidence_ids,
            status=new_status,
            created_timestamp=candidate.created_timestamp,
            metadata=candidate.metadata,
            canonical_hash=candidate.canonical_hash,
        )
        self._candidates[edge_id] = updated_candidate

        if self._persistence:
            self._persistence.edges.save(updated_candidate)
            self._persistence.promotions.save(pra)
            self._persistence.retirements.save(rta)
            self._persistence.decisions.save(gov_decision)
            self._persistence.audits.save(audit)

        return gov_decision, pra, rta, audit

    def generate_summary(self, timestamp: str | None = None) -> GovernanceSummary:
        """Generate and persist an EvaluationSummary snapshot."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        total_edges = len(self._candidates)
        total_decisions = len(self._governance_engine._decisions)

        st_counts: dict[str, int] = {s.value: 0 for s in EdgeStatus}
        dec_counts: dict[str, int] = {d.value: 0 for d in GovernanceDecisionOutcome}
        rsn_counts: dict[str, int] = {r.value: 0 for r in GovernanceReason}

        for c in self._candidates.values():
            st_counts[c.status.value] += 1
        for d in self._governance_engine._decisions.values():
            dec_counts[d.decision.value] += 1
            rsn_counts[d.reason.value] += 1

        gsm_id, canonical_hash = compute_summary_id(
            total_edges=total_edges,
            total_decisions=total_decisions,
            timestamp=now_str,
        )

        summary = GovernanceSummary(
            summary_id=gsm_id,
            total_edges=total_edges,
            total_decisions=total_decisions,
            status_counts=st_counts,
            decision_counts=dec_counts,
            reason_counts=rsn_counts,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        if self._persistence:
            self._persistence.summaries.save(summary)

        return summary

    def generate_reports(self, decision_id: str) -> dict[str, str]:
        """Generate Markdown and JSON reports for a given decision ID."""
        decision = self._governance_engine.get_decision(decision_id)
        if not decision:
            raise KeyError(f"Decision ID '{decision_id}' not found.")

        candidate = self.get_candidate(decision.edge_id)
        summary = self.generate_summary()
        recent_decisions = self._governance_engine.list_all_decisions()[:10]

        reports: dict[str, str] = {
            "decision": generate_governance_decision_report(decision),
            "executive": generate_executive_report(summary, recent_decisions),
            "json": generate_json_report(decision),
        }

        for pra in self._promotion_engine._assessments.values():
            if pra.edge_id == decision.edge_id:
                reports["promotion"] = generate_promotion_report(pra)
                break
        for rta in self._retirement_engine._assessments.values():
            if rta.edge_id == decision.edge_id:
                reports["retirement"] = generate_retirement_report(rta)
                break
        for aud in self._audit_engine._audits.values():
            if aud.decision_id == decision_id:
                reports["audit"] = generate_audit_report(aud)
                break

        if self._persistence:
            if "promotion" not in reports:
                pra_p = self._persistence.promotions.get_by_edge_id(decision.edge_id)
                if pra_p:
                    reports["promotion"] = generate_promotion_report(pra_p)
            if "retirement" not in reports:
                rta_p = self._persistence.retirements.get_by_edge_id(decision.edge_id)
                if rta_p:
                    reports["retirement"] = generate_retirement_report(rta_p)
            if "audit" not in reports:
                aud_p = self._persistence.audits.get_by_decision_id(decision_id)
                if aud_p:
                    reports["audit"] = generate_audit_report(aud_p)

        return reports
