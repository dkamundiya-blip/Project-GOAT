"""
Project GOAT v0.9 — Master Quantitative Edge Discovery Engine
"""

from typing import Any

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
from goat.edge_discovery.mining.engine import PatternMiningEngine
from goat.edge_discovery.novelty.engine import NoveltyAssessmentEngine
from goat.edge_discovery.persistence.sqlite import EdgeDiscoveryPersistenceContext
from goat.edge_discovery.reporting.reports import EdgeDiscoveryReportGenerator
from goat.edge_discovery.scoring.engine import EdgeScoringEngine
from goat.edge_discovery.validation.engine import DiscoveryValidationEngine


class MasterEdgeDiscoveryEngine:
    """Master Quantitative Edge Discovery Engine.

    Coordinates the discovery of candidate quantitative edges from research artifacts,
    microstructure observations, experiments, and controlled live validation history.

    Strict Non-Negotiable Protocol:
    • NEVER generates trading signals or orders
    • NEVER executes trades or connects to broker APIs
    • NEVER optimizes parameters
    • ONLY discovers candidate quantitative edges for Governance review
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db = EdgeDiscoveryPersistenceContext(db_path)
        self.miner = PatternMiningEngine()
        self.clusterer = PatternClusteringEngine()
        self.novelty_evaluator = NoveltyAssessmentEngine()
        self.scorer = EdgeScoringEngine()
        self.validator = DiscoveryValidationEngine()
        self.reporter = EdgeDiscoveryReportGenerator()

    def discover_edges(
        self,
        symbol: str,
        observations: list[Any],
        timestamp_str: str = "2026-01-01T00:00:00Z",
        min_sample_size: int = 10,
        significance_threshold: float = 0.05,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[list[EdgeCandidate], list[DiscoveryDecision]]:
        """Run complete quantitative edge discovery workflow on observations."""
        meta = dict(metadata or {})

        # 1. Pattern Mining
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

        # 2. Pattern Clustering
        clusters = self.clusterer.cluster_patterns(patterns, metadata=meta)
        for c in clusters:
            self.db.clusters.save(c)

        # Retrieve archived candidates for novelty comparison
        archived = self.db.edges.list_all()

        decisions: list[DiscoveryDecision] = []

        for candidate in candidates:
            # Save candidate
            self.db.edges.save(candidate)

            # 3. Novelty Assessment
            novelty = self.novelty_evaluator.evaluate_novelty(
                candidate=candidate,
                archived_candidates=archived,
                metadata=meta,
            )
            self.db.novelties.save(novelty)

            # 4. Edge Quality Scoring
            cand_patterns = [p for p in patterns if p.pattern_id in candidate.pattern_ids]
            score = self.scorer.score_candidate(
                candidate=candidate,
                patterns=cand_patterns,
                metadata=meta,
            )
            self.db.scores.save(score)

            # 5. Discovery Protocol Validation
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

    def close(self) -> None:
        """Close persistence context connection."""
        self.db.close()
