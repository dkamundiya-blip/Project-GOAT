"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Deriv Market Microstructure Engine
"""

import hashlib
import json
from typing import Any


def serialize_canonical_json(data: Any) -> str:
    """Recursively convert arbitrary structure into canonical JSON string with sorted keys.

    Args:
        data: Structure to serialize (dict, list, tuple, set, Enum, primitive, Pydantic model).

    Returns:
        Canonical JSON string formatted with sorted keys and tight separators.
    """
    def _normalize(val: Any) -> Any:
        if isinstance(val, dict):
            return {str(k): _normalize(v) for k, v in sorted(val.items(), key=lambda x: str(x[0]))}
        elif isinstance(val, (list, tuple, set)):
            return [_normalize(item) for item in val]
        elif hasattr(val, "value"):  # Enum support
            return str(val.value)
        elif hasattr(val, "model_dump"):  # Pydantic v2 support
            return _normalize(val.model_dump())
        elif hasattr(val, "dict"):  # Pydantic v1 fallback
            return _normalize(val.dict())
        elif isinstance(val, float):
            return round(val, 8)
        return val

    normalized = _normalize(data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_canonical_sha256(data: Any) -> str:
    """Compute 64-character uppercase SHA-256 hex digest of canonically serialized data."""
    canonical_json = serialize_canonical_json(data)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest().upper()


def compute_observation_id(
    symbol: str,
    metric_type: str,
    timestamp: str,
    value: float,
    window_seconds: int = 60,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (observation_id, canonical_hash) deterministically for MicrostructureObservation.

    Returns:
        Tuple of (MSO_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "metric_type": str(metric_type).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "value": round(float(value), 8),
        "version": str(version).strip(),
        "window_seconds": int(window_seconds),
    }
    digest = compute_canonical_sha256(payload)
    observation_id = f"MSO_{digest[:16].upper()}"
    return observation_id, digest.upper()


def compute_volatility_profile_id(
    symbol: str,
    timestamp: str,
    window_seconds: int,
    realized_volatility: float,
    observation_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (profile_id, canonical_hash) deterministically for VolatilityProfile.

    Returns:
        Tuple of (VLP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "observation_ids": sorted([str(o).strip() for o in observation_ids]),
        "realized_volatility": round(float(realized_volatility), 8),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
        "window_seconds": int(window_seconds),
    }
    digest = compute_canonical_sha256(payload)
    profile_id = f"VLP_{digest[:16].upper()}"
    return profile_id, digest.upper()


def compute_jump_profile_id(
    symbol: str,
    timestamp: str,
    window_seconds: int,
    jump_count: int,
    mean_jump_magnitude: float,
    observation_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (profile_id, canonical_hash) deterministically for JumpProfile.

    Returns:
        Tuple of (JMP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "jump_count": int(jump_count),
        "mean_jump_magnitude": round(float(mean_jump_magnitude), 8),
        "observation_ids": sorted([str(o).strip() for o in observation_ids]),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
        "window_seconds": int(window_seconds),
    }
    digest = compute_canonical_sha256(payload)
    profile_id = f"JMP_{digest[:16].upper()}"
    return profile_id, digest.upper()


def compute_liquidity_profile_id(
    symbol: str,
    timestamp: str,
    window_seconds: int,
    average_spread: float,
    tick_density: float,
    observation_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (profile_id, canonical_hash) deterministically for LiquidityProfile.

    Returns:
        Tuple of (LIQ_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "average_spread": round(float(average_spread), 8),
        "observation_ids": sorted([str(o).strip() for o in observation_ids]),
        "symbol": str(symbol).strip().upper(),
        "tick_density": round(float(tick_density), 8),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
        "window_seconds": int(window_seconds),
    }
    digest = compute_canonical_sha256(payload)
    profile_id = f"LIQ_{digest[:16].upper()}"
    return profile_id, digest.upper()


def compute_execution_profile_id(
    symbol: str,
    timestamp: str,
    window_seconds: int,
    mean_latency_ms: float,
    sample_count: int,
    observation_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (profile_id, canonical_hash) deterministically for ExecutionProfile.

    Returns:
        Tuple of (EXP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "mean_latency_ms": round(float(mean_latency_ms), 8),
        "observation_ids": sorted([str(o).strip() for o in observation_ids]),
        "sample_count": int(sample_count),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
        "window_seconds": int(window_seconds),
    }
    digest = compute_canonical_sha256(payload)
    profile_id = f"EXP_{digest[:16].upper()}"
    return profile_id, digest.upper()


def compute_market_profile_id(
    symbol: str,
    timestamp: str,
    volatility_profile_id: str,
    jump_profile_id: str,
    liquidity_profile_id: str,
    execution_profile_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (profile_id, canonical_hash) deterministically for MarketProfile.

    Returns:
        Tuple of (MRP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "execution_profile_id": str(execution_profile_id).strip(),
        "jump_profile_id": str(jump_profile_id).strip(),
        "liquidity_profile_id": str(liquidity_profile_id).strip(),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
        "volatility_profile_id": str(volatility_profile_id).strip(),
    }
    digest = compute_canonical_sha256(payload)
    profile_id = f"MRP_{digest[:16].upper()}"
    return profile_id, digest.upper()


def compute_research_summary_id(
    timestamp: str,
    total_observations: int,
    symbols_profiled: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically for ResearchSummary.

    Returns:
        Tuple of (MRS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "symbols_profiled": sorted([str(s).strip().upper() for s in symbols_profiled]),
        "timestamp": str(timestamp).strip(),
        "total_observations": int(total_observations),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"MRS_{digest[:16].upper()}"
    return summary_id, digest.upper()
