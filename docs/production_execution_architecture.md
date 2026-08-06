# PROJECT GOAT — Production Execution Engine Architecture Specification

**Subsystem**: Step 7.4 Production Execution Engine (`goat.execution`)  
**Phase**: Phase VII (Production Infrastructure Layer)  
**Status**: CERTIFIED & FROZEN  

---

## 1. Executive Summary & Overview

The **Production Execution Engine** (`goat.execution`) transforms qualified, risk-approved scientific trading signals into canonical execution requests. It acts as the final gatekeeper before order submission to broker adapters.

### Architectural Non-Bypass Invariants
Execution MUST NEVER bypass:
1. **Qualification Engine**: Un-qualified or expired signals are rejected immediately.
2. **Risk Engine**: Position sizing and capital allocation approvals are strictly verified.
3. **Market State Intelligence Engine**: Closed or degraded market states halt execution.
4. **Broker Abstraction Framework**: Dispatch occurs **ONLY** through `AbstractBrokerAdapter` implementations (e.g. `DerivAdapter`). Direct network/broker API calls are strictly forbidden.

---

## 2. Package Architecture

```
goat/execution/
├── __init__.py                # Top-level public API exports
├── core/                      # Enums, SHA-256 IDs, domain models
│   ├── __init__.py
│   ├── canonical.py
│   ├── enums.py
│   └── models.py
├── intents/                   # ExecutionIntent creation engine
│   ├── __init__.py
│   └── engine.py
├── validation/                # 8-rule pre-dispatch validation engine
│   ├── __init__.py
│   └── engine.py
├── dispatch/                  # AbstractBrokerAdapter dispatch engine
│   ├── __init__.py
│   └── engine.py
├── lifecycle/                 # State machine transition engine
│   ├── __init__.py
│   └── engine.py
├── idempotency/               # Single-execution lock registry engine
│   ├── __init__.py
│   └── engine.py
├── persistence/               # SQLite WAL repositories with foreign key integrity
│   ├── __init__.py
│   └── repository.py
└── reporting/                 # Subsystem markdown & canonical JSON reports
    ├── __init__.py
    └── reports.py
```

---

## 3. Core Domain Models & SHA-256 Identifiers

All models are immutable Pydantic V2 classes (`frozen=True`, `extra="forbid"`):

| Model | ID Format Prefix | Description |
| :--- | :---: | :--- |
| **`ExecutionIntent`** | `EXI_<HEX16>` | Canonical execution request container. |
| **`ExecutionRequest`** | `EXR_<HEX16>` | Dispatched broker order request record. |
| **`ExecutionDecision`** | `EXD_<HEX16>` | Pre-dispatch validation rule evaluation result. |
| **`ExecutionLifecycle`** | `EXL_<HEX16>` | State transition log entry. |
| **`ExecutionAudit`** | `EXA_<HEX16>` | Audit trail log entry. |
| **`ExecutionFailure`** | `EXF_<HEX16>` | Failure event record. |
| **`ExecutionSummary`** | `EXS_<HEX16>` | Aggregated execution statistics. |

---

## 4. Execution Pipeline & State Machine

```
Scientific Signal -> Qualification -> Risk Engine -> ExecutionIntent (CREATED)
                                                           │
                                                           ▼
                                                ValidationEngine (VALIDATED)
                                                           │
                                                           ▼
                                                IdempotencyEngine (READY)
                                                           │
                                                           ▼
                                              DispatchEngine (DISPATCHED)
                                                           │
                                                           ▼
                                               Broker Adapter (ACKNOWLEDGED)
                                                           │
                                                           ▼
                                                 Fill / Reject (FILLED / REJECTED)
```

---

## 5. Pre-Dispatch Validation Rules (8-Rule Gate)

`ExecutionValidationEngine` evaluates 8 mandatory pre-execution rules:
1. **Duplicate Check**: Verifies intent has not already been processed.
2. **Qualification Check**: Verifies signal qualification state.
3. **Risk Engine Check**: Verifies position sizing decision approval.
4. **Capital Allocation Check**: Verifies available unencumbered capital.
5. **Market State Check**: Verifies market status for target symbol.
6. **Broker Session Check**: Verifies connection status of target broker.
7. **Signal Freshness Check**: Verifies signal expiry timestamp.
8. **Volume Check**: Verifies positive volume quantity bounds.

---

## 6. Idempotency & Single-Execution Guarantees

`ExecutionIdempotencyEngine` maintains in-memory and persistent lock registries to enforce:
- **1 ExecutionIntent -> 1 Execution Path**
- Protection against duplicate retries and duplicate acknowledgements.

---

## 7. SQLite Persistence

Managed via SQLite in WAL mode with foreign key enforcement (`PRAGMA foreign_keys = ON;`):
- `ExecutionIntentRepository` -> `execution_intents`
- `ExecutionDecisionRepository` -> `execution_decisions`
- `ExecutionLifecycleRepository` -> `execution_lifecycles`
- `ExecutionAuditRepository` -> `execution_audits`
- `ExecutionFailureRepository` -> `execution_failures`
- `ExecutionReportRepository` -> `execution_reports`
