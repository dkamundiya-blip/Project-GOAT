"""
Project GOAT v0.9 — Comprehensive Dedicated Unit Tests for Evidence Domain Models
"""

import pytest
from pydantic import ValidationError

from goat.evidence.core.canonical import (
    compute_canonical_sha256,
    compute_collection_id,
    compute_evidence_record_id,
    compute_link_id,
    compute_observation_id,
    compute_summary_id,
    serialize_canonical_json,
)
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


@pytest.mark.parametrize("source", list(ObservationSource))
@pytest.mark.parametrize("category", list(EvidenceCategory))
@pytest.mark.parametrize("status", list(ObservationStatus))
@pytest.mark.parametrize("val", [10, 25.5, "high_vol", {"spread": 0.5}])
def test_scientific_observation_model_instantiation(
    source: ObservationSource,
    category: EvidenceCategory,
    status: ObservationStatus,
    val: float | str | dict,
):
    obs_id, canonical_hash = compute_observation_id(
        metric_name="volatility_std",
        metric_value=val,
        timestamp="2026-08-04T12:00:00Z",
        source=source.value,
        instrument="Volatility 100 Index",
    )

    obs = ScientificObservation(
        observation_id=obs_id,
        metric_name="volatility_std",
        metric_value=val,
        unit_of_measure="std_dev",
        timestamp="2026-08-04T12:00:00Z",
        source=source,
        category=category,
        instrument="Volatility 100 Index",
        status=status,
        observer_id="TEST_OBSERVER",
        tags=["volatility", "test"],
        metadata={"key": "val"},
        canonical_hash=canonical_hash,
    )

    assert obs.observation_id == obs_id
    assert obs.source == source
    assert obs.category == category
    assert obs.status == status
    assert obs.canonical_hash == canonical_hash


@pytest.mark.parametrize("invalid_id", ["INVALID_ID", "OBS_SHORT", "123_OBS", "HYP_1234567890ABCDEF"])
def test_scientific_observation_invalid_id_pattern(invalid_id: str):
    with pytest.raises(ValidationError):
        ScientificObservation(
            observation_id=invalid_id,
            metric_name="volatility_std",
            metric_value=1.5,
            timestamp="2026-08-04T12:00:00Z",
        )


def test_scientific_observation_immutability():
    obs_id, canonical_hash = compute_observation_id(
        metric_name="spread",
        metric_value=0.2,
        timestamp="2026-08-04T12:00:00Z",
    )
    obs = ScientificObservation(
        observation_id=obs_id,
        metric_name="spread",
        metric_value=0.2,
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=canonical_hash,
    )

    with pytest.raises(ValidationError):
        obs.metric_name = "new_metric"  # Frozen check


@pytest.mark.parametrize("category", list(EvidenceCategory))
@pytest.mark.parametrize("num_obs", range(1, 10))
def test_evidence_record_model(category: EvidenceCategory, num_obs: int):
    obs_ids = [f"OBS_{k:016X}" for k in range(1, num_obs + 1)]
    evr_id, evr_hash = compute_evidence_record_id(
        category=category.value,
        observation_ids=obs_ids,
        source="LIVE_MARKET",
        timestamp="2026-08-04T12:00:00Z",
    )

    record = EvidenceRecord(
        evidence_id=evr_id,
        category=category,
        observation_ids=obs_ids,
        title=f"Evidence Record {category.value}",
        description="Description of evidence record.",
        source=ObservationSource.LIVE_MARKET,
        instrument="Volatility 75 Index",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=evr_hash,
    )

    assert record.evidence_id == evr_id
    assert record.category == category
    assert len(record.observation_ids) == num_obs


@pytest.mark.parametrize("idx", range(1, 15))
def test_observation_collection_model(idx: int):
    obs_ids = [f"OBS_{k:016X}" for k in range(1, idx + 1)]
    col_id, col_hash = compute_collection_id(
        collection_name=f"Collection #{idx}",
        observation_ids=obs_ids,
        timestamp="2026-08-04T12:00:00Z",
    )

    collection = ObservationCollection(
        collection_id=col_id,
        collection_name=f"Collection #{idx}",
        observation_ids=obs_ids,
        start_timestamp="2026-08-04T12:00:00Z",
        end_timestamp="2026-08-04T13:00:00Z",
        collector_id="TEST_COLLECTOR",
        canonical_hash=col_hash,
    )

    assert collection.collection_id == col_id
    assert len(collection.observation_ids) == idx


@pytest.mark.parametrize("hyp_idx", range(1, 15))
def test_evidence_link_model(hyp_idx: int):
    hyp_id = f"HYP_{hyp_idx:016X}"
    evr_id = f"EVR_{hyp_idx:016X}"
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
        linker_id="TEST_LINKER",
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=lnk_hash,
    )

    assert link.link_id == lnk_id
    assert link.hypothesis_id == hyp_id
    assert link.target_id == evr_id


@pytest.mark.parametrize("obs_count", [0, 10, 50, 100])
def test_evidence_summary_model(obs_count: int):
    sum_id, sum_hash = compute_summary_id(
        total_observations=obs_count,
        total_evidence_records=obs_count // 2,
        timestamp="2026-08-04T12:00:00Z",
    )

    summary = EvidenceSummary(
        summary_id=sum_id,
        total_observations=obs_count,
        total_evidence_records=obs_count // 2,
        total_collections=obs_count // 5,
        total_links=obs_count // 2,
        category_counts={"PRICE": obs_count},
        source_counts={"LIVE_MARKET": obs_count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )

    assert summary.summary_id == sum_id
    assert summary.total_observations == obs_count
