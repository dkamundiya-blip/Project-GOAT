"""
Project GOAT v1.0 — Deriv Symbol Configurations and Registry

Defines symbol metadata, classification types, and canonical symbol registry
supporting extensible synthetic index definitions without code duplication.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class SymbolType(str, Enum):
    """Supported synthetic index categories."""

    VOLATILITY = "VOLATILITY"
    SPIKE = "SPIKE"
    STEP = "STEP"


class DerivSymbolConfig(BaseModel):
    """Immutable configuration and metadata for a supported Deriv symbol."""

    symbol_id: str = Field(..., description="Canonical GOAT symbol identifier (e.g. VOLATILITY_10, STEP_INDEX)")
    display_name: str = Field(..., description="Human readable display name")
    symbol_type: SymbolType = Field(..., description="Market index classification category")
    deriv_ws_symbol: str = Field(..., description="Exact Deriv WebSocket API symbol parameter (e.g. R_10, stpRNG)")
    volatility_profile: str = Field(..., description="Volatility percentage or descriptive level")
    pip_size: int = Field(default=2, ge=0, description="Price precision decimal places")
    enabled: bool = Field(default=True, description="Whether symbol ingestion is active")

    class Config:
        frozen = True
        extra = "forbid"


# Default registry of all initially supported Deriv synthetic instruments
SUPPORTED_SYMBOLS: dict[str, DerivSymbolConfig] = {
    "VOLATILITY_10": DerivSymbolConfig(
        symbol_id="VOLATILITY_10",
        display_name="Volatility 10 Index",
        symbol_type=SymbolType.VOLATILITY,
        deriv_ws_symbol="R_10",
        volatility_profile="10%",
        pip_size=3,
    ),
    "VOLATILITY_25": DerivSymbolConfig(
        symbol_id="VOLATILITY_25",
        display_name="Volatility 25 Index",
        symbol_type=SymbolType.VOLATILITY,
        deriv_ws_symbol="R_25",
        volatility_profile="25%",
        pip_size=3,
    ),
    "VOLATILITY_50": DerivSymbolConfig(
        symbol_id="VOLATILITY_50",
        display_name="Volatility 50 Index",
        symbol_type=SymbolType.VOLATILITY,
        deriv_ws_symbol="R_50",
        volatility_profile="50%",
        pip_size=4,
    ),
    "VOLATILITY_75": DerivSymbolConfig(
        symbol_id="VOLATILITY_75",
        display_name="Volatility 75 Index",
        symbol_type=SymbolType.VOLATILITY,
        deriv_ws_symbol="R_75",
        volatility_profile="75%",
        pip_size=4,
    ),
    "VOLATILITY_100": DerivSymbolConfig(
        symbol_id="VOLATILITY_100",
        display_name="Volatility 100 Index",
        symbol_type=SymbolType.VOLATILITY,
        deriv_ws_symbol="R_100",
        volatility_profile="100%",
        pip_size=2,
    ),
    "BOOM_1000": DerivSymbolConfig(
        symbol_id="BOOM_1000",
        display_name="Boom 1000 Index",
        symbol_type=SymbolType.SPIKE,
        deriv_ws_symbol="BOOM1000",
        volatility_profile="HIGH",
        pip_size=3,
    ),
    "CRASH_1000": DerivSymbolConfig(
        symbol_id="CRASH_1000",
        display_name="Crash 1000 Index",
        symbol_type=SymbolType.SPIKE,
        deriv_ws_symbol="CRASH1000",
        volatility_profile="HIGH",
        pip_size=3,
    ),
    "STEP_INDEX": DerivSymbolConfig(
        symbol_id="STEP_INDEX",
        display_name="Step Index",
        symbol_type=SymbolType.STEP,
        deriv_ws_symbol="stpRNG",
        volatility_profile="MODERATE",
        pip_size=2,
    ),
}


def get_symbol_config(symbol_id_or_ws: str) -> DerivSymbolConfig | None:
    """Resolve symbol config by GOAT symbol ID or Deriv WS symbol string."""
    sym = symbol_id_or_ws.strip().upper()
    if sym in SUPPORTED_SYMBOLS:
        return SUPPORTED_SYMBOLS[sym]
    for cfg in SUPPORTED_SYMBOLS.values():
        if cfg.deriv_ws_symbol.upper() == sym:
            return cfg
    return None
