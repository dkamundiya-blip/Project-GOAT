"""
Project GOAT v0.9 — Scientific Experiment Subsystem Public API
"""

# Legacy v0.7 Backward Compatibility Exports
from goat.experiments.audit import ExperimentAuditEvent
from goat.experiments.context import ExperimentContext
from goat.experiments.executor import ExperimentExecutor, ExperimentValidationError
from goat.experiments.hypothesis import (
    HypothesisRecord,
    HypothesisRegistry,
    HypothesisStatus,
    compute_hypothesis_id,
)
from goat.experiments.model import compute_experiment_fingerprint
from goat.experiments.protocol import ExperimentProtocol, compute_protocol_id
from goat.experiments.reporting import ExperimentReport
from goat.experiments.result import ExperimentOutcome, ExperimentResult, compute_result_id
from goat.experiments.sqlite import SQLiteExperimentRepository

# Step 9.3 v0.9 Subsystem Exports
from goat.experiments.core.canonical import (
    compute_canonical_sha256,
    compute_experiment_id,
    compute_lifecycle_id,
    compute_manifest_id,
    compute_replay_id,
    compute_schedule_id,
    compute_summary_id,
    serialize_canonical_json,
)
from goat.experiments.core.enums import (
    ExperimentPriority,
    ExperimentStatus,
    ExperimentType,
)
from goat.experiments.core.models import (
    ExperimentLifecycle,
    ExperimentManifest,
    ExperimentReplay,
    ExperimentSchedule,
    ExperimentSummary,
    ScientificExperiment,
)
from goat.experiments.engine import ScientificExperimentEngine
from goat.experiments.lifecycle.engine import ScientificExperimentLifecycleEngine
from goat.experiments.manifests.engine import ExperimentManifestEngine
from goat.experiments.persistence.sqlite import (
    ExperimentPersistenceContext,
    ExperimentRepository,
    LifecycleRepository,
    ManifestRepository,
    ReplayRepository,
    ScheduleRepository,
    SummaryRepository,
    init_experiment_db,
)
from goat.experiments.replay.engine import ExperimentReplayEngine
from goat.experiments.reporting.reports import (
    generate_executive_summary,
    generate_experiment_report,
    generate_json_report,
    generate_lifecycle_report,
    generate_manifest_report,
    generate_replay_report,
)
from goat.experiments.scheduling.engine import ExperimentSchedulingEngine

__all__ = [
    # v0.9 Step 9.3 Exports
    "ExperimentLifecycle",
    "ExperimentManifest",
    "ExperimentManifestEngine",
    "ExperimentPersistenceContext",
    "ExperimentPriority",
    "ExperimentReplay",
    "ExperimentReplayEngine",
    "ExperimentRepository",
    "ExperimentSchedule",
    "ExperimentSchedulingEngine",
    "ExperimentStatus",
    "ExperimentSummary",
    "ExperimentType",
    "LifecycleRepository",
    "ManifestRepository",
    "ReplayRepository",
    "ScheduleRepository",
    "ScientificExperiment",
    "ScientificExperimentEngine",
    "ScientificExperimentLifecycleEngine",
    "SummaryRepository",
    "compute_canonical_sha256",
    "compute_experiment_id",
    "compute_lifecycle_id",
    "compute_manifest_id",
    "compute_replay_id",
    "compute_schedule_id",
    "compute_summary_id",
    "generate_executive_summary",
    "generate_experiment_report",
    "generate_json_report",
    "generate_lifecycle_report",
    "generate_manifest_report",
    "generate_replay_report",
    "init_experiment_db",
    "serialize_canonical_json",
    # Legacy v0.7 Backward Compatibility Exports
    "ExperimentAuditEvent",
    "ExperimentContext",
    "ExperimentExecutor",
    "ExperimentOutcome",
    "ExperimentProtocol",
    "ExperimentReport",
    "ExperimentResult",
    "ExperimentValidationError",
    "HypothesisRecord",
    "HypothesisRegistry",
    "HypothesisStatus",
    "SQLiteExperimentRepository",
    "compute_experiment_fingerprint",
    "compute_hypothesis_id",
    "compute_protocol_id",
    "compute_result_id",
]
