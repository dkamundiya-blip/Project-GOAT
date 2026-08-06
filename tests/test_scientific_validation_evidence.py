"""
Project GOAT v0.7 — Step 5.7 Evidence Validation Subsystem Test Suite
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from goat.validation.evidence import (
    EvidenceAggregator,
    EvidenceCollector,
    ValidationEvidence,
    compute_evidence_id,
)


@pytest.mark.parametrize("idx", list(range(10)))
def test_evidence_id_determinism_parametrized(idx: int):
    """Verify deterministic evidence ID and hash generation across inputs."""
    eid1, hash1 = compute_evidence_id(f"VRN_{idx}", f"EXP_{idx}", "experiment", "2026-01-01T00:00:00Z")
    eid2, hash2 = compute_evidence_id(f"VRN_{idx}", f"EXP_{idx}", "experiment", "2026-01-01T00:00:00Z")

    assert eid1.startswith("VEV_")
    assert len(eid1) == 20
    assert len(hash1) == 64
    assert eid1 == eid2
    assert hash1 == hash2


def test_validation_evidence_model_immutability():
    """Verify ValidationEvidence model immutability and boundaries."""
    eid, ehash = compute_evidence_id("VRN_1", "EXP_1", "experiment", "2026-01-01T00:00:00Z")

    ev = ValidationEvidence(
        evidence_id=eid,
        evidence_hash=ehash,
        confidence=0.85,
        weight=1.5,
        timestamp="2026-01-01T00:00:00Z",
    )

    assert ev.confidence == 0.85
    assert ev.supports_hypothesis is True

    with pytest.raises(ValidationError):
        ev.confidence = 0.99

    # Test confidence boundaries [0.0, 1.0]
    with pytest.raises(ValidationError):
        ValidationEvidence(
            evidence_id=eid,
            evidence_hash=ehash,
            confidence=1.5,
            timestamp="2026-01-01T00:00:00Z",
        )

    with pytest.raises(ValidationError):
        ValidationEvidence(
            evidence_id=eid,
            evidence_hash=ehash,
            confidence=-0.1,
            timestamp="2026-01-01T00:00:00Z",
        )


@pytest.mark.parametrize("source_type,param_name", [
    ("experiment", "experiment_reference"),
    ("study", "study_reference"),
    ("consensus", "consensus_reference"),
    ("execution", "execution_reference"),
])
def test_evidence_collector_sources_parametrized(source_type: str, param_name: str):
    """Verify evidence collector across all 4 sources via parametrization."""
    collector = EvidenceCollector()
    kwargs = {
        "validation_run_id": "VRN_100",
        "hypothesis_id": "HYP_100",
        param_name: "REF_001",
        "confidence": 0.8,
        "supports": True,
    }

    if source_type == "experiment":
        ev = collector.collect_from_experiment(**kwargs)
    elif source_type == "study":
        ev = collector.collect_from_study(**kwargs)
    elif source_type == "consensus":
        ev = collector.collect_from_consensus(**kwargs)
    else:
        ev = collector.collect_from_execution(**kwargs)

    assert ev.evidence_type == source_type
    assert ev.confidence == 0.8
    assert ev.supports_hypothesis is True


def test_evidence_collector_get_missing_key():
    """Verify collector raises KeyError for missing evidence IDs."""
    collector = EvidenceCollector()
    with pytest.raises(KeyError):
        collector.get_evidence("VEV_NONEXISTENT")


def test_evidence_aggregator_empty_input():
    """Verify EvidenceAggregator handles empty inputs gracefully."""
    aggregator = EvidenceAggregator()
    summary = aggregator.aggregate_evidence([])

    assert summary["total_count"] == 0
    assert summary["supporting_count"] == 0
    assert summary["contradicting_count"] == 0
    assert summary["weighted_confidence"] == 0.0


@pytest.mark.parametrize("weights,confidences,expected_weighted_conf", [
    ([1.0, 1.0], [0.8, 0.6], 0.7),
    ([2.0, 1.0], [0.9, 0.6], 0.8),
    ([1.0, 3.0], [0.5, 0.9], 0.8),
])
def test_evidence_aggregator_weighted_confidence_parametrized(weights: list[float], confidences: list[float], expected_weighted_conf: float):
    """Verify evidence aggregator weighted confidence calculation across inputs."""
    aggregator = EvidenceAggregator()
    evidence_list = []
    for i, (w, c) in enumerate(zip(weights, confidences)):
        eid, eh = compute_evidence_id("VRN_1", f"REF_{i}", "experiment", f"2026-01-01T00:0{i}:00Z")
        ev = ValidationEvidence(evidence_id=eid, evidence_hash=eh, confidence=c, weight=w, timestamp=f"2026-01-01T00:0{i}:00Z")
        evidence_list.append(ev)

    summary = aggregator.aggregate_evidence(evidence_list)
    assert summary["weighted_confidence"] == expected_weighted_conf
