"""
Project GOAT v0.9 — Dedicated Unit Tests for Evidence Collection Engine
"""

import pytest

from goat.evidence.collection.engine import EvidenceCollectionEngine
from goat.evidence.core.enums import EvidenceCategory, ObservationSource
from goat.evidence.observation.engine import ScientificObservationEngine


@pytest.fixture
def obs_engine():
    return ScientificObservationEngine()


@pytest.fixture
def collection_engine():
    return EvidenceCollectionEngine()


@pytest.mark.parametrize("obs_count", range(1, 10))
def test_compile_evidence_record_success(
    obs_engine: ScientificObservationEngine,
    collection_engine: EvidenceCollectionEngine,
    obs_count: int,
):
    observations = [
        obs_engine.create_observation(
            metric_name=f"price_tick_{i}",
            metric_value=100.0 + i,
            timestamp=f"2026-08-04T12:{i:02d}:00Z",
        )
        for i in range(obs_count)
    ]

    record = collection_engine.compile_evidence_record(
        category=EvidenceCategory.PRICE,
        observations=observations,
        title=f"Compiled Record {obs_count}",
        description="Detailed description of price tick observations.",
        instrument="Volatility 100 Index",
    )

    assert record.evidence_id.startswith("EVR_")
    assert len(record.observation_ids) == obs_count
    assert record.category == EvidenceCategory.PRICE
    assert collection_engine.get_evidence_record(record.evidence_id) is not None


def test_compile_evidence_record_empty_observations(collection_engine: EvidenceCollectionEngine):
    with pytest.raises(ValueError):
        collection_engine.compile_evidence_record(
            category=EvidenceCategory.PRICE,
            observations=[],
            title="Empty Evidence Record",
        )


@pytest.mark.parametrize("col_idx", range(1, 10))
def test_create_collection_success(
    obs_engine: ScientificObservationEngine,
    collection_engine: EvidenceCollectionEngine,
    col_idx: int,
):
    observations = [
        obs_engine.create_observation(
            metric_name=f"metric_item_{k}",
            metric_value=k * 10,
            timestamp=f"2026-08-04T12:{k:02d}:00Z",
        )
        for k in range(col_idx)
    ]

    col = collection_engine.create_collection(
        collection_name=f"Collection Group #{col_idx}",
        observations=observations,
        collector_id="QUANT_COLLECTOR",
    )

    assert col.collection_id.startswith("COL_")
    assert len(col.observation_ids) == col_idx
    assert col.collector_id == "QUANT_COLLECTOR"
    assert collection_engine.get_collection(col.collection_id) is not None


def test_duplicate_record_idempotency(
    obs_engine: ScientificObservationEngine,
    collection_engine: EvidenceCollectionEngine,
):
    obs = obs_engine.create_observation(metric_name="spread", metric_value=0.2, timestamp="2026-08-04T12:00:00Z")

    rec1 = collection_engine.compile_evidence_record(
        category=EvidenceCategory.PRICE,
        observations=[obs],
        title="Idempotent Title",
        timestamp="2026-08-04T12:00:00Z",
    )

    rec2 = collection_engine.compile_evidence_record(
        category=EvidenceCategory.PRICE,
        observations=[obs],
        title="Idempotent Title",
        timestamp="2026-08-04T12:00:00Z",
    )

    assert rec1.evidence_id == rec2.evidence_id
    assert len(collection_engine.list_evidence_records()) == 1
