"""
Project GOAT v0.5 — Deterministic Experiment Orchestrator Subpackage
"""

from goat.orchestration.campaign import (
    CampaignDefinition,
    CampaignLifecycleLogEntry,
    CampaignManifest,
    CampaignStatus,
    ExperimentStatus,
    InfrastructureFailure,
    OrchestrationError,
    ProvenanceMismatchError,
    QueueSnapshot,
    ValidationFailure,
    WorkerFailure,
)
from goat.orchestration.checkpoint import CheckpointManager
from goat.orchestration.queue import ExperimentQueue, ExperimentTask
from goat.orchestration.report import CampaignReportGenerator, MarkdownReportGenerator, JsonReportGenerator
from goat.orchestration.scheduler import (
    ExperimentScheduler,
    compute_configuration_hash,
    compute_dependency_lockfile_hash,
    compute_experiment_id,
    generate_campaign_id,
    sort_nested_dict,
)
from goat.orchestration.worker import WorkerPool, derive_canonical_seed_material

__all__ = [
    "CampaignDefinition",
    "CampaignLifecycleLogEntry",
    "CampaignManifest",
    "CampaignReportGenerator",
    "CampaignStatus",
    "CheckpointManager",
    "ExperimentQueue",
    "ExperimentScheduler",
    "ExperimentStatus",
    "ExperimentTask",
    "InfrastructureFailure",
    "JsonReportGenerator",
    "MarkdownReportGenerator",
    "OrchestrationError",
    "ProvenanceMismatchError",
    "QueueSnapshot",
    "ValidationFailure",
    "WorkerFailure",
    "WorkerPool",
    "compute_configuration_hash",
    "compute_dependency_lockfile_hash",
    "compute_experiment_id",
    "derive_canonical_seed_material",
    "generate_campaign_id",
    "sort_nested_dict",
]
