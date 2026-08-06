"""
Project GOAT v0.9 — Comprehensive Evidence Public API & Canonical Hash Integrity Tests
"""

import pytest

import goat.evidence as evidence
from goat.evidence import (
    CollectionRepository,
    EvidenceCategory,
    EvidenceCollectionEngine,
    EvidenceLink,
    EvidenceLinkageEngine,
    EvidencePersistenceContext,
    EvidenceRecord,
    EvidenceRepository,
    EvidenceSummary,
    LinkRepository,
    ObservationCollection,
    ObservationRepository,
    ObservationSource,
    ObservationStatus,
    ScientificEvidenceEngine,
    ScientificObservation,
    ScientificObservationEngine,
    SummaryRepository,
    compute_canonical_sha256,
    compute_collection_id,
    compute_evidence_record_id,
    compute_link_id,
    compute_observation_id,
    compute_summary_id,
    generate_collection_summary_report,
    generate_evidence_report,
    generate_evidence_summary_report,
    generate_executive_report,
    generate_json_report,
    generate_observation_report,
    init_evidence_db,
    serialize_canonical_json,
)


def test_public_api_exports():
    expected_exports = [
        "CollectionRepository",
        "EvidenceCategory",
        "EvidenceCollectionEngine",
        "EvidenceLink",
        "EvidenceLinkageEngine",
        "EvidencePersistenceContext",
        "EvidenceRecord",
        "EvidenceRepository",
        "EvidenceSummary",
        "LinkRepository",
        "ObservationCollection",
        "ObservationRepository",
        "ObservationSource",
        "ObservationStatus",
        "ScientificEvidenceEngine",
        "ScientificObservation",
        "ScientificObservationEngine",
        "SummaryRepository",
        "compute_canonical_sha256",
        "compute_collection_id",
        "compute_evidence_record_id",
        "compute_link_id",
        "compute_observation_id",
        "compute_summary_id",
        "generate_collection_summary_report",
        "generate_evidence_report",
        "generate_evidence_summary_report",
        "generate_executive_report",
        "generate_json_report",
        "generate_observation_report",
        "init_evidence_db",
        "serialize_canonical_json",
    ]

    for export_name in expected_exports:
        assert hasattr(evidence, export_name)
        assert export_name in evidence.__all__

    assert len(evidence.__all__) == len(expected_exports)


@pytest.mark.parametrize("i", range(1, 1001))
def test_observation_id_determinism_large(i: int):
    metric = f"metric_name_{i}"
    val = i * 1.25
    ts = f"2026-08-04T12:{i % 60:02d}:00Z"

    id1, hash1 = compute_observation_id(metric_name=metric, metric_value=val, timestamp=ts)
    id2, hash2 = compute_observation_id(metric_name=metric, metric_value=val, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("OBS_")
    assert len(id1) == 20
    assert len(hash1) == 64


@pytest.mark.parametrize("r", range(1, 1001))
def test_evidence_record_id_determinism_large(r: int):
    obs_ids = [f"OBS_{r:016X}", f"OBS_{(r+1):016X}"]
    ts = f"2026-08-04T12:{r % 60:02d}:00Z"

    id1, hash1 = compute_evidence_record_id(category="PRICE", observation_ids=obs_ids, timestamp=ts)
    id2, hash2 = compute_evidence_record_id(category="PRICE", observation_ids=obs_ids, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EVR_")
    assert len(id1) == 20


@pytest.mark.parametrize("c", range(1, 1001))
def test_collection_id_determinism_large(c: int):
    obs_ids = [f"OBS_{c:016X}"]
    ts = f"2026-08-04T12:{c % 60:02d}:00Z"

    id1, hash1 = compute_collection_id(collection_name=f"Collection {c}", observation_ids=obs_ids, timestamp=ts)
    id2, hash2 = compute_collection_id(collection_name=f"Collection {c}", observation_ids=obs_ids, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("COL_")
    assert len(id1) == 20


@pytest.mark.parametrize("l", range(1, 1001))
def test_link_id_determinism_large(l: int):
    hyp_id = f"HYP_{l:016X}"
    evr_id = f"EVR_{l:016X}"
    ts = f"2026-08-04T12:{l % 60:02d}:00Z"

    id1, hash1 = compute_link_id(hypothesis_id=hyp_id, target_id=evr_id, timestamp=ts)
    id2, hash2 = compute_link_id(hypothesis_id=hyp_id, target_id=evr_id, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("LNK_")
    assert len(id1) == 20


@pytest.mark.parametrize("s", range(1, 1001))
def test_summary_id_determinism_large(s: int):
    ts = f"2026-08-04T12:{s % 60:02d}:00Z"

    id1, hash1 = compute_summary_id(total_observations=s, total_evidence_records=s // 2, timestamp=ts)
    id2, hash2 = compute_summary_id(total_observations=s, total_evidence_records=s // 2, timestamp=ts)

    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("EVS_")
    assert len(id1) == 20
