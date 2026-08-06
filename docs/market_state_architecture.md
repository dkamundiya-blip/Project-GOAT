# Market State Intelligence Engine Architecture (Step 7.1)

**Subsystem**: Step 7.1 — Market State Intelligence (`goat.marketstate`)  
**Phase**: Phase VII (Production Infrastructure Layer)  
**Status**: COMPLETE & CERTIFIED  

---

## 1. Overview

The Market State Intelligence Engine (`goat.marketstate`) is responsible for describing the **CURRENT** observable market state. It evaluates normalized Step 7.0 market data (`MarketTick`, `MarketCandle`, `MarketStreamState`, `MarketGap`, `ReplaySnapshot`) and classifies trend direction, price structure, volatility, liquidity, activity, spread quality, and stream quality.

### Strict Non-Goals
The Market State Intelligence Engine **NEVER**:
- Predicts future price movement
- Forecasts trend direction
- Generates trading signals
- Ranks market opportunities
- Recommends buy/sell entries, stop loss, or take profit targets
- Executes orders or communicates directly with brokers

---

## 2. Architecture & Component Interaction

```
[ Normalized Market Data from Step 7.0 ]
                    │
                    ▼
     +------------------------------+
     |   MarketStateEngine (Coord)  |
     +------------------------------+
         /         |        \        \
        v          v         v        v
 +------------+ +------------+ +------------+ +------------+
 | Volatility | | Liquidity  | | Structure  | |  Quality   |
 | Engine     | | Engine     | | Engine     | | Engine     |
 | (VOL_)     | | (LIQ_)     | | (STR_)     | | (MQA_)     |
 +------------+ +------------+ +------------+ +------------+
        \          |         /        /
         v         v        v        v
     +------------------------------+
     | MarketClassificationEngine   |
     +------------------------------+
                    │
                    ▼ Emits
     +------------------------------+
     |     MarketState (MST_)       |
     +------------------------------+
                    │
                    ▼
     +------------------------------+
     | SQLite Repositories & WAL    |
     +------------------------------+
```

---

## 3. Subpackage Inventory

| Package Path | Core Responsibility | Key Class Export |
| :--- | :--- | :--- |
| `goat.marketstate.core` | Core models, SHA-256 IDs, enums | `MarketState`, `VolatilityAssessment`, `LiquidityAssessment`, `StructureAssessment`, `MarketQualityAssessment` |
| `goat.marketstate.volatility` | Realized volatility & price intensity | `VolatilityAssessmentEngine` |
| `goat.marketstate.liquidity` | Spread quality & activity tracking | `LiquidityAssessmentEngine` |
| `goat.marketstate.structure` | Price action & trend structure | `StructureAssessmentEngine` |
| `goat.marketstate.quality` | Stream health & replay quality | `MarketQualityEngine` |
| `goat.marketstate.classification` | State synthesis & explanation generation | `MarketClassificationEngine` |
| `goat.marketstate.persistence` | SQLite persistence with foreign keys | `init_marketstate_db`, `MarketStateRepository`, etc. |
| `goat.marketstate.reporting` | Executive & component report models | `MarketStateExecutiveReport`, `MarketStateReport`, etc. |
| `goat.marketstate.engine` | Primary coordinator | `MarketStateEngine` |

---

## 4. Deterministic Identifiers & Prefixes

All entities use prefix-based deterministic SHA-256 hashes:
- **`MST_<HEX16>`**: MarketState ID (`compute_market_state_id`)
- **`VOL_<HEX16>`**: VolatilityAssessment ID (`compute_volatility_id`)
- **`LIQ_<HEX16>`**: LiquidityAssessment ID (`compute_liquidity_id`)
- **`STR_<HEX16>`**: StructureAssessment ID (`compute_structure_id`)
- **`MQA_<HEX16>`**: MarketQualityAssessment ID (`compute_quality_id`)
- **`MSR_<HEX16>`**: MarketStateReport ID (`compute_report_id`)

---

## 5. Classification Logic & Enums

1. **`TrendState`**: `STRONG_UPTREND`, `UPTREND`, `SIDEWAYS`, `DOWNTREND`, `STRONG_DOWNTREND`, `UNKNOWN`
2. **`VolatilityState`**: `VERY_LOW`, `LOW`, `NORMAL`, `HIGH`, `EXTREME`
3. **`LiquidityState`**: `VERY_LOW`, `LOW`, `NORMAL`, `HIGH`
4. **`SpreadState`**: `TIGHT`, `NORMAL`, `WIDE`, `EXTREME`
5. **`ActivityState`**: `QUIET`, `NORMAL`, `ACTIVE`, `VERY_ACTIVE`
6. **`StructureState`**: `BULLISH`, `BEARISH`, `RANGING`, `TRANSITIONAL`, `UNKNOWN`
7. **`QualityState`**: `EXCELLENT`, `GOOD`, `ACCEPTABLE`, `POOR`, `INVALID`

---

## 6. Replay & Persistence

Persistence is managed via SQLite tables enforcing `PRAGMA foreign_keys = ON;` and WAL mode:
- `volatility_assessments`
- `liquidity_assessments`
- `structure_assessments`
- `quality_assessments`
- `market_states`
- `market_state_reports`

Initialised via `init_marketstate_db(db_path)`. Supports 100% round-trip persistence and deterministic replay compatibility.

---

## 7. Future Broker Compatibility

Because `goat.marketstate` consumes only normalized Step 7.0 objects (`MarketTick`, `MarketCandle`, `MarketStreamState`), it is 100% decoupled from underlying broker transport layers. When new adapters (Weltrade, MT5, FIX Protocol) are added in future steps, `goat.marketstate` will process them without modification.
