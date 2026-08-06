"""
Project GOAT v0.7 — Feature Exploration Engine

Implements FeatureExplorationEngine for coordinating feature generation, transformation,
deduplication, ExplorationDecision provenance tracking, budget management, and ExplorationReport production.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, Field

from goat.features.core.base import BaseFeature
from goat.features.exploration.budget import ExplorationBudget
from goat.features.exploration.candidate import CandidateFeature
from goat.features.exploration.decision import ExplorationDecision, compute_decision_id
from goat.features.exploration.lineage import FeatureLineageEngine
from goat.features.exploration.strategies.base import BaseSearchStrategy
from goat.features.exploration.strategies.framework import ExhaustiveSearchStrategy
from goat.features.exploration.transformations.registry import TransformationRegistry
from goat.research.edge.canonical import compute_canonical_sha256


class DecisionValidationError(ValueError):
    """Raised when ExplorationDecision validation fails (orphan candidate, duplicate decision, etc.)."""
    pass


class ExplorationReport(BaseModel):
    """Immutable report summarizing feature space exploration campaign results and decision provenance."""

    report_id: str = Field(..., description="Unique Exploration Report ID (REP_<HEX16>)")
    timestamp: str = Field(..., description="ISO 8601 UTC execution timestamp")
    strategy_name: str = Field(..., description="Executed search strategy name")
    generated_candidates: list[CandidateFeature] = Field(
        default_factory=list, description="List of generated unique CandidateFeatures"
    )
    decisions: list[ExplorationDecision] = Field(
        default_factory=list, description="List of recorded ExplorationDecisions"
    )
    decision_count: int = Field(default=0, ge=0, description="Count of recorded decisions")
    rejected_candidates_count: int = Field(default=0, ge=0, description="Count of rejected candidates")
    duplicate_candidates_count: int = Field(default=0, ge=0, description="Count of duplicate candidates rejected")
    budget_summary: dict[str, Any] = Field(default_factory=dict, description="Resource budget usage summary")
    lineage_statistics: dict[str, Any] = Field(default_factory=dict, description="Lineage statistics summary")
    decision_statistics: dict[str, Any] = Field(default_factory=dict, description="Decision statistics summary")
    scientific_observations: list[str] = Field(default_factory=list, description="Scientific findings & notes")

    class Config:
        frozen = True
        extra = "forbid"


class FeatureExplorationEngine:
    """Scientific Feature Space Exploration Engine coordinating candidate generation, decisions, and deduplication."""

    def __init__(
        self,
        transformation_registry: TransformationRegistry | None = None,
        lineage_engine: FeatureLineageEngine | None = None,
    ) -> None:
        self._transformation_registry = transformation_registry or TransformationRegistry(load_defaults=True)
        self._lineage_engine = lineage_engine or FeatureLineageEngine()
        self._seen_fingerprints: set[str] = set()
        self._decisions: dict[str, ExplorationDecision] = {}

    @property
    def transformation_registry(self) -> TransformationRegistry:
        """Return bound TransformationRegistry."""
        return self._transformation_registry

    @property
    def lineage_engine(self) -> FeatureLineageEngine:
        """Return bound FeatureLineageEngine."""
        return self._lineage_engine

    @property
    def decisions(self) -> list[ExplorationDecision]:
        """Return recorded decisions map."""
        return list(self._decisions.values())

    def register_decision(self, decision: ExplorationDecision) -> None:
        """Register ExplorationDecision with fail-closed validation.

        Args:
            decision: ExplorationDecision instance.
        """
        did = decision.decision_id
        if did in self._decisions:
            raise DecisionValidationError(f"Duplicate decision ID registration: '{did}' already exists")

        # Verify decision hash digest match
        _, expected_hash = compute_decision_id(
            search_strategy_id=decision.search_strategy_id,
            generation_rule_id=decision.generation_rule_id,
            parent_candidate_ids=decision.parent_candidate_ids,
            transformation_ids=decision.transformation_ids,
            depth=decision.decision_depth,
        )
        if decision.decision_hash != expected_hash:
            raise DecisionValidationError(
                f"Decision hash verification failure for '{did}': expected '{expected_hash}', got '{decision.decision_hash}'"
            )

        self._decisions[did] = decision

    def explore(
        self,
        primitives: list[BaseFeature],
        strategy: BaseSearchStrategy | None = None,
        budget: ExplorationBudget | None = None,
    ) -> ExplorationReport:
        """Run feature space exploration campaign.

        Args:
            primitives: Base primitive feature set.
            strategy: Search strategy (defaults to ExhaustiveSearchStrategy).
            budget: Resource limits and budget controls.

        Returns:
            Immutable ExplorationReport.
        """
        strat = strategy or ExhaustiveSearchStrategy()
        budg = budget or ExplorationBudget(max_depth=2, max_candidates=50)
        transformations = self._transformation_registry.list_transformations()

        raw_candidates = strat.explore(primitives, transformations, budg)

        # Register raw strategy decisions
        if hasattr(strat, "decisions"):
            for dec in getattr(strat, "decisions"):
                if dec.decision_id not in self._decisions:
                    self.register_decision(dec)

        unique_candidates: list[CandidateFeature] = []
        accepted_decisions: list[ExplorationDecision] = []
        rejected_count = 0
        duplicate_count = 0

        # Register primitive fingerprints
        for p in primitives:
            self._seen_fingerprints.add(p.scientific_fingerprint)

        for cand in raw_candidates:
            fp = cand.scientific_fingerprint

            # Fail-closed decision reference validation (orphan candidate rejection)
            if cand.decision_id and cand.decision_id not in self._decisions:
                raise DecisionValidationError(
                    f"Orphan candidate detected: Candidate '{cand.candidate_id}' references non-existent Decision ID '{cand.decision_id}'"
                )

            # Fail-closed deduplication check
            if fp in self._seen_fingerprints:
                duplicate_count += 1
                rejected_count += 1
                budg.record_duplicate()
                continue

            self._seen_fingerprints.add(fp)
            try:
                self._lineage_engine.register_candidate(cand)
                unique_candidates.append(cand)
                if cand.decision_id in self._decisions:
                    accepted_decisions.append(self._decisions[cand.decision_id])
            except Exception:
                rejected_count += 1
                budg.record_rejection()

        # Generate report
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        report_payload = {
            "decisions_count": len(accepted_decisions),
            "strategy": strat.name,
            "timestamp": timestamp,
            "unique_count": len(unique_candidates),
        }
        report_hash = compute_canonical_sha256(report_payload)
        report_id = f"REP_{report_hash[:16].upper()}"

        max_depth_seen = max([c.generation_depth for c in unique_candidates], default=0)
        lineage_stats = {
            "max_generation_depth": max_depth_seen,
            "total_candidates": len(unique_candidates),
        }
        decision_stats = {
            "accepted_decisions": len(accepted_decisions),
            "total_decisions": len(self._decisions),
        }

        observations = [
            f"Successfully generated {len(unique_candidates)} unique candidate features across {len(accepted_decisions)} exploration decisions.",
            f"Deduplicated and rejected {duplicate_count} duplicate candidate fingerprints.",
            f"Maximum generation depth reached: {max_depth_seen}.",
        ]

        return ExplorationReport(
            report_id=report_id,
            timestamp=timestamp,
            strategy_name=strat.name,
            generated_candidates=unique_candidates,
            decisions=accepted_decisions,
            decision_count=len(accepted_decisions),
            rejected_candidates_count=rejected_count,
            duplicate_candidates_count=duplicate_count,
            budget_summary=budg.get_summary(),
            lineage_statistics=lineage_stats,
            decision_statistics=decision_stats,
            scientific_observations=observations,
        )
