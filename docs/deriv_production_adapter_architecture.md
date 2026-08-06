# PROJECT GOAT — Deriv Production Adapter Architecture Specification

**Subsystem**: Step 7.3 Deriv Production Adapter (`goat.brokers.deriv`)  
**Phase**: Phase VII (Production Infrastructure Layer)  
**Status**: CERTIFIED & FROZEN  
**Target Reference**: Deriv WebSocket Gateway Protocol (v3)  

---

## 1. Executive Summary & Overview

The **Deriv Production Adapter** (`goat.brokers.deriv`) implements the concrete `AbstractBrokerAdapter` contract defined in Step 7.2. It acts as an isolated, bi-directional gateway translation boundary between Project GOAT's broker-independent infrastructure and the Deriv WebSocket API specifications.

### Strict Architectural Invariants
1. **Payload Isolation**: Raw Deriv JSON payloads, WebSocket subscription strings, app IDs, and authorization tokens **NEVER** escape past the `goat.brokers.deriv` boundary.
2. **Canonical Model Mapping**: All incoming Deriv ticks, candles, balance updates, and contract executions are immediately converted into Step 7.0/7.2 canonical models (`MarketTick`, `MarketCandle`, `BrokerAccount`, `BrokerOrderIntent`).
3. **No Direct Brokering**: Zero GOAT subsystem outside `goat.brokers.deriv` is aware of Deriv protocol specifications.
4. **Deterministic Hashes**: All domain models carry immutable SHA-256 canonical fingerprints with standardized prefixes (`DRS_`, `DAT_`, `DAC_`, `DMS_`, `DOP_`, `DER_`, `DHB_`, `DRR_`).

---

## 2. Package Architecture

```
goat/brokers/deriv/
├── __init__.py                # Top-level public API exports
├── adapter.py                 # DerivAdapter implementing AbstractBrokerAdapter
├── core/                      # Enums, SHA-256 IDs, domain models
│   ├── __init__.py
│   ├── canonical.py
│   ├── enums.py
│   └── models.py
├── translation/               # Bidirectional Deriv JSON <-> GOAT Translation Engine
│   ├── __init__.py
│   └── engine.py
├── auth/                      # Authentication & token hashing engine
│   ├── __init__.py
│   └── engine.py
├── session/                   # Deriv session lifecycle & ping/pong telemetry
│   ├── __init__.py
│   └── engine.py
├── marketdata/                # Synthetic Indices stream subscription engine
│   ├── __init__.py
│   └── engine.py
├── accounts/                  # Balance & equity translation engine
│   ├── __init__.py
│   └── engine.py
├── orders/                    # Deriv contract proposal & purchase order engine
│   ├── __init__.py
│   └── engine.py
├── persistence/               # SQLite WAL repositories with foreign key integrity
│   ├── __init__.py
│   └── repository.py
└── reporting/                 # Executive, session, auth, & order reports
    ├── __init__.py
    └── reports.py
```

---

## 3. Core Models & Deterministic SHA-256 Identifiers

All models are immutable Pydantic V2 classes (`frozen=True`, `extra="forbid"`):

| Domain Model | ID Format Prefix | Description |
| :--- | :---: | :--- |
| **`DerivSession`** | `DRS_<HEX16>` | Deriv WebSocket session state and latency telemetry. |
| **`DerivAuthentication`** | `DAT_<HEX16>` | Authorization state storing SHA-256 token hash (never raw tokens). |
| **`DerivAccountSnapshot`** | `DAC_<HEX16>` | Balance, equity, and margin snapshot. |
| **`DerivMarketSubscription`**| `DMS_<HEX16>` | Market data stream subscription state. |
| **`DerivOrderPayload`** | `DOP_<HEX16>` | Translated Deriv contract buy request structure. |
| **`DerivExecutionResponse`** | `DER_<HEX16>` | Purchase execution fill response. |
| **`DerivHeartbeat`** | `DHB_<HEX16>` | Ping/pong latency measurement payload. |

---

## 4. Translation Layer (`DerivTranslationEngine`)

The `DerivTranslationEngine` isolates all Deriv JSON key names (`"proposal"`, `"ticks"`, `"ohlc"`, `"buy"`, `"balance"`) behind clean Python methods:
- `translate_order_intent_to_deriv_payload()`: Translates `BrokerOrderIntent` -> `DerivOrderPayload` & Deriv request JSON.
- `translate_deriv_execution_response()`: Translates raw Deriv purchase response -> `DerivExecutionResponse` & canonical execution dict.
- `translate_deriv_tick_to_market_tick()`: Translates Deriv tick JSON -> `MarketTick`.
- `translate_deriv_candle_to_market_candle()`: Translates Deriv ohlc JSON -> `MarketCandle`.
- `translate_deriv_balance_to_account()`: Translates Deriv balance JSON -> `DerivAccountSnapshot` & `BrokerAccount`.

---

## 5. Supported Symbols Matrix (Deriv Synthetic Indices)

Step 7.3 supports all 12 Deriv Synthetic Index symbols:
`R_10`, `R_25`, `R_50`, `R_75`, `R_100`, `BOOM500`, `BOOM1000`, `CRASH500`, `CRASH1000`, `JUMP10`, `JUMP25`, `STEP`.

---

## 6. SQLite Persistence & Replay Compatibility

Persistence is managed via SQLite in WAL mode with foreign key enforcement (`PRAGMA foreign_keys = ON;`):
- `SessionRepository` -> `deriv_sessions`
- `AuthenticationRepository` -> `deriv_authentications`
- `MarketSubscriptionRepository` -> `deriv_subscriptions`
- `OrderRepository` -> `deriv_order_payloads`
- `ExecutionRepository` -> `deriv_executions`
- `HeartbeatRepository` -> `deriv_heartbeats`
- `ReportRepository` -> `deriv_reports`

---

## 7. Future Broker Compatibility (Weltrade, MT5, FIX)

The separation between `goat.brokers` (Step 7.2 abstraction) and `goat.brokers.deriv` (Step 7.3 adapter) ensures that adding Stage 2 (Weltrade) or Stage 3 (MT5, FIX, Crypto, Stocks) adapters requires creating a new parallel directory (e.g., `goat/brokers/weltrade/`) implementing `AbstractBrokerAdapter` without modifying a single line of GOAT core logic.
