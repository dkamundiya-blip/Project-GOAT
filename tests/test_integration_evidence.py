"""
Project GOAT v0.7 — Test Suite for Evidence Merger Engine

Coverage:
- Confidence accumulation (noisy-OR formula determinism & bounds)
- Reproducibility accumulation (arithmetic mean determinism & bounds)
- Consensus accumulation (ratio of support count to total count)
- Reference accumulation (experiment_refs, study_refs, execution_refs, feature_refs)
- Empty evidence handling
- Full merge_evidence workflow and canonical hash verification
"""

import pytest

from goat.integration.evidence.merger import EvidenceMerger


def test_confidence_accumulation_empty():
    assert EvidenceMerger.accumulate_confidence([]) == 0.0


def test_confidence_accumulation_single():
    assert EvidenceMerger.accumulate_confidence([0.75]) == 0.75


def test_confidence_accumulation_multiple():
    # 1 - (1 - 0.5) * (1 - 0.5) = 1 - 0.25 = 0.75
    val = EvidenceMerger.accumulate_confidence([0.5, 0.5])
    assert val == 0.75


def test_confidence_accumulation_clamping():
    val = EvidenceMerger.accumulate_confidence([-0.5, 1.5, 0.8])
    assert 0.0 <= val <= 1.0


def test_reproducibility_accumulation():
    assert EvidenceMerger.accumulate_reproducibility([]) == 0.0
    assert EvidenceMerger.accumulate_reproducibility([0.8, 0.9, 1.0]) == 0.9


def test_consensus_accumulation():
    assert EvidenceMerger.accumulate_consensus(0, 0) == 0.0
    assert EvidenceMerger.accumulate_consensus(3, 4) == 0.75


def test_evidence_merger_full_workflow():
    merger = EvidenceMerger()
    items = [
        {
            "evidence_id": "EV_1",
            "confidence": 0.8,
            "reproducibility": 0.9,
            "status": "PASSED",
            "experiment_refs": ["EXP_1"],
            "study_refs": ["STD_1"],
            "execution_refs": ["EXE_1"],
            "feature_refs": ["feat_momentum"],
        },
        {
            "evidence_id": "EV_2",
            "confidence": 0.7,
            "reproducibility": 0.85,
            "status": "VALIDATED",
            "experiment_refs": ["EXP_2"],
            "study_refs": ["STD_1"],
            "execution_refs": ["EXE_2"],
            "feature_refs": ["feat_volatility"],
        },
    ]

    record = merger.merge_evidence(
        evidence_items=items,
        target_knowledge_id="IKN_1234567890ABCDEF",
        timestamp="2026-07-30T00:00:00Z",
    )

    assert record.merge_id.startswith("EMG_")
    assert len(record.source_evidence_ids) == 2
    assert record.accumulated_confidence > 0.8
    assert record.accumulated_reproducibility == 0.875
    assert record.accumulated_consensus == 1.0
    assert record.experiment_refs == ["EXP_1", "EXP_2"]
    assert record.study_refs == ["STD_1"]
    assert record.feature_refs == ["feat_momentum", "feat_volatility"]
    assert len(record.canonical_hash) == 64
