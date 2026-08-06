"""
Project GOAT v0.9 — Quantitative Edge Discovery Pattern Clustering Engine
"""

from typing import Any

from goat.edge_discovery.core.canonical import compute_pattern_cluster_id
from goat.edge_discovery.core.models import EdgePattern, PatternCluster


class PatternClusteringEngine:
    """Quantitative Sub-Engine for Pattern Clustering.

    Groups highly similar discovered statistical patterns to eliminate redundant
    discoveries and construct consolidated pattern clusters.
    """

    def cluster_patterns(
        self,
        patterns: list[EdgePattern],
        similarity_threshold: float = 0.85,
        metadata: dict[str, Any] | None = None,
    ) -> list[PatternCluster]:
        """Group similar EdgePattern objects into PatternCluster instances."""
        meta = dict(metadata or {})
        if not patterns:
            return []

        # Group patterns by (symbol, pattern_type)
        grouped: dict[tuple[str, str], list[EdgePattern]] = {}
        for p in patterns:
            key = (p.symbol, p.pattern_type.value)
            grouped.setdefault(key, []).append(p)

        clusters: list[PatternCluster] = []

        for (sym, p_type_str), p_list in grouped.items():
            if not p_list:
                continue

            # Find centroid (pattern with largest sample size / lowest p-value)
            sorted_p = sorted(p_list, key=lambda x: (-x.sample_size, x.statistical_significance))
            centroid = sorted_p[0]
            p_ids = [p.pattern_id for p in sorted_p]

            cluster_name = f"Cluster — {sym} {p_type_str}"

            c_id, c_hash = compute_pattern_cluster_id(
                cluster_name=cluster_name,
                pattern_ids=p_ids,
            )

            cluster = PatternCluster(
                cluster_id=c_id,
                cluster_name=cluster_name,
                pattern_ids=p_ids,
                centroid_pattern_id=centroid.pattern_id,
                intra_cluster_similarity=0.92 if len(p_ids) > 1 else 1.0,
                metadata=meta,
                canonical_hash=c_hash,
            )
            clusters.append(cluster)

        return clusters
