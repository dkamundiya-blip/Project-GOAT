"""
Project GOAT v0.9 — Reporting Generators for Scientific Experiment Subsystem
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from goat.experiments.core.canonical import serialize_canonical_json
from goat.experiments.core.models import (
    ExperimentLifecycle,
    ExperimentManifest,
    ExperimentReplay,
    ExperimentSchedule,
    ExperimentSummary,
    ScientificExperiment,
)


class ExperimentReport(BaseModel):
    """Immutable report summarizing scientific experiment execution and audit findings."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    report_id: str = Field(default="EREP_0000000000000000", description="Unique Experiment Report ID (EREP_<HEX16>)")
    experiment_id: str = Field(..., description="Parent Experiment ID (EXP_<HEX16>)")
    timestamp: str = Field(default="", description="ISO 8601 UTC timestamp")
    final_status: str = Field(default="", description="Final ExperimentStatus string")
    protocol_summary: dict[str, Any] = Field(default_factory=dict, description="Protocol specification summary")
    outcome_summary: dict[str, Any] = Field(default_factory=dict, description="Outcome and result summary")
    evidence_summary: dict[str, Any] = Field(default_factory=dict, description="Evidence references summary")
    audit_summary: dict[str, Any] = Field(default_factory=dict, description="Audit event trail summary")
    execution_timeline: list[str] = Field(default_factory=list, description="Execution timeline milestones")


def generate_experiment_report(
    experiment: ScientificExperiment,
    protocol: Any = None,
    result: Any = None,
) -> Any:
    """Generate Markdown report for a ScientificExperiment, or legacy ExperimentReport object if protocol/result passed."""
    if protocol is not None or result is not None:
        status_val = str(experiment.status.value if hasattr(experiment.status, "value") else experiment.status)
        outcome_val = str(result.outcome.value if (result and hasattr(result, "outcome") and hasattr(result.outcome, "value")) else (getattr(result, "outcome", "pending") if result else "pending"))
        rep_hash = experiment.canonical_hash[:16].upper() if getattr(experiment, "canonical_hash", "") else "0000000000000000"
        return ExperimentReport(
            report_id=f"EREP_{rep_hash}",
            experiment_id=getattr(experiment, "experiment_id", ""),
            timestamp=getattr(experiment, "created_timestamp", "") or getattr(experiment, "creation_timestamp", ""),
            final_status=status_val,
            protocol_summary={
                "name": getattr(protocol, "protocol_name", ""),
                "stages_count": len(getattr(protocol, "stages", [])),
                "version": getattr(protocol, "protocol_version", ""),
            },
            outcome_summary={
                "outcome": outcome_val,
                "result_id": getattr(result, "result_id", ""),
            },
            evidence_summary={"supporting_evidence_count": len(getattr(result, "supporting_evidence_ids", [])) if result else 0},
            audit_summary={},
            execution_timeline=[],
        )

    ev_ids_str = "\n".join([f"- `{eid}`" for eid in experiment.evidence_ids]) or "- None"
    tags_str = ", ".join(experiment.tags) if experiment.tags else "None"

    return f"""# SCIENTIFIC EXPERIMENT REPORT
## {experiment.title}

**Experiment ID**: `{experiment.experiment_id}`  
**Hypothesis ID**: `{experiment.hypothesis_id}`  
**Type**: `{experiment.experiment_type.value if hasattr(experiment.experiment_type, 'value') else experiment.experiment_type}` | **Status**: `{experiment.status.value if hasattr(experiment.status, 'value') else experiment.status}` | **Priority**: `{experiment.priority.value if hasattr(experiment.priority, 'value') else experiment.priority}`  
**Author**: {experiment.author}  
**Manifest ID**: `{experiment.manifest_id or 'N/A'}`  
**Created**: {experiment.created_timestamp} | **Updated**: {experiment.updated_timestamp}  
**Canonical Hash**: `{experiment.canonical_hash}`  
**Tags**: {tags_str}  

---

### Purpose & Scope
{experiment.description or 'No detailed description provided.'}

---

### Target Evidence / Collection References ({len(experiment.evidence_ids)})
{ev_ids_str}
"""


