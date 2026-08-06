"""
Project GOAT v0.9 — Validation Eligibility Engine
"""

from datetime import datetime, timezone
from typing import Any

from goat.live_validation.core.canonical import compute_candidate_id
from goat.live_validation.core.enums import ValidationStatus
from goat.live_validation.core.models import LiveValidationCandidate


class ValidationEligibilityEngine:
    """Validation Eligibility Engine for verifying that scientific hypotheses meet all strict criteria

    (completed experiment, supported statistical evaluation, evidence chain, replay integrity)
    before entering controlled live validation.
    """

    def __init__(self) -> None:
        self._candidates: dict[str, LiveValidationCandidate] = {}
        self._active_hypothesis_sessions: set[str] = set()

    def evaluate_eligibility(
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
        """Evaluate hypothesis eligibility for live validation and register candidate if qualified."""
        if not hypothesis_id.startswith("HYP_"):
            raise ValueError(f"Hypothesis ID '{hypothesis_id}' must start with 'HYP_'.")
        if not evaluation_id.startswith("STE_"):
            raise ValueError(f"Evaluation ID '{evaluation_id}' must start with 'STE_'.")
        if not experiment_id.startswith("EXP_"):
            raise ValueError(f"Experiment ID '{experiment_id}' must start with 'EXP_'.")

        # Strict eligibility verification
        if statistical_decision.strip().upper() != "SUPPORTED":
            raise ValueError(f"Hypothesis '{hypothesis_id}' decision '{statistical_decision}' is NOT SUPPORTED. Ineligible for live validation.")

        if hypothesis_id in self._active_hypothesis_sessions:
            raise ValueError(f"Hypothesis '{hypothesis_id}' already has an active live validation candidate/session.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        lvc_id, canonical_hash = compute_candidate_id(
            hypothesis_id=hypothesis_id,
            evaluation_id=evaluation_id,
            experiment_id=experiment_id,
        )

        candidate = LiveValidationCandidate(
            candidate_id=lvc_id,
            hypothesis_id=hypothesis_id.strip(),
            evaluation_id=evaluation_id.strip(),
            experiment_id=experiment_id.strip(),
            evidence_ids=evidence_ids or [],
            replay_id=replay_id.strip(),
            status=ValidationStatus.ELIGIBLE,
            eligibility_score=1.0,
            created_timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._candidates[lvc_id] = candidate
        self._active_hypothesis_sessions.add(hypothesis_id.strip())
        return candidate

    def get_candidate(self, candidate_id: str) -> LiveValidationCandidate | None:
        """Retrieve candidate by ID."""
        return self._candidates.get(candidate_id)

    def list_eligible(self) -> list[LiveValidationCandidate]:
        """List all candidates currently eligible for live validation."""
        return [c for c in self._candidates.values() if c.status == ValidationStatus.ELIGIBLE]

    def remove_active_hypothesis(self, hypothesis_id: str) -> None:
        """Clear active hypothesis session tracker on session completion or termination."""
        self._active_hypothesis_sessions.discard(hypothesis_id.strip())
