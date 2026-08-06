"""
Project GOAT v0.9 — Dedicated Tests for Pattern Clustering Engine
"""

import pytest

from goat.edge_discovery.clustering.engine import PatternClusteringEngine
from goat.edge_discovery.core.canonical import compute_edge_pattern_id
from goat.edge_discovery.core.enums import PatternType
from goat.edge_discovery.core.models import EdgePattern
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)
PATTERN_TYPES = list(PatternType)


@pytest.mark.parametrize("index_type", INDICES)
@pytest.mark.parametrize("p_type", PATTERN_TYPES[:3])
def test_pattern_clustering(index_type: SyntheticIndexType, p_type: PatternType) -> None:
    clusterer = PatternClusteringEngine()

    p_list = []
    for i in range(3):
        p_id, p_hash = compute_edge_pattern_id(p_type.value, index_type.value, 20 + i, 0.01)
        p = EdgePattern(
            pattern_id=p_id,
            pattern_type=p_type,
            symbol=index_type.value,
            sample_size=20 + i,
            effect_size=0.10,
            statistical_significance=0.01,
            regime_consistency=0.90,
            observation_ids=[f"MSO_{i}"],
            metadata={},
            canonical_hash=p_hash,
        )
        p_list.append(p)

    clusters = clusterer.cluster_patterns(p_list)
    assert len(clusters) == 1
    cluster = clusters[0]
    assert cluster.cluster_id.startswith("CLS_")
    assert len(cluster.pattern_ids) == 3
    assert cluster.intra_cluster_similarity > 0.0


def test_pattern_clustering_empty() -> None:
    clusterer = PatternClusteringEngine()
    clusters = clusterer.cluster_patterns([])
    assert len(clusters) == 0