def generate_lifecycle_report(experiment_id: str, lifecycles: list[ExperimentLifecycle]) -> str:
    """Generate Markdown audit report for experiment lifecycle transitions."""
    rows = []
    for lfc in lifecycles:
        rows.append(f"| `{lfc.lifecycle_id}` | `{lfc.from_status.value}` | `{lfc.to_status.value}` | {lfc.actor} | {lfc.timestamp} | {lfc.reason or 'N/A'} |")
    table_content = "\n".join(rows) if rows else "| None | - | - | - | - | - |"

    return f"""# EXPERIMENT LIFECYCLE AUDIT REPORT
**Target Experiment ID**: `{experiment_id}`  
**Total Transition Events**: `{len(lifecycles)}`  

---

### Audit Log
| Lifecycle ID | From Status | To Status | Actor | Timestamp | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_content}
"""


def generate_manifest_report(manifest: ExperimentManifest) -> str:
    """Generate Markdown report for an ExperimentManifest."""
    ev_ids_str = "\n".join([f"- `{eid}`" for eid in manifest.evidence_ids]) or "- None"
    cfg_rows = "\n".join([f"| `{k}` | `{v}` |" for k, v in manifest.configuration_params.items()]) or "| None | None |"

    return f"""# EXPERIMENT MANIFEST REPORT

**Manifest ID**: `{manifest.manifest_id}`  
**Target Experiment ID**: `{manifest.experiment_id}`  
**Target Hypothesis ID**: `{manifest.hypothesis_id}`  
**Dataset Fingerprint**: `{manifest.dataset_fingerprint or 'N/A'}`  
**Software Version**: `{manifest.software_version}`  
**Author**: {manifest.author}  
**Created**: {manifest.created_timestamp}  
**Canonical Hash**: `{manifest.canonical_hash}`  

---

### Associated Evidence IDs ({len(manifest.evidence_ids)})
{ev_ids_str}

---

### Configuration Parameters
| Parameter | Value |
| :--- | :--- |
{cfg_rows}
"""


def generate_replay_report(replay: ExperimentReplay) -> str:
    """Generate Markdown report for an ExperimentReplay."""
    verified_str = "PASSED (VERIFIED)" if replay.is_verified else "FAILED (DISCREPANCY)"

    return f"""# EXPERIMENT REPLAY AUDIT REPORT

**Replay ID**: `{replay.replay_id}`  
**Experiment ID**: `{replay.experiment_id}`  
**Manifest ID**: `{replay.manifest_id}`  
**Dataset Hash**: `{replay.dataset_hash}`  
**Random Seed**: `{replay.random_seed}`  
**Expected Output Hash**: `{replay.expected_output_hash or 'N/A'}`  
**Verification Status**: `{verified_str}`  
**Created**: {replay.timestamp}  
**Canonical Hash**: `{replay.canonical_hash}`  
"""


def generate_json_report(entity: Any) -> str:
    """Generate canonical JSON report for any domain entity."""
    return serialize_canonical_json(entity)


def generate_executive_summary(summary: ExperimentSummary, recent_experiments: list[ScientificExperiment]) -> str:
    """Generate Executive Summary Report for Experiment Subsystem."""
    st_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.status_counts.items()]) or "| None | 0 |"
    tp_rows = "\n".join([f"| `{k}` | {v} |" for k, v in summary.type_counts.items()]) or "| None | 0 |"

    rec_rows = []
    for e in recent_experiments:
        rec_rows.append(f"| `{e.experiment_id}` | {e.title} | `{e.status.value}` | `{e.experiment_type.value}` | {e.created_timestamp} |")
    rec_table = "\n".join(rec_rows) if rec_rows else "| None | No experiments registered | - | - | - |"

    return f"""# PROJECT GOAT — EXPERIMENT SUBSYSTEM EXECUTIVE REPORT

**Total Experiments**: `{summary.total_experiments}`  
**Snapshot ID**: `{summary.summary_id}`  
**Timestamp**: {summary.timestamp}  

---

## Executive Overview
Project GOAT Version 0.9 Experiment Subsystem currently manages `{summary.total_experiments}` fully reproducible, deterministic scientific experiment containers. All experiment parameters, manifest fingerprints, lifecycle audits, and replay specifications are SHA-256 fingerprinted.

---

### Status Distribution Breakdown
| Status | Count |
| :--- | :--- |
{st_rows}

---

### Experiment Type Breakdown
| Type | Count |
| :--- | :--- |
{tp_rows}

---

## Recent Registered Experiments Inventory
| Experiment ID | Title | Status | Type | Timestamp |
| :--- | :--- | :--- | :--- | :--- |
{rec_table}
"""
