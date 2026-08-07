"""
Project GOAT Phase 6 — Discovered Edge Domain Models

Defines immutable Pydantic models for validated quantitative edges, performance metrics, and deterministic ID computation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class EdgeStatus(str, Enum):
    """Lifecycle status of a validated market edge."""
    ACTIVE = "ACTIVE"
    WATCHLIST = "WATCHLIST"
    DEGRADING = "DEGRADING"
    RETIRED = "RETIRED"


class EdgePerformanceMetrics(BaseModel):
    """Immutable container holding 16 quantitative performance metrics."""

    sample_size: int = Field(..., description="Total sample observations evaluated")
    win_rate: float = Field(..., description="Ratio of positive outcome occurrences [0.0, 1.0]")
    loss_rate: float = Field(..., description="Ratio of negative outcome occurrences [0.0, 1.0]")
    expected_value: float = Field(..., description="Expected return per trade/observation")
    average_return: float = Field(..., description="Mean return per observation")
    median_return: float = Field(..., description="Median return per observation")
    max_gain: float = Field(..., description="Maximum observed single-trade return gain")
    max_loss: float = Field(..., description="Maximum observed single-trade return loss")
    profit_factor: float = Field(..., description="Gross profit divided by gross loss")
    sharpe_ratio: float = Field(..., description="Annualized risk-adjusted return ratio")
    sortino_ratio: float = Field(..., description="Downside risk-adjusted return ratio")
    calmar_ratio: float = Field(..., description="Return to max drawdown ratio")
    max_drawdown: float = Field(..., description="Maximum peak-to-trough equity drawdown [0.0, 1.0]")
    recovery_factor: float = Field(..., description="Net profit divided by max drawdown")
    trade_frequency: float = Field(..., description="Average trade occurrences per day")
    holding_period: float = Field(..., description="Average trade holding duration in bars")

    class Config:
        frozen = True


class DiscoveredEdge(BaseModel):
    """Immutable domain model representing a statistically validated market edge."""

    edge_id: str = Field(
        ...,
        description="Unique edge ID formatted as EDG_<HEX16>",
        pattern=r"^EDG_[A-Fa-f0-9]{16}$",
    )
    version: str = Field(default="6.0.0", description="Edge schema specification version")
    hypothesis_id: str = Field(..., description="Source hypothesis identifier")
    feature_combination: list[str] = Field(..., description="List of feature names forming the edge")
    supported_symbols: list[str] = Field(..., description="Symbols where edge is statistically valid")
    supported_timeframes: list[str] = Field(..., description="Timeframes where edge is statistically valid")
    metrics: EdgePerformanceMetrics = Field(..., description="16 quantitative performance metrics")
    p_value: float = Field(..., description="Statistical significance p-value")
    confidence_interval_low: float = Field(..., description="95% confidence interval lower bound")
    confidence_interval_high: float = Field(..., description="95% confidence interval upper bound")
    effect_size: float = Field(..., description="Cohen's d standardized effect size")
    composite_score: float = Field(..., description="Weighted edge ranking composite score")
    discovery_date: str = Field(..., description="ISO 8601 UTC discovery timestamp")
    last_validation_date: str = Field(..., description="ISO 8601 UTC last validation timestamp")
    status: EdgeStatus = Field(default=EdgeStatus.ACTIVE, description="Current lifecycle status")
    regime_performance: dict[str, dict[str, float]] = Field(
        default_factory=dict, description="Regime-specific performance breakdowns"
    )
    walk_forward_metrics: dict[str, float] = Field(
        default_factory=dict, description="Out-of-sample walk-forward validation metrics"
    )
    checksum: str = Field(..., description="SHA-256 canonical payload checksum")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    class Config:
        frozen = True
        extra = "forbid"


def compute_edge_id(
    hypothesis_id: str,
    feature_combination: list[str],
    symbols: list[str],
    timeframes: list[str],
    version: str = "6.0.0",
) -> tuple[str, str]:
    """Compute deterministic (edge_id, canonical_hash) for DiscoveredEdge.

    Returns:
        Tuple of (EDG_<HEX16>, SHA256_HEX64).
    """
    sorted_features = sorted(list(set(str(f).strip() for f in feature_combination)))
    sorted_symbols = sorted(list(set(str(s).strip().upper() for s in symbols)))
    sorted_tfs = sorted(list(set(str(tf).strip().lower() for tf in timeframes)))

    payload = {
        "feature_combination": sorted_features,
        "hypothesis_id": str(hypothesis_id).strip(),
        "symbols": sorted_symbols,
        "timeframes": sorted_tfs,
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    edge_id = f"EDG_{digest[:16].upper()}"
    return edge_id, digest.upper()
