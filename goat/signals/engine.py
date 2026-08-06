"""
Project GOAT v0.7 — Scientific Signal Engine Coordinator

Main coordinator executing the deterministic signal generation & execution readiness workflow:
1. Generate TradingSignal & SignalAuditRecord from qualified & validated opportunity
2. Advance signal lifecycle state (CREATED -> VALIDATED -> READY_FOR_DELIVERY -> DELIVERED)
3. Evaluate execution readiness (ExecutionReadinessEngine)
4. Generate delivery payloads (SignalDeliveryEngine & SignalPayloadGenerator)
5. Persist models to SQLite repositories
6. Generate sub-reports and executive report
7. Replay historical signal and audit trace from SQLite repository
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.qualification.core.models import ScientificQualification
from goat.risk.core.models import PositionSizingDecision, RiskAssessment
from goat.signals.core.canonical import compute_signal_report_id
from goat.signals.core.enums import (
    ExecutionStatus,
    PayloadFormat,
    SignalDirection,
    SignalLifecycleState,
)
from goat.signals.core.models import (
    ExecutionReadiness,
    SignalAuditRecord,
    SignalLifecycleEvent,
    SignalPayload,
    TradingSignal,
)
from goat.signals.delivery.engine import SignalDeliveryEngine
from goat.signals.generation.engine import (
    ExecutionReadinessEngine,
    ScientificSignalGenerationEngine,
)
from goat.signals.lifecycle.engine import SignalLifecycleEngine
from goat.signals.persistence.sqlite import (
    ExecutionReadinessRepository,
    SignalAuditRepository,
    SignalLifecycleRepository,
    SignalPayloadRepository,
    SignalReportRepository,
    TradingSignalRepository,
)
from goat.signals.reporting.reports import (
    ExecutionReadinessReport,
    SignalAuditReport,
    SignalExecutiveReport,
    SignalLifecycleReport,
    SignalPayloadReport,
    TradingSignalReport,
)
from goat.simulation.core.models import SimulationResult


class ScientificSignalEngineCoordinator:
    """Main coordinator executing deterministic signal generation, delivery, and readiness workflow."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.generation_engine = ScientificSignalGenerationEngine()
        self.readiness_engine = ExecutionReadinessEngine()
        self.lifecycle_engine = SignalLifecycleEngine()
        self.delivery_engine = SignalDeliveryEngine()

        # Repositories
        self.signal_repo = TradingSignalRepository(self.conn)
        self.payload_repo = SignalPayloadRepository(self.conn)
        self.lifecycle_repo = SignalLifecycleRepository(self.conn)
        self.readiness_repo = ExecutionReadinessRepository(self.conn)
        self.audit_repo = SignalAuditRepository(self.conn)
        self.report_repo = SignalReportRepository(self.conn)

    def execute_signal_workflow(
        self,
        qualification: ScientificQualification,
        simulation_result: SimulationResult,
        risk_assessment: RiskAssessment,
        position_sizing: PositionSizingDecision,
        direction: SignalDirection,
        generation_timestamp: str,
        expiration_timestamp: str,
        scientific_confidence: float = 0.90,
    ) -> tuple[TradingSignal, ExecutionReadiness, SignalExecutiveReport]:
        """Execute complete signal generation, readiness evaluation, payload formatting, and reporting workflow.

        Args:
            qualification: Target ScientificQualification model.
            simulation_result: Target SimulationResult model.
            risk_assessment: Target RiskAssessment model.
            position_sizing: Target PositionSizingDecision model.
            direction: SignalDirection enum (BUY/SELL/FLAT).
            generation_timestamp: ISO 8601 UTC timestamp string.
            expiration_timestamp: ISO 8601 UTC timestamp string.
            scientific_confidence: Scientific confidence rating (default 0.90).

        Returns:
            Tuple of (TradingSignal, ExecutionReadiness, SignalExecutiveReport).
        """
        # 1. Generate TradingSignal & SignalAuditRecord
        signal, audit = self.generation_engine.generate_signal(
            qualification=qualification,
            simulation_result=simulation_result,
            risk_assessment=risk_assessment,
            position_sizing=position_sizing,
            direction=direction,
            generation_timestamp=generation_timestamp,
            expiration_timestamp=expiration_timestamp,
            scientific_confidence=scientific_confidence,
        )
        self.signal_repo.save_signal(signal)
        self.audit_repo.save_audit(audit)

        # 2. Advance Lifecycle: CREATED -> VALIDATED -> READY_FOR_DELIVERY -> DELIVERED
        sig_v, ev1 = self.lifecycle_engine.transition_state(
            signal, SignalLifecycleState.VALIDATED, generation_timestamp, "Validation checks passed."
        )
        self.lifecycle_repo.save_event(ev1)

        sig_r, ev2 = self.lifecycle_engine.transition_state(
            sig_v, SignalLifecycleState.READY_FOR_DELIVERY, generation_timestamp, "Approved for delivery."
        )
        self.lifecycle_repo.save_event(ev2)

        sig_d, ev3 = self.lifecycle_engine.transition_state(
            sig_r, SignalLifecycleState.DELIVERED, generation_timestamp, "Signal payloads published internally."
        )
        self.lifecycle_repo.save_event(ev3)
        self.signal_repo.save_signal(sig_d)

        # 3. Evaluate Execution Readiness
        readiness = self.readiness_engine.evaluate_readiness(sig_d)
        self.readiness_repo.save_readiness(readiness)

        # 4. Generate & Save Delivery Payloads
        payloads = self.delivery_engine.prepare_all_delivery_payloads(sig_d)
        for payload in payloads.values():
            self.payload_repo.save_payload(payload)

        # 5. Generate Executive Report
        rep_id, _ = compute_signal_report_id("SignalExecutiveReport", generation_timestamp)
        executive_report = SignalExecutiveReport(
            report_id=rep_id,
            timestamp=generation_timestamp,
            total_signals_generated=1,
            total_signals_ready=1 if readiness.execution_status == ExecutionStatus.READY else 0,
            top_instrument=sig_d.instrument,
            top_direction=sig_d.direction.value,
            top_lot_size=sig_d.recommended_lot_size,
            top_monetary_risk=sig_d.monetary_risk,
            top_monetary_reward=sig_d.monetary_reward,
            summary_notes=f"Signal '{sig_d.signal_id}' for '{sig_d.instrument}' ({sig_d.direction.value}) generated, verified, and delivered deterministically.",
        )
        self.report_repo.save_report(rep_id, "SignalExecutiveReport", generation_timestamp, executive_report)

        return sig_d, readiness, executive_report

    def replay_signal(self, signal_id: str) -> TradingSignal:
        """Replay exact TradingSignal model from persistence repository."""
        s = self.signal_repo.get_signal(signal_id)
        if not s:
            raise KeyError(f"TradingSignal ID '{signal_id}' not found in persistence repository.")
        return s

    def replay_audit(self, audit_id: str) -> SignalAuditRecord:
        """Replay exact SignalAuditRecord model from persistence repository."""
        a = self.audit_repo.get_audit(audit_id)
        if not a:
            raise KeyError(f"SignalAuditRecord ID '{audit_id}' not found in persistence repository.")
        return a
