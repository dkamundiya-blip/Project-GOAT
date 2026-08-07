"""
Project GOAT Master Quantitative Edge Discovery Engine (`goat.edge_discovery.engine`)

Unified Master Edge Discovery Engine providing:
1. Phase 6 Quantitative Feature Edge Discovery & Statistical Research (Hypotheses, 16 Metrics, Bootstrap/Monte Carlo, Regimes, Walk-Forward, Feature Store, Ranking, Decay, Dataset Exports).
2. v0.9 Microstructure Pattern Mining & Discovery Validation.
"""

from __future__ import annotations

import datetime
from pathlib import Path
import sqlite3
import threading
from typing import Any, Callable, Sequence

from goat.edge_discovery.clustering.engine import PatternClusteringEngine
from goat.edge_discovery.core.canonical import compute_discovery_summary_id
from goat.edge_discovery.core.enums import ValidationStatus
from goat.edge_discovery.core.models import (
    DiscoveryDecision,
    DiscoverySummary,
    EdgeCandidate,
    EdgePattern,
    EdgeScore,
    NoveltyAssessment,
    PatternCluster,
)
from goat.edge_discovery.dataset.builder import ResearchDatasetBuilder
from goat.edge_discovery.decay.engine import EdgeDecayEngine
from goat.edge_discovery.evaluator.engine import HistoricalEvaluationEngine
from goat.edge_discovery.generator.engine import FeatureCombinationGenerator
from goat.edge_discovery.hypothesis.engine import HypothesisEngine
from goat.edge_discovery.mining.engine import PatternMiningEngine
from goat.edge_discovery.models.dataset import ResearchDataset
from goat.edge_discovery.models.edge import (
    DiscoveredEdge,
    EdgeStatus,
    compute_edge_id,
)
from goat.edge_discovery.models.hypothesis import (
    HypothesisPrediction,
    ResearchHypothesis,
)
from goat.edge_discovery.novelty.engine import NoveltyAssessmentEngine
from goat.edge_discovery.persistence.in_memory import InMemoryEdgeRepository
from goat.edge_discovery.persistence.interfaces import IEdgeRepository
from goat.edge_discovery.persistence.sqlite import (
    EdgeDiscoveryPersistenceContext,
    SQLiteEdgeRepository,
    init_edge_discovery_db,
)
from goat.edge_discovery.ranking.engine import EdgeRankingEngine
from goat.edge_discovery.regime.engine import MarketRegimeValidator
from goat.edge_discovery.reporting.reports import EdgeDiscoveryReportGenerator
from goat.edge_discovery.scoring.engine import EdgeScoringEngine
from goat.edge_discovery.significance.engine import StatisticalSignificanceEngine
from goat.edge_discovery.validation.engine import DiscoveryValidationEngine
from goat.edge_discovery.walk_forward.engine import WalkForwardValidator
from goat.feature_engineering.models.feature_vector import FeatureVector
from goat.logging import get_logger
from goat.research.edge.canonical import compute_canonical_sha256

_log = get_logger("edge_discovery.engine")


