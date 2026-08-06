"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Market State Intelligence

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- MarketState (MST_<HEX16>)
- VolatilityAssessment (VOL_<HEX16>)
- LiquidityAssessment (LIQ_<HEX16>)
- StructureAssessment (STR_<HEX16>)
- MarketQualityAssessment (MQA_<HEX16>)
- MarketStateReport (MSR_<HEX16>)
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_market_state_id(
    symbol: str,
    timestamp: str,
    trend_state: str,
    volatility_state: str,
    liquidity_state: str,
    structure_state: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (state_id, canonical_hash) for MarketState.

    Returns:
        Tuple of (MST_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "liquidity_state": str(liquidity_state).strip().upper(),
        "structure_state": str(structure_state).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "trend_state": str(trend_state).strip().upper(),
        "version": str(version).strip(),
        "volatility_state": str(volatility_state).strip().upper(),
    }
    digest = compute_canonical_sha256(payload)
    state_id = f"MST_{digest[:16].upper()}"
    return state_id, digest.upper()


def compute_volatility_id(
    symbol: str,
    timeframe: str,
    volatility_class: str,
    volatility_score: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (assessment_id, canonical_hash) for VolatilityAssessment.

    Returns:
        Tuple of (VOL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "symbol": str(symbol).strip().upper(),
        "timeframe": str(timeframe).strip().upper(),
        "version": str(version).strip(),
        "volatility_class": str(volatility_class).strip().upper(),
        "volatility_score": round(float(volatility_score), 6),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"VOL_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_liquidity_id(
    symbol: str,
    spread: float,
    spread_quality: str,
    liquidity_score: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (assessment_id, canonical_hash) for LiquidityAssessment.

    Returns:
        Tuple of (LIQ_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "liquidity_score": round(float(liquidity_score), 6),
        "spread": round(float(spread), 6),
        "spread_quality": str(spread_quality).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"LIQ_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_structure_id(
    symbol: str,
    structure_state: str,
    higher_highs: int,
    lower_lows: int,
    trend_strength: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (assessment_id, canonical_hash) for StructureAssessment.

    Returns:
        Tuple of (STR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "higher_highs": int(higher_highs),
        "lower_lows": int(lower_lows),
        "structure_state": str(structure_state).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "trend_strength": round(float(trend_strength), 6),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"STR_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_quality_id(
    symbol: str,
    data_quality: str,
    stream_health: str,
    overall_quality: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (assessment_id, canonical_hash) for MarketQualityAssessment.

    Returns:
        Tuple of (MQA_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "data_quality": str(data_quality).strip().upper(),
        "overall_quality": str(overall_quality).strip().upper(),
        "stream_health": str(stream_health).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    assessment_id = f"MQA_{digest[:16].upper()}"
    return assessment_id, digest.upper()


def compute_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (report_id, canonical_hash) for MarketState reports.

    Returns:
        Tuple of (MSR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"MSR_{digest[:16].upper()}"
    return report_id, digest.upper()
