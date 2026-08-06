"""
Project GOAT v0.9 — Master Controlled Live Scientific Validation Engine Facade
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.live_validation.core.canonical import compute_audit_id, compute_summary_id
from goat.live_validation.core.enums import (
    MonitoringStatus,
    ValidationDecisionOutcome,
    ValidationStatus,
)
from goat.live_validation.core.models import (
    LiveValidationCandidate,
    ValidationAudit,
    ValidationDecision,
    ValidationObservation,
    ValidationSession,
    ValidationSummary,
)
from goat.live_validation.eligibility.engine import ValidationEligibilityEngine
from goat.live_validation.monitoring.engine import ValidationMonitoringEngine
from goat.live_validation.persistence.sqlite import LiveValidationPersistenceContext
from goat.live_validation.reporting.reports import (
    generate_decision_report,
    generate_eligibility_report,
    generate_executive_report,
    generate_json_report,
    generate_monitoring_report,
    generate_validation_report,
)
from goat.live_validation.retirement.engine import ValidationRetirementEngine
from goat.live_validation.validation.engine import ControlledLiveValidationEngine


class MasterLiveValidationEngine:
    """Master Facade Engine orchestrating candidate eligibility, live validation sessions,

    execution monitoring, retirement recommendations, reporting, and optional SQLite persistence.
    """

    def __init__(
        self,
        persistence_context: LiveValidationPersistenceContext | None = None,
        eligibility_engine: ValidationEligibilityEngine | None = None,
        validation_engine: ControlledLiveValidationEngine | None = None,
        monitoring_engine: ValidationMonitoringEngine | None = None,
        retirement_engine: ValidationRetirementEngine | None = None,
    ) -> None:
        self._eligibility_engine = eligibility_engine or ValidationEligibilityEngine()
        self._validation_engine = validation_engine or ControlledLiveValidationEngine()
        self._monitoring_engine = monitoring_engine or ValidationMonitoringEngine()
        self._retirement_engine = retirement_engine or ValidationRetirementEngine()
        self._persistence = persistence_context

        # Sync existing database entities if persistence context provided
        if self._persistence:
            for c in self._persistence.candidates.list_all():
                self._eligibility_engine._candidates[c.candidate_id] = c
            for s in self._persistence.sessions.list_all():
                self._validation_engine._sessions[s.session_id] = s
                self._validation_engine._observations[s.session_id] = self._persistence.observations.list_by_session(s.session_id)
            for d in self._persistence.decisions.list_all():
                self._retirement_engine._decisions[d.decision_id] = d

    @property
    def eligibility_engine(self) -> ValidationEligibilityEngine:
        return self._eligibility_engine

    @property
    def validation_engine(self) -> ControlledLiveValidationEngine:
        return self._validation_engine

    @property
    def monitoring_engine(self) -> ValidationMonitoringEngine:
        return self._monitoring_engine

    @property
    def retirement_engine(self) -> ValidationRetirementEngine:
        return self._retirement_engine

    @property
    def persistence(self) -> LiveValidationPersistenceContext | None:
        return self._persistence

    def register_candidate(
        self,
        hypothesis_id: str,
        evaluation_id: str,
        experiment_id: str,
        statistical_decision: str,
        evidence_ids: list[str],
        replay_id: str = "",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> LiveValidationCandidate:
        """Evaluate hypothesis eligibility and register candidate if qualified."""
        candidate = self._eligibility_engine.evaluate_eligibility(
            hypothesis_id=hypothesis_id,
            evaluation_id=evaluation_id,
            experiment_id=experiment_id,
            statistical_decision=statistical_decision,
            evidence_ids=evidence_ids,
            replay_id=replay_id,
            timestamp=timestamp,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.candidates.save(candidate)

        return candidate

    def start_validation_session(
        self,
        candidate_id: str,
        operator: str = "LIVE_VALIDATION_ENGINE",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[ValidationSession, ValidationAudit]:
        """Start a controlled live validation session for a candidate."""
        candidate = self._eligibility_engine.get_candidate(candidate_id)
        if not candidate:
            raise KeyError(f"Candidate ID '{candidate_id}' not found.")

        session = self._validation_engine.start_session(
            candidate=candidate,
            operator=operator,
            timestamp=timestamp,
            metadata=metadata,
        )

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        vau_id, canonical_hash = compute_audit_id(
            session_id=session.session_id,
            action="CREATE",
            timestamp=now_str,
            operator=operator,
        )

        audit = ValidationAudit(
            audit_id=vau_id,
            session_id=session.session_id,
            action="CREATE",
            previous_status=ValidationStatus.ELIGIBLE,
            new_status=ValidationStatus.RUNNING,
            operator=operator,
            timestamp=now_str,
            notes="Session created and initiated.",
            canonical_hash=canonical_hash,
        )

        if self._persistence:
            self._persistence.sessions.save(session)
            self._persistence.audits.save(audit)

        return session, audit

    def record_live_observation(
        self,
        session_id: str,
        live_outcome: float,
        expected_outcome: float,
        slippage: float = 0.0,
        spread: float = 0.0,
        latency_ms: float = 0.0,
        fill_ratio: float = 1.0,
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[ValidationObservation, MonitoringStatus]:
        """Record live observation and evaluate real-time health monitoring status."""
        observation = self._validation_engine.record_observation(
            session_id=session_id,
            live_outcome=live_outcome,
            expected_outcome=expected_outcome,
            slippage=slippage,
            spread=spread,
            latency_ms=latency_ms,
            fill_ratio=fill_ratio,
            timestamp=timestamp,
            metadata=metadata,
        )

        observations = self._validation_engine.get_observations(session_id)
        health_status = self._monitoring_engine.evaluate_monitoring_status(observations)
        self._validation_engine.update_session_status(session_id, new_status=ValidationStatus.RUNNING, new_monitoring=health_status)

        if self._persistence:
            self._persistence.observations.save(observation)
            updated_s = self._validation_engine.get_session(session_id)
            if updated_s:
                self._persistence.sessions.save(updated_s)

        return observation, health_status

    def conclude_session(
        self,
        session_id: str,
        authorizer: str = "RETIREMENT_ENGINE",
        timestamp: str | None = None,
    ) -> tuple[ValidationSession, ValidationDecision, ValidationAudit]:
        """Conclude a live validation session and derive formal scientific recommendation."""
        session = self._validation_engine.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        observations = self._validation_engine.get_observations(session_id)
        decision = self._retirement_engine.derive_recommendation(
            session=session,
            observations=observations,
            monitoring_status=session.monitoring_status,
            authorizer=authorizer,
            timestamp=timestamp,
        )

        final_status = ValidationStatus.COMPLETED if decision.decision in (ValidationDecisionOutcome.SUPPORTED, ValidationDecisionOutcome.PROMOTION_RECOMMENDED) else ValidationStatus.FAILED
        updated_session = self._validation_engine.update_session_status(session_id, new_status=final_status)

        self._eligibility_engine.remove_active_hypothesis(session.hypothesis_id)

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        vau_id, canonical_hash = compute_audit_id(
            session_id=session_id,
            action="COMPLETE",
            timestamp=now_str,
            operator=authorizer,
        )

        audit = ValidationAudit(
            audit_id=vau_id,
            session_id=session_id,
            action="COMPLETE",
            previous_status=session.status,
            new_status=final_status,
            operator=authorizer,
            timestamp=now_str,
            notes=f"Session concluded with decision '{decision.decision.value}'.",
            canonical_hash=canonical_hash,
        )

        if self._persistence:
            self._persistence.sessions.save(updated_session)
            self._persistence.decisions.save(decision)
            self._persistence.audits.save(audit)

        return updated_session, decision, audit

    def generate_summary(self, timestamp: str | None = None) -> ValidationSummary:
        """Generate and persist an EvaluationSummary snapshot."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        total_candidates = len(self._eligibility_engine._candidates)
        total_sessions = len(self._validation_engine._sessions)
        total_obs = sum(len(obs) for obs in self._validation_engine._observations.values())

        st_counts: dict[str, int] = {s.value: 0 for s in ValidationStatus}
        dec_counts: dict[str, int] = {d.value: 0 for d in ValidationDecisionOutcome}

        for s in self._validation_engine._sessions.values():
            st_counts[s.status.value] += 1
        for d in self._retirement_engine._decisions.values():
            dec_counts[d.decision.value] += 1

        vsm_id, canonical_hash = compute_summary_id(
            total_candidates=total_candidates,
            total_sessions=total_sessions,
            timestamp=now_str,
        )

        summary = ValidationSummary(
            summary_id=vsm_id,
            total_candidates=total_candidates,
            total_sessions=total_sessions,
            total_observations=total_obs,
            status_counts=st_counts,
            decision_counts=dec_counts,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        if self._persistence:
            self._persistence.summaries.save(summary)

        return summary

    def generate_reports(self, session_id: str) -> dict[str, str]:
        """Generate Markdown and JSON reports for a given validation session ID."""
        session = self._validation_engine.get_session(session_id)
        if not session:
            raise KeyError(f"Session ID '{session_id}' not found.")

        observations = self._validation_engine.get_observations(session_id)
        candidate = self._eligibility_engine.get_candidate(session.candidate_id)
        summary = self.generate_summary()
        recent_sessions = list(self._validation_engine._sessions.values())[:10]

        reports: dict[str, str] = {
            "validation": generate_validation_report(session, observations),
            "monitoring": generate_monitoring_report(session_id, observations),
            "executive": generate_executive_report(summary, recent_sessions),
            "json": generate_json_report(session),
        }

        if candidate:
            reports["eligibility"] = generate_eligibility_report(candidate)

        for d in self._retirement_engine.list_all_decisions():
            if d.session_id == session_id:
                reports["decision"] = generate_decision_report(d)
                break

        if "decision" not in reports and self._persistence:
            d_p = self._persistence.decisions.get_by_session_id(session_id)
            if d_p:
                reports["decision"] = generate_decision_report(d_p)

        return reports
