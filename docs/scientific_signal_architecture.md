# Project GOAT — Scientific Signal Generation, Delivery & Execution Readiness Architecture

Version: v0.7 — Step 6.6 (Phase VI Milestone)  
Status: Active Implementation / Certified  
Package: `goat.signals`  

---

## 1. Architecture Summary

Step 6.6 introduces the **Scientific Signal Generation, Delivery & Execution Readiness Engine** (`goat.signals`), completing Phase VI and marking the completion of **Project GOAT Version 0.7**. 

This subsystem converts fully validated and risk-approved scientific opportunities into deterministic, execution-ready trading signals (`TradingSignal`, `SignalPayload`, `SignalLifecycleEvent`, `ExecutionReadiness`, `SignalAuditRecord`). 

Key Design Guarantees:
- **No Trade Execution / No Broker Connections**: Prepares signals for future execution adapters without placing orders or connecting to live broker APIs.
- **Zero AI / ML Reasoning**: 100% rule-based deterministic calculations. All signals are reproducible, replayable, and explainable.
- **Immutable Domain Models**: Core models (`TradingSignal`, `SignalPayload`, `SignalLifecycleEvent`, `ExecutionReadiness`, `SignalAuditRecord`) are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Prefix IDs (`SIG_<HEX16>`, `SPL_<HEX16>`, `SLE_<HEX16>`, `EXR_<HEX16>`, `SAD_<HEX16>`, `SSR_<HEX16>`) derived via canonical SHA-256 digests.
- **Special Required Fields Exposed**: Every signal exposes Instrument, Direction, Entry Price, Stop Loss, Take Profit, Recommended Lot Size, Minimum Lot Size, Monetary Risk, Monetary Reward, Risk %, Risk Reward Ratio, Scientific Confidence, Qualification Status, Validation Status, Replay Reference, and Audit Reference for direct consumption by dashboards, mobile apps, notifications, REST APIs, and future broker adapters without recalculation.
- **SQLite Persistence & Replay**: Full round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`) and exact state replay.

---

## 2. Signal Pipeline

`ScientificSignalEngineCoordinator` executes the signal pipeline:
1. `TradingSignal` & `SignalAuditRecord` Generation (`ScientificSignalGenerationEngine`)
2. Deterministic State Machine Transitions (`SignalLifecycleEngine`)
3. Execution Readiness Verification (`ExecutionReadinessEngine`)
4. Delivery Payload Formatting (`SignalDeliveryEngine` & `SignalPayloadGenerator`)

---

## 3. Signal Lifecycle (`SignalLifecycleEngine`)

State Machine Rules:
- `CREATED` -> `VALIDATED`, `INVALIDATED`
- `VALIDATED` -> `READY_FOR_DELIVERY`, `INVALIDATED`
- `READY_FOR_DELIVERY` -> `DELIVERED`, `EXPIRED`, `INVALIDATED`
- `DELIVERED` -> `ACKNOWLEDGED`, `EXPIRED`, `INVALIDATED`
- `ACKNOWLEDGED` -> `ARCHIVED`, `EXPIRED`
- Terminal States: `EXPIRED`, `ARCHIVED`, `INVALIDATED`

Illegal state transitions raise `ValueError` with clear explanations. Each transition emits an immutable `SignalLifecycleEvent`.

---

## 4. Delivery Payload Generator (`SignalPayloadGenerator` & `SignalDeliveryEngine`)

Formats deterministic payloads for distribution targets:
- `JSON`, `MARKDOWN`, `NOTIFICATION`, `WEBHOOK`, `TELEGRAM`, `EMAIL`, `PUSH`
- Every payload includes a SHA-256 checksum digest computed over payload data.

---

## 5. Execution Readiness Engine (`ExecutionReadinessEngine`)

Evaluates whether a generated signal satisfies all prerequisites:
- Scientific Qualification status (`QUALIFIED`)
- Historical Simulation validation (`VALIDATED`)
- Risk approval & Capital allocation reservation
- Portfolio exposure limits compliance
- Readiness score ($0.0$ to $1.0$) and status (`READY`, `BLOCKED`, `CANCELLED`)

---

## 6. Auditability & Scientific Traceability (`SignalAuditRecord`)

Every signal is linked to its full scientific lineage trace:
- Qualification ID & Composite Edge ID
- Regime ID & Simulation Result ID
- Risk Assessment ID & Position Sizing ID
- Evidence chain & Hypotheses chain
- Replay reference ID (`REPLAY_SIG_<HEX16>`)

---

## 7. Persistence & Replay

Repositories:
- `TradingSignalRepository`: Table `trading_signals`
- `SignalPayloadRepository`: Table `signal_payloads`
- `SignalLifecycleRepository`: Table `signal_lifecycle_events`
- `ExecutionReadinessRepository`: Table `execution_readiness_evaluations`
- `SignalAuditRepository`: Table `signal_audit_records`
- `SignalReportRepository`: Table `signal_reports`

Replay support: `coordinator.replay_signal(signal_id)` and `coordinator.replay_audit(audit_id)` restore exact historical models from SQLite persistence.

---

## 8. Public API

Exposed through `goat.signals.__all__`:

```python
from goat.signals import (
    ScientificSignalEngineCoordinator,
    ScientificSignalGenerationEngine,
    ExecutionReadinessEngine,
    SignalLifecycleEngine,
    SignalDeliveryEngine,
    SignalPayloadGenerator,
    TradingSignal,
    SignalPayload,
    SignalLifecycleEvent,
    ExecutionReadiness,
    SignalAuditRecord,
    SignalDirection,
    SignalLifecycleState,
    PayloadFormat,
    ExecutionStatus,
    TradingSignalRepository,
    SignalPayloadRepository,
    SignalLifecycleRepository,
    ExecutionReadinessRepository,
    SignalAuditRepository,
    SignalReportRepository,
)
```

---

## 9. Code Example

```python
import sqlite3
from goat.signals import ScientificSignalEngineCoordinator, SignalDirection
from goat.qualification.core.models import ScientificQualification, QualificationState
from goat.simulation.core.models import SimulationResult, ValidationStatus
from goat.risk.core.models import RiskAssessment, PositionSizingDecision

