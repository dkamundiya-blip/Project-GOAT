# Project GOAT v0.8 — Portfolio & Position Management Architecture

## 1. Subsystem Overview

The **Portfolio & Position Management Engine** (`goat.portfolio`) maintains Project GOAT's canonical financial portfolio state. It operates downstream in the core execution pipeline:

```
Execution Engine (Step 7.4)
        │
        ▼
Portfolio Engine (Step 7.5) ──► Position Engine / Exposure Engine / Account Engine / Performance Engine
        │
        ▼
Trade Lifecycle & Analytics (Step 8.x)
```

The Portfolio subsystem is strictly isolated and **consumes ONLY**:
1. `ExecutionResults` (or execution fill intents/events)
2. `BrokerAccount` state telemetry
3. `MarketState` classification
4. `LiveMarketData` stream updates

It **NEVER**:
- Generates trading signals or alpha logic
- Predicts prices or market direction
- Executes trades or dispatches orders directly
- Connects directly to broker sockets or APIs

---

## 2. Core Domain Models

All models in `goat.portfolio.core.models` are immutable Pydantic structures enforcing `frozen=True` and `extra="forbid"`.

### Deterministic SHA-256 Identifiers
Every model instance derives a deterministic 16-character hexadecimal ID using SHA-256 canonical hashing across its core payload fields:

| Prefix | Domain Entity | ID Example |
|---|---|---|
| `PTF_` | Portfolio | `PTF_A1B2C3D4E5F67890` |
| `POS_` | Position | `POS_B2C3D4E5F67890A1` |
| `CLS_` | ClosedPosition | `CLS_C3D4E5F67890A1B2` |
| `PSN_` | PortfolioSnapshot | `PSN_D4E5F67890A1B2C3` |
| `EXP_` | ExposureSummary | `EXP_E5F67890A1B2C3D4` |
| `PER_` | PerformanceSummary | `PER_F67890A1B2C3D4E5` |
| `ACC_` | AccountSnapshot | `ACC_7890A1B2C3D4E5F6` |
| `PAD_` | PortfolioAudit | `PAD_890A1B2C3D4E5F67` |

---

## 3. Subsystem Architecture & Engines

### 3.1 Position Engine (`goat.portfolio.positions`)
- **Scale-In / Scaling**: Maintains volume-weighted average price (VWAP) when scaling into an existing position:
  $$\text{VWAP} = \frac{(\text{Entry}_{old} \times Q_{old}) + (\text{Price}_{new} \times Q_{new})}{Q_{old} + Q_{new}}$$
- **Full & Partial Closes**: Supports partial lot closures, generating an immutable `ClosedPosition` record for the closed portion and updating the remaining active `Position` quantity.
- **Mark-to-Market Valuation**: Updates `current_price` and computes `unrealized_pnl` for `LONG` and `SHORT` positions dynamically.

### 3.2 Account Engine (`goat.portfolio.account`)
Maintains real-time balance and leverage telemetry:
- $\text{Balance} = \text{Initial Balance} + \sum \text{Realized PnL}$
- $\text{Equity} = \text{Balance} + \sum \text{Unrealized PnL}$
- $\text{Used Margin} = \sum \text{Margin}_{position}$
- $\text{Free Margin} = \max(0, \text{Equity} - \text{Used Margin})$
- $\text{Margin Level \%} = \left(\frac{\text{Equity}}{\text{Used Margin}}\right) \times 100$
- $\text{Buying Power} = \text{Free Margin} \times \text{Leverage}$

### 3.3 Exposure Engine (`goat.portfolio.exposure`)
Calculates total and per-symbol portfolio risk:
- $\text{Long Exposure} = \sum \text{Mark Value}_{Long}$
- $\text{Short Exposure} = \sum \text{Mark Value}_{Short}$
- $\text{Net Exposure} = \text{Long Exposure} - \text{Short Exposure}$
- $\text{Gross Exposure} = \text{Long Exposure} + \text{Short Exposure}$
- $\text{Risk Concentration}_{sym} = \frac{\text{Gross Exposure}_{sym}}{\text{Gross Exposure}_{total}}$

### 3.4 Performance Engine (`goat.portfolio.performance`)
Tracks historical trading metrics:
- **Win Rate & Loss Rate**
- **Average & Largest Winner / Loser**
- **Profit Factor**: $\frac{\text{Gross Profit}}{\text{Gross Loss}}$
- **Expectancy**: $(\text{Win Rate} \times \text{Avg Winner}) - (\text{Loss Rate} \times |\text{Avg Loser}|)$
- **Running & Maximum Drawdown**: $\text{Drawdown} = \text{Peak Equity} - \text{Current Equity}$

### 3.5 Reconciliation Engine (`goat.portfolio.reconciliation`)
Audits external broker state against GOAT internal state to detect:
1. `MISSING_POSITION`: Present in broker but missing in GOAT (or vice versa).
2. `DUPLICATE_POSITION`: Multiple positions registered for single intent.
3. `QUANTITY_MISMATCH`: Volume discrepancy between broker and GOAT.
4. `PRICE_MISMATCH`: Price deviation exceeding configured tolerance.
5. `ACCOUNT_MISMATCH`: Cash balance or equity discrepancy.

---

## 4. SQLite Persistence & Replay

- **WAL Mode**: Enforces `PRAGMA journal_mode=WAL;` and `PRAGMA foreign_keys=ON;` for fast concurrent writes and strict relational integrity.
- **Repositories**: `PortfolioRepository`, `PositionRepository`, `ClosedPositionRepository`, `ExposureRepository`, `PerformanceRepository`, `AccountRepository`, `AuditRepository`, `ReportRepository`.
- **Deterministic Replay**: Audit logs (`PortfolioAudit`) and snapshot sequences allow complete deterministic replay and state reconstruction from any starting point.

---

## 5. Reporting Pipeline

Generates standardized Markdown and Canonical JSON reports via `PortfolioReportEngine`:
- `PortfolioReport`
- `PositionReport`
- `ExposureReport`
- `PerformanceReport`
- `AccountReport`
- `ReconciliationReport`
- `PortfolioExecutiveReport`

---

## 6. Future Broker Compatibility

The architecture relies strictly on the Step 7.2 `AbstractBrokerAdapter` abstractions (`BrokerAccount`, symbol strings, and canonical price updates). This guarantees full compatibility with future broker integration targets (e.g. Deriv, Interactive Brokers, Binance) without changing a single line of portfolio code.
