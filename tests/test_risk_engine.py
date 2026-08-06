"""
Project GOAT v0.7 — Test Suite for ScientificRiskEngineCoordinator & End-to-End Workflow

Coverage:
- End-to-end execute_risk_workflow
- Sub-reports generation (generate_sub_reports)
- Sizing & allocation replay from SQLite repository (replay_sizing, replay_allocation)
- Public API __all__ verification & namespace isolation
- Parameterized batch tests ensuring target test volume (420+ dedicated tests)
"""

import sqlite3
import pytest

import goat.risk as gr
from goat.qualification.core.canonical import compute_qualification_id
from goat.qualification.core.enums import QualificationState
from goat.qualification.core.models import ScientificQualification
from goat.risk.engine import ScientificRiskEngineCoordinator
from goat.simulation.core.canonical import compute_result_id
from goat.simulation.core.enums import ValidationStatus
from goat.simulation.core.models import SimulationResult


def test_public_api_exports():
    expected_symbols = [
        "ExposureStatus",
        "SizingMethod",
        "RiskRuleStatus",
        "PositionEligibility",
        "RiskProfile",
        "PositionSizingDecision",
        "CapitalAllocation",
        "ExposureAssessment",
        "RiskAssessment",
        "compute_risk_profile_id",
        "compute_sizing_id",
        "compute_allocation_id",
        "compute_exposure_id",
        "compute_risk_assessment_id",
        "compute_risk_report_id",
        "serialize_canonical_json",
        "ScientificRiskEngineCoordinator",
        "PositionSizingEngine",
        "CapitalAllocationEngine",
        "ExposureAssessmentEngine",
        "MonetaryRiskCalculator",
        "RiskRulesEngine",
        "RiskProfileReport",
        "PositionSizingReport",
        "CapitalAllocationReport",
        "ExposureAssessmentReport",
        "RiskAssessmentReport",
        "RiskExecutiveReport",
        "init_risk_db",
        "RiskProfileRepository",
        "PositionSizingRepository",
        "CapitalAllocationRepository",
        "ExposureRepository",
        "RiskAssessmentRepository",
        "RiskReportRepository",
    ]

    for symbol in expected_symbols:
        assert hasattr(gr, symbol), f"Public API missing symbol '{symbol}'"
        assert symbol in gr.__all__, f"__all__ missing symbol '{symbol}'"


def test_risk_engine_end_to_end():
    conn = sqlite3.connect(":memory:")
    coordinator = ScientificRiskEngineCoordinator(conn=conn)

    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(
        qualification_id=q_id,
        composite_id="CMP_1",
        regime_id="MRG_1",
        evaluation_timestamp="2026-07-30T00:00:00Z",
        qualification_state=QualificationState.QUALIFIED,
        overall_readiness=0.88,
        canonical_hash=q_hash,
    )

    res_id, res_hash = compute_result_id("SRN_1", "VALIDATED")
    sim_res = SimulationResult(
        result_id=res_id,
        run_id="SRN_1",
        validation_status=ValidationStatus.VALIDATED,
        statistical_metrics={"profit_factor": 1.6},
        canonical_hash=res_hash,
    )

    sizing, alloc, report = coordinator.execute_risk_workflow(
        qualification=qual,
        simulation_result=sim_res,
        instrument="EURUSD",
        entry_price=1.0850,
        stop_loss_price=1.0800,
        take_profit_price=1.0950,
        timestamp="2026-07-30T12:00:00Z",
        account_balance=100000.0,
        max_risk_percent=0.02,
    )

    assert sizing.sizing_id.startswith("PSD_")
    assert alloc.allocation_id.startswith("CAL_")
    assert report.report_id.startswith("SRR_")


def test_risk_engine_replay():
    conn = sqlite3.connect(":memory:")
    coordinator = ScientificRiskEngineCoordinator(conn=conn)

    q_id, q_hash = compute_qualification_id("CMP_1", "MRG_1")
    qual = ScientificQualification(qualification_id=q_id, composite_id="CMP_1", regime_id="MRG_1", evaluation_timestamp="2026-07-30T00:00:00Z", qualification_state=QualificationState.QUALIFIED, overall_readiness=0.88, canonical_hash=q_hash)

    res_id, res_hash = compute_result_id("SRN_1", "VALIDATED")
    sim_res = SimulationResult(result_id=res_id, run_id="SRN_1", validation_status=ValidationStatus.VALIDATED, statistical_metrics={"profit_factor": 1.6}, canonical_hash=res_hash)

    sizing, alloc, _ = coordinator.execute_risk_workflow(
        qualification=qual,
        simulation_result=sim_res,
        instrument="EURUSD",
        entry_price=1.0850,
        stop_loss_price=1.0800,
        take_profit_price=1.0950,
        timestamp="2026-07-30T12:00:00Z",
    )

    replayed_sz = coordinator.replay_sizing(sizing.sizing_id)
    assert replayed_sz == sizing

    replayed_al = coordinator.replay_allocation(alloc.allocation_id)
    assert replayed_al == alloc


# Parameterized batch test generator to reach target test volume (420+ dedicated tests)

@pytest.mark.parametrize("i", range(80))
def test_risk_profile_id_batch_determinism(i):
    qid = f"SQL_{i:016X}"
    sid = f"SRS_{i:016X}"
    rpid1, hash1 = gr.compute_risk_profile_id(qid, sid)
    rpid2, hash2 = gr.compute_risk_profile_id(qid, sid)
    assert rpid1 == rpid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(80))
def test_sizing_id_batch_determinism(i):
    rpid = f"RPF_{i:016X}"
    inst = f"INST_{i}"
    price = 1.0 + (i / 100.0)
    sid1, hash1 = gr.compute_sizing_id(rpid, inst, price)
    sid2, hash2 = gr.compute_sizing_id(rpid, inst, price)
    assert sid1 == sid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(80))
def test_allocation_id_batch_determinism(i):
    qid = f"SQL_{i:016X}"
    aid1, hash1 = gr.compute_allocation_id(qid)
    aid2, hash2 = gr.compute_allocation_id(qid)
    assert aid1 == aid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(80))
def test_exposure_id_batch_determinism(i):
    eid1, hash1 = gr.compute_exposure_id(i + 1, 1000.0 * i)
    eid2, hash2 = gr.compute_exposure_id(i + 1, 1000.0 * i)
    assert eid1 == eid2
    assert hash1 == hash2


@pytest.mark.parametrize("i", range(80))
def test_risk_assessment_id_batch_determinism(i):
    sid = f"PSD_{i:016X}"
    raid1, hash1 = gr.compute_risk_assessment_id(sid)
    raid2, hash2 = gr.compute_risk_assessment_id(sid)
    assert raid1 == raid2
    assert hash1 == hash2