class MasterEdgeDiscoveryEngine:
    """Master Quantitative Edge Discovery Engine orchestrating statistical research and pattern mining."""

    def __init__(
        self,
        db_path: str | Path | sqlite3.Connection = ":memory:",
        repository: IEdgeRepository | None = None,
        version: str = "6.0.0",
    ) -> None:
        self.version = version

        # v0.9 Unified Database Context
        if isinstance(db_path, sqlite3.Connection):
            self.conn = init_edge_discovery_db(db_path)
            self.db = EdgeDiscoveryPersistenceContext(":memory:")
            self.db.conn = self.conn
        elif isinstance(db_path, (str, Path)):
            db_str = str(db_path)
            self.db = EdgeDiscoveryPersistenceContext(db_str)
            self.conn = self.db.conn
        else:
            self.db = EdgeDiscoveryPersistenceContext(":memory:")
            self.conn = self.db.conn

        # Phase 6 Repository
        self.repository = repository or SQLiteEdgeRepository(self.conn)

        # v0.9 Subsystem Engines
        self.miner = PatternMiningEngine()
        self.clusterer = PatternClusteringEngine()
        self.novelty_evaluator = NoveltyAssessmentEngine()
        self.scorer = EdgeScoringEngine()
        self.validator = DiscoveryValidationEngine()
        self.reporter = EdgeDiscoveryReportGenerator()

        # Phase 6 Research Subsystem Engines
        self.hypothesis_engine = HypothesisEngine(version=version)
        self.generator_engine = FeatureCombinationGenerator(hypothesis_engine=self.hypothesis_engine)
        self.evaluation_engine = HistoricalEvaluationEngine()
        self.significance_engine = StatisticalSignificanceEngine()
        self.regime_validator = MarketRegimeValidator(evaluation_engine=self.evaluation_engine)
        self.walk_forward_validator = WalkForwardValidator(evaluation_engine=self.evaluation_engine)
        self.ranking_engine = EdgeRankingEngine()
        self.decay_engine = EdgeDecayEngine()
        self.dataset_builder = ResearchDatasetBuilder()

        # Observer EventBus
        self._edge_listeners: list[Callable[[DiscoveredEdge], None]] = []
        self._bus_lock = threading.RLock()

    def subscribe_discovered_edges(self, callback: Callable[[DiscoveredEdge], None]) -> None:
        """Subscribe to real-time discovered edge events."""
        with self._bus_lock:
            self._edge_listeners.append(callback)

    def discover_edges(
        self,
        symbol: str,
        observations: list[Any] | None = None,
        timestamp_str: str = "2026-01-01T00:00:00Z",
        min_sample_size: int = 10,
        significance_threshold: float = 0.05,
        metadata: dict[str, Any] | None = None,
        timeframe: str = "1m",
        feature_vectors: Sequence[FeatureVector] | None = None,
        forward_returns: Sequence[float] | None = None,
        min_pvalue: float = 0.05,
    ) -> Any:
        """Dual-mode discovery workflow supporting both v0.9 observation mining and Phase 6 quantitative feature discovery."""
        # 1. Legacy v0.9 Microstructure Observation Mode
        if observations is not None:
            meta = dict(metadata or {})
            patterns, candidates = self.miner.mine_microstructure_patterns(
                symbol=symbol,
                observations=observations,
                timestamp_str=timestamp_str,
                min_sample_size=min_sample_size,
                significance_threshold=significance_threshold,
                metadata=meta,
            )
            for p in patterns:
                self.db.patterns.save(p)

            clusters = self.clusterer.cluster_patterns(patterns, metadata=meta)
            for c in clusters:
                self.db.clusters.save(c)

            archived = self.db.edges.list_all()
            decisions: list[DiscoveryDecision] = []

            for candidate in candidates:
                self.db.edges.save(candidate)
                novelty = self.novelty_evaluator.evaluate_novelty(
                    candidate=candidate,
                    archived_candidates=archived,
                    metadata=meta,
                )
                self.db.novelties.save(novelty)

                cand_patterns = [p for p in patterns if p.pattern_id in candidate.pattern_ids]
                score = self.scorer.score_candidate(
                    candidate=candidate,
                    patterns=cand_patterns,
                    metadata=meta,
                )
                self.db.scores.save(score)

                decision = self.validator.validate_candidate(
                    candidate=candidate,
                    novelty=novelty,
                    score=score,
                    timestamp_str=timestamp_str,
                    metadata=meta,
                )
                self.db.decisions.save(decision)
                decisions.append(decision)

            return candidates, decisions

        # 2. Phase 6 Quantitative Feature Vector Edge Discovery Mode
        if not feature_vectors or forward_returns is None:
            return []

        sample_fv = feature_vectors[0]
        feat_names = list(sample_fv.features.keys())
        thresholds = {f: [0.0, 0.5, 1.0] for f in feat_names[:10]}

        hypotheses = self.generator_engine.generate_candidate_hypotheses(
            available_features=feat_names[:10],
            feature_thresholds=thresholds,
            min_combination_size=1,
            max_combination_size=2,
            target_prediction=HypothesisPrediction(target_feature="future_return", min_return=0.0005),
        )

        discovered_edges: list[DiscoveredEdge] = []
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        for hyp in hypotheses:
            metrics = self.evaluation_engine.evaluate_hypothesis(hyp, feature_vectors, forward_returns)
            if metrics.sample_size < min_sample_size:
                continue

            matched_rets: list[float] = []
            for fv, r in zip(feature_vectors, forward_returns):
                if all(c.evaluate(fv.get_feature(c.feature_name, 0.0)) for c in hyp.conditions):
                    matched_rets.append(r * hyp.prediction.direction)

            sig_res = self.significance_engine.evaluate_significance(matched_rets)
            if sig_res["p_value"] > min_pvalue or sig_res["confidence_interval_low"] <= 0.0:
                continue

            regime_perf = self.regime_validator.evaluate_regimes(hyp, feature_vectors, forward_returns)
            wf_metrics = self.walk_forward_validator.validate_walk_forward(hyp, feature_vectors, forward_returns)

            cond_feat_names = [c.feature_name for c in hyp.conditions]
            edge_id, canon_hash = compute_edge_id(
                hypothesis_id=hyp.hypothesis_id,
                feature_combination=cond_feat_names,
                symbols=[symbol],
                timeframes=[timeframe],
                version=self.version,
            )

            temp_edge = DiscoveredEdge(
                edge_id=edge_id,
                version=self.version,
                hypothesis_id=hyp.hypothesis_id,
                feature_combination=cond_feat_names,
                supported_symbols=[symbol.upper()],
                supported_timeframes=[timeframe.lower()],
                metrics=metrics,
                p_value=sig_res["p_value"],
                confidence_interval_low=sig_res["confidence_interval_low"],
                confidence_interval_high=sig_res["confidence_interval_high"],
                effect_size=sig_res["effect_size"],
                composite_score=0.0,
                discovery_date=now_iso,
                last_validation_date=now_iso,
                status=EdgeStatus.ACTIVE,
                regime_performance=regime_perf,
                walk_forward_metrics=wf_metrics,
                checksum="TEMP",
                metadata={"condition_count": len(hyp.conditions)},
                canonical_hash=canon_hash,
            )

            score = self.ranking_engine.compute_composite_score(temp_edge)
            checksum = compute_canonical_sha256(
                {
                    "composite_score": score,
                    "edge_id": edge_id,
                    "hypothesis_id": hyp.hypothesis_id,
                    "p_value": sig_res["p_value"],
                    "version": self.version,
                }
            )

            final_edge = DiscoveredEdge(
                edge_id=edge_id,
                version=self.version,
                hypothesis_id=hyp.hypothesis_id,
                feature_combination=cond_feat_names,
                supported_symbols=[symbol.upper()],
                supported_timeframes=[timeframe.lower()],
                metrics=metrics,
                p_value=sig_res["p_value"],
                confidence_interval_low=sig_res["confidence_interval_low"],
                confidence_interval_high=sig_res["confidence_interval_high"],
                effect_size=sig_res["effect_size"],
                composite_score=score,
                discovery_date=now_iso,
                last_validation_date=now_iso,
                status=EdgeStatus.ACTIVE,
                regime_performance=regime_perf,
                walk_forward_metrics=wf_metrics,
                checksum=checksum,
                metadata={"condition_count": len(hyp.conditions)},
                canonical_hash=canon_hash,
            )

            self.repository.save_edge(final_edge)
            discovered_edges.append(final_edge)

            with self._bus_lock:
                for cb in self._edge_listeners:
                    try:
                        cb(final_edge)
                    except Exception as exc:
                        _log.error("discovered_edge_listener_exception", error=str(exc))

        discovered_edges.sort(key=lambda x: x.composite_score, reverse=True)
        return discovered_edges

    def generate_discovery_summary(
        self, timestamp_str: str = "2026-01-01T00:00:00Z", metadata: dict[str, Any] | None = None
    ) -> DiscoverySummary:
        """Compute and persist an immutable DiscoverySummary across archived state."""
        meta = dict(metadata or {})
        patterns = self.db.patterns.list_all()
        clusters = self.db.clusters.list_all()
        candidates = self.db.edges.list_all()
        decisions = self.db.decisions.list_all()
        scores = self.db.scores.list_all()

        validated_count = sum(1 for d in decisions if d.status == ValidationStatus.PASSED)
        rejected_count = sum(1 for d in decisions if d.status == ValidationStatus.REJECTED)

        category_counts: dict[str, int] = {}
        for c in candidates:
            cat_str = c.category.value
            category_counts[cat_str] = category_counts.get(cat_str, 0) + 1

        tier_counts: dict[str, int] = {}
        for s in scores:
            t_str = s.quality_tier.value
            tier_counts[t_str] = tier_counts.get(t_str, 0) + 1

        summary_id, s_hash = compute_discovery_summary_id(
            timestamp=timestamp_str,
            total_candidates=len(candidates),
            total_validated=validated_count,
        )

        summary = DiscoverySummary(
            summary_id=summary_id,
            timestamp=timestamp_str,
            total_patterns=len(patterns),
            total_clusters=len(clusters),
            total_candidates=len(candidates),
            total_validated=validated_count,
            total_rejected=rejected_count,
            category_counts=category_counts,
            tier_counts=tier_counts,
            metadata=meta,
            canonical_hash=s_hash,
        )

        self.db.summaries.save(summary)
        return summary

    def export_research_dataset(
        self,
        experiment_name: str,
        symbols: Sequence[str],
        timeframes: Sequence[str],
        raw_inputs_count: int,
        feature_vectors: Sequence[FeatureVector],
        edges: Sequence[DiscoveredEdge],
    ) -> ResearchDataset:
        """Export reproducible experiment dataset artifact."""
        return self.dataset_builder.build_dataset(
            experiment_name=experiment_name,
            symbols=symbols,
            timeframes=timeframes,
            raw_inputs_count=raw_inputs_count,
            feature_vectors=feature_vectors,
            discovered_edges=edges,
            version=self.version,
        )

    def close(self) -> None:
        """Close database connection."""
        self.db.close()


# Convenience alias matching prompt naming
EdgeDiscoveryEngine = MasterEdgeDiscoveryEngine
