# Deriv Market Microstructure & Synthetic Index Research Engine

## System Architecture

Project GOAT Version 0.9 — Step 9.8 introduces the **Deriv Market Microstructure & Synthetic Index Research Engine** (`goat/microstructure/`).

This subsystem is the first domain-specific quantitative research laboratory in Project GOAT. Its sole mandate is to scientifically observe, measure, classify, and archive market microstructure behavior across Deriv Synthetic Indices.

### Non-Negotiable Research Protocol
1. **NO Trading Signals**: Does not calculate or produce buy/sell signals.
2. **NO Execution Engine**: Does not connect to live broker order routing APIs for trading.
3. **NO Strategy Implementation**: Zero alpha or trading strategies.
4. **NO Hypothesis Testing**: Only records observable raw microstructure metrics; statistical inference and hypothesis evaluation are performed downstream.
5. **Deterministic Observation & Archiving**: All data is immutably modeled and stored in SQLite WAL databases with Foreign Keys and deterministic SHA-256 canonical hashing.

---

## Package Inventory & Architecture

```
goat/microstructure/
├── __init__.py                # Clean public exports API
├── engine.py                  # High-level MicrostructureResearchEngine
├── core/
│   ├── enums.py               # SyntheticIndexType, ObservationCategory, MetricType, etc.
│   ├── canonical.py           # Canonical JSON serialization & SHA-256 ID generators
│   ├── models.py              # Immutable Pydantic V2 domain models
│   └── __init__.py
├── volatility/
│   ├── engine.py              # VolatilityProfilingEngine
│   └── __init__.py
├── jumps/
│   ├── engine.py              # JumpProfilingEngine
│   └── __init__.py
├── liquidity/
│   ├── engine.py              # LiquidityProfilingEngine
│   └── __init__.py
├── execution/
│   ├── engine.py              # ExecutionProfilingEngine
│   └── __init__.py
├── profiling/
│   ├── engine.py              # MarketProfilingEngine
│   └── __init__.py
├── reporting/
│   ├── reports.py             # MicrostructureReportGenerator (Markdown & Canonical JSON)
│   └── __init__.py
└── persistence/
    ├── sqlite.py              # SQLite repositories and database context
    └── __init__.py
```

---

## Domain Models & Canonical ID Prefixes

All domain models are immutable Pydantic V2 models (`ConfigDict(frozen=True, extra="forbid")`).

| Model Name | ID Prefix | Canonical SHA-256 Fields |
|---|---|---|
| `MicrostructureObservation` | `MSO_` | metric_type, symbol, timestamp, value, version, window_seconds |
| `VolatilityProfile` | `VLP_` | symbol, timestamp, window_seconds, realized_volatility, observation_ids |
| `JumpProfile` | `JMP_` | symbol, timestamp, window_seconds, jump_count, mean_jump_magnitude, observation_ids |
| `LiquidityProfile` | `LIQ_` | symbol, timestamp, window_seconds, average_spread, tick_density, observation_ids |
| `ExecutionProfile` | `EXP_` | symbol, timestamp, window_seconds, mean_latency_ms, sample_count, observation_ids |
| `MarketProfile` | `MRP_` | symbol, timestamp, volatility_profile_id, jump_profile_id, liquidity_profile_id, execution_profile_id |
| `ResearchSummary` | `MRS_` | timestamp, total_observations, symbols_profiled |

---

## Quantitative Sub-Engines

### 1. VolatilityProfilingEngine
- **Realized Volatility**: Standard deviation of log price returns.
- **Volatility Clustering**: Autocorrelation of absolute returns.
- **Volatility Persistence**: Autocorrelation of squared returns.
- **Volatility Expansion / Contraction**: Peak & trough ratios relative to window mean volatility.

### 2. JumpProfilingEngine
- **Jump Frequency**: Jumps detected per minute exceeding standard deviation threshold.
- **Jump Magnitude**: Mean and peak magnitude of observed price discontinuities.
- **Jump Spacing**: Mean duration in seconds between consecutive jumps.
- **Jump Persistence & Clustering**: Fano factor and arrival process dispersion.

### 3. LiquidityProfilingEngine
- **Spread Stability**: Normalized index derived from spread variance.
- **Quote Continuity**: Fraction of active quotes relative to expected tick rate.
- **Tick Density & Activity**: Ticks per second and composite activity metrics.

### 4. ExecutionProfilingEngine
- **Execution Latency**: Mean, median, and P95 round-trip latency in milliseconds.
- **Fill Timing**: Mean fill confirmation time.
- **Execution Consistency**: Coefficient of variation metric.

### 5. MarketProfilingEngine
- Aggregates sub-profiles into an immutable `MarketProfile` with an overall market health score (0..100).

---

## SQLite Persistence & Repositories

Database schema enforced via SQLite with Foreign Keys enabled and Write-Ahead Logging (WAL) journal mode.

Repositories implemented:
- `ObservationRepository`
- `VolatilityRepository`
- `JumpRepository`
- `LiquidityRepository`
- `ExecutionRepository`
- `MarketProfileRepository`
- `SummaryRepository`

Round-trip serialization maintains exact float precision (rounded to 8 decimal places canonically) and lossless JSON metadata reconstruction.
