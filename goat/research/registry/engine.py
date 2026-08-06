"""
Project GOAT v0.9 — Scientific Hypothesis Registry Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.research.core.canonical import (
    compute_approval_id,
    compute_canonical_sha256,
    compute_hypothesis_id,
    compute_revision_id,
    compute_summary_id,
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
from goat.research.validation.engine import HypothesisValidationEngine


class ScientificHypothesisRegistry:
    """Deterministic Scientific Hypothesis Registry Engine for managing hypotheses,

    revisions, validations, approvals, and lifecycle state transitions.
    """

    def __init__(self, validation_engine: HypothesisValidationEngine | None = None) -> None:
        self._validation_engine = validation_engine or HypothesisValidationEngine()
        self._hypotheses: dict[str, ScientificHypothesis] = {}
        self._revisions: dict[str, list[HypothesisRevision]] = {}
        self._validations: dict[str, list[HypothesisValidation]] = {}
        self._approvals: dict[str, list[HypothesisApproval]] = {}

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
        """Register a new scientific hypothesis deterministically in the registry."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        hyp_id, canonical_hash = compute_hypothesis_id(
            title=title,
            null_hypothesis=null_hypothesis,
            alternative_hypothesis=alternative_hypothesis,
            author=author,
        )

        ind_vars = independent_variables or []
        dep_vars = dependent_variables or []
        assump = assumptions or []
        succ_crit = success_criteria or []
        fail_crit = failure_criteria or []
        tg = tags or []
        meta = metadata or {}

        hypothesis = ScientificHypothesis(
            hypothesis_id=hyp_id,
            title=title.strip(),
            research_question=research_question.strip(),
            null_hypothesis=null_hypothesis.strip(),
            alternative_hypothesis=alternative_hypothesis.strip(),
            expected_behaviour=expected_behaviour.strip(),
            independent_variables=ind_vars,
            dependent_variables=dep_vars,
            assumptions=assump,
            risk_statement=risk_statement.strip(),
            success_criteria=succ_crit,
            failure_criteria=fail_crit,
            author=author.strip(),
            created_timestamp=now_str,
            updated_timestamp=now_str,
            status=HypothesisStatus.DRAFT,
            priority=priority,
            evidence_level=evidence_level,
            revision_number=1,
            tags=tg,
            metadata=meta,
            canonical_hash=canonical_hash,
        )

        # Validate
        validation = self._validation_engine.validate_hypothesis(
            hypothesis=hypothesis,
            existing_hypotheses=list(self._hypotheses.values()),
            timestamp=now_str,
        )

        if not validation.is_valid:
            raise ValueError(f"Hypothesis validation failed: {'; '.join(validation.validation_errors)}")

        # Store initial state
        self._hypotheses[hyp_id] = hypothesis
        self._validations[hyp_id] = [validation]
        self._approvals[hyp_id] = []

        # Create Rev 1
        rev_id, rev_hash = compute_revision_id(
            hypothesis_id=hyp_id,
            revision_number=1,
            previous_hash="",
            timestamp=now_str,
        )
        initial_revision = HypothesisRevision(
            revision_id=rev_id,
            hypothesis_id=hyp_id,
            revision_number=1,
            previous_hash="",
            change_summary="Initial hypothesis registration (Rev 1).",
            author=author,
            timestamp=now_str,
            canonical_hash=rev_hash,
        )
        self._revisions[hyp_id] = [initial_revision]

        return hypothesis, validation

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
        """Update an existing hypothesis, incrementing revision number and logging a revision entry."""
        if hypothesis_id not in self._hypotheses:
            raise KeyError(f"Hypothesis ID '{hypothesis_id}' not found in registry.")

        existing = self._hypotheses[hypothesis_id]
        if existing.status in (HypothesisStatus.ARCHIVED, HypothesisStatus.RETIRED):
            raise ValueError(f"Cannot update hypothesis '{hypothesis_id}' in terminal status '{existing.status}'.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        new_rev_num = existing.revision_number + 1

        new_title = title.strip() if title is not None else existing.title
        new_rq = research_question.strip() if research_question is not None else existing.research_question
        new_h0 = null_hypothesis.strip() if null_hypothesis is not None else existing.null_hypothesis
        new_h1 = alternative_hypothesis.strip() if alternative_hypothesis is not None else existing.alternative_hypothesis
        new_eb = expected_behaviour.strip() if expected_behaviour is not None else existing.expected_behaviour
        new_ind = independent_variables if independent_variables is not None else existing.independent_variables
        new_dep = dependent_variables if dependent_variables is not None else existing.dependent_variables
        new_ass = assumptions if assumptions is not None else existing.assumptions
        new_rs = risk_statement.strip() if risk_statement is not None else existing.risk_statement
        new_sc = success_criteria if success_criteria is not None else existing.success_criteria
        new_fc = failure_criteria if failure_criteria is not None else existing.failure_criteria
        new_prio = priority if priority is not None else existing.priority
        new_ev = evidence_level if evidence_level is not None else existing.evidence_level
        new_tags = tags if tags is not None else existing.tags
        new_meta = {**existing.metadata, **(metadata or {})}

        # Re-compute digest
        _, new_hash = compute_hypothesis_id(
            title=new_title,
            null_hypothesis=new_h0,
            alternative_hypothesis=new_h1,
            author=existing.author,
        )

        updated_hypothesis = ScientificHypothesis(
            hypothesis_id=existing.hypothesis_id,
            title=new_title,
            research_question=new_rq,
            null_hypothesis=new_h0,
            alternative_hypothesis=new_h1,
            expected_behaviour=new_eb,
            independent_variables=new_ind,
            dependent_variables=new_dep,
            assumptions=new_ass,
            risk_statement=new_rs,
            success_criteria=new_sc,
            failure_criteria=new_fc,
            author=existing.author,
            created_timestamp=existing.created_timestamp,
            updated_timestamp=now_str,
            status=existing.status,
            priority=new_prio,
            evidence_level=new_ev,
            revision_number=new_rev_num,
            tags=new_tags,
            metadata=new_meta,
            canonical_hash=new_hash,
        )

        # Validate updated entity
        other_hyps = [h for h_id, h in self._hypotheses.items() if h_id != hypothesis_id]
        val = self._validation_engine.validate_hypothesis(
            hypothesis=updated_hypothesis,
            existing_hypotheses=other_hyps,
            timestamp=now_str,
        )
        if not val.is_valid:
            raise ValueError(f"Updated hypothesis validation failed: {'; '.join(val.validation_errors)}")

        # Log Revision
        rev_id, rev_hash = compute_revision_id(
            hypothesis_id=hypothesis_id,
            revision_number=new_rev_num,
            previous_hash=existing.canonical_hash,
            timestamp=now_str,
        )
        revision = HypothesisRevision(
            revision_id=rev_id,
            hypothesis_id=hypothesis_id,
            revision_number=new_rev_num,
            previous_hash=existing.canonical_hash,
            change_summary=change_summary.strip(),
            author=author.strip(),
            timestamp=now_str,
            canonical_hash=rev_hash,
        )

        self._hypotheses[hypothesis_id] = updated_hypothesis
        self._revisions[hypothesis_id].append(revision)
        self._validations[hypothesis_id].append(val)

        return updated_hypothesis, revision

    def approve_hypothesis(
        self,
        hypothesis_id: str,
        approver: str,
        approval_notes: str = "Approved for execution.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Transition a hypothesis to APPROVED status."""
        return self._transition_status(
            hypothesis_id=hypothesis_id,
            target_status=HypothesisStatus.APPROVED,
            actor=approver,
            notes=approval_notes,
            timestamp=timestamp,
        )

    def reject_hypothesis(
        self,
        hypothesis_id: str,
        reviewer: str,
        reason: str = "Rejected during evaluation.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Transition a hypothesis to REJECTED status."""
        return self._transition_status(
            hypothesis_id=hypothesis_id,
            target_status=HypothesisStatus.REJECTED,
            actor=reviewer,
            notes=reason,
            timestamp=timestamp,
        )

    def retire_hypothesis(
        self,
        hypothesis_id: str,
        reviewer: str,
        reason: str = "Retired due to performance degradation or market shift.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Transition a hypothesis to RETIRED status."""
        return self._transition_status(
            hypothesis_id=hypothesis_id,
            target_status=HypothesisStatus.RETIRED,
            actor=reviewer,
            notes=reason,
            timestamp=timestamp,
        )

    def archive_hypothesis(
        self,
        hypothesis_id: str,
        reviewer: str,
        reason: str = "Archived into append-only storage.",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Transition a hypothesis to ARCHIVED status."""
        return self._transition_status(
            hypothesis_id=hypothesis_id,
            target_status=HypothesisStatus.ARCHIVED,
            actor=reviewer,
            notes=reason,
            timestamp=timestamp,
        )

    def transition_status(
        self,
        hypothesis_id: str,
        target_status: HypothesisStatus,
        actor: str,
        notes: str = "",
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        """Generic status transition function."""
        return self._transition_status(
            hypothesis_id=hypothesis_id,
            target_status=target_status,
            actor=actor,
            notes=notes,
            timestamp=timestamp,
        )

    def _transition_status(
        self,
        hypothesis_id: str,
        target_status: HypothesisStatus,
        actor: str,
        notes: str,
        timestamp: str | None = None,
    ) -> tuple[ScientificHypothesis, HypothesisApproval]:
        if hypothesis_id not in self._hypotheses:
            raise KeyError(f"Hypothesis ID '{hypothesis_id}' not found in registry.")

        existing = self._hypotheses[hypothesis_id]
        now_str = timestamp or datetime.now(timezone.utc).isoformat()

        updated_hypothesis = ScientificHypothesis(
            hypothesis_id=existing.hypothesis_id,
            title=existing.title,
            research_question=existing.research_question,
            null_hypothesis=existing.null_hypothesis,
            alternative_hypothesis=existing.alternative_hypothesis,
            expected_behaviour=existing.expected_behaviour,
            independent_variables=existing.independent_variables,
            dependent_variables=existing.dependent_variables,
            assumptions=existing.assumptions,
            risk_statement=existing.risk_statement,
            success_criteria=existing.success_criteria,
            failure_criteria=existing.failure_criteria,
            author=existing.author,
            created_timestamp=existing.created_timestamp,
            updated_timestamp=now_str,
            status=target_status,
            priority=existing.priority,
            evidence_level=existing.evidence_level,
            revision_number=existing.revision_number,
            tags=existing.tags,
            metadata=existing.metadata,
            canonical_hash=existing.canonical_hash,
        )

        app_id, app_hash = compute_approval_id(
            hypothesis_id=hypothesis_id,
            approver=actor,
            status=target_status.value,
            timestamp=now_str,
        )

        approval = HypothesisApproval(
            approval_id=app_id,
            hypothesis_id=hypothesis_id,
            approver=actor.strip(),
            status=target_status,
            approval_notes=notes.strip(),
            timestamp=now_str,
            canonical_hash=app_hash,
        )

        self._hypotheses[hypothesis_id] = updated_hypothesis
        self._approvals[hypothesis_id].append(approval)

        return updated_hypothesis, approval

    def get_hypothesis(self, hypothesis_id: str) -> ScientificHypothesis | None:
        """Retrieve hypothesis by ID."""
        return self._hypotheses.get(hypothesis_id)

    def search_registry(
        self,
        query: str = "",
        status: HypothesisStatus | None = None,
        priority: HypothesisPriority | None = None,
        evidence_level: EvidenceLevel | None = None,
        tags: list[str] | None = None,
    ) -> list[ScientificHypothesis]:
        """Search and filter hypotheses in the registry."""
        results: list[ScientificHypothesis] = []
        q = query.strip().lower()
        tag_set = set(t.lower() for t in tags) if tags else None

        for hyp in self._hypotheses.values():
            if status is not None and hyp.status != status:
                continue
            if priority is not None and hyp.priority != priority:
                continue
            if evidence_level is not None and hyp.evidence_level != evidence_level:
                continue
            if tag_set and not tag_set.issubset(set(t.lower() for t in hyp.tags)):
                continue
            if q:
                combined = f"{hyp.title} {hyp.research_question} {hyp.null_hypothesis} {hyp.alternative_hypothesis}".lower()
                if q not in combined:
                    continue
            results.append(hyp)

        return sorted(results, key=lambda h: h.created_timestamp)

    def list_all_hypotheses(self) -> list[ScientificHypothesis]:
        """Return all registered hypotheses sorted by created timestamp."""
        return sorted(self._hypotheses.values(), key=lambda h: h.created_timestamp)

    def get_revision_history(self, hypothesis_id: str) -> list[HypothesisRevision]:
        """Return chronological list of revisions for a given hypothesis."""
        return self._revisions.get(hypothesis_id, [])

    def get_validation_history(self, hypothesis_id: str) -> list[HypothesisValidation]:
        """Return chronological list of validation runs for a given hypothesis."""
        return self._validations.get(hypothesis_id, [])

    def get_approval_history(self, hypothesis_id: str) -> list[HypothesisApproval]:
        """Return chronological list of approvals for a given hypothesis."""
        return self._approvals.get(hypothesis_id, [])

    def generate_summary(self, timestamp: str | None = None) -> HypothesisRegistrySummary:
        """Generate a summary snapshot of the registry."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        total = len(self._hypotheses)

        status_counts: dict[str, int] = {s.value: 0 for s in HypothesisStatus}
        priority_counts: dict[str, int] = {p.value: 0 for p in HypothesisPriority}
        evidence_counts: dict[str, int] = {e.value: 0 for e in EvidenceLevel}

        for hyp in self._hypotheses.values():
            status_counts[hyp.status.value] += 1
            priority_counts[hyp.priority.value] += 1
            evidence_counts[hyp.evidence_level.value] += 1

        summary_id, canonical_hash = compute_summary_id(
            total_hypotheses=total,
            timestamp=now_str,
        )

        return HypothesisRegistrySummary(
            summary_id=summary_id,
            total_hypotheses=total,
            status_counts=status_counts,
            priority_counts=priority_counts,
            evidence_level_counts=evidence_counts,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )
