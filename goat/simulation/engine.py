"""
Project GOAT v0.7 — Scientific Simulation Engine Coordinator

Main coordinator executing the deterministic simulation, replay, walk-forward validation, and performance attribution workflow:
1. Run backtest simulation over historical dataset events (ScientificSimulationEngine)
2. Run sequential walk-forward validation (WalkForwardValidationEngine)
3. Compute performance attribution (PerformanceAttributionEngine)
4. Persist models to SQLite repositories
5. Generate sub-reports and executive report
6. Replay past simulation and walk-forward validation runs
"""

from __future__ import annotations

import sqlite3
from typing import Any

from goat.composite.core.models import CompositeEdge
from goat.qualification.core.models import ScientificQualification
from goat.regimes.core.models import MarketRegime
from goat.simulation.backtest.engine import ScientificSimulationEngine
from goat.simulation.core.canonical import compute_simulation_report_id
from goat.simulation.core.enums import ValidationStatus
from goat.simulation.core.models import (
    PerformanceAttribution,
    SimulationResult,
    SimulationRun,
    SimulationScenario,
    WalkForwardWindow,
)
from goat.simulation.metrics.attribution import PerformanceAttributionEngine
from goat.simulation.persistence.sqlite import (
    PerformanceAttributionRepository,
    SimulationReportRepository,
    SimulationResultRepository,
    SimulationRunRepository,
    SimulationScenarioRepository,
    WalkForwardRepository,
)
from goat.simulation.reporting.reports import (
    PerformanceAttributionReport,
    SimulationExecutiveReport,
    SimulationResultReport,
    SimulationRunReport,
    SimulationScenarioReport,
    WalkForwardReport,
)
from goat.simulation.walkforward.engine import WalkForwardValidationEngine


