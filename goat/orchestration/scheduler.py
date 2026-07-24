"""
Project GOAT v0.5 — Experiment Scheduler & Lifecycle Orchestrator

Coordinates 10-state CampaignStatus transitions, pre-flight data integrity verification,
WorkerPool dispatching, Option A graceful cancellation, Benjamini-Hochberg FDR correction,
EdgeRegistry updates, and monotonic event_sequence structured logging.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import threading
from typing import Any, Callable

import pandas as pd
from pydantic import ValidationError
import structlog

from goat import __version__ as GOAT_VERSION
from goat.config import GoatSettings
from goat.orchestration.campaign import (
    CampaignDefinition,
    CampaignFailure,
    CampaignLifecycleLogEntry,
    CampaignManifest,
    CampaignStatus,
    ExperimentStatus,
    InfrastructureFailure,
    ProvenanceMismatchError,
    QueueSnapshot,
    ValidationFailure,
)
from goat.orchestration.checkpoint import CheckpointManager
from goat.orchestration.queue import ExperimentQueue, ExperimentTask
from goat.orchestration.report import CampaignReportGenerator
from goat.orchestration.worker import WorkerPool
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.multiple_testing import benjamini_hochberg_fdr
from goat.research.hypothesis.registry import EdgeRegistry
from goat.research.hypothesis.result import HypothesisResult
from goat.data.schemas import Timeframe
from goat.data.storage.parquet import ParquetStorage

_log = structlog.get_logger(__name__)

# Valid state transitions for CampaignStatus
VALID_CAMPAIGN_TRANSITIONS: dict[CampaignStatus, set[CampaignStatus]] = {
    CampaignStatus.CREATED: {CampaignStatus.VALIDATING, CampaignStatus.CANCELLED},
    CampaignStatus.VALIDATING: {CampaignStatus.QUEUED, CampaignStatus.FAILED, CampaignStatus.CANCELLED},
    CampaignStatus.QUEUED: {CampaignStatus.RUNNING, CampaignStatus.CANCELLED},
    CampaignStatus.RUNNING: {
        CampaignStatus.PAUSING,
        CampaignStatus.COMPLETED,
        CampaignStatus.FAILED,
        CampaignStatus.CANCELLED,
    },
    CampaignStatus.PAUSING: {CampaignStatus.PAUSED, CampaignStatus.CANCELLED},
    CampaignStatus.PAUSED: {CampaignStatus.RESUMING, CampaignStatus.CANCELLED},
    CampaignStatus.RESUMING: {CampaignStatus.RUNNING, CampaignStatus.FAILED, CampaignStatus.CANCELLED},
    CampaignStatus.COMPLETED: set(),  # Terminal
    CampaignStatus.FAILED: set(),     # Terminal
    CampaignStatus.CANCELLED: set(),  # Terminal
}


def compute_configuration_hash(
    hypothesis_grid: list[HypothesisDefinition],
    symbols: list[str],
    timeframes: list[str],
    master_seed: int,
    fdr_alpha: float,
    version: str = "v0.5.0",
) -> str:
    """Compute deterministic SHA256 configuration_hash for a campaign setup."""
    grid_payload = [
        {"id": h.hypothesis_id, "version": h.version, "cond": h.causal_condition, "params": h.condition_parameters}
        for h in hypothesis_grid
    ]
    payload = {
        "fdr_alpha": float(fdr_alpha),
        "grid": grid_payload,
        "master_seed": int(master_seed),
        "symbols": sorted(symbols),
        "timeframes": sorted(timeframes),
        "version": str(version),
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:16]
    return f"cfg_{digest}"


def generate_campaign_id(name: str) -> str:
    """Generate unique operational campaign execution ID: CMP-<UTC_TIMESTAMP>-<HEX_ENTROPY>."""
    now_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    entropy = hashlib.sha256(os.urandom(16)).hexdigest()[:6].upper()
    slug = "".join(c if c.isalnum() else "_" for c in name).strip("_")[:12]
    return f"CMP-{now_str}-{entropy}"


def sort_nested_dict(val: Any) -> Any:
    """Recursively sort dictionary keys and lists if elements are dicts."""
    if isinstance(val, dict):
        return {k: sort_nested_dict(v) for k, v in sorted(val.items())}
    elif isinstance(val, list):
        return [sort_nested_dict(x) for x in val]
    return val


def compute_experiment_id(
    hypothesis: HypothesisDefinition,
    symbol: str,
    timeframe: str,
    dataset_fingerprint: str = "",
    experiment_hash_schema: int = 1,
    experiment_hash_algorithm: str = "SHA256",
    goat_version: str = GOAT_VERSION,
) -> str:
    """Compute deterministic canonical experiment ID (EXP_<SHA256[:16]>).

    Follows v0.5 Architecture Specification Section 2.C:
    1. Construct payload with primitive fields.
    2. Sort keys recursively at every level.
    3. Serialize to compact single-line JSON: json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True).
    4. Encode UTF-8 bytes.
    5. SHA256 digest truncated to 16 hex characters prefixed with 'EXP_'.
    """
    payload = {
        "causal_condition": sort_nested_dict(hypothesis.causal_condition),
        "condition_parameters": sort_nested_dict(hypothesis.condition_parameters),
        "dataset_fingerprint": str(dataset_fingerprint),
        "event_spacing_bars": int(hypothesis.event_spacing_bars),
        "experiment_hash_algorithm": str(experiment_hash_algorithm),
        "experiment_hash_schema": int(experiment_hash_schema),
        "forward_horizon": int(hypothesis.forward_horizon),
        "forward_outcome_metric": str(hypothesis.forward_outcome_metric),
        "goat_version": str(goat_version),
        "hypothesis_id": str(hypothesis.hypothesis_id),
        "hypothesis_version": str(hypothesis.version),
        "statistical_test": str(hypothesis.statistical_test),
        "symbol": str(symbol),
        "timeframe": str(timeframe),
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:16]
    return f"EXP_{digest}"


def compute_dependency_lockfile_hash(
    workspace_dir: Path | None = None,
    allow_cwd_fallback: bool = True,
) -> str:
    """Compute deterministic SHA256 hex digest of authoritative dependency specification.

    Prefers lockfiles (poetry.lock, uv.lock, requirements.lock, requirements.txt) if present,
    falling back to pyproject.toml as the primary dependency specification.
    """
    candidate_files = [
        "poetry.lock",
        "uv.lock",
        "requirements.lock",
        "requirements.txt",
        "pyproject.toml",
    ]

    target_file: Path | None = None

    if workspace_dir is not None:
        for fname in candidate_files:
            candidate = workspace_dir / fname
            if candidate.exists() and candidate.is_file():
                target_file = candidate
                break

    if target_file is None and allow_cwd_fallback:
        cwd = Path.cwd()
        for fname in candidate_files:
            candidate = cwd / fname
            if candidate.exists() and candidate.is_file():
                target_file = candidate
                break

    if target_file is None:
        searched = str(workspace_dir) if workspace_dir else str(Path.cwd())
        raise InfrastructureFailure(
            f"Authoritative dependency specification file not found in '{searched}'. Checked candidates: {candidate_files}"
        )

    try:
        data_bytes = target_file.read_bytes()
        return hashlib.sha256(data_bytes).hexdigest()
    except Exception as exc:
        raise InfrastructureFailure(
            f"Failed to read authoritative dependency file '{target_file}': {exc}"
        ) from exc


class ExperimentScheduler:
    """Orchestrates campaign state transitions, task execution, and result collection."""

    def __init__(
        self,
        settings: GoatSettings | None = None,
        storage: ParquetStorage | None = None,
    ) -> None:
        self.settings = settings or GoatSettings()
        self.storage = storage or ParquetStorage(
            self.settings.get_raw_data_dir(),
            self.settings.get_processed_data_dir(),
        )
        self.checkpoint_manager = CheckpointManager(
            checkpoint_format_version=self.settings.checkpoint_format_version
        )
        self.report_generator = CampaignReportGenerator(settings=self.settings)
        self.edge_registry = EdgeRegistry(
            registry_path=self.settings.get_edge_registry_path()
        )

        self.status = CampaignStatus.CREATED
        self.lifecycle_history: list[CampaignLifecycleLogEntry] = []
        self.event_sequence: int = 0
        self.cancel_requested: bool = False
        self.log_file_path: Path | None = None
        self.log_enabled: bool = True
        self._log_lock = threading.Lock()

    def _log_event(
        self,
        level: str,
        event_type: str,
        message: str,
        component: str = "Scheduler",
        campaign_id: str = "",
        experiment_id: str = "",
        worker_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Emit structured log event with monotonic event_sequence to structlog and campaign.log.jsonl."""
        if not self.log_enabled:
            return

        with self._log_lock:
            self.event_sequence += 1
            seq = self.event_sequence
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            meta = metadata or {}

            record = {
                "log_schema_version": self.settings.log_schema_version,
                "event_sequence": seq,
                "utc_timestamp": now_iso,
                "log_level": level,
                "component": component,
                "event_type": event_type,
                "campaign_id": campaign_id,
                "experiment_id": experiment_id,
                "worker_id": worker_id,
                "message": message,
                "metadata": meta,
            }

            _log.msg(
                event_type,
                log_schema_version=self.settings.log_schema_version,
                event_sequence=seq,
                log_level=level,
                component=component,
                event_type=event_type,
                campaign_id=campaign_id,
                experiment_id=experiment_id,
                worker_id=worker_id,
                message=message,
                metadata=meta,
            )

            if self.log_file_path:
                try:
                    self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(self.log_file_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(record, sort_keys=True) + "\n")
                except Exception as exc:
                    _log.error(
                        "log_file_write_failed",
                        component=component,
                        error=str(exc),
                        path=str(self.log_file_path),
                    )

    def _transition_status(
        self,
        new_status: CampaignStatus,
        reason: str,
        component: str = "Scheduler",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Transition campaign status validating legal state transitions."""
        valid_targets = VALID_CAMPAIGN_TRANSITIONS.get(self.status, set())
        if new_status not in valid_targets:
            raise ValueError(
                f"Invalid CampaignStatus transition: cannot jump from {self.status.value} to {new_status.value}."
            )

        prev_status = self.status
        self.status = new_status

        entry = CampaignLifecycleLogEntry(
            previous_state=prev_status,
            new_state=new_status,
            reason=reason,
            triggering_component=component,
            metadata=metadata or {},
        )
        self.lifecycle_history.append(entry)

        self._log_event(
            level="INFO",
            event_type="campaign_status_transition",
            message=f"Campaign state changed from {prev_status.value} to {new_status.value}: {reason}",
            component=component,
            metadata={"previous_state": prev_status.value, "new_state": new_status.value},
        )

    def _build_campaign_manifest(
        self,
        campaign_id: str,
        name: str,
        description: str,
        configuration_hash: str,
        fdr_alpha: float,
        symbols: list[str],
        timeframes: list[str],
        master_seed: int,
        max_workers: int,
        fingerprint_map: dict[tuple[str, str], str],
        hypothesis_grid: list[HypothesisDefinition],
        tasks: list[ExperimentTask],
        queue: ExperimentQueue,
    ) -> CampaignManifest:
        """Build authoritative 6-section CampaignManifest instance."""
        return CampaignManifest(
            manifest_schema_version=self.settings.manifest_schema_version,
            provenance_schema_version=self.settings.provenance_schema_version,
            campaign={
                "campaign_id": campaign_id,
                "name": name,
                "description": description,
                "status": self.status.value,
            },
            configuration={
                "configuration_hash": configuration_hash,
                "fdr_alpha": fdr_alpha,
                "symbol_scope": symbols,
                "timeframe_scope": timeframes,
            },
            environment={
                "goat_version": GOAT_VERSION,
                "git_commit_sha": os.getenv("GIT_COMMIT_SHA", "unknown_commit"),
                "git_branch": os.getenv("GIT_BRANCH", "develop"),
                "python_version": sys.version.split()[0],
                "operating_system": platform.platform(),
                "cpu_architecture": platform.machine(),
                "machine_timezone": str(datetime.now().astimezone().tzinfo),
                "utc_execution_timestamp": datetime.now(timezone.utc).isoformat(),
                "dependency_lockfile_hash": compute_dependency_lockfile_hash(self.settings.get_campaign_data_dir().parent),
            },
            research_provenance={
                "experiment_hash_schema": self.settings.experiment_hash_schema,
                "experiment_hash_algorithm": self.settings.experiment_hash_algorithm,
                "dataset_fingerprint": list(fingerprint_map.values())[0] if fingerprint_map else "N/A",
                "dataset_version": "v0.3.0",
                "hypothesis_versions": {h.hypothesis_id: h.version for h in hypothesis_grid},
            },
            execution_configuration={
                "master_seed": master_seed,
                "worker_count": max_workers,
                "execution_mode": "PARALLEL",
                "checkpoint_format_version": self.settings.checkpoint_format_version,
            },
            validation={
                "preflight_integrity_verified": True,
                "total_experiments": len(tasks),
                "completed_experiments": len([t for t in queue.get_all_tasks() if t.status == ExperimentStatus.COMPLETED]),
                "failed_experiments": len([t for t in queue.get_all_tasks() if t.status == ExperimentStatus.FAILED]),
            },
            lifecycle_history=list(self.lifecycle_history),
        )

    def _build_campaign_statistics(
        self,
        campaign_id: str,
        configuration_hash: str,
        tasks: list[ExperimentTask],
        queue: ExperimentQueue,
        final_results: list[HypothesisResult],
    ) -> dict[str, Any]:
        """Build authoritative campaign statistics dictionary."""
        return {
            "campaign_id": campaign_id,
            "configuration_hash": configuration_hash,
            "total_experiments": len(tasks),
            "completed_count": len([t for t in queue.get_all_tasks() if t.status == ExperimentStatus.COMPLETED]),
            "failed_count": len([t for t in queue.get_all_tasks() if t.status == ExperimentStatus.FAILED]),
            "skipped_count": len([t for t in queue.get_all_tasks() if t.status == ExperimentStatus.SKIPPED]),
            "cancelled_count": len([t for t in queue.get_all_tasks() if t.status == ExperimentStatus.CANCELLED]),
            "total_retries": sum(t.retry_count for t in queue.get_all_tasks()),
            "supported_edges": len([r for r in final_results if r.validation_status == "SUPPORTED"]),
        }

    def perform_preflight_verification(
        self,
        symbols: list[str],
        timeframes: list[str],
        expected_fingerprints: dict[tuple[str, str], str] | None = None,
    ) -> tuple[dict[tuple[str, str], pd.DataFrame], dict[tuple[str, str], pd.DataFrame], dict[tuple[str, str], str]]:
        """Pre-flight integrity verification of dataset files and fingerprints.

        Raises:
            ProvenanceMismatchError: If fingerprints do not match or market data is missing.
        """
        self._log_event("INFO", "validation_started", "Starting pre-flight data integrity verification")

        df_map: dict[tuple[str, str], pd.DataFrame] = {}
        outcomes_map: dict[tuple[str, str], pd.DataFrame] = {}
        fingerprint_map: dict[tuple[str, str], str] = {}

        from goat.data.processing.aggregation import aggregate_ticks_to_candles
        from goat.research.dataset import ResearchDatasetBuilder
        from goat.research.outcomes import ForwardOutcomeTable

        builder = ResearchDatasetBuilder()
        fwd_gen = ForwardOutcomeTable(horizons=self.settings.forward_horizons)

        for sym in symbols:
            for tf_str in timeframes:
                key = (sym, tf_str)
                timeframe_enum = Timeframe(tf_str)
                df_raw = self.storage.read_candles(sym, timeframe_enum)

                if df_raw.empty:
                    # Fallback: attempt reading ticks and aggregating
                    ticks_df = self.storage.read_ticks(sym)
                    if not ticks_df.empty:
                        df_raw = aggregate_ticks_to_candles(ticks_df, timeframe_enum, source="historical")

                if df_raw.empty:
                    raise ProvenanceMismatchError(f"Missing market data for symbol={sym}, timeframe={tf_str}")

                # Build dataset and forward outcomes
                research_df, manifest = builder.build_dataset(df_raw, symbol=sym, timeframe=tf_str)
                outcomes_df = fwd_gen.compute_outcomes(research_df)
                actual_fp = manifest.dataset_id

                if expected_fingerprints and key in expected_fingerprints:
                    exp_fp = expected_fingerprints[key]
                    if actual_fp != exp_fp:
                        raise ProvenanceMismatchError(
                            f"Fingerprint mismatch for {key}: expected={exp_fp}, actual={actual_fp}"
                        )

                df_map[key] = research_df
                outcomes_map[key] = outcomes_df
                fingerprint_map[key] = actual_fp

        self._log_event("INFO", "provenance_verified", "Pre-flight integrity verification passed cleanly")
        return df_map, outcomes_map, fingerprint_map

    def run_campaign(
        self,
        campaign_def: CampaignDefinition,
        hypothesis_grid: list[HypothesisDefinition],
        symbols: list[str] | None = None,
        timeframes: list[str] | None = None,
        expected_fingerprints: dict[tuple[str, str], str] | None = None,
    ) -> Path:
        """Launch and execute a batch campaign.

        Args:
            campaign_def: CampaignDefinition specification.
            hypothesis_grid: List of HypothesisDefinitions to evaluate.
            symbols: Symbol scope list.
            timeframes: Timeframe scope list.
            expected_fingerprints: Expected fingerprint map for pre-flight check.

        Returns:
            Path to the output campaign directory.
        """
        symbols = symbols or campaign_def.symbol_scope
        timeframes = timeframes or campaign_def.timeframe_scope

        campaign_dir = self.settings.get_campaign_data_dir() / campaign_def.campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)
        self.log_file_path = campaign_dir / "campaign.log.jsonl"

        self._log_event("INFO", "campaign_started", f"Launching campaign '{campaign_def.name}'", campaign_id=campaign_def.campaign_id)

        try:
            # 1. Transition: CREATED -> VALIDATING
            self._transition_status(CampaignStatus.VALIDATING, "Beginning pre-flight integrity verification")

            # 2. Pre-flight verification
            df_map, outcomes_map, fingerprint_map = self.perform_preflight_verification(
                symbols=symbols,
                timeframes=timeframes,
                expected_fingerprints=expected_fingerprints,
            )

            # 3. Build ExperimentTasks grid
            tasks: list[ExperimentTask] = []
            for hyp in hypothesis_grid:
                for sym in symbols:
                    for tf in timeframes:
                        fp = fingerprint_map.get((sym, tf), "unknown")
                        exp_id = compute_experiment_id(
                            hypothesis=hyp,
                            symbol=sym,
                            timeframe=tf,
                            dataset_fingerprint=fp,
                            experiment_hash_schema=self.settings.experiment_hash_schema,
                            experiment_hash_algorithm=self.settings.experiment_hash_algorithm,
                            goat_version=GOAT_VERSION,
                        )
                        task = ExperimentTask(
                            experiment_id=exp_id,
                            hypothesis=hyp,
                            symbol=sym,
                            timeframe=tf,
                            priority=0,
                        )
                        tasks.append(task)

            queue = ExperimentQueue(
                campaign_id=campaign_def.campaign_id,
                configuration_hash=campaign_def.configuration_hash,
                tasks=tasks,
            )

            # 4. Transition: VALIDATING -> QUEUED -> RUNNING
            self._transition_status(CampaignStatus.QUEUED, f"Queued {len(tasks)} experiment tasks")
            self._transition_status(CampaignStatus.RUNNING, "Starting parallel worker execution")

            def worker_log_callback(
                level: str,
                event_type: str,
                message: str,
                component: str = "Worker",
                experiment_id: str = "",
                worker_id: str = "",
                metadata: dict[str, Any] | None = None,
            ) -> None:
                self._log_event(
                    level=level,
                    event_type=event_type,
                    message=message,
                    component=component,
                    campaign_id=campaign_def.campaign_id,
                    experiment_id=experiment_id,
                    worker_id=worker_id,
                    metadata=metadata,
                )

            worker_pool = WorkerPool(
                max_workers=campaign_def.max_workers,
                master_seed=campaign_def.master_seed,
                settings=self.settings,
                log_callback=worker_log_callback,
            )

            completed_results: list[HypothesisResult] = []
            tasks_processed_since_checkpoint = 0

            # 5. Worker execution loop
            while not queue.is_complete():
                if self.cancel_requested:
                    self._log_event("WARNING", "campaign_cancelling", "Cancellation requested. Option A graceful completion.")
                    break

                batch: list[ExperimentTask] = []
                while len(batch) < campaign_def.max_workers:
                    next_task = queue.get_next_task()
                    if not next_task:
                        break
                    queue.update_status(next_task.experiment_id, ExperimentStatus.RUNNING)
                    batch.append(next_task)

                if not batch:
                    break

                batch_results = worker_pool.execute_batch(
                    tasks=batch,
                    df_map=df_map,
                    outcomes_map=outcomes_map,
                    fingerprint_map=fingerprint_map,
                )

                for task, res, err in batch_results:
                    if res:
                        queue.update_status(task.experiment_id, ExperimentStatus.COMPLETED, result=res.model_dump(mode="json"))
                        completed_results.append(res)
                    else:
                        queue.update_status(task.experiment_id, ExperimentStatus.FAILED)
                        if task.retry_count < self.settings.max_experiment_retries:
                            task.retry_count += 1
                            queue.update_status(task.experiment_id, ExperimentStatus.PENDING)
                            self._log_event("WARNING", "experiment_retried", f"Task {task.experiment_id} retrying ({task.retry_count}/{self.settings.max_experiment_retries})")
                        else:
                            self._log_event("ERROR", "experiment_failed", f"Task {task.experiment_id} failed: {err}")

                    tasks_processed_since_checkpoint += 1

                # Checkpoint interval trigger
                if tasks_processed_since_checkpoint >= self.settings.checkpoint_interval_tasks:
                    snapshot = queue.take_snapshot(last_event_sequence=self.event_sequence)
                    self.checkpoint_manager.save_checkpoint(snapshot, campaign_dir)
                    tasks_processed_since_checkpoint = 0

            # 6. Final state transition
            if self.cancel_requested:
                self._transition_status(CampaignStatus.CANCELLED, "Campaign execution cancelled by user signal")
            else:
                self._transition_status(CampaignStatus.COMPLETED, "All experiment tasks evaluated successfully")

            # 7. Apply Benjamini-Hochberg FDR correction across batch results
            if completed_results:
                raw_pvals = [r.raw_p_value for r in completed_results]
                q_values, is_rejected = benjamini_hochberg_fdr(raw_pvals, alpha=campaign_def.fdr_alpha)
                final_results = []
                for res, q_val, rej in zip(completed_results, q_values, is_rejected):
                    res_copy = res.model_copy()
                    res_copy.adjusted_q_value = float(q_val)
                    if rej and res_copy.sufficiency_status == "SUFFICIENT":
                        res_copy.validation_status = "SUPPORTED"
                    else:
                        res_copy.validation_status = "REJECTED"
                    final_results.append(res_copy)
                final_results.sort(key=lambda r: (0, r.symbol, r.timeframe, r.hypothesis_id))
            else:
                final_results = []

            # 8. Record evaluation results in EdgeRegistry
            for r in final_results:
                self.edge_registry.register_hypothesis(
                    HypothesisDefinition(
                        hypothesis_id=r.hypothesis_id,
                        version=r.version,
                        name=f"Hypothesis {r.hypothesis_id}",
                        description="Campaign evaluated edge",
                        causal_condition={"primitive": "custom"},
                    )
                )
                self.edge_registry.record_evaluation_result(r)

            # 9. Build 6-section Manifest and write all artifacts
            self._log_event("INFO", "campaign_completed", f"Campaign execution completed successfully in status {self.status.value}")
            final_snapshot = queue.take_snapshot(last_event_sequence=self.event_sequence)

            manifest = self._build_campaign_manifest(
                campaign_id=campaign_def.campaign_id,
                name=campaign_def.name,
                description=campaign_def.description,
                configuration_hash=campaign_def.configuration_hash,
                fdr_alpha=campaign_def.fdr_alpha,
                symbols=symbols,
                timeframes=timeframes,
                master_seed=campaign_def.master_seed,
                max_workers=campaign_def.max_workers,
                fingerprint_map=fingerprint_map,
                hypothesis_grid=hypothesis_grid,
                tasks=tasks,
                queue=queue,
            )

            statistics = self._build_campaign_statistics(
                campaign_id=campaign_def.campaign_id,
                configuration_hash=campaign_def.configuration_hash,
                tasks=tasks,
                queue=queue,
                final_results=final_results,
            )

            self.report_generator.write_all_artifacts(
                manifest=manifest,
                snapshot=final_snapshot,
                results=final_results,
                statistics=statistics,
                output_dir=campaign_dir,
            )

            return campaign_dir

        except Exception as exc:
            if self.status != CampaignStatus.FAILED:
                try:
                    self._transition_status(CampaignStatus.FAILED, f"Campaign execution failed: {exc}")
                except ValueError:
                    self.status = CampaignStatus.FAILED

            _log.error("campaign_execution_failed", component="Scheduler", error=str(exc))
            raise CampaignFailure(f"Campaign execution aborted: {exc}") from exc

    def get_status(self, campaign_id: str) -> dict[str, Any]:
        """Retrieve persisted campaign status without mutating campaign execution."""
        camp_dir = self.settings.get_campaign_data_dir() / campaign_id
        manifest_path = camp_dir / "campaign_manifest.json"

        if not manifest_path.exists():
            raise InfrastructureFailure(f"Campaign '{campaign_id}' not found in {self.settings.get_campaign_data_dir()}")

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        camp_info = manifest_data.get("campaign", {})
        val_info = manifest_data.get("validation", {})
        cfg_info = manifest_data.get("configuration", {})

        return {
            "campaign_id": camp_info.get("campaign_id", campaign_id),
            "status": camp_info.get("status", "UNKNOWN"),
            "configuration_hash": cfg_info.get("configuration_hash", "N/A"),
            "total_experiments": val_info.get("total_experiments", 0),
            "completed_experiments": val_info.get("completed_experiments", 0),
            "failed_experiments": val_info.get("failed_experiments", 0),
        }

    def cancel_campaign(self, campaign_id: str) -> Path:
        """Cancel a running or paused campaign using Option A graceful cancellation semantics."""
        camp_dir = self.settings.get_campaign_data_dir() / campaign_id
        manifest_path = camp_dir / "campaign_manifest.json"

        if not manifest_path.exists():
            raise InfrastructureFailure(f"Campaign '{campaign_id}' not found in {self.settings.get_campaign_data_dir()}")

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        camp_info = manifest_data.get("campaign", {})
        current_status_str = camp_info.get("status", "CREATED")
        current_status = CampaignStatus(current_status_str)

        if current_status in (CampaignStatus.COMPLETED, CampaignStatus.FAILED, CampaignStatus.CANCELLED):
            raise ValueError(f"Cannot cancel campaign '{campaign_id}': status is already terminal '{current_status.value}'.")

        self.cancel_requested = True
        self.status = current_status
        self._transition_status(CampaignStatus.CANCELLED, "Campaign cancelled by request")

        manifest_data["campaign"]["status"] = CampaignStatus.CANCELLED.value
        manifest_data["lifecycle_history"] = [entry.model_dump(mode="json") for entry in self.lifecycle_history]

        manifest_path.write_text(json.dumps(manifest_data, indent=2, sort_keys=True), encoding="utf-8")
        self._log_event("WARNING", "campaign_cancelled", f"Campaign '{campaign_id}' set to CANCELLED", campaign_id=campaign_id)
        return camp_dir

    def generate_reports(self, campaign_id: str) -> Path:
        """Generate/regenerate reports for an existing campaign from persisted artifacts without re-running experiments."""
        camp_dir = self.settings.get_campaign_data_dir() / campaign_id
        manifest_path = camp_dir / "campaign_manifest.json"
        checkpoint_path = camp_dir / "checkpoint.json"
        results_path = camp_dir / "experiment_results.json"
        stats_path = camp_dir / "campaign_statistics.json"

        if not manifest_path.exists():
            raise InfrastructureFailure(f"Required campaign manifest artifact missing for campaign '{campaign_id}' at '{manifest_path}'")
        if not checkpoint_path.exists():
            raise InfrastructureFailure(f"Required campaign checkpoint artifact missing for campaign '{campaign_id}' at '{checkpoint_path}'")

        try:
            manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest = CampaignManifest.model_validate(manifest_data)
        except Exception as exc:
            raise InfrastructureFailure(
                f"Corrupted or invalid campaign manifest artifact for campaign '{campaign_id}' at '{manifest_path}': {exc}"
            ) from exc

        try:
            snapshot = self.checkpoint_manager.load_checkpoint(checkpoint_path)
        except Exception as exc:
            raise InfrastructureFailure(
                f"Corrupted or invalid checkpoint artifact for campaign '{campaign_id}' at '{checkpoint_path}': {exc}"
            ) from exc

        results: list[HypothesisResult] = []
        if results_path.exists():
            try:
                res_list = json.loads(results_path.read_text(encoding="utf-8"))
                if not isinstance(res_list, list):
                    raise ValueError("experiment_results.json content must be a JSON list")
                results = [HypothesisResult.model_validate(r) for r in res_list]
            except Exception as exc:
                raise InfrastructureFailure(
                    f"Corrupted or invalid experiment results artifact for campaign '{campaign_id}' at '{results_path}': {exc}"
                ) from exc
        elif snapshot.completed_task_ids:
            raise InfrastructureFailure(
                f"Missing required experiment results artifact for campaign '{campaign_id}' at '{results_path}' "
                f"(snapshot indicates {len(snapshot.completed_task_ids)} completed tasks)"
            )

        stats: dict[str, Any] = {}
        if stats_path.exists():
            try:
                stats = json.loads(stats_path.read_text(encoding="utf-8"))
                if not isinstance(stats, dict):
                    raise ValueError("campaign_statistics.json content must be a JSON object")
            except Exception as exc:
                raise InfrastructureFailure(
                    f"Corrupted or invalid statistics artifact for campaign '{campaign_id}' at '{stats_path}': {exc}"
                ) from exc
        else:
            stats = self._build_campaign_statistics(
                campaign_id=campaign_id,
                configuration_hash=snapshot.configuration_hash,
                tasks=[],
                queue=ExperimentQueue.from_snapshot(snapshot, []),
                final_results=results,
            )

        self.report_generator.write_all_artifacts(
            manifest=manifest,
            snapshot=snapshot,
            results=results,
            statistics=stats,
            output_dir=camp_dir,
        )
        return camp_dir

    def resume_campaign(
        self,
        campaign_id: str,
        hypothesis_grid: list[HypothesisDefinition] | None = None,
    ) -> Path:
        """Resume execution of an interrupted or paused campaign from its checkpoint.json."""
        camp_dir = self.settings.get_campaign_data_dir() / campaign_id
        checkpoint_file = camp_dir / "checkpoint.json"
        manifest_file = camp_dir / "campaign_manifest.json"

        if not checkpoint_file.exists() or not manifest_file.exists():
            raise InfrastructureFailure(f"Cannot resume campaign '{campaign_id}': checkpoint or manifest missing.")

        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        m_ver = manifest_data.get("manifest_schema_version", 1)
        if m_ver > self.settings.manifest_schema_version:
            raise ValidationFailure(f"Incompatible manifest schema version {m_ver} > {self.settings.manifest_schema_version}")

        camp_info = manifest_data.get("campaign", {})
        current_status_str = camp_info.get("status", "CREATED")
        current_status = CampaignStatus(current_status_str)

        if current_status in (CampaignStatus.COMPLETED, CampaignStatus.FAILED, CampaignStatus.CANCELLED):
            raise ValueError(f"Cannot resume campaign '{campaign_id}': status is terminal '{current_status.value}'.")

        snapshot = self.checkpoint_manager.load_checkpoint(checkpoint_file)

        # Restore sequence continuity & logging path
        self.event_sequence = snapshot.last_event_sequence
        self.log_file_path = camp_dir / "campaign.log.jsonl"

        # Restore lifecycle history
        hist_raw = manifest_data.get("lifecycle_history", [])
        self.lifecycle_history = [
            CampaignLifecycleLogEntry(
                utc_timestamp=datetime.fromisoformat(h["utc_timestamp"]) if isinstance(h.get("utc_timestamp"), str) else datetime.now(timezone.utc),
                previous_state=CampaignStatus(h["previous_state"]),
                new_state=CampaignStatus(h["new_state"]),
                reason=h.get("reason", ""),
                triggering_component=h.get("triggering_component", "Scheduler"),
                metadata=h.get("metadata", {}),
            )
            for h in hist_raw
        ]

        self.status = current_status
        if self.status not in (CampaignStatus.RESUMING, CampaignStatus.RUNNING):
            self._transition_status(CampaignStatus.RESUMING, f"Resuming campaign from {checkpoint_file.name}")
        if self.status == CampaignStatus.RESUMING:
            self._transition_status(CampaignStatus.RUNNING, "Starting worker execution for resumed campaign")

        cfg_info = manifest_data.get("configuration", {})
        exec_info = manifest_data.get("execution_configuration", {})
        symbols = cfg_info.get("symbol_scope", ["R_10"])
        timeframes = cfg_info.get("timeframe_scope", ["M1"])
        master_seed = exec_info.get("master_seed", 42)
        max_workers = exec_info.get("worker_count", 4)
        fdr_alpha = cfg_info.get("fdr_alpha", 0.05)

        # Pre-flight integrity verification before scientific execution
        df_map, outcomes_map, fingerprint_map = self.perform_preflight_verification(
            symbols=symbols,
            timeframes=timeframes,
        )

        if hypothesis_grid is None:
            from scripts.run_hypothesis_experiment import build_volatility_compression_grid
            hypothesis_grid = build_volatility_compression_grid(symbols=symbols, timeframes=timeframes)

        tasks: list[ExperimentTask] = []
        for hyp in hypothesis_grid:
            for sym in symbols:
                for tf in timeframes:
                    fp = fingerprint_map.get((sym, tf), "unknown")
                    exp_id = compute_experiment_id(
                        hypothesis=hyp,
                        symbol=sym,
                        timeframe=tf,
                        dataset_fingerprint=fp,
                        experiment_hash_schema=self.settings.experiment_hash_schema,
                        experiment_hash_algorithm=self.settings.experiment_hash_algorithm,
                        goat_version=GOAT_VERSION,
                    )
                    task = ExperimentTask(
                        experiment_id=exp_id,
                        hypothesis=hyp,
                        symbol=sym,
                        timeframe=tf,
                        priority=0,
                    )
                    tasks.append(task)

        # Reconstruct ExperimentQueue from snapshot (interrupted RUNNING tasks become PENDING, COMPLETED stay COMPLETED)
        queue = ExperimentQueue.from_snapshot(snapshot, tasks=tasks)

        worker_pool = WorkerPool(
            max_workers=max_workers,
            master_seed=master_seed,
            settings=self.settings,
            log_callback=lambda level, event_type, message, component="Worker", experiment_id="", worker_id="", metadata=None: self._log_event(
                level=level,
                event_type=event_type,
                message=message,
                component=component,
                campaign_id=campaign_id,
                experiment_id=experiment_id,
                worker_id=worker_id,
                metadata=metadata,
            ),
        )

        completed_results: list[HypothesisResult] = []
        for exp_id, res_dict in snapshot.task_results.items():
            try:
                completed_results.append(HypothesisResult.model_validate(res_dict))
            except (ValidationError, TypeError, ValueError, KeyError) as exc:
                raise InfrastructureFailure(
                    f"Corrupted or invalid completed task result in checkpoint for experiment '{exp_id}' in campaign '{campaign_id}': {exc}"
                ) from exc

        tasks_processed_since_checkpoint = 0

        while not queue.is_complete():
            if self.cancel_requested:
                self._log_event("WARNING", "campaign_cancelling", "Cancellation requested. Option A graceful completion.")
                break

            batch: list[ExperimentTask] = []
            while len(batch) < max_workers:
                next_task = queue.get_next_task()
                if not next_task:
                    break
                queue.update_status(next_task.experiment_id, ExperimentStatus.RUNNING)
                batch.append(next_task)

            if not batch:
                break

            batch_results = worker_pool.execute_batch(
                tasks=batch,
                df_map=df_map,
                outcomes_map=outcomes_map,
                fingerprint_map=fingerprint_map,
            )

            for task, res, err in batch_results:
                if res:
                    queue.update_status(task.experiment_id, ExperimentStatus.COMPLETED, result=res.model_dump(mode="json"))
                    completed_results.append(res)
                else:
                    queue.update_status(task.experiment_id, ExperimentStatus.FAILED)
                    if task.retry_count < self.settings.max_experiment_retries:
                        task.retry_count += 1
                        queue.update_status(task.experiment_id, ExperimentStatus.PENDING)
                        self._log_event("WARNING", "experiment_retried", f"Task {task.experiment_id} retrying ({task.retry_count}/{self.settings.max_experiment_retries})")
                    else:
                        self._log_event("ERROR", "experiment_failed", f"Task {task.experiment_id} failed: {err}")

                tasks_processed_since_checkpoint += 1

            if tasks_processed_since_checkpoint >= self.settings.checkpoint_interval_tasks:
                snp = queue.take_snapshot(last_event_sequence=self.event_sequence)
                self.checkpoint_manager.save_checkpoint(snp, camp_dir)
                tasks_processed_since_checkpoint = 0

        if self.cancel_requested:
            self._transition_status(CampaignStatus.CANCELLED, "Campaign execution cancelled by user signal")
        else:
            self._transition_status(CampaignStatus.COMPLETED, "All experiment tasks evaluated successfully")

        if completed_results:
            raw_pvals = [r.raw_p_value for r in completed_results]
            q_values, is_rejected = benjamini_hochberg_fdr(raw_pvals, alpha=fdr_alpha)
            final_results = []
            for res, q_val, rej in zip(completed_results, q_values, is_rejected):
                res_copy = res.model_copy()
                res_copy.adjusted_q_value = float(q_val)
                if rej and res_copy.sufficiency_status == "SUFFICIENT":
                    res_copy.validation_status = "SUPPORTED"
                else:
                    res_copy.validation_status = "REJECTED"
                final_results.append(res_copy)
            final_results.sort(key=lambda r: (0, r.symbol, r.timeframe, r.hypothesis_id))
        else:
            final_results = []

        for r in final_results:
            self.edge_registry.register_hypothesis(
                HypothesisDefinition(
                    hypothesis_id=r.hypothesis_id,
                    version=r.version,
                    name=f"Hypothesis {r.hypothesis_id}",
                    description="Campaign evaluated edge",
                    causal_condition={"primitive": "custom"},
                )
            )
            self.edge_registry.record_evaluation_result(r)

        self._log_event("INFO", "campaign_resumed_completed", f"Resumed campaign completed in status {self.status.value}")
        final_snapshot = queue.take_snapshot(last_event_sequence=self.event_sequence)

        manifest = self._build_campaign_manifest(
            campaign_id=campaign_id,
            name=camp_info.get("name", "Resumed Campaign"),
            description=camp_info.get("description", ""),
            configuration_hash=snapshot.configuration_hash,
            fdr_alpha=fdr_alpha,
            symbols=symbols,
            timeframes=timeframes,
            master_seed=master_seed,
            max_workers=max_workers,
            fingerprint_map=fingerprint_map,
            hypothesis_grid=hypothesis_grid,
            tasks=tasks,
            queue=queue,
        )

        statistics = self._build_campaign_statistics(
            campaign_id=campaign_id,
            configuration_hash=snapshot.configuration_hash,
            tasks=tasks,
            queue=queue,
            final_results=final_results,
        )

        self.report_generator.write_all_artifacts(
            manifest=manifest,
            snapshot=final_snapshot,
            results=final_results,
            statistics=statistics,
            output_dir=camp_dir,
        )

        return camp_dir
