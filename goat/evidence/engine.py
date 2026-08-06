"""
Project GOAT v0.9 — Master Evidence Engine Facade
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.evidence.collection.engine import EvidenceCollectionEngine
from goat.evidence.core.canonical import compute_summary_id
from goat.evidence.core.enums import (
    EvidenceCategory,
    ObservationSource,
    ObservationStatus,
)
from goat.evidence.core.models import (
    EvidenceLink,
    EvidenceRecord,
    EvidenceSummary,
    ObservationCollection,
    ScientificObservation,
)
from goat.evidence.linkage.engine import EvidenceLinkageEngine
from goat.evidence.observation.engine import ScientificObservationEngine
from goat.evidence.persistence.sqlite import EvidencePersistenceContext
from goat.evidence.reporting.reports import (
    generate_collection_summary_report,
    generate_evidence_report,
    generate_evidence_summary_report,
    generate_executive_report,
    generate_json_report,
    generate_observation_report,
)


class ScientificEvidenceEngine:
    """Master Facade Engine orchestrating observation creation, evidence compilation,

    hypothesis linkage, reporting, and optional SQLite persistence.
    """

    def __init__(
        self,
        persistence_context: EvidencePersistenceContext | None = None,
        observation_engine: ScientificObservationEngine | None = None,
        collection_engine: EvidenceCollectionEngine | None = None,
        linkage_engine: EvidenceLinkageEngine | None = None,
    ) -> None:
        self._observation_engine = observation_engine or ScientificObservationEngine()
        self._collection_engine = collection_engine or EvidenceCollectionEngine()
        self._linkage_engine = linkage_engine or EvidenceLinkageEngine()
        self._persistence = persistence_context

        # Sync existing database entities if persistence context provided
        if self._persistence:
            for obs in self._persistence.observations.list_all():
                self._observation_engine._observations[obs.observation_id] = obs
            for evr in self._persistence.evidence_records.list_all():
                self._collection_engine._evidence_records[evr.evidence_id] = evr
            for col in self._persistence.collections.list_all():
                self._collection_engine._collections[col.collection_id] = col
            for lnk in self._persistence.links.list_all():
                self._linkage_engine._links[lnk.link_id] = lnk
                self._linkage_engine._hypothesis_map.setdefault(lnk.hypothesis_id, set()).add(lnk.link_id)
                self._linkage_engine._target_map.setdefault(lnk.target_id, set()).add(lnk.link_id)

    @property
    def observation_engine(self) -> ScientificObservationEngine:
        return self._observation_engine

    @property
    def collection_engine(self) -> EvidenceCollectionEngine:
        return self._collection_engine

    @property
    def linkage_engine(self) -> EvidenceLinkageEngine:
        return self._linkage_engine

    @property
    def persistence(self) -> EvidencePersistenceContext | None:
        return self._persistence

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
        """Create and persist an objective, uninterpreted scientific observation."""
        obs = self._observation_engine.create_observation(
            metric_name=metric_name,
            metric_value=metric_value,
            unit_of_measure=unit_of_measure,
            timestamp=timestamp,
            source=source,
            category=category,
            instrument=instrument,
            observer_id=observer_id,
            tags=tags,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.observations.save(obs)

        return obs

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
        """Compile multiple observations into an immutable EvidenceRecord."""
        record = self._collection_engine.compile_evidence_record(
            category=category,
            observations=observations,
            title=title,
            description=description,
            source=source,
            instrument=instrument,
            timestamp=timestamp,
            tags=tags,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.evidence_records.save(record)

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
        """Group observations into a chronological ObservationCollection."""
        collection = self._collection_engine.create_collection(
            collection_name=collection_name,
            observations=observations,
            collector_id=collector_id,
            timestamp=timestamp,
            tags=tags,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.collections.save(collection)

        return collection

    def create_link(
        self,
        hypothesis_id: str,
        target_id: str,
        link_type: str = "HYPOTHESIS_EVIDENCE_LINK",
        linker_id: str = "GOAT_LINKER",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceLink:
        """Link a hypothesis ID to an evidence or observation ID without evaluating support/refutation."""
        link = self._linkage_engine.create_link(
            hypothesis_id=hypothesis_id,
            target_id=target_id,
            link_type=link_type,
            linker_id=linker_id,
            timestamp=timestamp,
            metadata=metadata,
        )

        if self._persistence:
            self._persistence.links.save(link)

        return link

    def generate_summary(self, timestamp: str | None = None) -> EvidenceSummary:
        """Generate an EvidenceSummary snapshot of subsystem metrics."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        total_obs = len(self._observation_engine._observations)
        total_evr = len(self._collection_engine._evidence_records)
        total_col = len(self._collection_engine._collections)
        total_lnk = len(self._linkage_engine._links)

        cat_counts: dict[str, int] = {c.value: 0 for c in EvidenceCategory}
        src_counts: dict[str, int] = {s.value: 0 for s in ObservationSource}

        for obs in self._observation_engine._observations.values():
            cat_counts[obs.category.value] += 1
            src_counts[obs.source.value] += 1

        sum_id, canonical_hash = compute_summary_id(
            total_observations=total_obs,
            total_evidence_records=total_evr,
            timestamp=now_str,
        )

        summary = EvidenceSummary(
            summary_id=sum_id,
            total_observations=total_obs,
            total_evidence_records=total_evr,
            total_collections=total_col,
            total_links=total_lnk,
            category_counts=cat_counts,
            source_counts=src_counts,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

        if self._persistence:
            self._persistence.summaries.save(summary)

        return summary

    def generate_reports(self, entity_id: str) -> dict[str, str]:
        """Generate Markdown and JSON reports for a given entity ID (OBS_, EVR_, COL_)."""
        summary = self.generate_summary()
        recent_records = self._collection_engine.list_evidence_records()[:10]

        reports: dict[str, str] = {
            "summary": generate_evidence_summary_report(summary),
            "executive": generate_executive_report(summary, recent_records),
        }

        if entity_id.startswith("OBS_"):
            obs = self._observation_engine.get_observation(entity_id)
            if obs:
                reports["markdown"] = generate_observation_report(obs)
                reports["json"] = generate_json_report(obs)
        elif entity_id.startswith("EVR_"):
            evr = self._collection_engine.get_evidence_record(entity_id)
            if evr:
                reports["markdown"] = generate_evidence_report(evr)
                reports["json"] = generate_json_report(evr)
        elif entity_id.startswith("COL_"):
            col = self._collection_engine.get_collection(entity_id)
            if col:
                reports["markdown"] = generate_collection_summary_report(col)
                reports["json"] = generate_json_report(col)

        return reports
