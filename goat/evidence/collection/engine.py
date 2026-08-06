"""
Project GOAT v0.9 — Evidence Collection Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.evidence.core.canonical import (
    compute_collection_id,
    compute_evidence_record_id,
)
from goat.evidence.core.enums import (
    EvidenceCategory,
    ObservationSource,
)
from goat.evidence.core.models import (
    EvidenceRecord,
    ObservationCollection,
    ScientificObservation,
)


class EvidenceCollectionEngine:
    """Evidence Collection Engine for collecting, grouping, and packaging scientific observations

    into immutable EvidenceRecord and ObservationCollection entities.
    """

    def __init__(self) -> None:
        self._evidence_records: dict[str, EvidenceRecord] = {}
        self._collections: dict[str, ObservationCollection] = {}

    def compile_evidence_record(
        self,
        category: EvidenceCategory,
        observations: Sequence[ScientificObservation],
        title: str,
        description: str = "",
        source: ObservationSource = ObservationSource.LIVE_MARKET,
        instrument: str = "",
        timestamp: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceRecord:
        """Compile a list of observations into an immutable EvidenceRecord (EVR_<HEX16>)."""
        if not observations:
            raise ValueError("EvidenceRecord requires at least one ScientificObservation.")
        if not title or len(title.strip()) < 3:
            raise ValueError("Title must be at least 3 non-whitespace characters.")

        obs_ids = sorted([obs.observation_id for obs in observations])
        now_str = timestamp or datetime.now(timezone.utc).isoformat()

        evr_id, canonical_hash = compute_evidence_record_id(
            category=category.value,
            observation_ids=obs_ids,
            source=source.value,
            timestamp=now_str,
        )

        if evr_id in self._evidence_records:
            return self._evidence_records[evr_id]

        record = EvidenceRecord(
            evidence_id=evr_id,
            category=category,
            observation_ids=obs_ids,
            title=title.strip(),
            description=description.strip(),
            source=source,
            instrument=instrument.strip().upper(),
            timestamp=now_str,
            tags=tags or [],
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._evidence_records[evr_id] = record
        return record

    def create_collection(
        self,
        collection_name: str,
        observations: Sequence[ScientificObservation],
        collector_id: str = "GOAT_COLLECTOR",
        timestamp: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ObservationCollection:
        """Group observations into a chronological ObservationCollection (COL_<HEX16>)."""
        if not collection_name or len(collection_name.strip()) < 3:
            raise ValueError("Collection name must be at least 3 non-whitespace characters.")

        obs_list = sorted(observations, key=lambda o: o.timestamp)
        obs_ids = [o.observation_id for o in obs_list]
        now_str = timestamp or datetime.now(timezone.utc).isoformat()

        start_time = obs_list[0].timestamp if obs_list else now_str
        end_time = obs_list[-1].timestamp if obs_list else now_str

        col_id, canonical_hash = compute_collection_id(
            collection_name=collection_name,
            observation_ids=obs_ids,
            timestamp=now_str,
        )

        if col_id in self._collections:
            return self._collections[col_id]

        collection = ObservationCollection(
            collection_id=col_id,
            collection_name=collection_name.strip(),
            observation_ids=obs_ids,
            start_timestamp=start_time,
            end_timestamp=end_time,
            collector_id=collector_id.strip(),
            tags=tags or [],
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._collections[col_id] = collection
        return collection

    def get_evidence_record(self, evidence_id: str) -> EvidenceRecord | None:
        """Retrieve evidence record by ID."""
        return self._evidence_records.get(evidence_id)

    def get_collection(self, collection_id: str) -> ObservationCollection | None:
        """Retrieve collection by ID."""
        return self._collections.get(collection_id)

    def list_evidence_records(self) -> list[EvidenceRecord]:
        """List all compiled evidence records sorted by timestamp."""
        return sorted(self._evidence_records.values(), key=lambda r: r.timestamp)

    def list_collections(self) -> list[ObservationCollection]:
        """List all observation collections sorted by start timestamp."""
        return sorted(self._collections.values(), key=lambda c: c.start_timestamp)
