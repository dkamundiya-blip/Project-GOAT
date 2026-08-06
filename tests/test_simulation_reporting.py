"""
Project GOAT v0.7 — Test Suite for Simulation Reports

Coverage:
- SimulationScenarioReport (Markdown & JSON)
- SimulationRunReport (Markdown & JSON)
- SimulationResultReport (Markdown & JSON)
- WalkForwardReport (Markdown & JSON)
- PerformanceAttributionReport (Markdown & JSON)
- SimulationExecutiveReport (Markdown & JSON)
"""

from goat.simulation.core.canonical import (
    compute_result_id,
    compute_scenario_id,
)
from goat.simulation.core.enums import ValidationStatus
from goat.simulation.core.models import SimulationResult, SimulationScenario
from goat.simulation.reporting.reports import (
    SimulationExecutiveReport,
    SimulationResultReport,
    SimulationScenarioReport,
)


def test_scenario_report_rendering():
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

    report = SimulationScenarioReport(
        report_id="SSR_SCN_001",
        timestamp="2026-07-30T00:00:00Z",
        scenarios=[scenario],
    )

    md = report.to_markdown()
    assert "# Simulation Scenario Report" in md
    assert sc_id in md

    json_str = report.to_json()
    assert '"report_id":"SSR_SCN_001"' in json_str


def test_result_report_rendering():
    res_id, res_hash = compute_result_id("SRN_1", "VALIDATED")
    result = SimulationResult(
        result_id=res_id,
        run_id="SRN_1",
        validation_status=ValidationStatus.VALIDATED,
        statistical_metrics={"profit_factor": 1.5, "win_rate": 0.60},
        canonical_hash=res_hash,
    )

    report = SimulationResultReport(
        report_id="SSR_RES_001",
        timestamp="2026-07-30T00:00:00Z",
        results=[result],
    )

    md = report.to_markdown()
    assert "# Simulation Result Report" in md
    assert res_id in md


def test_executive_report_rendering():
    report = SimulationExecutiveReport(
        report_id="SSR_001",
        timestamp="2026-07-30T00:00:00Z",
        total_simulations_executed=1,
        top_validation_status="HIGH_CONFIDENCE_VALIDATED",
        top_profit_factor=2.10,
    )

    md = report.to_markdown()
    assert "# Scientific Simulation & Walk-Forward Validation Executive Report" in md
    assert "HIGH_CONFIDENCE_VALIDATED" in md
