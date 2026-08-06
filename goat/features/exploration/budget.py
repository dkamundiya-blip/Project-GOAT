"""
Project GOAT v0.7 — Exploration Budget & Limits Engine

Implements ExplorationBudget for deterministic resource, depth, and termination control during feature space exploration.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExplorationBudget(BaseModel):
    """Immutable configuration and state tracker for exploration budget limits."""

    max_depth: int = Field(default=4, ge=1, description="Maximum generation depth limit")
    max_branching_factor: int = Field(default=10, ge=1, description="Maximum branching factor per parent node")
    max_candidates: int = Field(default=100, ge=1, description="Maximum total candidate budget limit")
    max_time_seconds: float = Field(default=300.0, gt=0.0, description="Maximum execution time budget interface")

    # Mutable tracking fields
    generated_count: int = Field(default=0, ge=0, description="Count of successfully generated candidates")
    rejected_count: int = Field(default=0, ge=0, description="Count of rejected candidates")
    duplicate_count: int = Field(default=0, ge=0, description="Count of duplicate candidates detected")

    def is_exhausted(self) -> bool:
        """Check if candidate budget limit is exhausted."""
        return self.generated_count >= self.max_candidates

    def is_depth_allowed(self, depth: int) -> bool:
        """Check if target depth is within max_depth limit."""
        return depth <= self.max_depth

    def record_generation(self) -> None:
        """Record successful candidate generation."""
        self.generated_count += 1

    def record_rejection(self) -> None:
        """Record candidate rejection."""
        self.rejected_count += 1

    def record_duplicate(self) -> None:
        """Record duplicate candidate detection."""
        self.duplicate_count += 1
        self.rejected_count += 1

    def get_summary(self) -> dict[str, Any]:
        """Export budget usage summary."""
        return {
            "budget_exhausted": self.is_exhausted(),
            "duplicate_count": self.duplicate_count,
            "generated_count": self.generated_count,
            "max_branching_factor": self.max_branching_factor,
            "max_candidates": self.max_candidates,
            "max_depth": self.max_depth,
            "max_time_seconds": self.max_time_seconds,
            "rejected_count": self.rejected_count,
        }
