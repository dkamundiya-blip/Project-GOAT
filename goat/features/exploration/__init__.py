"""
Project GOAT v0.7 — Feature Space Exploration Subsystem
"""

from goat.features.exploration.budget import ExplorationBudget
from goat.features.exploration.candidate import CandidateFeature, compute_candidate_id
from goat.features.exploration.decision import ExplorationDecision, compute_decision_id
from goat.features.exploration.engine import (
    DecisionValidationError,
    ExplorationReport,
    FeatureExplorationEngine,
)
from goat.features.exploration.lineage import (
    FeatureLineageEngine,
    LineageValidationError,
    compute_lineage_hash,
)
from goat.features.exploration.strategies import (
    BaseSearchStrategy,
    BayesianSearchAdapter,
    BeamSearchStrategy,
    EvolutionarySearchAdapter,
    ExhaustiveSearchStrategy,
    GrammarGuidedSearchStrategy,
    RuleBasedSearchStrategy,
    SymbolicSearchAdapter,
)
from goat.features.exploration.transformations import (
    AbsoluteTransform,
    BaseTransformation,
    DifferenceTransform,
    LogTransform,
    ProductTransform,
    RatioTransform,
    RollingMeanTransform,
    RollingStdDevTransform,
    SignTransform,
    TransformationRegistry,
)

__all__ = [
    # Transformations & Registry
    "BaseTransformation",
    "LogTransform",
    "AbsoluteTransform",
    "SignTransform",
    "RatioTransform",
    "DifferenceTransform",
    "ProductTransform",
    "RollingMeanTransform",
    "RollingStdDevTransform",
    "TransformationRegistry",
    # Decision Model
    "ExplorationDecision",
    "compute_decision_id",
    "DecisionValidationError",
    # Candidate & Lineage
    "CandidateFeature",
    "compute_candidate_id",
    "FeatureLineageEngine",
    "LineageValidationError",
    "compute_lineage_hash",
    # Budget & Strategies
    "ExplorationBudget",
    "BaseSearchStrategy",
    "ExhaustiveSearchStrategy",
    "RuleBasedSearchStrategy",
    "GrammarGuidedSearchStrategy",
    "BeamSearchStrategy",
    "BayesianSearchAdapter",
    "EvolutionarySearchAdapter",
    "SymbolicSearchAdapter",
    # Exploration Engine & Report
    "FeatureExplorationEngine",
    "ExplorationReport",
]
