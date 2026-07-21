"""
Project GOAT v0.3 — Market Fingerprint Object & Comparative Analyzer

Defines the standardized MarketFingerprint schema and cross-market / cross-timeframe
comparative tools. Strictly descriptive — contains ZERO trading strategy rankings.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from goat.logging import get_logger
from goat.research.events import ImpulseCharacterization, PullbackCharacterization
from goat.research.regimes import RegimeClassifier
from goat.research.returns import calculate_returns
from goat.research.stats import (
    calculate_distribution_stats,
    calculate_range_stats,
    calculate_run_lengths,
    calculate_serial_dependence,
)
from goat.research.sufficiency import DatasetSufficiencyReport, evaluate_dataset_sufficiency

_log = get_logger("research.fingerprint")


class MarketFingerprint(BaseModel):
    """Standardized quantitative fingerprint summarizing a market's characteristics."""

    symbol: str
    timeframe: str
    summary_period: dict[str, str] = Field(default_factory=dict)
    distribution: dict[str, float] = Field(default_factory=dict)
    volatility: dict[str, float] = Field(default_factory=dict)
    serial_dependence: dict[str, float] = Field(default_factory=dict)
    directional_runs: dict[str, Any] = Field(default_factory=dict)
    range_dynamics: dict[str, float] = Field(default_factory=dict)
    impulses: dict[str, Any] = Field(default_factory=dict)
    pullbacks: dict[str, Any] = Field(default_factory=dict)
    regime_distribution: dict[str, float] = Field(default_factory=dict)
    sufficiency: DatasetSufficiencyReport

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)


def generate_market_fingerprint(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str = "M1",
    price_col: str = "close",
) -> MarketFingerprint:
    """Generate standardized MarketFingerprint from research DataFrame.

    Args:
        df: Input research DataFrame (Ticks or Candles).
        symbol: Instrument identifier.
        timeframe: Timeframe label.
        price_col: Price column name.

    Returns:
        ``MarketFingerprint`` instance.
    """
    sufficiency = evaluate_dataset_sufficiency(df, symbol=symbol, timeframe=timeframe)

    if df.empty:
        return MarketFingerprint(
            symbol=symbol,
            timeframe=timeframe,
            sufficiency=sufficiency,
        )

    # 1. Calculate returns
    returns_df = calculate_returns(df, price_col=price_col)

    # 2. Summary Period
    summary_period = {}
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], utc=True)
        summary_period["start"] = ts.iloc[0].isoformat()
        summary_period["end"] = ts.iloc[-1].isoformat()

    # 3. Distribution & Volatility Stats
    arithmetic_returns = returns_df["ret_arithmetic"].dropna()
    dist_stats = calculate_distribution_stats(arithmetic_returns)

    # 4. Serial Dependence (Autocorrelation lags 1..10)
    serial_dep = calculate_serial_dependence(arithmetic_returns, lags=[1, 2, 3, 5, 10])
    abs_serial_dep = calculate_serial_dependence(
        returns_df["ret_abs"].dropna(), lags=[1, 2, 3, 5, 10]
    )
    for k, v in abs_serial_dep.items():
        serial_dep[f"abs_{k}"] = v

    # 5. Directional Runs
    run_stats = calculate_run_lengths(arithmetic_returns)

    # 6. Range Dynamics
    range_stats = calculate_range_stats(df)

    # 7. Impulse & Pullback Characterization
    imp_detector = ImpulseCharacterization(std_threshold=2.0)
    impulses_df = imp_detector.detect_impulses(df, price_col=price_col)

    impulse_summary = {
        "count": len(impulses_df),
        "mean_magnitude": round(float(impulses_df["impulse_magnitude"].mean()), 6) if not impulses_df.empty else 0.0,
        "max_magnitude": round(float(impulses_df["impulse_magnitude"].max()), 6) if not impulses_df.empty else 0.0,
    }

    pullback_analyzer = PullbackCharacterization(forward_horizon=10)
    pullbacks_df = pullback_analyzer.analyze_pullbacks(df, impulses_df, price_col=price_col)

    pullback_summary = {
        "analyzed_count": len(pullbacks_df),
        "mean_retracement_fraction": round(float(pullbacks_df["retracement_fraction"].mean()), 4) if not pullbacks_df.empty else 0.0,
        "max_retracement_fraction": round(float(pullbacks_df["retracement_fraction"].max()), 4) if not pullbacks_df.empty else 0.0,
    }

    # 8. Regime Breakdown
    regime_clf = RegimeClassifier()
    regime_clf.fit(df, price_col=price_col)
    regime_df = regime_clf.apply(df, price_col=price_col)

    regime_dist_raw = regime_df["volatility_regime"].value_counts(normalize=True).to_dict()
    regime_distribution = {str(k): round(float(v), 4) for k, v in regime_dist_raw.items()}

    _log.info("market_fingerprint_generated", symbol=symbol, timeframe=timeframe)

    return MarketFingerprint(
        symbol=symbol,
        timeframe=timeframe,
        summary_period=summary_period,
        distribution=dist_stats,
        volatility={
            "std": dist_stats["std"],
            "variance": dist_stats["variance"],
            "mean_relative_range": range_stats.get("mean_relative_range", 0.0),
        },
        serial_dependence=serial_dep,
        directional_runs=run_stats,
        range_dynamics=range_stats,
        impulses=impulse_summary,
        pullbacks=pullback_summary,
        regime_distribution=regime_distribution,
        sufficiency=sufficiency,
    )


def compare_market_fingerprints(
    fingerprints: list[MarketFingerprint],
) -> pd.DataFrame:
    """Compare multiple MarketFingerprint objects in a structured summary DataFrame.

    Args:
        fingerprints: List of ``MarketFingerprint`` instances.

    Returns:
        DataFrame comparing key metrics across symbols/timeframes.
    """
    records = []
    for fp in fingerprints:
        records.append({
            "symbol": fp.symbol,
            "timeframe": fp.timeframe,
            "observations": fp.sufficiency.observation_count,
            "mean_return": fp.distribution.get("mean", 0.0),
            "std_return": fp.distribution.get("std", 0.0),
            "skewness": fp.distribution.get("skewness", 0.0),
            "kurtosis": fp.distribution.get("kurtosis", 0.0),
            "autocorr_lag1": fp.serial_dependence.get("autocorr_lag_1", 0.0),
            "abs_autocorr_lag1": fp.serial_dependence.get("abs_autocorr_lag_1", 0.0),
            "pos_run_max": fp.directional_runs.get("positive_run_max", 0.0),
            "neg_run_max": fp.directional_runs.get("negative_run_max", 0.0),
            "impulse_count": fp.impulses.get("count", 0),
            "high_vol_regime_pct": fp.regime_distribution.get("HIGH", 0.0),
            "sufficiency": fp.sufficiency.status,
        })
    return pd.DataFrame(records)
