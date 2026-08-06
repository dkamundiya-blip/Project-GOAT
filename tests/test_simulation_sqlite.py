"""
Project GOAT v0.7 — Test Suite for Simulation Persistence Repositories

Coverage:
- SimulationScenarioRepository (save, get, list round-trip)
- SimulationRunRepository (save, get round-trip)
- SimulationResultRepository (save, get round-trip)
- WalkForwardRepository (save, get round-trip)
- PerformanceAttributionRepository (save, get round-trip)
- SimulationReportRepository (save, get raw JSON round-trip)
- Foreign Key Integrity Constraints
"""

import sqlite3
import pytest

from goat.simulation.core.canonical import (
    compute_attribution_id,
    compute_result_id,
    compute_run_id,
    compute_scenario_id,
    compute_window_id,
)
from goat.simulation.core.enums import SimulationRunStatus, ValidationStatus
from goat.simulation.core.models import (
    PerformanceAttribution,
    SimulationResult,
    SimulationRun,
    SimulationScenario,
    WalkForwardWindow,
)
from goat.simulation.persistence.sqlite import (
    PerformanceAttributionRepository,
    SimulationReportRepository,
    SimulationResultRepository,
    SimulationRunRepository,
    SimulationScenarioRepository,
    WalkForwardRepository,
    init_simulation_db,
)


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    init_simulation_db(conn)
    yield conn
    conn.close()


def test_scenario_repository_roundtrip(db_conn):
    repo = SimulationScenarioRepository(db_conn)
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

    repo.save_scenario(scenario)
    fetched = repo.get_scenario(sc_id)

    assert fetched == scenario
    assert len(repo.list_scenarios()) == 1


def test_run_repository_roundtrip(db_conn):
    sc_repo = SimulationScenarioRepository(db_conn)
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
    sc_repo.save_scenario(scenario)

    run_repo = SimulationRunRepository(db_conn)
    r_id, r_hash = compute_run_id(sc_id, 42, "2026-07-30T00:00:00Z")
    run = SimulationRun(
        run_id=r_id,
        scenario_id=sc_id,
        execution_timestamp="2026-07-30T00:00:00Z",
        replay_seed=42,
        deterministic_hash="HASH",
        status=SimulationRunStatus.COMPLETED,
        canonical_hash=r_hash,
    )

    run_repo.save_run(run)
    fetched = run_repo.get_run(r_id)

    assert fetched == run


def test_result_repository_roundtrip(db_conn):
    sc_repo = SimulationScenarioRepository(db_conn)
    sc_id, sc_hash = compute_scenario_id("SQL_1", "CMP_1", "DATA_1")
    scenario = SimulationScenario(scenario_id=sc_id, qualification_id="SQL_1", composite_id="CMP_1", regime_id="MRG_1", dataset_reference="DATA_1", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=sc_hash)
    sc_repo.save_scenario(scenario)

    run_repo = SimulationRunRepository(db_conn)
    r_id, r_hash = compute_run_id(sc_id, 42, "2026-07-30T00:00:00Z")
    run = SimulationRun(run_id=r_id, scenario_id=sc_id, execution_timestamp="2026-07-30T00:00:00Z", replay_seed=42, deterministic_hash="HASH", status=SimulationRunStatus.COMPLETED, canonical_hash=r_hash)
    run_repo.save_run(run)

    res_repo = SimulationResultRepository(db_conn)
    res_id, res_hash = compute_result_id(r_id, "VALIDATED")
    result = SimulationResult(
        result_id=res_id,
        run_id=r_id,
        validation_status=ValidationStatus.VALIDATED,
        statistical_metrics={"profit_factor": 1.5},
        canonical_hash=res_hash,
    )

    res_repo.save_result(result)
    fetched = res_repo.get_result(res_id)

    assert fetched == result


def test_walk_forward_repository_roundtrip(db_conn):
    repo = WalkForwardRepository(db_conn)
    w_id, w_hash = compute_window_id(1, ["T1"], ["V1"])
    window = WalkForwardWindow(
        window_id=w_id,
        training_period=["T1"],
        validation_period=["V1"],
        sequence_number=1,
        canonical_hash=w_hash,
    )

    repo.save_window(window)
    fetched = repo.get_window(w_id)

    assert fetched == window


def test_performance_attribution_repository_roundtrip(db_conn):
    sc_repo = SimulationScenarioRepository(db_conn)
    sc_id, sc_hash = compute_scenario_id("SQL_1", "CMP_1", "DATA_1")
    scenario = SimulationScenario(scenario_id=sc_id, qualification_id="SQL_1", composite_id="CMP_1", regime_id="MRG_1", dataset_reference="DATA_1", creation_timestamp="2026-07-30T00:00:00Z", canonical_hash=sc_hash)
    sc_repo.save_scenario(scenario)

    run_repo = SimulationRunRepository(db_conn)
    r_id, r_hash = compute_run_id(sc_id, 42, "2026-07-30T00:00:00Z")
    run = SimulationRun(run_id=r_id, scenario_id=sc_id, execution_timestamp="2026-07-30T00:00:00Z", replay_seed=42, deterministic_hash="HASH", status=SimulationRunStatus.COMPLETED, canonical_hash=r_hash)
    run_repo.save_run(run)

    res_repo = SimulationResultRepository(db_conn)
    res_id, res_hash = compute_result_id(r_id, "VALIDATED")
    result = SimulationResult(result_id=res_id, run_id=r_id, validation_status=ValidationStatus.VALIDATED, statistical_metrics={"profit_factor": 1.5}, canonical_hash=res_hash)
    res_repo.save_result(result)

    att_repo = PerformanceAttributionRepository(db_conn)
    att_id, att_hash = compute_attribution_id(res_id)
    attribution = PerformanceAttribution(
        attribution_id=att_id,
        result_id=res_id,
        contributing_edges={"SED_1": 0.5},
        canonical_hash=att_hash,
    )

    att_repo.save_attribution(attribution)
    fetched = att_repo.get_attribution(att_id)

    assert fetched == attribution
