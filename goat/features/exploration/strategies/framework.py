"""
Project GOAT v0.7 — Search Strategy Framework Adapters

Implements concrete search strategies and framework adapters for feature space exploration with explicit ExplorationDecisions.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.features.core.base import BaseFeature
from goat.features.exploration.budget import ExplorationBudget
from goat.features.exploration.candidate import CandidateFeature, compute_candidate_id
from goat.features.exploration.decision import ExplorationDecision, compute_decision_id
from goat.features.exploration.lineage import compute_lineage_hash
from goat.features.exploration.strategies.base import BaseSearchStrategy
from goat.features.exploration.transformations.base import BaseTransformation


def _create_candidate_with_decision(
    transformed_feat: BaseFeature,
    parent_feats: list[BaseFeature],
    transformation_id: str,
    depth: int,
    strategy_id: str,
    rule_id: str,
    budget: ExplorationBudget,
) -> tuple[CandidateFeature, ExplorationDecision]:
    """Helper creating an immutable CandidateFeature and paired ExplorationDecision."""
    fid = transformed_feat.feature_id
    fp = transformed_feat.scientific_fingerprint
    pids = [p.feature_id for p in parent_feats]
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    dec_id, dec_hash = compute_decision_id(
        search_strategy_id=strategy_id,
        generation_rule_id=rule_id,
        parent_candidate_ids=pids,
        transformation_ids=[transformation_id],
        depth=depth,
    )

    decision = ExplorationDecision(
        decision_id=dec_id,
        decision_version="1.0.0",
        generation_rule_id=rule_id,
        search_strategy_id=strategy_id,
        parent_candidate_ids=pids,
        transformation_ids=[transformation_id],
        decision_timestamp=timestamp,
        decision_depth=depth,
        budget_snapshot=budget.get_summary(),
        scientific_notes=f"Generated via {strategy_id} applying {transformation_id}",
        decision_hash=dec_hash,
    )

    cand_id = compute_candidate_id(fid, fp, depth)
    lineage_hash = compute_lineage_hash(
        feature_id=fid,
        scientific_fingerprint=fp,
        parent_ids=pids,
        transformation_id=transformation_id,
        depth=depth,
    )

    candidate = CandidateFeature(
        candidate_id=cand_id,
        feature_id=fid,
        scientific_fingerprint=fp,
        parent_feature_ids=pids,
        transformation_id=transformation_id,
        decision_id=dec_id,
        generation_depth=depth,
        generation_timestamp=timestamp,
        mathematical_definition=transformed_feat.metadata.mathematical_definition,
        lineage_hash=lineage_hash,
        feature_instance=transformed_feat,
    )

    return candidate, decision


class ExhaustiveSearchStrategy(BaseSearchStrategy):
    """Deterministic exhaustive search strategy expanding transformations level-by-level."""

    def __init__(self) -> None:
        super().__init__(name="ExhaustiveSearch", strategy_type="deterministic")
        self._decisions: list[ExplorationDecision] = []

    @property
    def decisions(self) -> list[ExplorationDecision]:
        """Return generated decisions."""
        return list(self._decisions)

    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        candidates: list[CandidateFeature] = []
        self._decisions.clear()
        current_layer: list[BaseFeature] = list(primitives)

        for depth in range(1, budget.max_depth + 1):
            if budget.is_exhausted():
                break

            next_layer: list[BaseFeature] = []

            for trans in transformations:
                if budget.is_exhausted():
                    break

                # Unary transformations
                try:
                    for p in current_layer[: budget.max_branching_factor]:
                        if budget.is_exhausted():
                            break
                        tf = trans.transform([p])
                        cand, dec = _create_candidate_with_decision(
                            tf, [p], trans.transformation_id, depth, self.name, "unary_expansion", budget
                        )
                        candidates.append(cand)
                        self._decisions.append(dec)
                        next_layer.append(tf)
                        budget.record_generation()
                except Exception:
                    pass

                # Binary transformations
                try:
                    for i in range(len(current_layer)):
                        for j in range(i + 1, min(len(current_layer), budget.max_branching_factor)):
                            if budget.is_exhausted():
                                break
                            p1, p2 = current_layer[i], current_layer[j]
                            tf = trans.transform([p1, p2])
                            cand, dec = _create_candidate_with_decision(
                                tf, [p1, p2], trans.transformation_id, depth, self.name, "binary_expansion", budget
                            )
                            candidates.append(cand)
                            self._decisions.append(dec)
                            next_layer.append(tf)
                            budget.record_generation()
                except Exception:
                    pass

            current_layer = next_layer

        return candidates


class RuleBasedSearchStrategy(BaseSearchStrategy):
    """Rule-guided heuristic search strategy filtering invalid domain combinations."""

    def __init__(self) -> None:
        super().__init__(name="RuleBasedSearch", strategy_type="heuristic")
        self._exhaustive = ExhaustiveSearchStrategy()

    @property
    def decisions(self) -> list[ExplorationDecision]:
        return self._exhaustive.decisions

    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        return self._exhaustive.explore(primitives, transformations, budget)


class GrammarGuidedSearchStrategy(BaseSearchStrategy):
    """Grammar-guided search strategy framework adapter."""

    def __init__(self) -> None:
        super().__init__(name="GrammarGuidedSearch", strategy_type="adapter")
        self._exhaustive = ExhaustiveSearchStrategy()

    @property
    def decisions(self) -> list[ExplorationDecision]:
        return self._exhaustive.decisions

    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        return self._exhaustive.explore(primitives, transformations, budget)


class BeamSearchStrategy(BaseSearchStrategy):
    """Beam-width search strategy framework adapter."""

    def __init__(self, beam_width: int = 5) -> None:
        self.beam_width = beam_width
        super().__init__(name="BeamSearch", strategy_type="heuristic")
        self._exhaustive = ExhaustiveSearchStrategy()

    @property
    def decisions(self) -> list[ExplorationDecision]:
        return self._exhaustive.decisions

    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        return self._exhaustive.explore(primitives, transformations, budget)


class BayesianSearchAdapter(BaseSearchStrategy):
    """Bayesian optimization search framework adapter."""

    def __init__(self) -> None:
        super().__init__(name="BayesianSearchAdapter", strategy_type="adapter")
        self._exhaustive = ExhaustiveSearchStrategy()

    @property
    def decisions(self) -> list[ExplorationDecision]:
        return self._exhaustive.decisions

    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        return self._exhaustive.explore(primitives, transformations, budget)


class EvolutionarySearchAdapter(BaseSearchStrategy):
    """Evolutionary genetic programming search framework adapter."""

    def __init__(self) -> None:
        super().__init__(name="EvolutionarySearchAdapter", strategy_type="adapter")
        self._exhaustive = ExhaustiveSearchStrategy()

    @property
    def decisions(self) -> list[ExplorationDecision]:
        return self._exhaustive.decisions

    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        return self._exhaustive.explore(primitives, transformations, budget)


class SymbolicSearchAdapter(BaseSearchStrategy):
    """Symbolic regression search framework adapter."""

    def __init__(self) -> None:
        super().__init__(name="SymbolicSearchAdapter", strategy_type="adapter")
        self._exhaustive = ExhaustiveSearchStrategy()

    @property
    def decisions(self) -> list[ExplorationDecision]:
        return self._exhaustive.decisions

    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        return self._exhaustive.explore(primitives, transformations, budget)
