"""
Project GOAT v0.9 — Master Scientific Research Engine & Registry Facade
"""

from typing import Any, Sequence

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
from goat.research.registry.engine import ScientificHypothesisRegistry
from goat.research.reporting.reports import (
    generate_executive_report,
    generate_json_report,
    generate_markdown_report,
    generate_registry_summary_report,
    generate_validation_report,
)
from goat.research.validation.engine import HypothesisValidationEngine


class ScientificResearchEngine:
    """Master Facade Engine orchestrating registry management, validation, reporting,

    and optional SQLite persistence.
    """

    def __init__(
        self,
        persistence_context: ResearchPersistenceContext | None = None,
        validation_engine: HypothesisValidationEngine | None = None,
    ) -> None:
        self._validation_engine = validation_engine or HypothesisValidationEngine()
        self._registry = ScientificHypothesisRegistry(validation_engine=self._validation_engine)
        self._persistence = persistence_context

        # Sync existing database entities if persistence provided
        if self._persistence:
            for hyp in self._persistence.hypotheses.list_all():
                self._registry._hypotheses[hyp.hypothesis_id] = hyp
                self._registry._revisions[hyp.hypothesis_id] = self._persistence.revisions.get_by_hypothesis_id(
                    hyp.hypothesis_id
                )
                self._registry._validations[hyp.hypothesis_id] = self._persistence.validations.get_by_hypothesis_id(
                    hyp.hypothesis_id
                )
                self._registry._approvals[hyp.hypothesis_id] = self._persistence.approvals.get_by_hypothesis_id(
                    hyp.hypothesis_id
                )

    @property
    def registry(self) -> ScientificHypothesisRegistry:
        return self._registry

    @property
    def validation_engine(self) -> HypothesisValidationEngine:
        return self._validation_engine

    @property
    def persistence(self) -> ResearchPersistenceContext | None:
        return self._persistence

    def register_hypothesis(
        self,
        title: str,
        research_question: str,
        null_hypothesis: str,
        alternative_hypothesis: str,
        expected_behaviour: str,
        independent_variables: list[str] | None = None,
        dependent_variables: list[str] | None = None,
        assumptions: list[str] | None = None,
        risk_statement: str = "Unspecified risk statement.",
        success_criteria: list[str] | None = None,
        failure_criteria: list[str] | None = None,
        author: str = "QUANT_RESEARCHER",
        priority: HypothesisPriority = HypothesisPriority.NORMAL,
        evidence_level: EvidenceLevel = EvidenceLevel.L0,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisValidation]:
        """Register a new scientific hypothesis across registry and optional persistence."""
        hyp, val = self._registry.register_hypothesis(
            title=title,
            research_question=research_question,
            null_hypothesis=null_hypothesis,
            alternative_hypothesis=alternative_hypothesis,
            expected_behaviour=expected_behaviour,
            independent_variables=independent_variables,
            dependent_variables=dependent_variables,
            assumptions=assumptions,
            risk_statement=risk_statement,
            success_criteria=success_criteria,
            failure_criteria=failure_criteria,
            author=author,
            priority=priority,
            evidence_level=evidence_level,
            tags=tags,
            metadata=metadata,
            timestamp=timestamp,
        )

        if self._persistence:
            self._persistence.hypotheses.save(hyp)
            self._persistence.validations.save(val)
            revs = self._registry.get_revision_history(hyp.hypothesis_id)
            if revs:
                self._persistence.revisions.save(revs[-1])

        return hyp, val

    def update_hypothesis(
        self,
        hypothesis_id: str,
        change_summary: str,
        author: str,
        title: str | None = None,
        research_question: str | None = None,
        null_hypothesis: str | None = None,
        alternative_hypothesis: str | None = None,
        expected_behaviour: str | None = None,
        independent_variables: list[str] | None = None,
        dependent_variables: list[str] | None = None,
        assumptions: list[str] | None = None,
        risk_statement: str | None = None,
        success_criteria: list[str] | None = None,
        failure_criteria: list[str] | None = None,
        priority: HypothesisPriority | None = None,
        evidence_level: EvidenceLevel | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisRevision]:
        """Update an existing hypothesis revision."""
        hyp, rev = self._registry.update_hypothesis(
            hypothesis_id=hypothesis_id,
            change_summary=change_summary,
            author=author,
            title=title,
            research_question=research_question,
            null_hypothesis=null_hypothesis,
            alternative_hypothesis=alternative_hypothesis,
            expected_behaviour=expected_behaviour,
            independent_variables=independent_variables,
            dependent_variables=dependent_variables,
            assumptions=assumptions,
            risk_statement=risk_statement,
            success_criteria=success_criteria,
            failure_criteria=failure_criteria,
            priority=priority,
            evidence_level=evidence_level,
            tags=tags,
            metadata=metadata,
            timestamp=timestamp,
        )

        if self._persistence:
            self._persistence.hypotheses.save(hyp)
            self._persistence.revisions.save(rev)

        return hyp, rev

    def approve_hypothesis(
        self,
        hypothesis_id: str,
        approver: str,
        notes: str = "Approved for execution.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Approve a registered hypothesis."""
        hyp, app = self._registry.approve_hypothesis(
            hypothesis_id=hypothesis_id,
            approver=approver,
            approval_notes=notes,
            timestamp=timestamp,
        )
        if self._persistence:
            self._persistence.hypotheses.save(hyp)
            self._persistence.approvals.save(app)
        return hyp, app

    def reject_hypothesis(
        self,
        hypothesis_id: str,
        reviewer: str,
        reason: str = "Rejected during review.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Reject a hypothesis."""
        hyp, app = self._registry.reject_hypothesis(
            hypothesis_id=hypothesis_id,
            reviewer=reviewer,
            reason=reason,
            timestamp=timestamp,
        )
        if self._persistence:
            self._persistence.hypotheses.save(hyp)
            self._persistence.approvals.save(app)
        return hyp, app

    def retire_hypothesis(
        self,
        hypothesis_id: str,
        reviewer: str,
        reason: str = "Retired due to performance degradation.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Retire a hypothesis."""
        hyp, app = self._registry.retire_hypothesis(
            hypothesis_id=hypothesis_id,
            reviewer=reviewer,
            reason=reason,
            timestamp=timestamp,
        )
        if self._persistence:
            self._persistence.hypotheses.save(hyp)
            self._persistence.approvals.save(app)
        return hyp, app

    def archive_hypothesis(
        self,
        hypothesis_id: str,
        reviewer: str,
        reason: str = "Archived to append-only storage.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Archive a hypothesis."""
        hyp, app = self._registry.archive_hypothesis(
            hypothesis_id=hypothesis_id,
            reviewer=reviewer,
            reason=reason,
            timestamp=timestamp,
        )
        if self._persistence:
            self._persistence.hypotheses.save(hyp)
            self._persistence.approvals.save(app)
        return hyp, app

    def get_hypothesis(self, hypothesis_id: str) -> ScientificHypothesis | None:
        """Retrieve hypothesis by ID."""
        return self._registry.get_hypothesis(hypothesis_id)

    def search_registry(
        self,
        query: str = "",
        status: HypothesisStatus | None = None,
        priority: HypothesisPriority | None = None,
        evidence_level: EvidenceLevel | None = None,
        tags: list[str] | None = None,
    ) -> list[ScientificHypothesis]:
        """Search registered hypotheses."""
        return self._registry.search_registry(
            query=query,
            status=status,
            priority=priority,
            evidence_level=evidence_level,
            tags=tags,
        )

    def generate_summary(self) -> HypothesisRegistrySummary:
        """Generate registry summary and persist if context configured."""
        summary = self._registry.generate_summary()
        if self._persistence:
            self._persistence.summaries.save(summary)
        return summary

    def generate_reports(self, hypothesis_id: str) -> dict[str, str]:
        """Generate Markdown and JSON reports for a hypothesis."""
        hyp = self.get_hypothesis(hypothesis_id)
        if not hyp:
            raise KeyError(f"Hypothesis ID '{hypothesis_id}' not found.")

        return {
            "markdown": generate_markdown_report(hyp),
            "json": generate_json_report(hyp),
            "executive": generate_executive_report(self._registry),
        }
