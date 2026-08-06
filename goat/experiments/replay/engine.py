"""
Project GOAT v0.9 — Experiment Replay Engine
"""

from datetime import datetime, timezone
from typing import Any

from goat.experiments.core.canonical import compute_replay_id
from goat.experiments.core.models import ExperimentManifest, ExperimentReplay, ScientificExperiment


class ExperimentReplayEngine:
    """Experiment Replay Engine for generating and verifying deterministic replay specifications (RPL_<HEX16>).

    IMPORTANT: This engine MUST NOT execute any replay simulation or trading code.
    It purely maintains replay metadata, random seed specifications, and integrity verifications.
    """

    def __init__(self) -> None:
        self._replays: dict[str, ExperimentReplay] = {}
        self._experiment_replay_map: dict[str, list[str]] = {}

    def create_replay_spec(
        self,
        experiment: ScientificExperiment,
        manifest: ExperimentManifest,
        dataset_hash: str,
        random_seed: int = 42,
        expected_output_hash: str = "",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExperimentReplay:
        """Create a deterministic ExperimentReplay specification entity (RPL_<HEX16>)."""
        exp_id = experiment.experiment_id
        man_id = manifest.manifest_id

        if not dataset_hash or len(dataset_hash.strip()) < 8:
            raise ValueError("Dataset hash must be at least 8 non-whitespace characters.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        rpl_id, canonical_hash = compute_replay_id(
            experiment_id=exp_id,
            manifest_id=man_id,
            dataset_hash=dataset_hash,
            timestamp=now_str,
        )

        replay = ExperimentReplay(
            replay_id=rpl_id,
            experiment_id=exp_id,
            manifest_id=man_id,
            dataset_hash=dataset_hash.strip(),
            random_seed=random_seed,
            expected_output_hash=expected_output_hash.strip(),
            is_verified=True,
            timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._replays[rpl_id] = replay
        self._experiment_replay_map.setdefault(exp_id, []).append(rpl_id)

        return replay

    def verify_replay_integrity(self, replay_id: str, actual_output_hash: str) -> bool:
        """Verify that an output dataset hash matches expected output hash without re-running code."""
        replay = self._replays.get(replay_id)
        if not replay:
            raise KeyError(f"Replay ID '{replay_id}' not found.")
        if not replay.expected_output_hash:
            return True
        return replay.expected_output_hash.upper() == actual_output_hash.strip().upper()

    def get_replay(self, replay_id: str) -> ExperimentReplay | None:
        """Get replay by ID."""
        return self._replays.get(replay_id)

    def get_replays_for_experiment(self, experiment_id: str) -> list[ExperimentReplay]:
        """Get list of replays for an experiment ID sorted by timestamp."""
        rpl_ids = self._experiment_replay_map.get(experiment_id, [])
        return sorted([self._replays[rid] for rid in rpl_ids], key=lambda r: r.timestamp)

    def list_all_replays(self) -> list[ExperimentReplay]:
        """List all replay records sorted by timestamp."""
        return sorted(self._replays.values(), key=lambda r: r.timestamp)
