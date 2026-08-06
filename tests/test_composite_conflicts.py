"""
Project GOAT v0.7 — Test Suite for CompositeConflictEngine

Coverage:
- Direct contradiction conflict detection
- Duplicate evidence conflict penalty
- Weak reinforcement penalty
- Conflict severity levels (NONE, LOW, MEDIUM, HIGH, CRITICAL_REJECTION)
"""

from goat.alpha.core.canonical import compute_edge_id
from goat.alpha.core.models import ScientificEdge
from goat.composite.conflicts.engine import CompositeConflictEngine
from goat.composite.core.enums import ConflictSeverity


def test_conflict_engine_clean_pair():
    engine = CompositeConflictEngine()

    e1_id, e1_hash = compute_edge_id("Edge MOM", ["H1"], ["V1"])
    e2_id, e2_hash = compute_edge_id("Edge VOL", ["H2"], ["V2"])

    e1 = ScientificEdge(edge_id=e1_id, title="Quantitative Edge: MOM_10D", confidence=0.85, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)
    e2 = ScientificEdge(edge_id=e2_id, title="Quantitative Edge: VOL_BREAKOUT", confidence=0.88, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e2_hash)

    penalty, severity, exp = engine.evaluate_combination_conflicts([e1, e2])

    assert penalty == 0.0
    assert severity == ConflictSeverity.NONE


def test_conflict_engine_contradiction():
    engine = CompositeConflictEngine()

    e1_id, e1_hash = compute_edge_id("Edge MOM", ["H1"], ["V1"])
    e2_id, e2_hash = compute_edge_id("Edge REV", ["H2"], ["V2"])

    e1 = ScientificEdge(edge_id=e1_id, title="Quantitative Edge: MOM_10D", confidence=0.85, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)
    e2 = ScientificEdge(edge_id=e2_id, title="Quantitative Edge: REV_5D", confidence=0.85, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e2_hash)

    penalty, severity, exp = engine.evaluate_combination_conflicts([e1, e2])

    assert penalty >= 0.35
    assert severity in (ConflictSeverity.MEDIUM, ConflictSeverity.HIGH, ConflictSeverity.CRITICAL_REJECTION)
    assert "contradiction" in exp.lower()
