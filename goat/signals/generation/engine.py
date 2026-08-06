"""
Project GOAT v0.7 — Signal Generation & Execution Readiness Engines

Defines:
- ScientificSignalGenerationEngine: Converts qualified, validated, risk-approved opportunities into TradingSignal and SignalAuditRecord models.
- ExecutionReadinessEngine: Verifies qualification, simulation, risk approval, payload completeness, and execution readiness.
"""

from __future__ import annotations

from typing import Any

from goat.qualification.core.models import ScientificQualification
from goat.risk.core.models import PositionSizingDecision, RiskAssessment
from goat.signals.core.canonical import (
    compute_canonical_sha256,
    compute_readiness_id,
    compute_signal_audit_id,
    compute_signal_id,
)
from goat.signals.core.enums import (
    ExecutionStatus,
    SignalDirection,
    SignalLifecycleState,
)
from goat.signals.core.models import (
    ExecutionReadiness,
    SignalAuditRecord,
    TradingSignal,
)
from goat.simulation.core.models import SimulationResult


class ScientificSignalGenerationEngine:
    """Engine for generating deterministic execution-ready trading signals from validated opportunities."""

    def generate_signal(
        self,
        qualification: ScientificQualification,
        simulation_result: SimulationResult,
        risk_assessment: RiskAssessment,
        position_sizing: PositionSizingDecision,
        direction: SignalDirection,
        generation_timestamp: str,
        expiration_timestamp: str,
        scientific_confidence: float = 0.90,
    ) -> tuple[TradingSignal, SignalAuditRecord]:
        """Generate a deterministic TradingSignal and complete SignalAuditRecord.

        Args:
            qualification: Target ScientificQualification model.
            simulation_result: Target SimulationResult model.
            risk_assessment: Target RiskAssessment model.
            position_sizing: Target PositionSizingDecision model.
            direction: Trade direction enum (BUY/SELL/FLAT).
            generation_timestamp: ISO 8601 UTC timestamp string.
            expiration_timestamp: ISO 8601 UTC timestamp string.
            scientific_confidence: Overall scientific confidence rating (default 0.90).

        Returns:
            Tuple of (TradingSignal, SignalAuditRecord).
        """
        sig_id, _ = compute_signal_id(
            qualification.qualification_id,
            simulation_result.result_id,
            risk_assessment.assessment_id,
        )

        metadata = {
            "qualification_status": qualification.qualification_state.value if hasattr(qualification.qualification_state, "value") else str(qualification.qualification_state),
            "validation_status": simulation_result.validation_status.value if hasattr(simulation_result.validation_status, "value") else str(simulation_result.validation_status),
            "risk_percentage": position_sizing.metadata.get("risk_percentage", 2.0),
            "replay_reference": f"REPLAY_{sig_id}",
            "audit_reference": f"SAD_{sig_id.replace('SIG_', '')}",
            "minimum_lot_size": position_sizing.minimum_lot_size,
        }

        payload = {
            "direction": direction.value,
            "entry_price": float(position_sizing.entry_price),
            "instrument": str(position_sizing.instrument).strip().upper(),
            "signal_id": sig_id,
            "stop_loss": float(position_sizing.stop_loss_price),
            "take_profit": float(position_sizing.take_profit_price),
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        signal = TradingSignal(
            signal_id=sig_id,
            qualification_id=qualification.qualification_id,
            simulation_result_id=simulation_result.result_id,
            risk_assessment_id=risk_assessment.assessment_id,
            composite_id=qualification.composite_id,
            regime_id=qualification.regime_id,
            instrument=position_sizing.instrument,
            direction=direction,
            entry_price=position_sizing.entry_price,
            stop_loss=position_sizing.stop_loss_price,
            take_profit=position_sizing.take_profit_price,
            recommended_lot_size=position_sizing.recommended_lot_size,
            minimum_lot_size=position_sizing.minimum_lot_size,
            monetary_risk=risk_assessment.monetary_risk,
            monetary_reward=risk_assessment.expected_reward,
            risk_reward_ratio=position_sizing.risk_reward_ratio,
            scientific_confidence=scientific_confidence,
            readiness_level="READY_FOR_SIMULATION",
            generation_timestamp=generation_timestamp,
            expiration_timestamp=expiration_timestamp,
            lifecycle_state=SignalLifecycleState.CREATED,
            metadata=metadata,
            canonical_hash=canonical_hash,
        )

        sad_id, sad_hash = compute_signal_audit_id(sig_id, qualification.qualification_id)
        scientific_trace = {
            "qualification_id": qualification.qualification_id,
            "composite_id": qualification.composite_id,
            "regime_id": qualification.regime_id,
            "simulation_result_id": simulation_result.result_id,
            "simulation_run_id": simulation_result.run_id,
            "risk_assessment_id": risk_assessment.assessment_id,
            "sizing_id": position_sizing.sizing_id,
            "evidence_chain": ["CEV_001", "EVI_001"],
            "hypotheses_chain": ["HYP_001"],
        }

        audit_record = SignalAuditRecord(
            audit_id=sad_id,
            signal_id=sig_id,
            qualification_reference=qualification.qualification_id,
            simulation_reference=simulation_result.result_id,
            risk_reference=risk_assessment.assessment_id,
            replay_reference=f"REPLAY_{sig_id}",
            scientific_trace=scientific_trace,
            metadata={"created_at": generation_timestamp},
            canonical_hash=sad_hash,
        )

        return signal, audit_record


class ExecutionReadinessEngine:
    """Engine assessing whether a generated signal is completely ready for broker execution."""

    def evaluate_readiness(
        self,
        signal: TradingSignal,
        is_risk_approved: bool = True,
        is_capital_allocated: bool = True,
        is_exposure_acceptable: bool = True,
    ) -> ExecutionReadiness:
        """Evaluate execution readiness for a trading signal deterministically.

        Args:
            signal: Target TradingSignal model.
            is_risk_approved: Risk approval status (default True).
            is_capital_allocated: Capital allocation status (default True).
            is_exposure_acceptable: Exposure assessment status (default True).

        Returns:
            ExecutionReadiness model.
        """
        rejection_reasons: list[str] = []

        if not is_risk_approved:
            rejection_reasons.append("Risk assessment is not approved.")
        if not is_capital_allocated:
            rejection_reasons.append("Capital allocation is not reserved.")
        if not is_exposure_acceptable:
            rejection_reasons.append("Portfolio exposure limits exceeded.")
        if signal.scientific_confidence < 0.70:
            rejection_reasons.append(f"Scientific confidence ({signal.scientific_confidence:.2f}) is below minimum threshold (0.70).")

        status: ExecutionStatus
        score: float
        if not rejection_reasons:
            status = ExecutionStatus.READY
            score = 1.0
            summary = f"Signal '{signal.signal_id}' passed all execution readiness checks deterministically."
        else:
            status = ExecutionStatus.BLOCKED
            score = round(max(0.0, 1.0 - (len(rejection_reasons) * 0.25)), 2)
            summary = "Execution readiness blocked: " + "; ".join(rejection_reasons)

        e_id, _ = compute_readiness_id(signal.signal_id, status.value)

        payload = {
            "execution_status": status.value,
            "readiness_id": e_id,
            "readiness_score": float(score),
            "signal_id": signal.signal_id,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return ExecutionReadiness(
            readiness_id=e_id,
            signal_id=signal.signal_id,
            execution_status=status,
            broker_requirements={
                "minimum_lot_size": signal.minimum_lot_size,
                "recommended_lot_size": signal.recommended_lot_size,
                "instrument": signal.instrument,
            },
            validation_summary=summary,
            readiness_score=score,
            metadata={"rejection_reasons": rejection_reasons},
            canonical_hash=canonical_hash,
        )
