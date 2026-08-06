"""
Project GOAT v0.7 — Scientific Simulation Reports

Provides immutable, deterministic report models and renderers:
- SimulationScenarioReport
- SimulationRunReport
- SimulationResultReport
- WalkForwardReport
- PerformanceAttributionReport
- SimulationExecutiveReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.simulation.core.models import (
    PerformanceAttribution,
    SimulationResult,
    SimulationRun,
    SimulationScenario,
    WalkForwardWindow,
)


class SimulationScenarioReport(BaseModel):
    """Report detailing SimulationScenario objects."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    scenarios: list[SimulationScenario] = Field(default_factory=list, description="List of scenarios")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Simulation Scenario Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Scenarios**: {len(self.scenarios)}",
            "",
            "| Scenario ID | Qualification ID | Composite ID | Regime ID | Dataset Reference |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for s in sorted(self.scenarios, key=lambda x: x.scenario_id):
            lines.append(
                f"| `{s.scenario_id}` | `{s.qualification_id}` | `{s.composite_id}` | `{s.regime_id}` | `{s.dataset_reference}` |"
            )
        return "\n".join(lines)


class SimulationRunReport(BaseModel):
    """Report detailing SimulationRun executions."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    runs: list[SimulationRun] = Field(default_factory=list, description="List of simulation runs")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Simulation Run Execution Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Runs**: {len(self.runs)}",
            "",
            "| Run ID | Scenario ID | Status | Seed | Replay Digest |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for r in sorted(self.runs, key=lambda x: x.run_id):
            st = r.status.value if hasattr(r.status, "value") else str(r.status)
            lines.append(
                f"| `{r.run_id}` | `{r.scenario_id}` | `{st}` | `{r.replay_seed}` | `{r.deterministic_hash[:16]}...` |"
            )
        return "\n".join(lines)


class SimulationResultReport(BaseModel):
    """Report detailing SimulationResult objects and statistical metrics."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    results: list[SimulationResult] = Field(default_factory=list, description="List of simulation results")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Simulation Result Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Results**: {len(self.results)}",
            "",
            "| Result ID | Run ID | Status | Win Rate | Profit Factor | Max Drawdown | Expectancy |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for r in sorted(self.results, key=lambda x: x.result_id):
            m = r.statistical_metrics
            st = r.validation_status.value if hasattr(r.validation_status, "value") else str(r.validation_status)
            lines.append(
                f"| `{r.result_id}` | `{r.run_id}` | `{st}` | `{m.get('win_rate', 0.0):.2f}` | `{m.get('profit_factor', 1.0):.2f}` | `{m.get('maximum_drawdown', 0.0):.2f}` | `{m.get('expected_value', 0.0):.4f}` |"
            )
        return "\n".join(lines)


class WalkForwardReport(BaseModel):
    """Report detailing WalkForwardWindow sequence evaluations."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    windows: list[WalkForwardWindow] = Field(default_factory=list, description="List of WalkForwardWindows")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Walk-Forward Validation Window Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Windows**: {len(self.windows)}",
            "",
            "| Window ID | Sequence | Training Period | Validation Period |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for w in sorted(self.windows, key=lambda x: x.sequence_number):
            tr = " - ".join(w.training_period) if w.training_period else "N/A"
            val = " - ".join(w.validation_period) if w.validation_period else "N/A"
            lines.append(f"| `{w.window_id}` | {w.sequence_number} | `{tr}` | `{val}` |")
        return "\n".join(lines)


class PerformanceAttributionReport(BaseModel):
    """Report detailing PerformanceAttribution breakdowns."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    attributions: list[PerformanceAttribution] = Field(default_factory=list, description="List of PerformanceAttributions")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Performance Attribution Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Attributions**: {len(self.attributions)}",
            "",
            "| Attribution ID | Result ID | Edge Count | Regime Contribution | Evidence Count |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for a in sorted(self.attributions, key=lambda x: x.attribution_id):
            lines.append(
                f"| `{a.attribution_id}` | `{a.result_id}` | {len(a.contributing_edges)} | `{sum(a.contributing_regimes.values()):.2f}` | {len(a.contributing_evidence)} |"
            )
        return "\n".join(lines)


class SimulationExecutiveReport(BaseModel):
    """Executive root report for Scientific Simulation & Walk-Forward Validation Engine."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_simulations_executed: int = Field(..., ge=0)
    top_validation_status: str = Field(default="")
    top_profit_factor: float = Field(default=1.0)
    summary_notes: str = Field(default="")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Simulation & Walk-Forward Validation Executive Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Simulations Executed**: {self.total_simulations_executed}",
            f"- **Highest Validation Status**: `{self.top_validation_status or 'NONE'}`",
            f"- **Top Profit Factor**: `{self.top_profit_factor:.2f}`",
            "",
            "## Summary Rationale",
            self.summary_notes or "Scientific simulation and walk-forward validation completed deterministically without ML or parameter optimization.",
        ]
        return "\n".join(lines)
