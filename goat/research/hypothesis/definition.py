"""
Project GOAT v0.4 — Hypothesis Definition Schema & Versioning

Defines the immutable, versioned schema for quantitative hypothesis specifications.
Any change to research parameters automatically computes a new version hash string.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class HypothesisDefinition(BaseModel):
    """Immutable quantitative hypothesis definition."""

    hypothesis_id: str
    version: str = "1.0.0"
    name: str
    description: str
    symbol_scope: list[str] = Field(default_factory=lambda: ["R_10", "R_50", "R_75"])
    timeframe_scope: list[str] = Field(default_factory=lambda: ["M1", "M5"])
    causal_condition: dict[str, Any]
    condition_parameters: dict[str, Any] = Field(default_factory=dict)
    required_causal_features: list[str] = Field(default_factory=list)
    forward_outcome_metric: str = "fwd_return_5"
    forward_horizon: int = 5
    baseline_definition: str = "unconditional"  # "unconditional", "conditional_excluded", "regime_matched"
    event_spacing_bars: int = 0  # 0 = allow overlap, k = embargo spacing
    statistical_test: str = "welch_ttest"  # "welch_ttest", "mann_whitney", "permutation", "fisher_exact"
    effect_size_method: str = "cohens_d"  # "cohens_d", "mean_diff", "median_diff", "rank_biserial", "relative_risk", "prop_diff"
    min_sample_requirement: int = 100
    exploratory_confirmatory_status: str = "exploratory"
    is_frozen: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    config_identity: str = ""

    def compute_version_hash(self) -> str:
        """Compute deterministic SHA256 version hash string for the current parameter state."""
        payload = {
            "hypothesis_id": self.hypothesis_id,
            "causal_condition": self.causal_condition,
            "condition_parameters": self.condition_parameters,
            "forward_outcome_metric": self.forward_outcome_metric,
            "forward_horizon": self.forward_horizon,
            "baseline_definition": self.baseline_definition,
            "event_spacing_bars": self.event_spacing_bars,
            "statistical_test": self.statistical_test,
            "effect_size_method": self.effect_size_method,
            "min_sample_requirement": self.min_sample_requirement,
            "symbol_scope": sorted(self.symbol_scope),
            "timeframe_scope": sorted(self.timeframe_scope),
        }
        raw_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:12]

    def freeze(self) -> HypothesisDefinition:
        """Freeze hypothesis parameters before validation."""
        data = self.model_dump()
        data["is_frozen"] = True
        return HypothesisDefinition(**data)

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)
