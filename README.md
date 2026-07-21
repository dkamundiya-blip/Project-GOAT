# 🐐 Project GOAT

**Generative Opportunity Analysis & Trading**

A rigorous quantitative research platform for studying synthetic financial
markets, discovering recurring statistical price structures, and validating
potential edges.

---

## Current Version: v0.1 — Quant Data Foundation

This release establishes the **production-quality data foundation** for all
future quantitative research.  It provides:

- ✅ Strongly-validated data schemas (Tick, Candle) with Decimal precision
- ✅ Data provenance tracking (LIVE / HISTORICAL_IMPORT / TEST)
- ✅ Async market-data collector interface (broker-agnostic)
- ✅ Parquet-based storage with date partitioning and duplicate protection
- ✅ Tick → OHLC candle aggregation (M1)
- ✅ Report-only data validation engine
- ✅ Structured logging with automatic secret redaction
- ✅ Comprehensive test suite

### What v0.1 Does NOT Include

> **⚠️ The following are explicitly out of scope for v0.1:**
>
> - Real market-data connectors
> - Technical indicators
> - Pattern detection
> - Machine learning models
> - Strategy optimization
> - Signal generation
> - Backtesting
> - Profitability calculations
> - Live/simulated trading execution

---

## Installation

### Prerequisites

- Python 3.12 or later
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd project-goat

# Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install in development mode with test dependencies
pip install -e ".[dev]"

# Copy the environment template
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```

---

## Project Architecture

```
project-goat/
│
├── goat/                          # Main Python package
│   ├── __init__.py                # Package root (version)
│   ├── config.py                  # Pydantic settings (from env vars)
│   ├── logging.py                 # Structured logging (structlog)
│   │
│   ├── data/                      # ── DATA LAYER ──
│   │   ├── schemas.py             # Tick, Candle, DataSource, Timeframe
│   │   ├── collector/
│   │   │   ├── base.py            # AbstractCollector (async interface)
│   │   │   └── mock.py            # MockMarketDataCollector (TEST ONLY)
│   │   ├── storage/
│   │   │   ├── base.py            # AbstractStorage interface
│   │   │   └── parquet.py         # ParquetStorage implementation
│   │   ├── processing/
│   │   │   └── aggregation.py     # Tick → OHLC candle aggregation
│   │   └── validation/
│   │       └── validators.py      # Report-only validation engine
│   │
│   ├── features/                  # Future: feature engineering
│   ├── patterns/                  # Future: pattern discovery
│   ├── regimes/                   # Future: regime detection
│   ├── models/                    # Future: statistical models
│   ├── scanner/                   # Future: scanner mode
│   ├── signals/                   # Future: signal generation
│   ├── simulation/                # Future: simulation/auto mode
│   └── risk/                      # Future: risk management
│
├── tests/                         # Pytest test suite
├── research/                      # Notebooks, experiments, reports
├── data/                          # Raw and processed data (gitignored)
├── config/                        # Configuration templates
├── scripts/                       # Utility scripts
├── dashboard/                     # Future: monitoring dashboard
└── docs/                          # Documentation
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Decimal prices** in schemas | Avoids float rounding at the API boundary |
| **float64 in Parquet** | Ecosystem compatibility (pandas/numpy/pyarrow) |
| **Frozen Pydantic models** | Enforces immutability of raw observations |
| **DataSource provenance** | Test data can never be confused with real data |
| **metadata dict** | Provider-specific extensions without schema migration |
| **Report-only validation** | Raw data is never silently modified |
| **Date-based partitioning** | Balances query performance with file simplicity |
| **Abstract interfaces** | Collector and storage are broker/backend-agnostic |

---

## Data Pipeline

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Data Source     │────▶│   Collector      │────▶│   Storage        │
│ (Future: broker)  │     │ (AbstractCollector)│    │ (ParquetStorage) │
│ (Now: mock only)  │     │                  │     │                  │
└──────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                           │
                                                           ▼
                          ┌──────────────────┐     ┌──────────────────┐
                          │   Validation     │◀────│   Read/Query     │
                          │ (Report-only)    │     │                  │
                          └──────────────────┘     └────────┬─────────┘
                                                           │
                                                           ▼
                                                  ┌──────────────────┐
                                                  │   Aggregation    │
                                                  │ (Tick → OHLC)    │
                                                  └──────────────────┘
```

### Data Provenance

Every observation in Project GOAT carries an explicit `DataSource` tag:

| Source | Meaning |
|--------|---------|
| `LIVE` | Real-time data from an external market feed |
| `HISTORICAL_IMPORT` | Imported historical dataset |
| `TEST` | Generated mock/test data — **NOT real market data** |

### Validation Rules

The validation engine detects (but never repairs):

- Missing values in required fields
- Duplicate ticks/candles
- Non-monotonic timestamps
- Non-positive prices
- Suspicious timestamp gaps (> 5× median interval)
- OHLC inconsistencies (high < open, low > close, high < low, etc.)

---

## Running Tests

```bash
# Run the full test suite
pytest -v

# Run with coverage report
pytest -v --cov=goat --cov-report=term-missing

# Run a specific test module
pytest tests/test_schemas.py -v
```

---

## Configuration

Settings are loaded from environment variables with the `GOAT_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `GOAT_DATA_DIR` | `data` | Root data directory |
| `GOAT_RAW_DATA_DIR` | `data/raw` | Raw tick storage |
| `GOAT_PROCESSED_DATA_DIR` | `data/processed` | Processed candle storage |
| `GOAT_LOG_LEVEL` | `INFO` | Logging verbosity |

**⚠️ Never commit `.env` files or real credentials.** Use `.env.example` as a template.

---

## Current Limitations

1. **No real data connector** — Only `MockMarketDataCollector` (test data) is available.
   A real external market-data connector will be implemented in a later milestone.
2. **M1 only** — Candle aggregation currently supports only 1-minute candles.
   The architecture supports trivial extension to M5, M15, H1, H4, D1.
3. **No research conversion** — Decimal→float64 conversion for vectorized research
   computation is not yet implemented as a formal utility.
4. **No SQLite metadata store** — Lightweight metadata/configuration database
   is planned but not yet implemented.
5. **Single-process** — No distributed processing or parallel I/O yet.

---

## Quantitative Principles

1. **Raw observations are immutable.** Processed datasets are always derived
   from raw data so research can be reproduced.
2. **Validation is report-only.** The system never silently repairs, drops,
   reorders, interpolates, or mutates raw data.
3. **Provenance is explicit.** Every data point carries a source tag so test
   data can never contaminate research.
4. **Reproducibility first.** Seeded fixtures, deterministic aggregation,
   and append-only storage support reproducible research.

---

## License

*To be determined.*
