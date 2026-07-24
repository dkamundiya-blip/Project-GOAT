"""
Project GOAT v0.5 — Worker Pool & Seed Derivation

Executes individual experiment tasks in parallel while enforcing generator-independent
deterministic random seed derivation (`canonical_seed_material`).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from typing import Any, Callable, Protocol

import numpy as np
import pandas as pd
import structlog

from goat.config import GoatSettings
from goat.orchestration.campaign import (
    ExperimentStatus,
    WorkerFailure,
)
from goat.orchestration.queue import ExperimentTask
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.experiment import ExperimentRunner
from goat.research.hypothesis.result import HypothesisResult

_log = structlog.get_logger(__name__)


class WorkerLogCallback(Protocol):
    """Callback interface for WorkerPool execution event logging."""

    def __call__(
        self,
        level: str,
        event_type: str,
        message: str,
        component: str = "Worker",
        experiment_id: str = "",
        worker_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        ...


def derive_canonical_seed_material(master_seed: int, experiment_id: str) -> bytes:
    """Derive deterministic 32-byte canonical seed material for a task.

    Args:
        master_seed: Campaign master random seed.
        experiment_id: Canonical experiment ID string.

    Returns:
        32 raw bytes from SHA256 digest.
    """
    payload = {
        "experiment_id": str(experiment_id),
        "master_seed": int(master_seed),
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    canonical_bytes = canonical_json.encode("utf-8")
    return hashlib.sha256(canonical_bytes).digest()


def seed_material_to_int(seed_material: bytes, num_bytes: int = 16) -> int:
    """Convert seed material bytes to big-endian integer."""
    return int.from_bytes(seed_material[:num_bytes], byteorder="big")


class WorkerPool:
    """Worker pool manager executing tasks concurrently."""

    def __init__(
        self,
        max_workers: int = 4,
        master_seed: int = 42,
        settings: GoatSettings | None = None,
        log_callback: WorkerLogCallback | Callable[..., None] | None = None,
    ) -> None:
        self.max_workers = max_workers
        self.master_seed = master_seed
        self.settings = settings or GoatSettings()
        self.runner = ExperimentRunner(settings=self.settings)
        self.log_callback = log_callback

    def execute_task(
        self,
        task: ExperimentTask,
        df: pd.DataFrame,
        outcomes_df: pd.DataFrame,
        dataset_fingerprint: str,
        worker_id: str = "worker_0",
    ) -> tuple[ExperimentTask, HypothesisResult | None, str | None]:
        """Execute a single experiment task deterministically.

        Args:
            task: The ExperimentTask instance.
            df: Input price DataFrame.
            outcomes_df: Forward outcome DataFrame.
            dataset_fingerprint: SHA256 dataset checksum.
            worker_id: Worker thread identity.

        Returns:
            Tuple of (task, HypothesisResult if successful else None, error_message if failed else None).
        """
        seed_bytes = derive_canonical_seed_material(self.master_seed, task.experiment_id)
        seed_int = seed_material_to_int(seed_bytes, num_bytes=16)

        if self.log_callback:
            self.log_callback(
                level="DEBUG",
                event_type="worker_task_started",
                message=f"Worker task started for {task.experiment_id}",
                component="Worker",
                experiment_id=task.experiment_id,
                worker_id=worker_id,
                metadata={
                    "hypothesis_id": task.hypothesis.hypothesis_id,
                    "symbol": task.symbol,
                    "timeframe": task.timeframe,
                },
            )
        else:
            _log.debug(
                "worker_task_started",
                component="Worker",
                worker_id=worker_id,
                experiment_id=task.experiment_id,
                hypothesis_id=task.hypothesis.hypothesis_id,
                symbol=task.symbol,
                timeframe=task.timeframe,
            )

        try:
            # Overwrite task-level random seed in hypothesis definition for permutation test
            hyp_copy = task.hypothesis.model_copy()

            # Execute evaluation on train partition by default with derived task seed
            res = self.runner.evaluate_hypothesis_on_partition(
                hypothesis=hyp_copy,
                df=df,
                outcomes_df=outcomes_df,
                partition_name="train",
                dataset_fingerprint=dataset_fingerprint,
                symbol=task.symbol,
                timeframe=task.timeframe,
                seed=seed_int,
            )

            if self.log_callback:
                self.log_callback(
                    level="INFO",
                    event_type="worker_task_completed",
                    message="Experiment evaluation finished cleanly",
                    component="Worker",
                    experiment_id=task.experiment_id,
                    worker_id=worker_id,
                    metadata={
                        "validation_status": res.validation_status,
                        "edge_score": res.edge_score,
                    },
                )
            else:
                _log.info(
                    "worker_task_completed",
                    component="Worker",
                    worker_id=worker_id,
                    experiment_id=task.experiment_id,
                    validation_status=res.validation_status,
                    edge_score=res.edge_score,
                )
            return (task, res, None)
        except Exception as exc:
            if self.log_callback:
                self.log_callback(
                    level="ERROR",
                    event_type="worker_task_failed",
                    message=f"Worker task failed: {exc}",
                    component="Worker",
                    experiment_id=task.experiment_id,
                    worker_id=worker_id,
                    metadata={"error": str(exc)},
                )
            else:
                _log.error(
                    "worker_task_failed",
                    component="Worker",
                    worker_id=worker_id,
                    experiment_id=task.experiment_id,
                    error=str(exc),
                )
            return (task, None, str(exc))

    def execute_batch(
        self,
        tasks: list[ExperimentTask],
        df_map: dict[tuple[str, str], pd.DataFrame],
        outcomes_map: dict[tuple[str, str], pd.DataFrame],
        fingerprint_map: dict[tuple[str, str], str],
    ) -> list[tuple[ExperimentTask, HypothesisResult | None, str | None]]:
        """Execute a batch of tasks concurrently across worker threads.

        Args:
            tasks: List of ExperimentTasks to evaluate.
            df_map: Map of (symbol, timeframe) -> price DataFrame.
            outcomes_map: Map of (symbol, timeframe) -> outcomes DataFrame.
            fingerprint_map: Map of (symbol, timeframe) -> dataset fingerprint.

        Returns:
            List of (task, result, error) tuples.
        """
        results: list[tuple[ExperimentTask, HypothesisResult | None, str | None]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {}
            for idx, task in enumerate(tasks):
                worker_id = f"worker_{idx % self.max_workers}"
                key = (task.symbol, task.timeframe)

                df = df_map.get(key)
                outcomes_df = outcomes_map.get(key)
                fp = fingerprint_map.get(key, "unknown_fp")

                if df is None or outcomes_df is None or df.empty or outcomes_df.empty:
                    results.append((task, None, f"No market data for {key}"))
                    continue

                future = executor.submit(
                    self.execute_task,
                    task=task,
                    df=df,
                    outcomes_df=outcomes_df,
                    dataset_fingerprint=fp,
                    worker_id=worker_id,
                )
                future_to_task[future] = task

            for future in as_completed(future_to_task):
                try:
                    res_tuple = future.result()
                    results.append(res_tuple)
                except Exception as exc:
                    t = future_to_task[future]
                    results.append((t, None, f"Worker thread crashed: {exc}"))

        return results
