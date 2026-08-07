"""
Project GOAT Phase 6 — Feature Combination Generator (`goat.edge_discovery.generator`)

Systematically generates candidate pairwise, triple, and N-feature hypotheses under search constraints.
"""

from __future__ import annotations

import itertools
from typing import Sequence

from goat.edge_discovery.hypothesis.engine import HypothesisEngine
from goat.edge_discovery.models.hypothesis import (
    HypothesisCondition,
    HypothesisOperator,
    HypothesisPrediction,
    ResearchHypothesis,
)


class FeatureCombinationGenerator:
    """Quantitative Feature Combination Generator constructing candidate hypotheses across feature spaces."""

    def __init__(
        self,
        hypothesis_engine: HypothesisEngine | None = None,
        max_combinations: int = 100,
    ):
        self.hypothesis_engine = hypothesis_engine or HypothesisEngine()
        self.max_combinations = max_combinations

    def generate_candidate_hypotheses(
        self,
        available_features: Sequence[str],
        feature_thresholds: dict[str, list[float]],
        min_combination_size: int = 1,
        max_combination_size: int = 3,
        target_prediction: HypothesisPrediction | None = None,
    ) -> list[ResearchHypothesis]:
        """Generate candidate hypotheses for pairwise, triple, or N-feature combinations."""
        pred = target_prediction or HypothesisPrediction()
        candidates: list[ResearchHypothesis] = []
        seen_hashes: set[str] = set()

        feat_list = sorted(list(set(available_features)))

        for k in range(min_combination_size, min(max_combination_size + 1, len(feat_list) + 1)):
            for comb in itertools.combinations(feat_list, k):
                if len(candidates) >= self.max_combinations:
                    break

                # Create combinations of thresholds for the features
                threshold_options = [
                    feature_thresholds.get(f, [0.0, 0.5, 1.0]) for f in comb
                ]

                for t_vals in itertools.product(*threshold_options):
                    if len(candidates) >= self.max_combinations:
                        break

                    conditions = [
                        HypothesisCondition(
                            feature_name=comb[idx],
                            operator=HypothesisOperator.GT,
                            threshold_value=t_vals[idx],
                        )
                        for idx in range(k)
                    ]

                    desc = "IF " + " AND ".join(
                        f"{c.feature_name} {c.operator.value} {c.threshold_value}" for c in conditions
                    ) + f" THEN {pred.target_feature} > {pred.min_return}"

                    hyp = self.hypothesis_engine.create_hypothesis(
                        description=desc,
                        conditions=conditions,
                        prediction=pred,
                    )

                    if hyp.canonical_hash not in seen_hashes:
                        seen_hashes.add(hyp.canonical_hash)
                        candidates.append(hyp)

        return candidates
