"""
Project GOAT v0.7 — Step 4.2 Feature Dependency Graph Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest

from goat.features import (
    BarRange,
    BodyRatio,
    CircularDependencyError,
    CompositeFeature,
    DerivedFeature,
    FeatureDependencyGraph,
    FeatureRegistryService,
    GraphValidationError,
    LogReturn,
    PrimitiveFeature,
    RegistrationStatus,
    RegistryRecord,
    SQLiteFeatureRepository,
    TaxonomyCategory,
)
from goat.features.core.context import MarketDataWindow


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


def test_dag_construction_and_topological_sort(temp_service):
    """Verify DAG construction and deterministic topological sorting."""
    service, repo, _ = temp_service

    f1 = LogReturn()
    f2 = BarRange()
    comp = DummyComposite([f1, f2], name="Comp1")

    r1 = service.register_feature(f1)
    r2 = service.register_feature(f2)
    rc = service.register_feature(comp)

    graph = FeatureDependencyGraph()
    graph.build_from_records([rc, r2, r1])

    top_order = graph.topological_sort()
    assert len(top_order) == 3
    # Root primitives (r1, r2) must come before composite (rc)
    assert top_order.index(r1.feature_id) < top_order.index(rc.feature_id)
    assert top_order.index(r2.feature_id) < top_order.index(rc.feature_id)


def test_dag_cycle_detection(temp_service):
    """Verify static DFS cycle detection raises CircularDependencyError."""
    service, repo, _ = temp_service

    f1 = LogReturn()
    r1 = service.register_feature(f1)

    # Construct synthetic circular dependency records
    dict1 = r1.model_dump()
    dict1["feature_id"] = "FEAT_AAAA111122223333"
    dict1["dependency_spec"] = ["FEAT_BBBB111122223333"]
    rec_a = r1.__class__(**dict1)

    dict2 = r1.model_dump()
    dict2["feature_id"] = "FEAT_BBBB111122223333"
    dict2["dependency_spec"] = ["FEAT_AAAA111122223333"]
    rec_b = r1.__class__(**dict2)

    graph = FeatureDependencyGraph()
    graph.add_node(rec_a)
    graph.add_node(rec_b)

    with pytest.raises(CircularDependencyError, match="Circular dependency detected"):
        graph.topological_sort()


def test_dag_missing_node_rejection():
    """Verify graph validation rejects missing upstream feature dependencies."""
    f1 = LogReturn()
    f2 = BarRange()
    comp = DummyComposite([f1, f2])

    # Construct RegistryRecord in memory for DAG structure testing
    meta = comp.metadata
    rc = RegistryRecord(
        feature_id=meta.feature_id,
        scientific_fingerprint=meta.scientific_fingerprint,
        canonical_hash=meta.canonical_hash,
        semantic_version=meta.version,
        feature_metadata=meta,
        capability_contract=meta.capabilities,
        input_contract=meta.input_contract,
        output_contract=meta.output_contract,
        execution_constraints=meta.constraints,
        dependency_spec=meta.dependencies,
        registration_timestamp=meta.creation_timestamp,
        registration_status=RegistrationStatus.REGISTERED,
    )

    graph = FeatureDependencyGraph()
    # Add composite without adding its required primitives f1, f2
    graph.add_node(rc)

    with pytest.raises(GraphValidationError, match="non-existent parent node|requires missing upstream feature"):
        graph.validate_graph()


def test_graph_hash_determinism(temp_service):
    """Verify compute_graph_hash is 100% bitwise deterministic across builds."""
    service, repo, _ = temp_service

    f1 = LogReturn()
    f2 = BarRange()
    comp = DummyComposite([f1, f2], name="Comp1")

    r1 = service.register_feature(f1)
    r2 = service.register_feature(f2)
    rc = service.register_feature(comp)

    graph1 = FeatureDependencyGraph()
    graph1.build_from_records([rc, r1, r2])
    hash1 = graph1.compute_graph_hash()

    graph2 = FeatureDependencyGraph()
    graph2.build_from_records([r2, rc, r1])
    hash2 = graph2.compute_graph_hash()

    assert hash1 == hash2
    assert len(hash1) == 64
