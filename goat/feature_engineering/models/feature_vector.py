"""
Project GOAT Phase 5 — Feature Vector Domain Model

Defines the immutable FeatureVector domain model and canonical SHA-256 ID generation.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.research.edge.canonical import compute_canonical_sha256


class FeatureVector(BaseModel):
    """Immutable domain model representing an engineered quantitative feature vector."""

    vector_id: str = Field(
        ...,
        description="Unique feature vector ID formatted as FVR_<HEX16>",
        pattern=r"^FVR_[A-Fa-f0-9]{16}$",
    )
    symbol: str = Field(..., description="Canonical instrument symbol (e.g. VOLATILITY_100)")
    timeframe: str = Field(..., description="Feature calculation resolution (e.g. 1m, 5m, 1h, tick)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of feature calculation")
    version: str = Field(default="5.0.0", description="Feature schema version specification")
    features: dict[str, float] = Field(..., description="Dictionary mapping feature names to numerical float values")
    checksum: str = Field(..., description="SHA-256 canonical digest of feature key-value payload")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extensible operational metadata")
    canonical_hash: str = Field(..., description="Full SHA-256 canonical hash digest")

    def get_feature(self, name: str, default: float = 0.0) -> float:
        """Fetch a specific feature value by name with default fallback."""
        return self.features.get(name, default)

    class Config:
        frozen = True
        extra = "forbid"


def compute_feature_vector_id(
    symbol: str,
    timeframe: str,
    timestamp: str,
    features: dict[str, float],
    version: str = "5.0.0",
) -> tuple[str, str]:
    """Compute deterministic (vector_id, canonical_hash) for FeatureVector.

    Returns:
        Tuple of (FVR_<HEX16>, SHA256_HEX64).
    """
    sorted_features = {
        str(k).strip(): round(float(v), 8)
        for k, v in sorted(features.items(), key=lambda item: str(item[0]))
    }
    payload = {
        "features": sorted_features,
        "symbol": str(symbol).strip().upper(),
        "timeframe": str(timeframe).strip().lower(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    vector_id = f"FVR_{digest[:16].upper()}"
    return vector_id, digest.upper()
