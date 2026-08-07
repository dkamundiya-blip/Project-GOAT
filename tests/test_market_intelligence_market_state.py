"""
Project GOAT Phase 4 — Unit Tests for Market State Engine
"""

from goat.market_intelligence.market_state import MarketStateEngine
from goat.market_intelligence.models import (
    LiquidityLevel,
    MarketStatistics,
    MomentumState,
    RecordedTick,
    RegimeState,
    TrendState,
    VolatilityLevel,
    compute_market_statistics_id,
    compute_recorded_tick_id,
)
from goat.market_intelligence.persistence import InMemoryMarketStateRepository


def test_market_state_classification():
    repo = InMemoryMarketStateRepository()
    engine = MarketStateEngine(repository=repo)

    s_id, s_hash = compute_market_statistics_id("VOLATILITY_100", "2026-08-07T12:00:00Z", 50, 2.5, 0.008, 4550.0)
    stats = MarketStatistics(
        stat_id=s_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00Z",
        window_size=50,
        atr=2.5,
        true_range=2.6,
        rolling_volatility=0.008,  # High volatility (> 0.005)
        standard_deviation=5.0,
        variance=25.0,
        average_tick_rate=6.0,      # High liquidity (>= 5.0)
        average_candle_size=4.0,
        mean_spread=0.2,
        min_spread=0.1,
        max_spread=0.3,
        spread_variance=0.001,
        market_speed=0.5,
        rolling_high=4560.0,
        rolling_low=4500.0,
        rolling_vwap=4550.0,
        checksum="CHK",
        metadata={},
        canonical_hash=s_hash,
    )

    t_id, t_hash = compute_recorded_tick_id("VOLATILITY_100", 4555.0, 4555.4, 4555.2, "2026-08-07T12:00:00Z", 50)
    tick = RecordedTick(
        tick_id=t_id,
        symbol="VOLATILITY_100",
        timestamp="2026-08-07T12:00:00Z",
        bid=4555.0,
        ask=4555.4,
        mid_price=4555.2,
        spread=0.4,
        latency_ms=10.0,
        sequence_number=50,
        source="WS",
        checksum="CHK",
        metadata={},
        canonical_hash=t_hash,
    )

    state = engine.classify_state(stats, current_tick=tick)

    assert state.symbol == "VOLATILITY_100"
    assert state.volatility == VolatilityLevel.HIGH
    assert state.liquidity == LiquidityLevel.HIGH
    assert isinstance(state.trend, TrendState)
    assert isinstance(state.momentum, MomentumState)
    assert isinstance(state.regime, RegimeState)

    # Repository verification
    assert repo.get_latest_state("VOLATILITY_100").state_id == state.state_id
