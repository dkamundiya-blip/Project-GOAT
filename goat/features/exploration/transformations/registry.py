"""
Project GOAT v0.7 — Transformation Registry

Implements TransformationRegistry for registering, querying, versioning, and auditing
mathematical transformation operators used during feature space exploration.
"""

from __future__ import annotations

from typing import Any

from goat.features.exploration.transformations.base import BaseTransformation
from goat.features.exploration.transformations.operators import (
    AbsoluteTransform,
    DifferenceTransform,
    LogTransform,
    ProductTransform,
    RatioTransform,
    RollingMeanTransform,
    RollingStdDevTransform,
    SignTransform,
)


class TransformationRegistry:
    """Authoritative scientific registry for mathematical transformation operators."""

    def __init__(self, load_defaults: bool = True) -> None:
        self._transformations: dict[str, BaseTransformation] = {}
        if load_defaults:
            self._register_defaults()

    def _register_defaults(self) -> None:
        """Register baseline standard mathematical operators."""
        defaults = [
            LogTransform(),
            AbsoluteTransform(),
            SignTransform(),
            RatioTransform(),
            DifferenceTransform(),
            ProductTransform(),
            RollingMeanTransform(window=5),
            RollingMeanTransform(window=10),
            RollingStdDevTransform(window=10),
        ]
        for t in defaults:
            self.register_transformation(t)

    def register_transformation(self, transformation: BaseTransformation) -> BaseTransformation:
        """Register a transformation operator in the registry.

        Args:
            transformation: BaseTransformation instance.

        Returns:
            Registered BaseTransformation instance.
        """
        tid = transformation.transformation_id
        if tid in self._transformations:
            # Idempotent registration of duplicate transformation ID
            return self._transformations[tid]

        self._transformations[tid] = transformation
        return transformation

    def get_by_id(self, transformation_id: str) -> BaseTransformation:
        """Retrieve transformation operator by Transformation ID (TRNS_<HEX16>)."""
        if transformation_id not in self._transformations:
            raise KeyError(f"Transformation ID '{transformation_id}' not found in TransformationRegistry")
        return self._transformations[transformation_id]

    def get_by_name(self, name: str) -> BaseTransformation:
        """Retrieve transformation operator by name."""
        for t in self._transformations.values():
            if t.name.lower() == name.lower():
                return t
        raise KeyError(f"Transformation name '{name}' not found in TransformationRegistry")

    def list_transformations(self) -> list[BaseTransformation]:
        """List all registered transformation operators."""
        return list(self._transformations.values())

    def get_transformation_metadata(self) -> list[dict[str, Any]]:
        """Export metadata summaries of all registered transformations."""
        res = []
        for t in self._transformations.values():
            res.append({
                "transformation_id": t.transformation_id,
                "name": t.name,
                "version": t.version,
                "scientific_description": t.scientific_description,
                "mathematical_definition": t.mathematical_definition,
                "parameters": t.parameters,
            })
        return res
