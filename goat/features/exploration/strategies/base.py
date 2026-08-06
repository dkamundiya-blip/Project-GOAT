"""
Project GOAT v0.7 — Base Search Strategy Interface

Defines the abstract base class BaseSearchStrategy for feature space exploration search algorithms.
"""

from __future__ import annotations

import abc
from typing import Any

from goat.features.core.base import BaseFeature
from goat.features.exploration.budget import ExplorationBudget
from goat.features.exploration.candidate import CandidateFeature
from goat.features.exploration.transformations.base import BaseTransformation


class BaseSearchStrategy(abc.ABC):
    """Abstract base class for all feature exploration search strategies."""

    def __init__(self, name: str, strategy_type: str = "deterministic") -> None:
        self._name = name
        self._strategy_type = strategy_type

    @property
    def name(self) -> str:
        """Return strategy name."""
        return self._name

    @property
    def strategy_type(self) -> str:
        """Return strategy classification ('deterministic', 'heuristic', 'adapter')."""
        return self._strategy_type

    @abc.abstractmethod
    def explore(
        self,
        primitives: list[BaseFeature],
        transformations: list[BaseTransformation],
        budget: ExplorationBudget,
    ) -> list[CandidateFeature]:
        """Execute feature space exploration according to the search strategy logic.

        Args:
            primitives: Base primitive feature set.
            transformations: Registered transformation operators.
            budget: ExplorationBudget limits and state tracker.

        Returns:
            List of generated CandidateFeature instances.
        """
        ...
