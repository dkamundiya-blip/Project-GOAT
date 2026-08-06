# Project GOAT v0.8 — Trade Lifecycle Management Architecture

## 1. Subsystem Purpose

The **Trade Lifecycle Management Engine** (`goat.lifecycle`) tracks, validates, synchronizes, and audits the full state machine lifecycle of every trade after it has been created by the Production Execution Engine.

It operates downstream of Steps 7.3 (Broker Production Adapter), 7.4 (Production Execution Engine), and 7.5 (Portfolio Engine):

```
Execution Engine (Step 7.4)
        │
        ▼
Trade Lifecycle Engine (Step 7.6) ──► TradeTrackingEngine / TradeEventEngine / TradeReconciliationEngine
        │
        ▼
Portfolio & Analytics (Step 7.5 & Phase VIII)
```

The Trade Lifecycle Engine **MUST NEVER**:
- Generate signals or trading decisions
- Perform market analysis or technical indicator calculations
- Calculate entry, stop-loss (SL), or take-profit (TP) levels
- Execute risk management policies or size positions
- Perform broker networking or socket communication directly

---

## 2. Package Architecture

```
goat/lifecycle/
├── __init__.py                # Top-level public API exports (__all__)
├── engine.py                  # Master TradeLifecycleEngine coordinator
├── core/                      # Enums, SHA-256 ID generators, Pydantic V2 models
│   ├── __init__.py
│   ├── canonical.py
│   ├── enums.py
│   └── models.py
├── tracking/                  # TradeTrackingEngine (State machine tracker)
│   ├── __init__.py
│   └── engine.py
├── events/                    # TradeEventEngine (Append-only event stream generator)
│   ├── __init__.py
│   └── engine.py
├── reconciliation/            # TradeReconciliationEngine (Broker vs Portfolio vs Lifecycle 3-way audit)
│   ├── __init__.py
│   └── engine.py
├── persistence/               # SQLite WAL repositories
│   ├── __init__.py
│   └── repository.py
└── reporting/                 # Markdown & Canonical JSON reporting engine
    ├── __init__.py
    └── reports.py
```

---

## 3. Lifecycle State Machine & Transition Rules

The subsystem enforces a deterministic finite state machine (`TradeState`). Any illegal transition raises an explicit `ValueError` (no silent fallback or recovery).

### Allowed States
- `CREATED`: Initial intent created.
- `SUBMITTED`: Dispatched to broker adapter.
- `ACKNOWLEDGED`: Received broker acknowledgment.
- `PARTIALLY_FILLED`: Received partial lot fill.
- `FILLED`: 100% filled lot.
- `OPEN`: Active position tracking.
- `MODIFIED`: General parameter update.
- `SL_UPDATED`: Stop loss level modified.
- `TP_UPDATED`: Take profit level modified.
- `TRAILING_UPDATED`: Trailing stop distance modified.
- `PARTIALLY_CLOSED`: Partial quantity closed.
- `CLOSED`: Fully closed position (Terminal).
- `CANCELLED`: Cancelled prior to fill (Terminal).
- `REJECTED`: Rejected by broker (Terminal).
- `FAILED`: System/Execution failure (Terminal).

### Valid State Transition Matrix

| From State | Allowed Destination States |
|---|---|
| `CREATED` | `SUBMITTED`, `CANCELLED`, `REJECTED`, `FAILED` |
| `SUBMITTED` | `ACKNOWLEDGED`, `PARTIALLY_FILLED`, `FILLED`, `REJECTED`, `CANCELLED`, `FAILED` |
| `ACKNOWLEDGED` | `PARTIALLY_FILLED`, `FILLED`, `OPEN`, `REJECTED`, `CANCELLED`, `FAILED` |
| `PARTIALLY_FILLED` | `PARTIALLY_FILLED`, `FILLED`, `OPEN`, `CANCELLED`, `FAILED` |
| `FILLED` | `OPEN`, `PARTIALLY_CLOSED`, `CLOSED`, `FAILED` |
| `OPEN` | `MODIFIED`, `SL_UPDATED`, `TP_UPDATED`, `TRAILING_UPDATED`, `PARTIALLY_CLOSED`, `CLOSED`, `FAILED` |
| `MODIFIED` | `OPEN`, `SL_UPDATED`, `TP_UPDATED`, `TRAILING_UPDATED`, `PARTIALLY_CLOSED`, `CLOSED`, `FAILED` |
| `SL_UPDATED` | `OPEN`, `MODIFIED`, `SL_UPDATED`, `TP_UPDATED`, `TRAILING_UPDATED`, `PARTIALLY_CLOSED`, `CLOSED`, `FAILED` |
| `TP_UPDATED` | `OPEN`, `MODIFIED`, `SL_UPDATED`, `TP_UPDATED`, `TRAILING_UPDATED`, `PARTIALLY_CLOSED`, `CLOSED`, `FAILED` |
| `TRAILING_UPDATED` | `OPEN`, `MODIFIED`, `SL_UPDATED`, `TP_UPDATED`, `TRAILING_UPDATED`, `PARTIALLY_CLOSED`, `CLOSED`, `FAILED` |
| `PARTIALLY_CLOSED` | `OPEN`, `MODIFIED`, `SL_UPDATED`, `TP_UPDATED`, `TRAILING_UPDATED`, `PARTIALLY_CLOSED`, `CLOSED`, `FAILED` |
| `CLOSED` / `CANCELLED` / `REJECTED` / `FAILED` | *Terminal (No outgoing transitions permitted)* |

