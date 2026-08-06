"""
Project GOAT v0.7 — Test Suite for EdgeEvidenceAggregator

Coverage:
- Supporting EdgeEvidence extraction from validations and clusters
- EdgeExplainabilityRecord generation
- Scientific traceability verification
"""

from goat.alpha.core.canonical import compute_edge_id
from goat.alpha.core.enums import EdgeMaturity, EvidenceSourceType
from goat.alpha.core.models import ScientificEdge
from goat.alpha.evidence.aggregator import EdgeEvidenceAggregator


def test_aggregate_evidence():
    aggregator = EdgeEvidenceAggregator()

    e_id, e_hash = compute_edge_id("Edge Alpha", ["HYP_1"], ["VAL_100"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge Alpha",
        maturity=EdgeMaturity.EMERGING,
        originating_hypotheses=["HYP_1"],
        originating_validations=["VAL_100"],
        originating_clusters=["RCL_100"],
        confidence=0.85,
        reproducibility=0.90,
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    ev_list = aggregator.aggregate_evidence(edge, [{"validation_id": "VAL_100"}])

    assert len(ev_list) == 2  # 1 Validation + 1 Cluster
    val_ev = [ev for ev in ev_list if ev.source_type == EvidenceSourceType.VALIDATION][0]
    assert val_ev.source_reference == "VAL_100"


def test_build_explainability_record():
    aggregator = EdgeEvidenceAggregator()

    e_id, e_hash = compute_edge_id("Edge Alpha", ["HYP_1"], ["VAL_100"])
    edge = ScientificEdge(
        edge_id=e_id,
        title="Edge Alpha",
        maturity=EdgeMaturity.VALIDATED,
        originating_hypotheses=["HYP_1"],
        originating_validations=["VAL_100"],
        discovery_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=e_hash,
    )

    ev_list = aggregator.aggregate_evidence(edge, [{"validation_id": "VAL_100"}])
    expl = aggregator.build_explainability_record(edge, ev_list)

    assert expl.explanation_id.startswith("EEX_")
    assert expl.origin == "HYP_1"
    assert "VAL_100" in expl.supporting_experiments
    assert len(expl.scientific_explanation) > 0
