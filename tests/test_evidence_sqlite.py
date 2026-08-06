"""
Project GOAT v0.9 — Dedicated Unit Tests for Evidence SQLite Persistence
"""

import pytest

from goat.evidence.core.canonical import (
    compute_collection_id,
    compute_evidence_record_id,
    compute_link_id,
    compute_observation_id,
    compute_summary_id,
)
from goat.evidence.core.enums import EvidenceCategory, ObservationSource, ObservationStatus
from goat.evidence.core.models import (
    EvidenceLink,
    EvidenceRecord,
    EvidenceSummary,
    ObservationCollection,
    ScientificObservation,
)
from goat.evidence.persistence.sqlite import EvidencePersistenceContext


@pytest.fixture
def persistence_ctx():
    ctx = EvidencePersistenceContext(db_path=":memory:")
    yield ctx
    ctx.close()


@pytest.mark.parametrize("idx", range(1, 15))
def test_observation_repository_roundtrip(persistence_ctx: EvidencePersistenceContext, idx: int):
    obs_id, canonical_hash = compute_observation_id(
        metric_name=f"sqlite_metric_{idx}",
        metric_value=idx * 5.0,
        timestamp="2026-08-04T12:00:00Z",
    )

    obs = ScientificObservation(
        observation_id=obs_id,
        metric_name=f"sqlite_metric_{idx}",
        metric_value=idx * 5.0,
        unit_of_measure="units",
        timestamp="2026-08-04T12:00:00Z",
        source=ObservationSource.LIVE_MARKET,
        category=EvidenceCategory.PRICE,
        instrument="Volatility 100 Index",
        status=ObservationStatus.CREATED,
        observer_id="OBSERVER",
        tags=[f"tag_{idx}"],
        metadata={"idx": idx},
        canonical_hash=canonical_hash,
    )

    persistence_ctx.observations.save(obs)
    fetched = persistence_ctx.observations.get_by_id(obs_id)

    assert fetched is not None
    assert fetched.observation_id == obs.observation_id
    assert fetched.metric_name == obs.metric_name
    assert fetched.canonical_hash == obs.canonical_hash
    assert fetched.tags == obs.tags
    assert fetched.metadata == obs.metadata


@pytest.mark.parametrize("idx", range(1, 10))
def test_evidence_record_repository_roundtrip(persistence_ctx: EvidencePersistenceContext, idx: int):
    obs_id = f"OBS_{idx:016X}"
    evr_id, evr_hash = compute_evidence_record_id(
        category="PRICE",
        observation_ids=[obs_id],
        timestamp="2026-08-04T12:00:00Z",
    )

    record = EvidenceRecord(
        evidence_id=evr_id,
        category=EvidenceCategory.PRICE,
        observation_ids=[obs_id],
        title=f"Record #{idx}",
        description="SQLite test description",
        source=ObservationSource.LIVE_MARKET,
        instrument="Volatility 100 Index",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=evr_hash,
    )

    persistence_ctx.evidence_records.save(record)
    fetched = persistence_ctx.evidence_records.get_by_id(evr_id)

    assert fetched is not None
    assert fetched.evidence_id == evr_id
    assert fetched.title == record.title
    assert fetched.observation_ids == [obs_id]


@pytest.mark.parametrize("idx", range(1, 10))
def test_collection_repository_roundtrip(persistence_ctx: EvidencePersistenceContext, idx: int):
    obs_id = f"OBS_{idx:016X}"
    col_id, col_hash = compute_collection_id(
        collection_name=f"SQLite Collection #{idx}",
        observation_ids=[obs_id],
        timestamp="2026-08-04T12:00:00Z",
    )

    col = ObservationCollection(
        collection_id=col_id,
        collection_name=f"SQLite Collection #{idx}",
        observation_ids=[obs_id],
        start_timestamp="2026-08-04T12:00:00Z",
        end_timestamp="2026-08-04T13:00:00Z",
        collector_id="COLLECTOR",
        canonical_hash=col_hash,
    )

    persistence_ctx.collections.save(col)
    fetched = persistence_ctx.collections.get_by_id(col_id)

    assert fetched is not None
    assert fetched.collection_id == col_id
    assert fetched.collection_name == col.collection_name


@pytest.mark.parametrize("idx", range(1, 10))
def test_link_repository_roundtrip(persistence_ctx: EvidencePersistenceContext, idx: int):
    hyp_id = f"HYP_{idx:016X}"
    evr_id = f"EVR_{idx:016X}"
    lnk_id, lnk_hash = compute_link_id(
        hypothesis_id=hyp_id,
        target_id=evr_id,
        timestamp="2026-08-04T12:00:00Z",
    )

    link = EvidenceLink(
        link_id=lnk_id,
        hypothesis_id=hyp_id,
        target_id=evr_id,
        link_type="HYPOTHESIS_EVIDENCE_LINK",
        linker_id="LINKER",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=lnk_hash,
    )

    persistence_ctx.links.save(link)
    links = persistence_ctx.links.get_by_hypothesis_id(hyp_id)

    assert len(links) == 1
    assert links[0].link_id == lnk_id
    assert links[0].target_id == evr_id
