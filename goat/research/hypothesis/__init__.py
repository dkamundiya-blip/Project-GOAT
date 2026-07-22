"""Project GOAT v0.4 — Hypothesis Engine & Statistical Edge Discovery Package."""

from goat.research.hypothesis.conditions import CausalConditionEvaluator
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.dependence import apply_embargo_spacing, evaluate_dependence_risk
from goat.research.hypothesis.experiment import Experiment, ExperimentRunner
from goat.research.hypothesis.multiple_testing import benjamini_hochberg_fdr
from goat.research.hypothesis.registry import EdgeRegistry
from goat.research.hypothesis.report import HypothesisReportGenerator
from goat.research.hypothesis.result import HypothesisResult
from goat.research.hypothesis.scoring import calculate_edge_score, normalize_effect_magnitude
from goat.research.hypothesis.testing import calculate_effect_size, run_statistical_test

__all__ = [
    "HypothesisDefinition",
    "CausalConditionEvaluator",
    "calculate_effect_size",
    "run_statistical_test",
    "apply_embargo_spacing",
    "evaluate_dependence_risk",
    "benjamini_hochberg_fdr",
    "calculate_edge_score",
    "normalize_effect_magnitude",
    "HypothesisResult",
    "Experiment",
    "ExperimentRunner",
    "EdgeRegistry",
    "HypothesisReportGenerator",
]
