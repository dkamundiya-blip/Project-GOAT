# Broker Abstraction Framework Architecture (Step 7.2)

**Subsystem**: Step 7.2 — Broker Abstraction Framework (`goat.brokers`)  
**Phase**: Phase VII (Production Infrastructure Layer)  
**Status**: COMPLETE & CERTIFIED  

---

## 1. Overview

The Broker Abstraction Framework (`goat.brokers`) defines a broker-independent contract between Project GOAT's production infrastructure layer and all future broker implementations (Deriv Synthetic Indices, Weltrade, MT5, Forex, Commodities, Crypto, Stocks).

It guarantees that GOAT's scientific engine and core infrastructure **never communicate directly with broker-specific APIs or protocols**. The framework serves as the MANDATORY single gateway for broker communications while containing **zero live network execution logic**.

---

## 2. Adapter Pattern & Contract Specification

```
+-------------------------------------------------------------+
|                Project GOAT Production Layer                |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|              AbstractBrokerAdapter Interface                |
|  - connect() / disconnect() / heartbeat()                   |
|  - get_account()                                            |
|  - subscribe_market_data() / unsubscribe_market_data()     |
|  - submit_order_intent() / cancel_order() / modify_order()  |
|  - get_positions() / get_open_orders()                      |
|  - health() / capabilities()                                |
+-------------------------------------------------------------+
            │                        │                       │
            ▼                        ▼                       ▼
 +--------------------+    +--------------------+    +--------------------+
 | DerivAdapter       |    | WeltradeAdapter    |    | MT5Adapter         |
 | (Step 7.3 Target)  |    | (Future Step)      |    | (Future Step)      |
 +--------------------+    +--------------------+    +--------------------+
```

---

## 3. Subpackage Inventory

| Subpackage | Responsibility | Key Classes |
| :--- | :--- | :--- |
| `goat.brokers.core` | Enums, SHA-256 IDs, domain models | `BrokerProfile`, `BrokerConnection`, `BrokerAccount`, `BrokerOrderIntent` |
| `goat.brokers.contracts` | Mandatory interface & capability registry | `AbstractBrokerAdapter`, `BrokerCapabilityRegistry` |
| `goat.brokers.session` | Connection lifecycle & telemetry tracking | `BrokerSessionEngine` |
| `goat.brokers.orders` | Deterministic order intent structural validation | `BrokerOrderIntentEngine`, `IntentValidationResult` |
| `goat.brokers.account` | Account balance & margin calculation proxies | `BrokerAccountEngine` |
| `goat.brokers.errors` | Deterministic broker error hierarchy | `BrokerError`, `ConnectionError`, `OrderValidationError`, etc. |
| `goat.brokers.persistence` | SQLite WAL storage with foreign keys | `init_brokers_db`, `BrokerRepository`, `AccountRepository`, etc. |
| `goat.brokers.reporting` | Executive & component report models | `BrokerExecutiveReport`, `BrokerProfileReport`, etc. |

---

## 4. Deterministic Identifiers & Prefixes

All models use prefix-based deterministic SHA-256 hashes:
- **`BRK_<HEX16>`**: BrokerProfile ID (`compute_broker_profile_id`)
- **`BCN_<HEX16>`**: BrokerConnection ID (`compute_connection_id`)
- **`BAC_<HEX16>`**: BrokerAccount ID (`compute_account_id`)
- **`BOI_<HEX16>`**: BrokerOrderIntent ID (`compute_order_intent_id`)
- **`BRE_<HEX16>`**: BrokerError ID (`compute_error_id`)
- **`BRR_<HEX16>`**: BrokerReport ID (`compute_report_id`)

---

## 5. Error Framework Hierarchy

```
BrokerError (Base)
├── ConnectionError (ERR_CONNECTION_FAILED)
├── AuthenticationError (ERR_AUTHENTICATION_FAILED)
├── PermissionError (ERR_PERMISSION_DENIED)
├── RateLimitError (ERR_RATE_LIMIT_EXCEEDED)
├── OrderValidationError (ERR_ORDER_VALIDATION_FAILED)
├── BrokerUnavailableError (ERR_BROKER_UNAVAILABLE)
├── TimeoutError (ERR_TIMEOUT)
└── ReplayError (ERR_REPLAY_FAILED)
```

Each error produces a deterministic `BrokerErrorModel` (`BRE_<HEX16>`) with `code`, `category`, `message`, `explanation`, and `canonical_hash`.

---

## 6. Persistence & SQLite Schema

Persistence is managed via SQLite tables enforcing `PRAGMA foreign_keys = ON;` and WAL mode:
- `broker_profiles`
- `broker_connections`
- `broker_accounts`
- `broker_order_intents`
- `broker_errors`
- `broker_reports`

Initialized via `init_brokers_db(db_path)`. Supports 100% round-trip persistence and deterministic serialization.

---

## 7. Future Broker Integration

Future broker adapters (such as MT5 or Weltrade) simply implement `AbstractBrokerAdapter` and register their capabilities with `BrokerCapabilityRegistry`. ZERO architectural changes to GOAT core infrastructure are required.
