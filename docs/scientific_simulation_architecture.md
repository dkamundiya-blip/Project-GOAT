# Project GOAT — Scientific Simulation & Walk-Forward Validation Architecture

Version: v0.7 — Step 6.4 (Phase VI)  
Status: Active Implementation / Certified  
Package: `goat.simulation`  

---

## 1. Architecture Summary

Step 6.4 introduces the deterministic **Scientific Simulation, Walk-Forward Validation & Performance Attribution Engine** (`goat.simulation`). Scientifically qualified market opportunities (`ScientificQualification`) require objective historical validation before they can ever become production trading signals. This subsystem executes deterministic historical replay, rolling walk-forward validation, performance attribution, and 15 descriptive statistical metric evaluations without generating trading signals or relying on AI, machine learning, or parameter optimization.

Key Design Guarantees:
- **No Signal Generation / No Live Trading**: Purely objective historical evaluation and scientific validation.
- **Zero AI / ML Reasoning**: Rule-based deterministic event replay and metric calculation. All calculations are 100% reproducible and auditable.
- **Immutable Pydantic Models**: Core domain models (`SimulationScenario`, `SimulationRun`, `SimulationResult`, `WalkForwardWindow`, `PerformanceAttribution`) are strictly frozen Pydantic models.
- **Deterministic Identifiers**: Prefix IDs (`SIM_<HEX16>`, `SRN_<HEX16>`, `SRS_<HEX16>`, `WFW_<HEX16>`, `PAT_<HEX16>`, `SSR_<HEX16>`) derived via canonical SHA-256 digests.
- **Complete Traceability & Walk-Forward Integrity**: Sequential, independent walk-forward windows without data leakage.
- **SQLite Persistence & Replay**: Full round-trip persistence with referential integrity (`PRAGMA foreign_keys = ON`) and exact state replay.

---

## 2. Replay Engine (`HistoricalReplayEngine`)

Chronologically sorts event streams by timestamp and event ID, computes canonical SHA-256 replay hashes, and verifies replay integrity.

---

## 3. Simulation Pipeline (`ScientificSimulationEngine`)

Loads qualified opportunities, loads historical event datasets, executes event replay, computes 15 descriptive statistical metrics, and evaluates validation status.

---

## 4. Walk-Forward Validation (`WalkForwardValidationEngine`)

Generates non-overlapping, sequential training and validation periods (`WalkForwardWindow`). Evaluates rolling performance without data leakage across window boundaries.

---

## 5. Performance Attribution Framework (`PerformanceAttributionEngine`)

Quantifies scientific performance contribution breakdown across component edges, active market regimes, supporting evidence, originating hypotheses, and validations.

---

## 6. Statistical Metrics Framework (`StatisticalMetricsCalculator`)

Computes 15 descriptive statistical metrics:
1. `win_rate`
2. `loss_rate`
3. `average_reward`
4. `average_risk`
5. `expected_value`
6. `profit_factor`
7. `maximum_drawdown`
8. `recovery_factor`
9. `payoff_ratio`
10. `trade_frequency`
11. `risk_adjusted_expectancy`
12. `simulation_consistency`
13. `validation_consistency`
14. `reproducibility_score`
15. `statistical_confidence`

> [!IMPORTANT]
> All metrics are purely descriptive. They NEVER optimize future behavior or fit parameters.

---

## 7. Validation Decisions Framework (`ValidationStatus`)

Decision classifications based on deterministic profit factor and win rate thresholds:
- `FAILED`: Profit factor $< 1.10$.
- `PARTIALLY_VALIDATED`: Profit factor $1.10 - 1.39$.
- `VALIDATED`: Profit factor $1.40 - 1.74$ and win rate $\ge 0.55$.
- `HIGH_CONFIDENCE_VALIDATED`: Profit factor $\ge 1.75$ and win rate $\ge 0.65$.

---

## 8. Persistence & Replay

Repositories:
- `SimulationScenarioRepository`: Table `simulation_scenarios`
- `SimulationRunRepository`: Table `simulation_runs`
- `SimulationResultRepository`: Table `simulation_results`
- `WalkForwardRepository`: Table `walk_forward_windows`
- `PerformanceAttributionRepository`: Table `performance_attributions`
- `SimulationReportRepository`: Table `simulation_reports`

Replay support: `coordinator.replay_simulation(result_id)` and `coordinator.replay_walkforward(window_id)` restore exact historical models from SQLite repositories.

---

## 9. Public API

Exposed through `goat.simulation.__all__`:

```python
from goat.simulation import (
    ScientificSimulationEngineCoordinator,
    ScientificSimulationEngine,
    HistoricalReplayEngine,
    WalkForwardValidationEngine,
    PerformanceAttributionEngine,
    StatisticalMetricsCalculator,
    SimulationScenario,
    SimulationRun,
    SimulationResult,
    WalkForwardWindow,
    PerformanceAttribution,
    ValidationStatus,
    SimulationRunStatus,
    SimulationScenarioRepository,
    SimulationRunRepository,
    SimulationResultRepository,
    WalkForwardRepository,
    PerformanceAttributionRepository,
    SimulationReportRepository,
)
```

---

## 10. Code Example

```python
import sqlite3
from goat.simulation import ScientificSimulationEngineCoordinator
from goat.qualification.core.models import ScientificQualification, QualificationState
from goat.composite.core.models import CompositeEdge
from goat.regimes.core.models import MarketRegime

conn = sqlite3.connect(":memory:")
coordinator = ScientificSimulationEngineCoordinator(conn=conn)

qual = ScientificQualification(
    qualification_id="SQL_1111111111111111",
    composite_id="CMP_1111111111111111",
    regime_id="MRG_1111111111111111",
    evaluation_timestamp="2026-07-30T12:00:00Z",
    qualification_state=QualificationState.QUALIFIED,
    overall_readiness=0.88,
)

composite = CompositeEdge(
    composite_id="CMP_1111111111111111",
    title="Composite Edge Alpha",
    participating_edges=["SED_1", "SED_2"],
    creation_timestamp="2026-07-30T12:00:00Z",
)

regime = MarketRegime(
    regime_id="MRG_1111111111111111",
    timestamp="2026-07-30T12:00:00Z",
    regime_type="TRENDING",
    confidence=0.85,
)

raw_events = [
    {"timestamp": "2026-01-01T00:00:00Z", "pnl": 150.0},
    {"timestamp": "2026-01-02T00:00:00Z", "pnl": -50.0},
    {"timestamp": "2026-01-03T00:00:00Z", "pnl": 200.0},
]

result, att, report = coordinator.execute_simulation_workflow(
    qualification=qual,
    composite=composite,
    regime=regime,
    raw_events=raw_events,
    dataset_reference="HISTORICAL_TICKS_2026_Q1",
    timestamp="2026-07-30T12:00:00Z",
)

print(report.to_markdown())
```

---

## 11. Future Extension Points

- **Multi-Asset Portfolio Stress Testing**: Simulating cross-asset correlation breakdowns across historical systemic liquidity events.
- **Microsecond Order-Book Replay**: High-granularity L2/L3 order-book tick replay engines.
