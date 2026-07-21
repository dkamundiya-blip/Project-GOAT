"""
Project GOAT v0.3 — Research Report Generator

Produces human-readable markdown research reports and machine-readable JSON artifacts.
Strictly descriptive — contains ZERO trading signal recommendations or strategy advice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from goat.logging import get_logger
from goat.research.dataset import DatasetManifest
from goat.research.fingerprint import MarketFingerprint

_log = get_logger("research.report")


class ResearchReportGenerator:
    """Generates structured research reports for market fingerprints and datasets."""

    def generate_markdown_report(
        self,
        manifest: DatasetManifest,
        fingerprint: MarketFingerprint,
    ) -> str:
        """Generate human-readable markdown research report text."""
        lines = [
            f"# Project GOAT v0.3 — Market Research Report: {manifest.symbol} ({manifest.timeframe})",
            "",
            "> [!NOTE]",
            "> **Descriptive Quantitative Research Only**: This report characterizes market statistics. "
            "It contains **NO** trading signals, buy/sell recommendations, entry algorithms, or strategy optimizations.",
            "",
            "## 1. Dataset Manifest & Data Quality",
            "",
            f"- **Dataset Fingerprint**: `{manifest.dataset_id}`",
            f"- **Operational Run ID**: `{manifest.run_id}`",
            f"- **Symbol**: `{manifest.symbol}`",
            f"- **Timeframe**: `{manifest.timeframe}`",
            f"- **Temporal Coverage (Actual)**: `{manifest.actual_start_timestamp.isoformat()}` to `{manifest.actual_end_timestamp.isoformat()}`",
            f"- **Observation Count (Actual)**: `{manifest.actual_observation_count:,}`",
            f"- **History Truncated**: `{manifest.history_truncated}`",
        ]

        if manifest.history_truncated:
            lines.append(f"  - **Truncation Reason**: `{manifest.truncation_reason}`")

        lines.extend([
            f"- **Provenance Composition**: `{manifest.provenance_counts}`",
            f"- **Duplicate Count**: `{manifest.duplicate_count}`",
            f"- **Canonical Checksum**: `{manifest.canonical_checksum}`",
            f"- **Construction Version**: `{manifest.construction_version}`",
            "",
            "## 2. Dataset Sufficiency Status",
            "",
            f"- **Sufficiency Status**: `{fingerprint.sufficiency.status}`",
            f"- **Is Sufficient**: `{fingerprint.sufficiency.is_sufficient}`",
        ])

        if fingerprint.sufficiency.warnings:
            lines.append("  - **Sufficiency Warnings**:")
            for w in fingerprint.sufficiency.warnings:
                lines.append(f"    - {w}")

        lines.extend([
            "",
            "## 3. Return Distribution Statistics",
            "",
            "| Statistic | Value |",
            "| :--- | :--- |",
            f"| Mean Return | `{fingerprint.distribution.get('mean', 0.0)}` |",
            f"| Median Return | `{fingerprint.distribution.get('median', 0.0)}` |",
            f"| Standard Deviation | `{fingerprint.distribution.get('std', 0.0)}` |",
            f"| Variance | `{fingerprint.distribution.get('variance', 0.0)}` |",
            f"| Skewness | `{fingerprint.distribution.get('skewness', 0.0)}` |",
            f"| Excess Kurtosis | `{fingerprint.distribution.get('kurtosis', 0.0)}` |",
            f"| Min Return | `{fingerprint.distribution.get('min', 0.0)}` |",
            f"| Max Return | `{fingerprint.distribution.get('max', 0.0)}` |",
            f"| Quantile 1% | `{fingerprint.distribution.get('q01', 0.0)}` |",
            f"| Quantile 99% | `{fingerprint.distribution.get('q99', 0.0)}` |",
            "",
            "## 4. Serial Dependence (Autocorrelation)",
            "",
            "| Lag | Return Autocorrelation | Absolute Return Autocorrelation |",
            "| :--- | :--- | :--- |",
        ])

        for lag in [1, 2, 3, 5, 10]:
            r_ac = fingerprint.serial_dependence.get(f"autocorr_lag_{lag}", 0.0)
            abs_ac = fingerprint.serial_dependence.get(f"abs_autocorr_lag_{lag}", 0.0)
            lines.append(f"| Lag {lag} | `{r_ac}` | `{abs_ac}` |")

        lines.extend([
            "",
            "## 5. Directional Run-Length Analysis",
            "",
            "| Metric | Positive Runs | Negative Runs |",
            "| :--- | :--- | :--- |",
            f"| Mean Run Length | `{fingerprint.directional_runs.get('positive_run_mean', 0.0)}` | `{fingerprint.directional_runs.get('negative_run_mean', 0.0)}` |",
            f"| Max Run Length | `{fingerprint.directional_runs.get('positive_run_max', 0.0)}` | `{fingerprint.directional_runs.get('negative_run_max', 0.0)}` |",
            "",
            "## 6. Volatility & Impulse Characterization",
            "",
            f"- **Impulse Events Detected**: `{fingerprint.impulses.get('count', 0)}`",
            f"- **Mean Impulse Magnitude**: `{fingerprint.impulses.get('mean_magnitude', 0.0)}`",
            f"- **Mean Retracement Fraction**: `{fingerprint.pullbacks.get('mean_retracement_fraction', 0.0)}`",
            f"- **Vol Regimes Breakdown**: `{fingerprint.regime_distribution}`",
            "",
            "==================================================",
        ])

        return "\n".join(lines)

    def save_report_artifacts(
        self,
        output_dir: Path,
        manifest: DatasetManifest,
        fingerprint: MarketFingerprint,
    ) -> tuple[Path, Path, Path]:
        """Save manifest JSON, fingerprint JSON, and markdown report files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        sym = manifest.symbol
        tf = manifest.timeframe

        manifest_path = output_dir / f"{sym}_{tf}_manifest.json"
        fingerprint_path = output_dir / f"{sym}_{tf}_fingerprint.json"
        report_path = output_dir / f"{sym}_{tf}_report.md"

        manifest_path.write_text(manifest.to_json(), encoding="utf-8")
        fingerprint_path.write_text(fingerprint.to_json(), encoding="utf-8")

        md_text = self.generate_markdown_report(manifest, fingerprint)
        report_path.write_text(md_text, encoding="utf-8")

        _log.info(
            "research_report_artifacts_saved",
            manifest_path=str(manifest_path),
            report_path=str(report_path),
        )

        return manifest_path, fingerprint_path, report_path
