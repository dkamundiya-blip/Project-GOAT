"""
Project GOAT v0.4 — Hypothesis Experiment Report Generator

Produces human-readable markdown research reports and machine-readable JSON artifacts.
Strictly descriptive — contains ZERO trading signals, buy/sell advice, or execution logic.
"""

from __future__ import annotations

from pathlib import Path

from goat.logging import get_logger
from goat.research.hypothesis.experiment import Experiment

_log = get_logger("hypothesis.report")


class HypothesisReportGenerator:
    """Generates markdown reports and JSON artifacts for hypothesis experiments."""

    def generate_experiment_report(self, experiment: Experiment) -> str:
        """Generate markdown summary for an experiment family."""
        lines = [
            f"# Project GOAT v0.4 — Hypothesis Experiment Report: {experiment.family_name}",
            "",
            "> [!NOTE]",
            "> **Statistical Edge Research Engine Only**: This report presents quantitative hypothesis testing results. "
            "It contains **NO** trading signals, buy/sell recommendations, entry execution rules, or strategy optimizations.",
            "",
            "## 1. Experiment Summary",
            "",
            f"- **Experiment ID**: `{experiment.experiment_id}`",
            f"- **Family Name**: `{experiment.family_name}`",
            f"- **Dataset Fingerprints**: `{experiment.dataset_fingerprints}`",
            f"- **Partitions Accessed**: `{experiment.partitions_accessed}`",
            f"- **Multiple Testing Method**: `{experiment.multiple_testing_method}` (FDR alpha = {experiment.fdr_alpha})",
            f"- **Hypotheses Evaluated**: `{len(experiment.hypotheses_evaluated)}`",
            f"- **Statistically Supported (q <= {experiment.fdr_alpha})**: `{experiment.supported_count}`",
            f"- **Rejected / Non-Significant**: `{experiment.rejected_count}`",
            "",
            "## 2. Tested Hypotheses & Results Table",
            "",
            "| Hypothesis ID | Partition | Metric | Cond N | Base N | Effect Size | Test Stat | Raw p-val | Adjusted q-val | EdgeScore | Status |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]

        for res in experiment.results:
            score_val = res.edge_score.get("total_edge_score", 0.0)
            q_str = f"{res.adjusted_q_value:.6f}" if res.adjusted_q_value is not None else "N/A"
            lines.append(
                f"| `{res.hypothesis_id}` | `{res.partition}` | `{res.effect_size_type}` | `{res.conditional_sample_count}` | "
                f"`{res.baseline_sample_count}` | `{res.effect_size:.4f}` | `{res.statistic_value:.4f}` | "
                f"`{res.raw_p_value:.6f}` | `{q_str}` | `{score_val:.1f}` | `{res.stability_status}` |"
            )

        lines.extend([
            "",
            "## 3. Methodological & Dependence Warnings",
            "",
        ])

        has_warnings = False
        for res in experiment.results:
            if res.warnings:
                has_warnings = True
                lines.append(f"### `{res.hypothesis_id}`")
                for w in res.warnings:
                    lines.append(f"- {w}")

        if not has_warnings:
            lines.append("- No explicit dependence or sample sufficiency warnings detected.")

        lines.extend([
            "",
            "==================================================",
        ])

        return "\n".join(lines)

    def save_experiment_artifacts(
        self,
        output_dir: Path,
        experiment: Experiment,
    ) -> tuple[Path, Path]:
        """Save JSON experiment log and markdown report files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        name_slug = experiment.family_name.lower().replace(" ", "_")
        json_path = output_dir / f"experiment_{name_slug}.json"
        md_path = output_dir / f"experiment_{name_slug}_report.md"

        json_path.write_text(experiment.to_json(), encoding="utf-8")

        md_text = self.generate_experiment_report(experiment)
        md_path.write_text(md_text, encoding="utf-8")

        _log.info(
            "experiment_artifacts_saved",
            json_path=str(json_path),
            md_path=str(md_path),
        )

        return json_path, md_path
