"""
Project GOAT v0.7 — Initial Price Primitive Features

Stateless, direct transformations on raw market data windows (N <= 2 lookback):
- LogReturn: Logarithmic price returns r_t = ln(C_t / C_{t-1})
- BarRange: Bar high-low range Range_t = H_t - L_t
- BodyRatio: Bar body to total range ratio |C_t - O_t| / Range_t
- UpperWickRatio: Upper shadow to total range ratio (H_t - max(O_t, C_t)) / Range_t
- LowerWickRatio: Lower shadow to total range ratio (min(O_t, C_t) - L_t) / Range_t
"""

from __future__ import annotations

from typing import Any

import numpy as np

from goat.features.core.base import PrimitiveFeature
from goat.features.core.context import MarketDataWindow
from goat.features.core.enums import StationarityType, TaxonomyCategory

EPSILON = 1e-12


class LogReturn(PrimitiveFeature):
    """Logarithmic return primitive feature r_t = ln(C_t / C_{t-1})."""

    def __init__(self, name: str = "LogReturn", version: str = "1.0.0") -> None:
        super().__init__(
            name=name,
            version=version,
            taxonomy_category=TaxonomyCategory.TREND,
            taxonomy_subcategory="returns",
            mathematical_definition=r"r_t = \ln\left(\frac{C_t}{C_{t-1}}\right)",
            algorithmic_spec="r_0 = 0.0; r_t = np.log(C_t / C_{t-1}) for t >= 1",
            expected_stationarity=StationarityType.STATIONARY,
        )

    def compute(self, context: MarketDataWindow) -> np.ndarray:
        close = context.close
        if len(close) == 0:
            return np.array([], dtype=np.float64)

        result = np.zeros_like(close, dtype=np.float64)
        if len(close) > 1:
            result[1:] = np.log(close[1:] / close[:-1])
        return result

    def to_ast_dict(self) -> dict[str, Any]:
        return {
            "op": "LogReturn",
            "inputs": ["close"],
            "version": self._version,
        }

    def _get_input_requirements(self) -> dict[str, Any]:
        return {"min_bars": 2, "required_columns": ["close"]}


class BarRange(PrimitiveFeature):
    """Bar High-Low range primitive feature Range_t = H_t - L_t."""

    def __init__(self, name: str = "BarRange", version: str = "1.0.0") -> None:
        super().__init__(
            name=name,
            version=version,
            taxonomy_category=TaxonomyCategory.RANGE,
            taxonomy_subcategory="bar_span",
            mathematical_definition=r"\text{Range}_t = H_t - L_t",
            algorithmic_spec="Range_t = High_t - Low_t",
            expected_stationarity=StationarityType.NON_STATIONARY_RAW,
        )

    def compute(self, context: MarketDataWindow) -> np.ndarray:
        high = context.high
        low = context.low
        return (high - low).astype(np.float64)

    def to_ast_dict(self) -> dict[str, Any]:
        return {
            "op": "BarRange",
            "inputs": ["high", "low"],
            "version": self._version,
        }

    def _get_input_requirements(self) -> dict[str, Any]:
        return {"min_bars": 1, "required_columns": ["high", "low"]}


class BodyRatio(PrimitiveFeature):
    """Bar real body to total range ratio |C_t - O_t| / max(H_t - L_t, epsilon)."""

    def __init__(self, name: str = "BodyRatio", version: str = "1.0.0") -> None:
        super().__init__(
            name=name,
            version=version,
            taxonomy_category=TaxonomyCategory.CANDLE_BEHAVIOUR,
            taxonomy_subcategory="body_proportion",
            mathematical_definition=r"\text{BodyRatio}_t = \frac{|C_t - O_t|}{\max(H_t - L_t, \epsilon)}",
            algorithmic_spec="BodyRatio_t = abs(Close_t - Open_t) / max(High_t - Low_t, 1e-12)",
            value_range=(0.0, 1.0),
            expected_stationarity=StationarityType.STATIONARY,
        )

    def compute(self, context: MarketDataWindow) -> np.ndarray:
        open_p = context.open
        high = context.high
        low = context.low
        close = context.close

        body = np.abs(close - open_p)
        rng = np.maximum(high - low, EPSILON)
        return (body / rng).astype(np.float64)

    def to_ast_dict(self) -> dict[str, Any]:
        return {
            "op": "BodyRatio",
            "inputs": ["open", "high", "low", "close"],
            "version": self._version,
        }

    def _get_input_requirements(self) -> dict[str, Any]:
        return {"min_bars": 1, "required_columns": ["open", "high", "low", "close"]}


class UpperWickRatio(PrimitiveFeature):
    """Upper shadow to total range ratio (H_t - max(O_t, C_t)) / max(H_t - L_t, epsilon)."""

    def __init__(self, name: str = "UpperWickRatio", version: str = "1.0.0") -> None:
        super().__init__(
            name=name,
            version=version,
            taxonomy_category=TaxonomyCategory.WICK_BEHAVIOUR,
            taxonomy_subcategory="upper_shadow",
            mathematical_definition=r"\text{UpperWick}_t = \frac{H_t - \max(O_t, C_t)}{\max(H_t - L_t, \epsilon)}",
            algorithmic_spec="UpperWick_t = (High_t - max(Open_t, Close_t)) / max(High_t - Low_t, 1e-12)",
            value_range=(0.0, 1.0),
            expected_stationarity=StationarityType.STATIONARY,
        )

    def compute(self, context: MarketDataWindow) -> np.ndarray:
        open_p = context.open
        high = context.high
        low = context.low
        close = context.close

        upper_shadow = high - np.maximum(open_p, close)
        rng = np.maximum(high - low, EPSILON)
        return (upper_shadow / rng).astype(np.float64)

    def to_ast_dict(self) -> dict[str, Any]:
        return {
            "op": "UpperWickRatio",
            "inputs": ["open", "high", "low", "close"],
            "version": self._version,
        }

    def _get_input_requirements(self) -> dict[str, Any]:
        return {"min_bars": 1, "required_columns": ["open", "high", "low", "close"]}


class LowerWickRatio(PrimitiveFeature):
    """Lower shadow to total range ratio (min(O_t, C_t) - L_t) / max(H_t - L_t, epsilon)."""

    def __init__(self, name: str = "LowerWickRatio", version: str = "1.0.0") -> None:
        super().__init__(
            name=name,
            version=version,
            taxonomy_category=TaxonomyCategory.WICK_BEHAVIOUR,
            taxonomy_subcategory="lower_shadow",
            mathematical_definition=r"\text{LowerWick}_t = \frac{\min(O_t, C_t) - L_t}{\max(H_t - L_t, \epsilon)}",
            algorithmic_spec="LowerWick_t = (min(Open_t, Close_t) - Low_t) / max(High_t - Low_t, 1e-12)",
            value_range=(0.0, 1.0),
            expected_stationarity=StationarityType.STATIONARY,
        )

    def compute(self, context: MarketDataWindow) -> np.ndarray:
        open_p = context.open
        high = context.high
        low = context.low
        close = context.close

        lower_shadow = np.minimum(open_p, close) - low
        rng = np.maximum(high - low, EPSILON)
        return (lower_shadow / rng).astype(np.float64)

    def to_ast_dict(self) -> dict[str, Any]:
        return {
            "op": "LowerWickRatio",
            "inputs": ["open", "high", "low", "close"],
            "version": self._version,
        }

    def _get_input_requirements(self) -> dict[str, Any]:
        return {"min_bars": 1, "required_columns": ["open", "high", "low", "close"]}
