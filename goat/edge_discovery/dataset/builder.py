"""
Project GOAT Phase 6 — Research Dataset Builder (`goat.edge_discovery.dataset`)

Generates reproducible research dataset exports capturing complete quantitative experiment state.
"""

from __future__ import annotations

import datetime
from typing import Sequence

from goat.edge_discovery.models.dataset import ResearchDataset, compute_dataset_id
from goat.edge_discovery.models.edge import DiscoveredEdge
from goat.feature_engineering.models.feature_vector import FeatureVector
from goat.research.edge.canonical import compute_canonical_sha256


class ResearchDatasetBuilder:
    """Quantitative Research Dataset Builder exporting reproducible research experiment artifacts."""

    def build_dataset(
        self,
        experiment_name: str,
        symbols: Sequence[str],
        timeframes: Sequence[str],
        raw_inputs_count: int,
        feature_vectors: Sequence[FeatureVector],
        discovered_edges: Sequence[DiscoveredEdge],
        version: str = "6.0.0",
        metadata: dict | None = None,
    ) -> ResearchDataset:
        """Build an immutable, reproducible ResearchDataset artifact."""
        sym_list = sorted(list(set(str(s).upper() for s in symbols)))
        tf_list = sorted(list(set(str(tf).lower() for tf in timeframes)))
        fv_count = len(feature_vectors)
        edge_count = len(discovered_edges)

        ds_id, canon_hash = compute_dataset_id(
            experiment_name=experiment_name,
            symbols=sym_list,
            timeframes=tf_list,
            feature_vectors_count=fv_count,
            version=version,
        )

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Aggregate regime distributions across feature vectors
        regime_counts: dict[str, int] = {"BULL_TREND": 0, "BEAR_TREND": 0, "SIDEWAYS": 0}
        for fv in feature_vectors:
            trend_dir = fv.get_feature("trend_direction", default=0.0)
            if trend_dir > 0:
                regime_counts["BULL_TREND"] += 1
            elif trend_dir < 0:
                regime_counts["BEAR_TREND"] += 1
            else:
                regime_counts["SIDEWAYS"] += 1

        val_summary = {
            "total_hypotheses_evaluated": fv_count,
            "edges_validated": edge_count,
            "validation_pass_rate": round(edge_count / max(fv_count, 1), 4),
            "top_edge_id": discovered_edges[0].edge_id if discovered_edges else None,
            "top_edge_sharpe": discovered_edges[0].metrics.sharpe_ratio if discovered_edges else 0.0,
        }

        checksum = compute_canonical_sha256(
            {
                "dataset_id": ds_id,
                "edges_count": edge_count,
                "experiment_name": experiment_name,
                "feature_vectors_count": fv_count,
                "version": version,
            }
        )

        return ResearchDataset(
            dataset_id=ds_id,
            experiment_name=experiment_name,
            version=version,
            creation_timestamp=now_iso,
            symbols=sym_list,
            timeframes=tf_list,
            raw_inputs_count=raw_inputs_count,
            feature_vectors_count=fv_count,
            edges_count=edge_count,
            regime_distribution=regime_counts,
            validation_summary=val_summary,
            checksum=checksum,
            metadata=metadata or {},
            canonical_hash=canon_hash,
        )
