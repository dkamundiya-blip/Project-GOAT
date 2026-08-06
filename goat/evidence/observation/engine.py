"""
Project GOAT v0.9 — Scientific Observation Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.evidence.core.canonical import compute_observation_id
from goat.evidence.core.enums import (
    EvidenceCategory,
    ObservationSource,
    ObservationStatus,
)
from goat.evidence.core.models import ScientificObservation


class ScientificObservationEngine:
    """Scientific Observation Engine for creating, timestamping, verifying, and maintaining

    chronological market observations without applying strategy interpretation or predictive logic.
    """

    def __init__(self) -> None:
        self._observations: dict[str, ScientificObservation] = {}

    def create_observation(
        self,
        metric_name: str,
        metric_value: Any,
        unit_of_measure: str = "",
        timestamp: str | None = None,
        source: ObservationSource = ObservationSource.LIVE_MARKET,
        category: EvidenceCategory = EvidenceCategory.PRICE,
        instrument: str = "",
        observer_id: str = "GOAT_OBSERVER",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ScientificObservation:
        """Observe and record an objective, uninterpreted market metric."""
        if not metric_name or len(metric_name.strip()) < 2:
            raise ValueError("Metric name must be at least 2 non-whitespace characters.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        obs_id, canonical_hash = compute_observation_id(
            metric_name=metric_name,
            metric_value=metric_value,
            timestamp=now_str,
            source=source.value,
            instrument=instrument,
        )

        observation = ScientificObservation(
            observation_id=obs_id,
            metric_name=metric_name.strip(),
            metric_value=metric_value,
            unit_of_measure=unit_of_measure.strip(),
            timestamp=now_str,
            source=source,
            category=category,
            instrument=instrument.strip().upper(),
            status=ObservationStatus.CREATED,
            observer_id=observer_id.strip(),
            tags=tags or [],
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self.verify_observation_integrity(observation)
        self._observations[obs_id] = observation
        return observation

    def verify_observation_integrity(self, observation: ScientificObservation) -> bool:
        """Verify deterministic ID, prefix, and non-empty timestamp of an observation."""
        if not observation.observation_id.startswith("OBS_"):
            raise ValueError(f"Observation ID '{observation.observation_id}' must start with 'OBS_'.")
        if not observation.timestamp:
            raise ValueError("Observation timestamp must not be empty.")
        if not observation.metric_name:
            raise ValueError("Observation metric_name must not be empty.")
        return True

    def get_observation(self, observation_id: str) -> ScientificObservation | None:
        """Retrieve observation by ID."""
        return self._observations.get(observation_id)

    def list_observations(
        self,
        instrument: str | None = None,
        category: EvidenceCategory | None = None,
        source: ObservationSource | None = None,
    ) -> list[ScientificObservation]:
        """Return chronological list of observations filtered by optional criteria."""
        results: list[ScientificObservation] = []
        inst_target = instrument.strip().upper() if instrument else None

        for obs in self._observations.values():
            if inst_target and obs.instrument != inst_target:
                continue
            if category is not None and obs.category != category:
                continue
            if source is not None and obs.source != source:
                continue
            results.append(obs)

        return sorted(results, key=lambda o: o.timestamp)
