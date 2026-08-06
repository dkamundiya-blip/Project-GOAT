"""
Project GOAT v0.7 — Scientific Simulation Package

Public API Exports for Step 6.4 (Phase VI).
"""

from goat.simulation.backtest import ScientificSimulationEngine
from goat.simulation.core import (
    AttributionCategory,
    PerformanceAttribution,
    SimulationResult,
    SimulationRun,
    SimulationRunStatus,
    SimulationScenario,
    ValidationStatus,
    WalkForwardWindow,
    compute_attribution_id,
    compute_result_id,
    compute_run_id,
    compute_scenario_id,
    compute_simulation_report_id,
    compute_window_id,
    serialize_canonical_json,
)
from goat.simulation.engine import ScientificSimulationEngineCoordinator
from goat.simulation.metrics import (
    PerformanceAttributionEngine,
    StatisticalMetricsCalculator,
)
from goat.simulation.persistence import (
    PerformanceAttributionRepository,
    SimulationReportRepository,
    SimulationResultRepository,
    SimulationRunRepository,
    SimulationScenarioRepository,
    WalkForwardRepository,
    init_simulation_db,
)
from goat.simulation.replay import HistoricalReplayEngine
from goat.simulation.reporting import (
    PerformanceAttributionReport,
    SimulationExecutiveReport,
    SimulationResultReport,
    SimulationRunReport,
    SimulationScenarioReport,
    WalkForwardReport,
)
from goat.simulation.walkforward import WalkForwardValidationEngine

__all__ = [
    # Core Models & Enums
    "ValidationStatus",
    "SimulationRunStatus",
    "AttributionCategory",
    "SimulationScenario",
    "SimulationRun",
    "SimulationResult",
    "WalkForwardWindow",
    "PerformanceAttribution",
    # Identifiers & Canonical Hashing
    "compute_scenario_id",
    "compute_run_id",
    "compute_result_id",
    "compute_window_id",
    "compute_attribution_id",
    "compute_simulation_report_id",
    "serialize_canonical_json",
    # Engines & Coordinators
    "ScientificSimulationEngineCoordinator",
    "ScientificSimulationEngine",
    "HistoricalReplayEngine",
    "WalkForwardValidationEngine",
    "PerformanceAttributionEngine",
    "StatisticalMetricsCalculator",
    # Reports
    "SimulationScenarioReport",
    "SimulationRunReport",
    "SimulationResultReport",
    "WalkForwardReport",
    "PerformanceAttributionReport",
    "SimulationExecutiveReport",
    # Repositories & Database Initialization
    "init_simulation_db",
    "SimulationScenarioRepository",
    "SimulationRunRepository",
    "SimulationResultRepository",
    "WalkForwardRepository",
    "PerformanceAttributionRepository",
    "SimulationReportRepository",
]
