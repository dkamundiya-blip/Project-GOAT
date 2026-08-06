"""
Project GOAT v0.7 — Scientific Simulation Engine

Executes deterministic backtest simulation over historical event datasets:
- Loads qualified opportunities & historical datasets
- Executes historical event replay via HistoricalReplayEngine
- Computes 15 descriptive statistical metrics via StatisticalMetricsCalculator
- Produces SimulationScenario, SimulationRun, and SimulationResult models
"""

from __future__ import annotations

from typing import Any

from goat.composite.core.models import CompositeEdge
from goat.qualification.core.models import ScientificQualification
from goat.regimes.core.models import MarketRegime
from goat.simulation.core.canonical import (
    compute_canonical_sha256,
    compute_result_id,
    compute_run_id,
    compute_scenario_id,
)
from goat.simulation.core.enums import SimulationRunStatus, ValidationStatus
from goat.simulation.core.models import (
    SimulationResult,
    SimulationRun,
    SimulationScenario,
)
from goat.simulation.metrics.attribution import PerformanceAttributionEngine
from goat.simulation.metrics.calculator import StatisticalMetricsCalculator
from goat.simulation.replay.engine import HistoricalReplayEngine


class ScientificSimulationEngine:
    """Engine executing deterministic scientific backtest simulations."""

    def __init__(self) -> None:
        self.replay_engine = HistoricalReplayEngine()
        self.metrics_calculator = StatisticalMetricsCalculator()
        self.attribution_engine = PerformanceAttributionEngine()

    def run_simulation(
        self,
        qualification: ScientificQualification,
        composite: CompositeEdge,
        regime: MarketRegime,
        raw_events: list[dict[str, Any]],
        dataset_reference: str,
        timestamp: str,
        seed: int = 42,
    ) -> tuple[SimulationScenario, SimulationRun, SimulationResult]:
        """Run deterministic simulation pipeline over historical dataset events.

        Args:
            qualification: Target ScientificQualification model.
            composite: Target CompositeEdge model.
            regime: Target MarketRegime model.
            raw_events: List of raw historical event dictionaries.
            dataset_reference: Dataset reference URI or identifier.
            timestamp: ISO 8601 UTC timestamp string.
            seed: Deterministic seed integer.

        Returns:
            Tuple of (SimulationScenario, SimulationRun, SimulationResult).
        """
        # 1. Create SimulationScenario
        sc_id, sc_hash = compute_scenario_id(
            qualification.qualification_id,
            composite.composite_id,
            dataset_reference,
        )
        window = ["2026-01-01T00:00:00Z", "2026-07-30T00:00:00Z"]
        scenario = SimulationScenario(
            scenario_id=sc_id,
            qualification_id=qualification.qualification_id,
            composite_id=composite.composite_id,
            regime_id=regime.regime_id,
            dataset_reference=dataset_reference,
            simulation_window=window,
            configuration={"seed": seed},
            creation_timestamp=timestamp,
            canonical_hash=sc_hash,
        )

        # 2. Replay Events & Create SimulationRun
        replayed_events, replay_hash = self.replay_engine.replay_events(raw_events, seed=seed)
        run_id, run_hash = compute_run_id(scenario.scenario_id, seed, timestamp)

        run = SimulationRun(
            run_id=run_id,
            scenario_id=scenario.scenario_id,
            execution_timestamp=timestamp,
            replay_seed=seed,
            deterministic_hash=replay_hash,
            status=SimulationRunStatus.COMPLETED,
            canonical_hash=run_hash,
        )

        # 3. Calculate Statistical Metrics
        metrics = self.metrics_calculator.compute_all_metrics(replayed_events)

        # 4. Determine Validation Decision Status
        val_status: ValidationStatus
        pf = metrics.get("profit_factor", 1.0)
        win_rate = metrics.get("win_rate", 0.0)

        if pf >= 1.75 and win_rate >= 0.65:
            val_status = ValidationStatus.HIGH_CONFIDENCE_VALIDATED
        elif pf >= 1.40 and win_rate >= 0.55:
            val_status = ValidationStatus.VALIDATED
        elif pf >= 1.10:
            val_status = ValidationStatus.PARTIALLY_VALIDATED
        else:
            val_status = ValidationStatus.FAILED

        res_id, res_hash = compute_result_id(run.run_id, val_status.value)

        # 5. Compute Attribution
        attribution_model = self.attribution_engine.compute_attribution(
            result_id=res_id,
            composite=composite,
            regime=regime,
            metrics=metrics,
        )

        result = SimulationResult(
            result_id=res_id,
            run_id=run.run_id,
            simulated_events=replayed_events,
            outcome_summary={"total_events": len(replayed_events), "dataset_reference": dataset_reference},
            validation_status=val_status,
            statistical_metrics=metrics,
            attribution=attribution_model.dict(),
            canonical_hash=res_hash,
        )

        return scenario, run, result