class ScientificSimulationEngineCoordinator:
    """Main coordinator executing deterministic simulation & walk-forward validation workflow."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn or sqlite3.connect(":memory:")
        self.simulation_engine = ScientificSimulationEngine()
        self.walkforward_engine = WalkForwardValidationEngine()
        self.attribution_engine = PerformanceAttributionEngine()

        # Repositories
        self.scenario_repo = SimulationScenarioRepository(self.conn)
        self.run_repo = SimulationRunRepository(self.conn)
        self.result_repo = SimulationResultRepository(self.conn)
        self.walkforward_repo = WalkForwardRepository(self.conn)
        self.attribution_repo = PerformanceAttributionRepository(self.conn)
        self.report_repo = SimulationReportRepository(self.conn)

    def execute_simulation_workflow(
        self,
        qualification: ScientificQualification,
        composite: CompositeEdge,
        regime: MarketRegime,
        raw_events: list[dict[str, Any]],
        dataset_reference: str,
        timestamp: str,
        seed: int = 42,
    ) -> tuple[SimulationResult, PerformanceAttribution, SimulationExecutiveReport]:
        """Execute complete backtest simulation, attribution, and reporting workflow deterministically.

        Args:
            qualification: Target ScientificQualification model.
            composite: Target CompositeEdge model.
            regime: Target MarketRegime model.
            raw_events: List of raw historical event dictionaries.
            dataset_reference: Reference name or URI of historical dataset.
            timestamp: ISO 8601 UTC timestamp string.
            seed: Deterministic seed integer.

        Returns:
            Tuple of (SimulationResult, PerformanceAttribution, SimulationExecutiveReport).
        """
        # 1. Run Simulation
        scenario, run, result = self.simulation_engine.run_simulation(
            qualification=qualification,
            composite=composite,
            regime=regime,
            raw_events=raw_events,
            dataset_reference=dataset_reference,
            timestamp=timestamp,
            seed=seed,
        )

        self.scenario_repo.save_scenario(scenario)
        self.run_repo.save_run(run)
        self.result_repo.save_result(result)

        # 2. Compute Performance Attribution
        attribution = self.attribution_engine.compute_attribution(
            result_id=result.result_id,
            composite=composite,
            regime=regime,
            metrics=result.statistical_metrics,
        )
        self.attribution_repo.save_attribution(attribution)

        # 3. Generate Executive Report
        rep_id, _ = compute_simulation_report_id("SimulationExecutiveReport", timestamp)
        val_str = result.validation_status.value if hasattr(result.validation_status, "value") else str(result.validation_status)
        pf = result.statistical_metrics.get("profit_factor", 1.0)

        report = SimulationExecutiveReport(
            report_id=rep_id,
            timestamp=timestamp,
            total_simulations_executed=1,
            top_validation_status=val_str,
            top_profit_factor=pf,
            summary_notes=f"Simulation scenario '{scenario.scenario_id}' executed deterministically with profit factor {pf:.2f}.",
        )
        self.report_repo.save_report(rep_id, "SimulationExecutiveReport", timestamp, report)

        return result, attribution, report

    def execute_walk_forward_workflow(
        self,
        start_timestamp: str,
        end_timestamp: str,
        events_by_window: dict[str, list[dict[str, Any]]],
        timestamp: str,
    ) -> tuple[ValidationStatus, list[WalkForwardWindow]]:
        """Execute walk-forward validation workflow deterministically across sequential windows."""
        windows = self.walkforward_engine.generate_walk_forward_windows(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            num_windows=len(events_by_window) if events_by_window else 3,
        )

        for w in windows:
            self.walkforward_repo.save_window(w)

        # Ensure window mapping matches generated window IDs
        window_events_map = {}
        for idx, w in enumerate(windows):
            key = list(events_by_window.keys())[idx] if idx < len(events_by_window) else w.window_id
            window_events_map[w.window_id] = events_by_window.get(key, [])

        overall_status, _ = self.walkforward_engine.evaluate_walk_forward_windows(windows, window_events_map)

        return overall_status, windows

    def generate_sub_reports(
        self,
        scenario: SimulationScenario,
        run: SimulationRun,
        result: SimulationResult,
        attribution: PerformanceAttribution,
        windows: list[WalkForwardWindow],
        timestamp: str,
    ) -> dict[str, Any]:
        """Generate sub-reports (ScenarioReport, RunReport, ResultReport, WalkForwardReport, AttributionReport)."""
        sc_report = SimulationScenarioReport(
            report_id=f"SSR_SCN_{timestamp[:10]}",
            timestamp=timestamp,
            scenarios=[scenario],
        )
        run_report = SimulationRunReport(
            report_id=f"SSR_RUN_{timestamp[:10]}",
            timestamp=timestamp,
            runs=[run],
        )
        res_report = SimulationResultReport(
            report_id=f"SSR_RES_{timestamp[:10]}",
            timestamp=timestamp,
            results=[result],
        )
        wf_report = WalkForwardReport(
            report_id=f"SSR_WFW_{timestamp[:10]}",
            timestamp=timestamp,
            windows=windows,
        )
        att_report = PerformanceAttributionReport(
            report_id=f"SSR_ATT_{timestamp[:10]}",
            timestamp=timestamp,
            attributions=[attribution],
        )

        return {
            "scenario_report": sc_report,
            "run_report": run_report,
            "result_report": res_report,
            "walkforward_report": wf_report,
            "attribution_report": att_report,
        }

    def replay_simulation(self, result_id: str) -> SimulationResult:
        """Replay exact SimulationResult model from persistence repository."""
        res = self.result_repo.get_result(result_id)
        if not res:
            raise KeyError(f"SimulationResult ID '{result_id}' not found in persistence repository.")
        return res

    def replay_walkforward(self, window_id: str) -> WalkForwardWindow:
        """Replay exact WalkForwardWindow model from persistence repository."""
        w = self.walkforward_repo.get_window(window_id)
        if not w:
            raise KeyError(f"WalkForwardWindow ID '{window_id}' not found in persistence repository.")
        return w
