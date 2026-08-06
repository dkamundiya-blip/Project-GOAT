# Project GOAT v1.0 — Dashboard Backend API & Real-Time Gateway Architecture Specification

**Subsystem**: Step 1.1 Dashboard Backend Server (`goat.dashboard`)  
**Target Release**: Project GOAT Version 1.0  
**Status**: CERTIFIED & VERIFIED  

---

## 1. Executive Summary & Overview

The **Dashboard Backend Server** (`goat.dashboard`) serves as the high-performance REST API and real-time WebSocket telemetry gateway connecting the React 18 frontend control room (`apps/dashboard/`) to Project GOAT's frozen Version 0.9.1 quantitative research foundation.

### Strict Architectural Invariants
1. **Frozen Backend Protection**: No frozen Version 0.8 through Version 0.9.1 package, schema, or model is modified.
2. **Read-Only Database Adapters**: All SQLite data queries occur through read-only, thread-safe query adapters (`DashboardReadOnlyRepositoryAdapter`).
3. **Deterministic Identity**: All domain models carry immutable SHA-256 canonical fingerprints with standardized prefixes (`DSH_`, `DTR_`, `DWS_`, `DAP_`).
4. **Zero Brokering/Signals**: The backend server purely visualizes system telemetry, research hypotheses, evidence, and governance decisions.

---

## 2. Subsystem Package Topology

```
goat/dashboard/
├── __init__.py                # Public API exports
├── server.py                  # MasterDashboardServer facade
├── core/
│   ├── __init__.py
│   ├── canonical.py           # Canonical JSON & SHA-256 ID prefix generators
│   ├── enums.py               # Enums (ServerStatus, TelemetryChannel, StreamState)
│   └── models.py              # Immutable Pydantic V2 domain models
├── api/
│   ├── __init__.py
│   ├── rest.py                # REST API request handlers
│   └── router.py              # FastAPI APIRouter builder
├── websocket/
│   ├── __init__.py
│   ├── engine.py              # Telemetry broadcast engine
│   └── manager.py             # Active WebSocket connection manager
├── telemetry/
│   ├── __init__.py
│   └── collector.py           # System resource telemetry collector
├── persistence/
│   ├── __init__.py
│   └── sqlite.py              # Read-only repository adapters
└── reporting/
    ├── __init__.py
    └── reports.py             # Session & health markdown/JSON report generators
```

---

## 3. Core Domain Models & SHA-256 Identifiers

| Model Name | Prefix | Description | Immutable |
| :--- | :---: | :--- | :---: |
| **`DashboardSession`** | `DSH_` | Session lifecycle state & host configuration | Yes |
| **`TelemetryFrame`** | `DTR_` | Real-time telemetry event stream payload | Yes |
| **`WSConnectionState`** | `DWS_` | Active WebSocket client connection metadata | Yes |
| **`APIResponsePayload`** | `DAP_` | Canonical API response container | Yes |
| **`DashboardHealthStatus`** | — | System resource, uptime, and database health | Yes |

---

## 4. API & Real-Time Endpoint Matrix

- `GET /health` — Returns system resource utilization and health status (`DashboardHealthStatus`).
- `GET /api/v1/summary` — Returns scientific pipeline high-level aggregate metrics (`APIResponsePayload`).
- `GET /api/v1/hypotheses` — Returns active research hypotheses registry items (`APIResponsePayload`).
- `GET /api/v1/governance` — Returns binding edge promotion and retirement decision records (`APIResponsePayload`).
- `GET /api/v1/symbols` — Returns real-time synthetic index market stream status (`APIResponsePayload`).
- `WS /ws` — Real-time WebSocket channel streaming system telemetry and pipeline events (`TelemetryFrame`).
