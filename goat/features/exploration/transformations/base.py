"""
Project GOAT v0.7 — Base Feature Transformation Interface

Defines the abstract base class BaseTransformation for immutable mathematical transformation operators.
"""

from __future__ import annotations

import abc
from typing import Any

from goat.features.core.base import BaseFeature
from goat.features.core.contracts import (
    FeatureCapabilityContract,
    FeatureInputContract,
    FeatureOutputContract,
)
from goat.research.edge.canonical import compute_canonical_sha256


class BaseTransformation(abc.ABC):
    """Abstract base class for all feature transformation operators."""

    def __init__(
        self,
        name: str,
        version: str,
        scientific_description: str,
        mathematical_definition: str,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        self._name = name
        self._version = version
        self._scientific_description = scientific_description
        self._mathematical_definition = mathematical_definition
        self._parameters = parameters or {}

        # Compute deterministic Transformation ID (TRNS_<HEX16>)
        payload = {
            "math_def": self._mathematical_definition,
            "name": self._name,
            "params": self._parameters,
            "version": self._version,
        }
        digest = compute_canonical_sha256(payload)
        self._transformation_id = f"TRNS_{digest[:16].upper()}"

    @property
    def transformation_id(self) -> str:
        """Return deterministic Transformation ID (TRNS_<HEX16>)."""
        return self._transformation_id

    @property
    def name(self) -> str:
        """Return transformation operator name."""
        return self._name

    @property
    def version(self) -> str:
        """Return transformation version string."""
        return self._version

    @property
    def scientific_description(self) -> str:
        """Return scientific description."""
        return self._scientific_description

    @property
    def mathematical_definition(self) -> str:
        """Return LaTeX or formal mathematical definition."""
        return self._mathematical_definition

    @property
    def parameters(self) -> dict[str, Any]:
        """Return bound parameters dictionary."""
        return self._parameters.copy()

    @abc.abstractmethod
    def transform(self, parents: list[BaseFeature]) -> BaseFeature:
        """Apply transformation operator to parent feature(s) returning a new transformed feature.

        Args:
            parents: List of upstream parent BaseFeature instances.

        Returns:
            New BaseFeature instance.
        """
        ...
