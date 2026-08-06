"""
Project GOAT v0.8 — Canonical Hashing & Deterministic ID Generation for Portfolio Engine

Provides deterministic SHA-256 hash computation and prefix-based ID generation for:
- Portfolio (PTF_<HEX16>)
- Position (POS_<HEX16>)
- ClosedPosition (CLS_<HEX16>)
- PortfolioSnapshot (PSN_<HEX16>)
- ExposureSummary (EXP_<HEX16>)
- PerformanceSummary (PER_<HEX16>)
- AccountSnapshot (ACC_<HEX16>)
- PortfolioAudit (PAD_<HEX16>)
"""

from goat.research.edge.canonical import compute_canonical_sha256


def compute_portfolio_id(
    portfolio_name: str,
    account_id: str,
    created_at: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "account_id": str(account_id).strip(),
        "created_at": str(created_at).strip(),
        "portfolio_name": str(portfolio_name).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PTF_{digest[:16].upper()}", digest.upper()


def compute_position_id(
    portfolio_id: str,
    symbol: str,
    side: str,
    open_price: float,
    open_time: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "open_price": round(float(open_price), 6),
        "open_time": str(open_time).strip(),
        "portfolio_id": str(portfolio_id).strip(),
        "side": str(side).strip().upper(),
        "symbol": str(symbol).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"POS_{digest[:16].upper()}", digest.upper()


def compute_closed_position_id(
    position_id: str,
    close_price: float,
    close_time: str,
    closed_quantity: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "close_price": round(float(close_price), 6),
        "close_time": str(close_time).strip(),
        "closed_quantity": round(float(closed_quantity), 6),
        "position_id": str(position_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"CLS_{digest[:16].upper()}", digest.upper()


def compute_portfolio_snapshot_id(
    portfolio_id: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "portfolio_id": str(portfolio_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PSN_{digest[:16].upper()}", digest.upper()


def compute_exposure_summary_id(
    portfolio_id: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "portfolio_id": str(portfolio_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"EXP_{digest[:16].upper()}", digest.upper()


def compute_performance_summary_id(
    portfolio_id: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "portfolio_id": str(portfolio_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PER_{digest[:16].upper()}", digest.upper()


def compute_account_snapshot_id(
    portfolio_id: str,
    account_id: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "account_id": str(account_id).strip(),
        "portfolio_id": str(portfolio_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"ACC_{digest[:16].upper()}", digest.upper()


def compute_portfolio_audit_id(
    portfolio_id: str,
    event_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    payload = {
        "event_type": str(event_type).strip().upper(),
        "portfolio_id": str(portfolio_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"PAD_{digest[:16].upper()}", digest.upper()
