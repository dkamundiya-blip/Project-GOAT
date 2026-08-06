# Project GOAT v0.8 — Operational Monitoring & Reliability Engine Architecture

## 1. Subsystem Purpose

The **Operational Monitoring & Reliability Engine** (`goat.monitoring`) serves as the institutional "Control Room" for Project GOAT. It continuously monitors the health, integrity, performance, availability, and reliability of every production subsystem.

It operates strictly downstream of Steps 7.0 through 7.7:

```
Step 7.0 Live Market Data   ──┐
Step 7.1 Market State Intelligence ──┤
Step 7.2/7.3 Broker Adapter ──┼──► Monitoring Engine (Step 7.8) ──► Control Room Dashboard & Diagnostics
Step 7.4 Execution Engine   ──┤
Step 7.5 Portfolio Engine   ──┤
Step 7.6 Trade Lifecycle    ──┤
Step 7.7 Notification Platform ──┘
```

The Operational Monitoring Engine **MUST NEVER**:
- Generate or modify trading signals
- Modify executions or portfolio states
- Place orders or communicate directly with brokers
- Calculate entry or exit prices
- Perform automated recovery or mutations

It ONLY observes, validates, reports, alerts, and records.

---

## 2. Package Architecture

```
goat/monitoring/
├── __init__.py                # Top-level public API exports (__all__)
├── engine.py                  # Master MonitoringEngine coordinator
├── core/                      # Enums, SHA-256 ID generators, Pydantic V2 models
│   ├── __init__.py
│   ├── canonical.py
│   ├── enums.py
│   └── models.py
├── health/                    # SystemHealthEngine (Monitors 7 production subsystems)
│   ├── __init__.py
│   └── engine.py
├── watchdog/                  # WatchdogEngine (Heartbeat freshness & stale/dead component detection)
│   ├── __init__.py
│   └── engine.py
├── heartbeat/                 # HeartbeatEngine (Heartbeat generation, sequence, verification, replay)
│   ├── __init__.py
│   └── engine.py
├── telemetry/                 # TelemetryEngine (Abstract operational metrics collection)
│   ├── __init__.py
│   └── engine.py
├── diagnostics/               # DiagnosticsEngine (Anomaly detection & diagnostic findings)
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

## 3. Deterministic SHA-256 Identifiers

All monitoring entities implement canonical SHA-256 digests across payload attributes to produce 16-character hexadecimal IDs:

| Prefix | Entity | Example ID |
|---|---|---|
| `SYH_` | `SystemHealth` | `SYH_1A2B3C4D5E6F7890` |
| `SBH_` | `SubsystemHealth` | `SBH_2B3C4D5E6F7890A1` |
| `HBT_` | `HeartbeatRecord` | `HBT_3C4D5E6F7890A1B2` |
| `HAL_` | `HealthAlert` | `HAL_4D5E6F7890A1B2C3` |
| `TEL_` | `TelemetrySnapshot` | `TEL_5E6F7890A1B2C3D4` |
| `RAS_` | `ReliabilityAssessment` | `RAS_6F7890A1B2C3D4E5` |
| `WDG_` | `WatchdogStatus` | `WDG_7890A1B2C3D4E5F6` |
| `MSM_` | `MonitoringSummary` | `MSM_890A1B2C3D4E5F67` |

---

## 4. System Health Engine

`SystemHealthEngine` monitors 7 production subsystems:
1. `LIVE_MARKET_DATA`
2. `MARKET_STATE`
3. `BROKER_ADAPTER`
4. `EXECUTION_ENGINE`
5. `PORTFOLIO_ENGINE`
6. `LIFECYCLE_ENGINE`
7. `NOTIFICATION_PLATFORM`

Assigns deterministic health levels:
- `HEALTHY`: Normal operating state.
- `WARNING`: Non-critical performance anomaly.
- `DEGRADED`: Partial feature degradation.
- `CRITICAL`: Severe subsystem failure.
- `OFFLINE`: Complete subsystem unreachability.

---

## 5. Watchdog Engine

`WatchdogEngine` audits heartbeat freshness across subsystems:
- Identifies **stale** (delayed heartbeats) and **dead** (timed-out heartbeats) components.
- Generates passive `HealthAlert` records (`HAL_<HEX16>`).
- **Strict Rule**: Zero automated restart, mutation, or recovery logic (human-in-the-loop observation only).

---

## 6. Heartbeat Engine

`HeartbeatEngine` manages subsystem pulse telemetry:
- **Sequence Tracking**: Increments and verifies monotonic sequence counters per subsystem.
- **Integrity Verification**: Verifies SHA-256 canonical digest of heartbeat records.
- **Replayability**: Replays historical pulse streams sequentially.

---

## 7. Telemetry Engine

`TelemetryEngine` collects abstract, platform-agnostic performance metrics:
- Resource usage: CPU, Memory, Disk percentages.
- Subsystem latencies: Database, Tick ingestion, Notification dispatch, Execution engine latency (in milliseconds).
- Queue depth, processing time, repository size, replay throughput (eps), live event throughput (eps).
- **Rule**: Zero OS-specific library calls (`psutil`, `win32api`).

---

## 8. Diagnostics Engine & Alert Model

`DiagnosticsEngine` evaluates telemetry snapshots and watchdog statuses to detect:
- Stale market feeds, DB degradation, queue congestion, execution bottlenecks, reconciliation failures, and storage growth.
- **Alert Levels**: `INFO`, `NOTICE`, `WARNING`, `ERROR`, `CRITICAL`.
- All alerts are strictly immutable (`ConfigDict(frozen=True, extra="forbid")`).

---

## 9. Persistence & Replay

All state is persisted to transactional SQLite WAL databases (`PRAGMA foreign_keys = ON;`, `PRAGMA journal_mode = WAL;`, `ON CONFLICT DO UPDATE`). Replay engines re-evaluate historical telemetry and pulse sequences deterministically.
