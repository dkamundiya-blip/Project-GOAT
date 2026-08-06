"""
Project GOAT v0.7 — Test Suite for ScientificSignalGenerationEngine & ExecutionReadinessEngine

Coverage:
- Signal and audit creation from qualified, validated, risk-approved opportunity
- Special required metadata attributes
- ExecutionReadiness evaluation
"""

from goat.qualification.core.canonical import compute_qualification_id
from goat.qualification.core.enums import QualificationState
from goat.qualification.core.models import ScientificQualification
from goat.risk.core.canonical import compute_risk_assessment_id, compute_sizing_id
from goat.risk.core.models import PositionSizingDecision, RiskAssessment
from goat.signals.core.enums import ExecutionStatus, SignalDirection
from goat.signals.generation.engine import (
    ExecutionReadinessEngine,
    ScientificSignalGenerationEngine,
)
from goat.simulation.core.canonical import compute_result_id
from goat.simulation.core.enums import ValidationStatus
from goat.simulation.core.models import SimulationResult


def test_signal_generation_engine():
    gen_engine = ScientificSignalGenerationEngine()

    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(qualification_id=q_id, composite_id="CMP_1", regime_id="MRG_1", evaluation_timestamp="2026-07-30T00:00:00Z", qualification_state=QualificationState.QUALIFIED, overall_readiness=0.88, canonical_hash=q_hash)

    res_id, res_hash = compute_result_id("SRN_1", "VALIDATED")
    sim_res = SimulationResult(result_id=res_id, run_id="SRN_1", validation_status=ValidationStatus.VALIDATED, statistical_metrics={"profit_factor": 1.6}, canonical_hash=res_hash)

    r_id, r_hash = compute_risk_assessment_id("PSD_1")
    risk_ass = RiskAssessment(assessment_id=r_id, sizing_id="PSD_1", total_risk=2.0, monetary_risk=2000.0, expected_reward=4000.0, expected_return_percent=4.0, drawdown_impact=0.02, canonical_hash=r_hash)

    s_id, s_hash = compute_sizing_id("RPF_1", "EURUSD", 1.0850)
    pos_sz = PositionSizingDecision(sizing_id=s_id, risk_profile_id="RPF_1", instrument="EURUSD", entry_price=1.0850, stop_loss_price=1.0800, take_profit_price=1.0950, stop_distance=0.0050, reward_distance=0.0100, risk_reward_ratio=2.0, position_size=400000.0, recommended_lot_size=4.0, minimum_lot_size=0.01, canonical_hash=s_hash)

    signal, audit = gen_engine.generate_signal(
        qualification=qual,
        simulation_result=sim_res,
        risk_assessment=risk_ass,
        position_sizing=pos_sz,
        direction=SignalDirection.BUY,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
    )

    assert signal.signal_id.startswith("SIG_")
    assert signal.instrument == "EURUSD"
    assert signal.direction == SignalDirection.BUY
    assert signal.entry_price == 1.0850
    assert signal.recommended_lot_size == 4.0
    assert signal.monetary_risk == 2000.0
    assert signal.monetary_reward == 4000.0

    # Required public properties check
    assert signal.qualification_status == "QUALIFIED"
    assert signal.validation_status == "VALIDATED"
    assert signal.replay_reference.startswith("REPLAY_SIG_")
    assert signal.audit_reference.startswith("SAD_")

    assert audit.audit_id.startswith("SAD_")
    assert audit.signal_id == signal.signal_id


def test_execution_readiness_engine():
    gen_engine = ScientificSignalGenerationEngine()
    readiness_engine = ExecutionReadinessEngine()

    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(qualification_id=q_id, composite_id="CMP_1", regime_id="MRG_1", evaluation_timestamp="2026-07-30T00:00:00Z", qualification_state=QualificationState.QUALIFIED, overall_readiness=0.88, canonical_hash=q_hash)

    res_id, res_hash = compute_result_id("SRN_1", "VALIDATED")
    sim_res = SimulationResult(result_id=res_id, run_id="SRN_1", validation_status=ValidationStatus.VALIDATED, canonical_hash=res_hash)

    r_id, r_hash = compute_risk_assessment_id("PSD_1")
    risk_ass = RiskAssessment(assessment_id=r_id, sizing_id="PSD_1", total_risk=2.0, monetary_risk=2000.0, expected_reward=4000.0, expected_return_percent=4.0, drawdown_impact=0.02, canonical_hash=r_hash)

    s_id, s_hash = compute_sizing_id("RPF_1", "EURUSD", 1.0850)
    pos_sz = PositionSizingDecision(sizing_id=s_id, risk_profile_id="RPF_1", instrument="EURUSD", entry_price=1.0850, stop_loss_price=1.0800, take_profit_price=1.0950, stop_distance=0.0050, reward_distance=0.0100, risk_reward_ratio=2.0, position_size=400000.0, recommended_lot_size=4.0, minimum_lot_size=0.01, canonical_hash=s_hash)

    signal, _ = gen_engine.generate_signal(
        qualification=qual,
        simulation_result=sim_res,
        risk_assessment=risk_ass,
        position_sizing=pos_sz,
        direction=SignalDirection.BUY,
        generation_timestamp="2026-07-30T00:00:00Z",
        expiration_timestamp="2026-07-31T00:00:00Z",
    )

    readiness = readiness_engine.evaluate_readiness(signal)

    assert readiness.readiness_id.startswith("EXR_")
    assert readiness.execution_status == ExecutionStatus.READY
    assert readiness.readiness_score == 1.0
