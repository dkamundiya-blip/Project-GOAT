"""
Project GOAT v0.9 — Controlled Live Validation Engine
"""

from datetime import datetime, timezone
from typing import Any

from goat.live_validation.core.canonical import compute_observation_id, compute_session_id
from goat.live_validation.core.enums import MonitoringStatus, ValidationStatus
from goat.live_validation.core.models import (
    LiveValidationCandidate,
    ValidationObservation,
    ValidationSession,
)


class ControlledLiveValidationEngine:
    """Controlled Live Validation Engine managing live validation sessions and recording empirical live observations."""

    def __init__(self) -> None:
        self._sessions: dict[str, ValidationSession] = {}
        self._observations: dict[str, list[ValidationObservation]] = {}

    def start_session(
        self,
        candidate: LiveValidationCandidate,
        operator: str = "LIVE_VALIDATION_ENGINE",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ValidationSession:
        """Start a new controlled live validation session for an eligible candidate."""
        if candidate.status != ValidationStatus.ELIGIBLE:
            raise ValueError(f"Candidate '{candidate.candidate_id}' is not in ELIGIBLE status.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        vsn_id, canonical_hash = compute_session_id(
            candidate_id=candidate.candidate_id,
            start_timestamp=now_str,
            operator=operator,
        )

        session = ValidationSession(
            session_id=vsn_id,
            candidate_id=candidate.candidate_id,
            hypothesis_id=candidate.hypothesis_id,
            status=ValidationStatus.RUNNING,
            monitoring_status=MonitoringStatus.NORMAL,
            start_timestamp=now_str,
            total_observations=0,
            operator=operator,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._sessions[vsn_id] = session
        self._observations[vsn_id] = []
        return session

    def record_observation(
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
    ) -> ValidationObservation:
        """Record an empirical live observation under controlled live market conditions."""
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Validation session '{session_id}' not found.")
        if session.status != ValidationStatus.RUNNING:
            raise ValueError(f"Cannot record observation on session '{session_id}' in status '{session.status}'.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        vob_id, canonical_hash = compute_observation_id(
            session_id=session_id,
            timestamp=now_str,
            live_outcome=live_outcome,
            expected_outcome=expected_outcome,
        )

        observation = ValidationObservation(
            observation_id=vob_id,
            session_id=session_id,
            timestamp=now_str,
            live_outcome=live_outcome,
            expected_outcome=expected_outcome,
            slippage=slippage,
            spread=spread,
            latency_ms=latency_ms,
            fill_ratio=fill_ratio,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._observations[session_id].append(observation)

        # Update observation count on session model
        updated_session = ValidationSession(
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            hypothesis_id=session.hypothesis_id,
            status=session.status,
            monitoring_status=session.monitoring_status,
            start_timestamp=session.start_timestamp,
            end_timestamp=session.end_timestamp,
            total_observations=len(self._observations[session_id]),
            operator=session.operator,
            metadata=session.metadata,
            canonical_hash=session.canonical_hash,
        )
        self._sessions[session_id] = updated_session

        return observation

    def get_session(self, session_id: str) -> ValidationSession | None:
        """Retrieve session by ID."""
        return self._sessions.get(session_id)

    def get_observations(self, session_id: str) -> list[ValidationObservation]:
        """Retrieve observations recorded for a session."""
        return self._observations.get(session_id, [])

    def update_session_status(self, session_id: str, new_status: ValidationStatus, new_monitoring: MonitoringStatus | None = None) -> ValidationSession:
        """Update session status."""
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        now_str = datetime.now(timezone.utc).isoformat() if new_status in (ValidationStatus.COMPLETED, ValidationStatus.FAILED) else session.end_timestamp

        updated = ValidationSession(
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            hypothesis_id=session.hypothesis_id,
            status=new_status,
            monitoring_status=new_monitoring or session.monitoring_status,
            start_timestamp=session.start_timestamp,
            end_timestamp=now_str,
            total_observations=session.total_observations,
            operator=session.operator,
            metadata=session.metadata,
            canonical_hash=session.canonical_hash,
        )
        self._sessions[session_id] = updated
        return updated
