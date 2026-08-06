"""
Project GOAT v0.7 — Scientific Simulation Core Package
"""

from goat.simulation.core.canonical import (
    compute_attribution_id,
    compute_result_id,
    compute_run_id,
    compute_scenario_id,
    compute_simulation_report_id,
    compute_window_id,
    serialize_canonical_json,
)
from goat.simulation.core.enums import (
    AttributionCategory,
    SimulationRunStatus,
    ValidationStatus,
)
from goat.simulation.core.models import (
    PerformanceAttribution,
    SimulationResult,
    SimulationRun,
    SimulationScenario,
    WalkForwardWindow,
)

__all__ = [
    "ValidationStatus",
    "SimulationRunStatus",
    "AttributionCategory",
    "SimulationScenario",
    "SimulationRun",
    "SimulationResult",
    "WalkForwardWindow",
    "PerformanceAttribution",
    "compute_scenario_id",
    "compute_run_id",
    "compute_result_id",
    "compute_window_id",
    "compute_attribution_id",
    "compute_simulation_report_id",
    "serialize_canonical_json",
]
