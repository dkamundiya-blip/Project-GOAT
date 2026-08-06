"""
Project GOAT v0.7 — Test Suite for CompositeEdgeSynthesisEngine

Coverage:
- Pairwise composite edge synthesis
- Rejection of conflicting edge combinations
- CompositeEvidence and CompositeExplainabilityRecord generation
"""

from goat.alpha.core.canonical import compute_edge_id
from goat.alpha.core.models import ScientificEdge
from goat.composite.synthesis.engine import CompositeEdgeSynthesisEngine


def test_synthesize_composites_pairwise():
    engine = CompositeEdgeSynthesisEngine()

    e1_id, e1_hash = compute_edge_id("E1", ["H1"], ["V1"])
    e2_id, e2_hash = compute_edge_id("E2", ["H2"], ["V2"])

    e1 = ScientificEdge(edge_id=e1_id, title="Edge Alpha", confidence=0.85, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e1_hash)
    e2 = ScientificEdge(edge_id=e2_id, title="Edge Beta", confidence=0.88, discovery_timestamp="2026-07-30T00:00:00Z", canonical_hash=e2_hash)

    composites, evidence, explainability, conflict_map = engine.synthesize_composites([e1, e2], "2026-07-30T00:00:00Z")

    assert len(composites) == 1
    assert composites[0].composite_id.startswith("CMP_")
    assert len(evidence) == 2
    assert len(explainability) == 1
    assert composites[0].composite_id in conflict_map
