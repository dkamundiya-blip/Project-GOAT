"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Market Data

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- MarketTick (MTK_<HEX16>)
- MarketCandle (MCD_<HEX16>)
- MarketStreamState (MSS_<HEX16>)
- MarketGap (MGP_<HEX16>)
- ReplaySnapshot (RPS_<HEX16>)
- MarketReport (MRP_<HEX16>)
"""

from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_tick_id(
    symbol: str,
    broker: str,
    bid: float,
    ask: float,
    timestamp: str,
    sequence_number: int,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (tick_id, canonical_hash) for MarketTick.

    Returns:
        Tuple of (MTK_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "ask": round(float(ask), 8),
        "bid": round(float(bid), 8),
        "broker": str(broker).strip().upper(),
        "sequence_number": int(sequence_number),
        "symbol": str(symbol).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    tick_id = f"MTK_{digest[:16].upper()}"
    return tick_id, digest.upper()


def compute_candle_id(
    symbol: str,
    timeframe: str,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    open_timestamp: str,
    close_timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (candle_id, canonical_hash) for MarketCandle.

    Returns:
        Tuple of (MCD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "close": round(float(close_price), 8),
        "close_timestamp": str(close_timestamp).strip(),
        "high": round(float(high_price), 8),
        "low": round(float(low_price), 8),
        "open": round(float(open_price), 8),
        "open_timestamp": str(open_timestamp).strip(),
        "symbol": str(symbol).strip().upper(),
        "timeframe": str(timeframe).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    candle_id = f"MCD_{digest[:16].upper()}"
    return candle_id, digest.upper()


def compute_stream_id(
    broker: str,
    symbol: str,
    heartbeat_timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (stream_id, canonical_hash) for MarketStreamState.

    Returns:
        Tuple of (MSS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "broker": str(broker).strip().upper(),
        "heartbeat_timestamp": str(heartbeat_timestamp).strip(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    stream_id = f"MSS_{digest[:16].upper()}"
    return stream_id, digest.upper()


def compute_gap_id(
    symbol: str,
    start_timestamp: str,
    end_timestamp: str,
    reason: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (gap_id, canonical_hash) for MarketGap.

    Returns:
        Tuple of (MGP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "end_timestamp": str(end_timestamp).strip(),
        "reason": str(reason).strip().upper(),
        "start_timestamp": str(start_timestamp).strip(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    gap_id = f"MGP_{digest[:16].upper()}"
    return gap_id, digest.upper()


def compute_replay_id(
    symbol: str,
    replay_timestamp: str,
    snapshot_reference: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (replay_id, canonical_hash) for ReplaySnapshot.

    Returns:
        Tuple of (RPS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "replay_timestamp": str(replay_timestamp).strip(),
        "snapshot_reference": str(snapshot_reference).strip(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    replay_id = f"RPS_{digest[:16].upper()}"
    return replay_id, digest.upper()


def compute_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute deterministic (report_id, canonical_hash) for MarketData reports.

    Returns:
        Tuple of (MRP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"MRP_{digest[:16].upper()}"
    return report_id, digest.upper()
