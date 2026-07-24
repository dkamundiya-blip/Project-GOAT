"""
Project GOAT v0.5 — Reporting & Output Abstraction Layer

Implements modular report generators (`MarkdownReportGenerator`, `JsonReportGenerator`)
and canonical artifact persistence for data/campaigns/<campaign_id>/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Any

import structlog

from goat.config import GoatSettings
from goat.orchestration.campaign import (
    CampaignManifest,
    QueueSnapshot,
)
from goat.research.hypothesis.result import HypothesisResult

_log = structlog.get_logger(__name__)


class BaseReportGenerator(ABC):
    """Abstract base class for all report generators."""

    @abstractmethod
    def generate(
        self,
        manifest: CampaignManifest,
        results: list[HypothesisResult],
        statistics: dict[str, Any],
        output_dir: Path,
    ) -> Path:
        """Generate and save report artifact."""


class MarkdownReportGenerator(BaseReportGenerator):
    """Generates human-readable Markdown research report (report.md)."""

    def generate(
        self,
        manifest: CampaignManifest,
        results: list[HypothesisResult],
        statistics: dict[str, Any],
        output_dir: Path,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "report.md"

        camp_info = manifest.campaign
        cfg_info = manifest.configuration
        prov_info = manifest.research_provenance
        status = camp_info.get("status", "UNKNOWN")

        lines = [
            "# Project GOAT v0.5 — Campaign Research Report",
            "",
            f"**Campaign ID**         : `{camp_info.get('campaign_id', 'N/A')}`  ",
            f"**Configuration Hash**  : `{cfg_info.get('configuration_hash', 'N/A')}`  ",
            f"**Campaign Status**     : `{status}`  ",
            f"**FDR Alpha**           : `{cfg_info.get('fdr_alpha', 0.05)}`  ",
            f"**Master Seed**         : `{manifest.execution_configuration.get('master_seed', 42)}`  ",
            f"**Dataset Fingerprint** : `{prov_info.get('dataset_fingerprint', 'N/A')}`  ",
            "",
        ]

        if status in ("FAILED", "CANCELLED"):
            lines.extend([
                "> [!WARNING]",
                f"> **Campaign Terminated Early**: Status is `{status}`. Reports reflect partial progress.",
                "",
            ])

        lines.extend([
            "## Execution Statistics",
            "",
            f"- **Total Experiments Grid** : {statistics.get('total_experiments', 0)}",
            f"- **Completed Tasks**       : {statistics.get('completed_count', 0)}",
            f"- **Failed Tasks**          : {statistics.get('failed_count', 0)}",
            f"- **Skipped Tasks**         : {statistics.get('skipped_count', 0)}",
            f"- **Cancelled Tasks**       : {statistics.get('cancelled_count', 0)}",
            f"- **Total Retries**         : {statistics.get('total_retries', 0)}",
            "",
            "## Research Results & Edge Summary",
            "",
        ])

        supported_results = [r for r in results if r.validation_status == "SUPPORTED"]
        rejected_results = [r for r in results if r.validation_status == "REJECTED"]

        lines.append(f"**Supported Edges** : {len(supported_results)} / {len(results)} evaluated")
        lines.append("")

        if supported_results:
            lines.extend([
                "### Supported Candidate Edges",
                "",
                "| Experiment ID | Symbol | Timeframe | Outcome Metric | Edge Score | q-value | Effect Size |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
            ])
            for r in supported_results:
                q_str = f"{r.adjusted_q_value:.6f}" if r.adjusted_q_value is not None else "N/A"
                eff_str = f"{r.effect_size:.4f}" if r.effect_size is not None else "N/A"
                if isinstance(r.edge_score, dict):
                    edge_val = r.edge_score.get("total_score", r.edge_score.get("edge_score", 0.0))
                else:
                    edge_val = r.edge_score
                lines.append(
                    f"| `{r.hypothesis_id}` | `{r.symbol}` | `{r.timeframe}` | `{r.hypothesis_id}` | `{edge_val:.2f}` | `{q_str}` | `{eff_str}` |"
                )
            lines.append("")

        lines.extend([
            "## Lifecycle State Transitions History",
            "",
            "| Timestamp (UTC) | Previous State | New State | Trigger / Reason | Component |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])
        for entry in manifest.lifecycle_history:
            lines.append(
                f"| `{entry.utc_timestamp.isoformat()}` | `{entry.previous_state.value}` | `{entry.new_state.value}` | {entry.reason} | `{entry.triggering_component}` |"
            )
        lines.append("")

        temp_path = output_dir / "report.md.tmp"
        temp_path.write_text("\n".join(lines), encoding="utf-8")
        temp_path.replace(report_path)
        _log.info("markdown_report_generated", component="Reporter", path=str(report_path))
        return report_path


class JsonReportGenerator(BaseReportGenerator):
    """Generates machine-readable JSON research report (report.json)."""

    def __init__(self, report_schema_version: int = 1) -> None:
        self.report_schema_version = report_schema_version

    def generate(
        self,
        manifest: CampaignManifest,
        results: list[HypothesisResult],
        statistics: dict[str, Any],
        output_dir: Path,
    ) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "report.json"

        report_payload = {
            "report_schema_version": self.report_schema_version,
            "campaign": manifest.campaign,
            "configuration": manifest.configuration,
            "research_provenance": manifest.research_provenance,
            "statistics": statistics,
            "results": [r.model_dump(mode="json") for r in results],
            "lifecycle_history": [entry.model_dump(mode="json") for entry in manifest.lifecycle_history],
        }

        temp_path = output_dir / "report.json.tmp"
        temp_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")
        temp_path.replace(report_path)
        _log.info("json_report_generated", component="Reporter", path=str(report_path))
        return report_path


class CampaignReportGenerator:
    """High-level report orchestrator writing all canonical campaign artifacts."""

    def __init__(self, settings: GoatSettings | None = None) -> None:
        self.settings = settings or GoatSettings()
        self.md_generator = MarkdownReportGenerator()
        self.json_generator = JsonReportGenerator(report_schema_version=self.settings.report_schema_version)

    def write_all_artifacts(
        self,
        manifest: CampaignManifest,
        snapshot: QueueSnapshot,
        results: list[HypothesisResult],
        statistics: dict[str, Any],
        output_dir: Path,
    ) -> None:
        """Write all canonical campaign output files to output_dir.

        Artifacts written:
          - campaign_manifest.json
          - checkpoint.json
          - experiment_results.json
          - campaign_statistics.json
          - report.md
          - report.json
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. campaign_manifest.json
        manifest_path = output_dir / "campaign_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )

        # 2. checkpoint.json
        checkpoint_path = output_dir / "checkpoint.json"
        checkpoint_data = snapshot.model_dump(mode="json")
        checkpoint_data["checkpoint_format_version"] = self.settings.checkpoint_format_version
        checkpoint_path.write_text(
            json.dumps(checkpoint_data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        # 3. experiment_results.json
        results_path = output_dir / "experiment_results.json"
        results_data = [r.model_dump(mode="json") for r in results]
        results_path.write_text(
            json.dumps(results_data, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        # 4. campaign_statistics.json
        stats_path = output_dir / "campaign_statistics.json"
        stats_path.write_text(
            json.dumps(statistics, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        # 5. report.md & report.json
        self.md_generator.generate(manifest, results, statistics, output_dir)
        self.json_generator.generate(manifest, results, statistics, output_dir)

        _log.info(
            "all_campaign_artifacts_written",
            component="Reporter",
            campaign_id=manifest.campaign.get("campaign_id"),
            output_dir=str(output_dir),
        )