conn = sqlite3.connect(":memory:")
coordinator = ScientificSignalEngineCoordinator(conn=conn)

qual = ScientificQualification(
    qualification_id="SQL_1111111111111111",
    composite_id="CMP_1111111111111111",
    regime_id="MRG_1111111111111111",
    evaluation_timestamp="2026-07-30T12:00:00Z",
    qualification_state=QualificationState.QUALIFIED,
    overall_readiness=0.88,
)

sim_res = SimulationResult(
    result_id="SRS_1111111111111111",
    run_id="SRN_1111111111111111",
    validation_status=ValidationStatus.VALIDATED,
)

risk_ass = RiskAssessment(
    assessment_id="RSA_1111111111111111",
    sizing_id="PSD_1111111111111111",
    total_risk=2.0,
    monetary_risk=2000.0,
    expected_reward=4000.0,
    expected_return_percent=4.0,
    drawdown_impact=0.02,
)

pos_sz = PositionSizingDecision(
    sizing_id="PSD_1111111111111111",
    risk_profile_id="RPF_1111111111111111",
    instrument="EURUSD",
    entry_price=1.0850,
    stop_loss_price=1.0800,
    take_profit_price=1.0950,
    stop_distance=0.0050,
    reward_distance=0.0100,
    risk_reward_ratio=2.0,
    position_size=400000.0,
    recommended_lot_size=4.0,
)

signal, readiness, report = coordinator.execute_signal_workflow(
    qualification=qual,
    simulation_result=sim_res,
    risk_assessment=risk_ass,
    position_sizing=pos_sz,
    direction=SignalDirection.BUY,
    generation_timestamp="2026-07-30T12:00:00Z",
    expiration_timestamp="2026-07-31T12:00:00Z",
)

print(report.to_markdown())
```

---

## 10. Future Extension Points & Version 0.8 Roadmap

- **Broker Execution Adapters**: FIX Protocol, MetaTrader 5 Bridge, Interactive Brokers API integration.
- **External Notification Connectors**: Telegram Bot API dispatchers, Webhook listeners, FCM Mobile Push Service.
- **REST API Endpoints**: FastAPI endpoints exposing active signals and execution readiness statuses.
