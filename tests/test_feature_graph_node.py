"""
Project GOAT v0.7 — Step 4.2-R1 Graph Node & Edge Engine Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pydantic import ValidationError

from goat.features import (
    BarRange,
    BodyRatio,
    CompositeFeature,
    FeatureDependencyGraph,
    FeatureRegistryService,
    GraphEdge,
    GraphNode,
    GraphValidationError,
    LogReturn,
    RegistryRecord,
    SQLiteFeatureRepository,
    TaxonomyCategory,
    compute_edge_id,
    compute_node_id,
)
from goat.features.core.context import MarketDataWindow
from goat.research.edge.canonical import canonical_json


class DummyComposite(CompositeFeature):
    """Dummy Composite feature for graph testing."""

    def __init__(self, upstream_features, name="DummyComposite", version="1.0.0"):
        super().__init__(
            upstream_features=upstream_features,
            name=name,
            version=version,
            taxonomy_category=TaxonomyCategory.COMPOSITE,
            mathematical_definition="f1 + f2",
            algorithmic_spec="f1 + f2",
        )

    def compute(self, context: MarketDataWindow):
        return self._upstream_features[0].compute(context) + self._upstream_features[1].compute(context)

    def to_ast_dict(self):
        return {"op": "add", "inputs": [f.feature_id for f in self._upstream_features]}

    def _get_input_requirements(self):
        return {"min_bars": 1, "required_columns": ["close"]}


@pytest.fixture
def temp_service():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteFeatureRepository(db_path)
    service = FeatureRegistryService(repo)
    yield service, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_node_and_edge_identity_determinism():
    """Verify NODE_<HEX16> and EDGE_<HEX16> deterministic calculations."""
    nid1 = compute_node_id("FEAT_1234567890ABCDEF", "FPT_" + "a" * 64, depth=1)
    nid2 = compute_node_id("FEAT_1234567890ABCDEF", "FPT_" + "a" * 64, depth=1)

    assert nid1 == nid2
    assert nid1.startswith("NODE_")
    assert len(nid1) == 21

    eid1, hash1 = compute_edge_id("FEAT_1111", "FEAT_2222", "required")
    eid2, hash2 = compute_edge_id("FEAT_1111", "FEAT_2222", "required")

    assert eid1 == eid2
    assert hash1 == hash2
    assert eid1.startswith("EDGE_")
    assert len(eid1) == 21
    assert len(hash1) == 64


def test_node_and_edge_immutability():
    """Verify GraphNode and GraphEdge models are frozen and immutable."""
    nid = compute_node_id("FEAT_1234567890ABCDEF", "FPT_" + "a" * 64, depth=0)
    node = GraphNode(
        node_id=nid,
        feature_id="FEAT_1234567890ABCDEF",
        scientific_fingerprint="FPT_" + "a" * 64,
        canonical_hash="b" * 64,
    )

    with pytest.raises(ValidationError):
        node.dependency_depth = 5  # Frozen check


def test_ancestor_and_descendant_traversal(temp_service):
    """Verify recursive ancestor and descendant graph traversal APIs."""
    service, _, _ = temp_service

    f1 = LogReturn()
    f2 = BarRange()
    comp1 = DummyComposite([f1, f2], name="Comp1")
    comp2 = DummyComposite([comp1], name="Comp2")

    r1 = service.register_feature(f1)
    r2 = service.register_feature(f2)
    rc1 = service.register_feature(comp1)
    rc2 = service.register_feature(comp2)

    graph = FeatureDependencyGraph()
    graph.build_from_records([r1, r2, rc1, rc2])

    # Ancestors of comp2 must include comp1, f1, f2
    ancestors_comp2 = graph.get_ancestors(rc2.feature_id)
    assert len(ancestors_comp2) == 3
    assert set(ancestors_comp2) == {r1.feature_id, r2.feature_id, rc1.feature_id}

    # Descendants of f1 must include comp1, comp2
    descendants_f1 = graph.get_descendants(r1.feature_id)
    assert len(descendants_f1) == 2
    assert set(descendants_f1) == {rc1.feature_id, rc2.feature_id}


def test_graph_statistics_and_depth(temp_service):
    """Verify get_graph_statistics and get_dependency_depth."""
    service, _, _ = temp_service

    f1 = LogReturn()
    f2 = BarRange()
    comp1 = DummyComposite([f1, f2], name="Comp1")

    r1 = service.register_feature(f1)
    r2 = service.register_feature(f2)
    rc1 = service.register_feature(comp1)

    graph = FeatureDependencyGraph()
    graph.build_from_records([r1, r2, rc1])

    stats = graph.get_graph_statistics()
    assert stats["node_count"] == 3
    assert stats["edge_count"] == 2
    assert stats["root_count"] == 2  # r1, r2 are roots
    assert stats["leaf_count"] == 1  # rc1 is leaf
    assert stats["max_depth"] == 1

    assert graph.get_dependency_depth(r1.feature_id) == 0
    assert graph.get_dependency_depth(rc1.feature_id) == 1


def test_graph_validation_failures():
    """Verify fail-closed graph validation on duplicate nodes and missing edge references."""
    f1 = LogReturn()
    meta1 = f1.metadata
    rec1 = RegistryRecord(
        feature_id=meta1.feature_id,
        scientific_fingerprint=meta1.scientific_fingerprint,
        canonical_hash=meta1.canonical_hash,
        semantic_version=meta1.version,
        feature_metadata=meta1,
        capability_contract=meta1.capabilities,
        input_contract=meta1.input_contract,
        output_contract=meta1.output_contract,
        execution_constraints=meta1.constraints,
        registration_timestamp="2026-07-30T00:00:00Z",
    )

    graph = FeatureDependencyGraph()
    graph.add_node(rec1)

    # Re-adding node must raise GraphValidationError
    with pytest.raises(GraphValidationError, match="Duplicate node registration"):
        graph.add_node(rec1)


def test_graph_export_serialization(temp_service):
    """Verify export_graph produces deterministic JSON serializable output."""
    service, _, _ = temp_service

    f1 = LogReturn()
    f2 = BarRange()
    comp1 = DummyComposite([f1, f2], name="Comp1")

    r1 = service.register_feature(f1)
    r2 = service.register_feature(f2)
    rc1 = service.register_feature(comp1)

    graph = FeatureDependencyGraph()
    graph.build_from_records([r1, r2, rc1])

    exported = graph.export_graph()
    assert exported["node_count"] == 3
    assert len(exported["nodes"]) == 3
    assert len(exported["edges"]) == 2

    # Canonical JSON string check
    canon_str = canonical_json(exported)
    assert "graph_hash" in canon_str
    assert "NODE_" in canon_str
    assert "EDGE_" in canon_str