---

## 4. Deterministic Hashing & Identifiers

All models implement SHA-256 canonical hashing across payload attributes to generate deterministic IDs:

| Prefix | Entity | Example ID |
|---|---|---|
| `TRL_` | TradeLifecycle | `TRL_1A2B3C4D5E6F7890` |
| `TST_` | TradeStateRecord | `TST_2B3C4D5E6F7890A1` |
| `TEV_` | TradeEvent | `TEV_3C4D5E6F7890A1B2` |
| `BEX_` | BrokerExecution | `BEX_4D5E6F7890A1B2C3` |
| `PSP_` | PositionSnapshot | `PSP_5E6F7890A1B2C3D4` |
| `LTR_` | LifecycleTransition | `LTR_6F7890A1B2C3D4E5` |
| `LAD_` | LifecycleAudit | `LAD_7890A1B2C3D4E5F6` |
| `LSM_` | LifecycleSummary | `LSM_890A1B2C3D4E5F67` |

---

## 5. Event Model & Replay Support

`TradeEventEngine` records immutable, append-only, replayable event streams across 15 event types:
1. `ORDER_SUBMITTED`
2. `BROKER_ACCEPTED`
3. `BROKER_REJECTED`
4. `PARTIAL_FILL`
5. `COMPLETE_FILL`
6. `POSITION_OPENED`
7. `POSITION_MODIFIED`
8. `STOP_LOSS_UPDATED`
9. `TAKE_PROFIT_UPDATED`
10. `TRAILING_STOP_UPDATED`
11. `PARTIAL_CLOSE`
12. `COMPLETE_CLOSE`
13. `EXECUTION_FAILURE`
14. `MANUAL_CLOSE`
15. `AUTOMATIC_CLOSE`

Event streams are replayable sequentially to reconstruct the exact state of any trade lifecycle at any historical timestamp.

---

## 6. Reconciliation Engine

`TradeReconciliationEngine` performs 3-way audit across **Broker Executions**, **Portfolio Positions**, and **Trade Lifecycles** to detect:
- `ORPHAN_EXECUTION`: Unlinked broker execution fill.
- `ORPHAN_POSITION`: Unlinked active portfolio position.
- `MISSING_FILL`: Acknowledged intent with no execution fill.
- `DUPLICATE_FILL`: Multiple executions registered for single intent.
- `VOLUME_MISMATCH`: Fill volume != position volume != lifecycle volume.
- `EXECUTION_MISMATCH`: Price/symbol discrepancy.
- `MISSING_CLOSE`: Position closed on broker/portfolio but open on lifecycle.
- `INCONSISTENT_LIFECYCLE`: Active lifecycle with missing portfolio position.

---

## 7. SQLite Persistence & Integration

- **WAL Mode**: Enforces `PRAGMA journal_mode = WAL;` and `PRAGMA foreign_keys = ON;`.
- **Repositories**: `TradeLifecycleRepository`, `TradeEventRepository`, `BrokerExecutionRepository`, `LifecycleAuditRepository`, `LifecycleReportRepository`.
- **Integration**:
  - Consumes `DerivExecutionResponse` / `BrokerOrderIntent` from Step 7.3.
  - Consumes `ExecutionIntent` / `ExecutionDecision` from Step 7.4.
  - Consumes `Position` / `PortfolioSnapshot` from Step 7.5.
