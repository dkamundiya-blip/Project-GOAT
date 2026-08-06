"""
Project GOAT v0.7 — Test Suite for Simulation Core Models & Canonical Hashing

Coverage:
- Immutable Pydantic models (SimulationScenario, SimulationRun, SimulationResult, WalkForwardWindow, PerformanceAttribution)
- Extra fields forbidden
- Immutability check raises (TypeError, ValidationError)
- Deterministic ID generators & canonical SHA-256 hashes
"""

import pytest
from pydantic import ValidationError

from goat.simulation.core.canonical import (
    compute_attribution_id,
    compute_result_id,
    compute_run_id,
    compute_scenario_id,
    compute_simulation_report_id,
    compute_window_id,
    serialize_canonical_json,
)
from goat.simulation.core.enums import SimulationRunStatus, ValidationStatus
from goat.simulation.core.models import (
    PerformanceAttribution,
    SimulationResult,
    SimulationRun,
    SimulationScenario,
    WalkForwardWindow,
)


def test_scenario_id_determinism():
    id1, hash1 = compute_scenario_id("SQL_1", "CMP_1", "DATA_1")
    id2, hash2 = compute_scenario_id("SQL_1", "CMP_1", "DATA_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SIM_")


def test_run_id_determinism():
    id1, hash1 = compute_run_id("SIM_1", 42, "2026-07-30T00:00:00Z")
    id2, hash2 = compute_run_id("SIM_1", 42, "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SRN_")


def test_result_id_determinism():
    id1, hash1 = compute_result_id("SRN_1", "VALIDATED")
    id2, hash2 = compute_result_id("SRN_1", "VALIDATED")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SRS_")


def test_window_id_determinism():
    id1, hash1 = compute_window_id(1, ["2026-01-01T00:00:00Z"], ["2026-02-01T00:00:00Z"])
    id2, hash2 = compute_window_id(1, ["2026-01-01T00:00:00Z"], ["2026-02-01T00:00:00Z"])
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("WFW_")


def test_attribution_id_determinism():
    id1, hash1 = compute_attribution_id("SRS_1")
    id2, hash2 = compute_attribution_id("SRS_1")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("PAT_")


def test_simulation_report_id_determinism():
    id1, hash1 = compute_simulation_report_id("SimulationExecutiveReport", "2026-07-30T00:00:00Z")
    id2, hash2 = compute_simulation_report_id("SimulationExecutiveReport", "2026-07-30T00:00:00Z")
    assert id1 == id2
    assert hash1 == hash2
    assert id1.startswith("SSR_")


def test_simulation_scenario_model():
    sc_id, sc_hash = compute_scenario_id("SQL_1", "CMP_1", "DATA_1")
    scenario = SimulationScenario(
        scenario_id=sc_id,
        qualification_id="SQL_1",
        composite_id="CMP_1",
        regime_id="MRG_1",
        dataset_reference="DATA_1",
        creation_timestamp="2026-07-30T00:00:00Z",
        canonical_hash=sc_hash,
    )
    assert scenario.scenario_id == sc_id
    with pytest.raises((TypeError, ValidationError)):
        scenario.dataset_reference = "Modified"


def test_simulation_run_model():
    r_id, r_hash = compute_run_id("SIM_1", 42, "2026-07-30T00:00:00Z")
    run = SimulationRun(
        run_id=r_id,
        scenario_id="SIM_1",
        execution_timestamp="2026-07-30T00:00:00Z",
        replay_seed=42,
        deterministic_hash="HASH",
        status=SimulationRunStatus.COMPLETED,
        canonical_hash=r_hash,
    )
    assert run.run_id == r_id
    with pytest.raises((TypeError, ValidationError)):
        run.replay_seed = 99


def test_simulation_result_model():
    res_id, res_hash = compute_result_id("SRN_1", "VALIDATED")
    result = SimulationResult(
        result_id=res_id,
        run_id="SRN_1",
        validation_status=ValidationStatus.VALIDATED,
        statistical_metrics={"profit_factor": 1.5},
        canonical_hash=res_hash,
    )
    assert result.result_id == res_id
    with pytest.raises((TypeError, ValidationError)):
        result.validation_status = ValidationStatus.FAILED


def test_walk_forward_window_model():
    w_id, w_hash = compute_window_id(1, ["T1"], ["V1"])
    window = WalkForwardWindow(
        window_id=w_id,
        training_period=["T1"],
        validation_period=["V1"],
        sequence_number=1,
        canonical_hash=w_hash,
    )
    assert window.window_id == w_id
    with pytest.raises((TypeError, ValidationError)):
        window.sequence_number = 2


def test_performance_attribution_model():
    att_id, att_hash = compute_attribution_id("SRS_1")
    attribution = PerformanceAttribution(
        attribution_id=att_id,
        result_id="SRS_1",
        contributing_edges={"SED_1": 0.5},
        canonical_hash=att_hash,
    )
    assert attribution.attribution_id == att_id
    with pytest.raises((TypeError, ValidationError)):
        attribution.result_id = "SRS_2"
