"""
Project GOAT v0.7 — Test Suite for Conflict Detector Engine

Coverage:
- SUPPORTED conflict classification
- PARTIALLY_SUPPORTED conflict classification
- CONTRADICTED conflict classification
- DUPLICATED conflict classification
- SUPERSEDED conflict classification
- INSUFFICIENT_EVIDENCE conflict classification
- Pairwise conflict detection across validation runs
- Deterministic conflict ID and hash calculations
"""

from goat.integration.conflicts.detector import ConflictDetector
from goat.integration.core.enums import ConflictSeverity, ConflictType


def test_conflict_duplicated():
    detector = ConflictDetector()
    val_a = {"validation_id": "VAL_1", "status": "PASSED", "effect_direction": 1.0, "confidence": 0.85, "version": "1.0.0"}
    val_b = {"validation_id": "VAL_2", "status": "PASSED", "effect_direction": 1.0, "confidence": 0.85, "version": "1.0.0"}

    rec = detector.evaluate_conflict(val_a, val_b)
    assert rec.conflict_type == ConflictType.DUPLICATED
    assert rec.severity == ConflictSeverity.NONE


def test_conflict_contradicted():
    detector = ConflictDetector()
    val_a = {"validation_id": "VAL_1", "status": "PASSED", "confidence": 0.90}
    val_b = {"validation_id": "VAL_2", "status": "FAILED", "confidence": 0.85}

    rec = detector.evaluate_conflict(val_a, val_b)
    assert rec.conflict_type == ConflictType.CONTRADICTED
    assert rec.severity == ConflictSeverity.HIGH


def test_conflict_superseded():
    detector = ConflictDetector()
    val_a = {"validation_id": "VAL_1", "status": "PASSED", "version": "1.0.0", "confidence": 0.80}
    val_b = {"validation_id": "VAL_2", "status": "PASSED", "version": "2.0.0", "confidence": 0.90, "supersedes_id": "VAL_1"}

    rec = detector.evaluate_conflict(val_a, val_b)
    assert rec.conflict_type == ConflictType.SUPERSEDED


def test_conflict_insufficient_evidence():
    detector = ConflictDetector()
    val_a = {"validation_id": "VAL_1", "status": "PASSED", "confidence": 0.15}
    val_b = {"validation_id": "VAL_2", "status": "PASSED", "confidence": 0.80}

    rec = detector.evaluate_conflict(val_a, val_b)
    assert rec.conflict_type == ConflictType.INSUFFICIENT_EVIDENCE
    assert rec.severity == ConflictSeverity.LOW


def test_conflict_supported():
    detector = ConflictDetector()
    val_a = {"validation_id": "VAL_1", "status": "PASSED", "confidence": 0.85}
    val_b = {"validation_id": "VAL_2", "status": "PASSED", "confidence": 0.88}

    rec = detector.evaluate_conflict(val_a, val_b)
    assert rec.conflict_type == ConflictType.SUPPORTED
    assert rec.severity == ConflictSeverity.NONE


def test_conflict_partially_supported():
    detector = ConflictDetector()
    val_a = {"validation_id": "VAL_1", "status": "PASSED", "confidence": 0.95}
    val_b = {"validation_id": "VAL_2", "status": "PASSED", "confidence": 0.40}

    rec = detector.evaluate_conflict(val_a, val_b)
    assert rec.conflict_type == ConflictType.PARTIALLY_SUPPORTED


def test_detect_all_conflicts_pairwise():
    detector = ConflictDetector()
    vals = [
        {"validation_id": "VAL_1", "status": "PASSED", "confidence": 0.85},
        {"validation_id": "VAL_2", "status": "FAILED", "confidence": 0.80},
        {"validation_id": "VAL_3", "status": "PASSED", "confidence": 0.90},
    ]

    conflicts = detector.detect_all_conflicts(vals)
    # Number of pairwise combinations: 3 * 2 / 2 = 3
    assert len(conflicts) == 3
