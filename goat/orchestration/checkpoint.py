"""
Project GOAT v0.5 — Checkpoint Manager

Handles atomic disk persistence, loading, saving, and crash recovery for
QueueSnapshot objects with ZERO queue scheduling logic.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

import structlog

from goat.orchestration.campaign import (
    InfrastructureFailure,
    QueueSnapshot,
)

_log = structlog.get_logger(__name__)


class CheckpointManager:
    """Manages atomic checkpoint disk persistence for QueueSnapshot objects."""

    def __init__(self, checkpoint_format_version: int = 1) -> None:
        self.checkpoint_format_version = checkpoint_format_version

    def save_checkpoint(self, snapshot: QueueSnapshot, output_dir: Path) -> Path:
        """Write QueueSnapshot atomically to checkpoint.json via temporary file rename.

        Args:
            snapshot: Immutable QueueSnapshot object.
            output_dir: Directory where checkpoint.json should be saved.

        Returns:
            Path to the saved checkpoint.json file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        final_path = output_dir / "checkpoint.json"

        data_dict = snapshot.model_dump(mode="json")
        data_dict["checkpoint_format_version"] = self.checkpoint_format_version

        content = json.dumps(data_dict, indent=2, sort_keys=True)

        try:
            # Atomic write: write to temp file first, then replace
            with tempfile.NamedTemporaryFile("w", dir=output_dir, delete=False, encoding="utf-8") as tf:
                temp_name = tf.name
                tf.write(content)

            temp_path = Path(temp_name)
            temp_path.replace(final_path)

            _log.info(
                "checkpoint_saved",
                component="CheckpointManager",
                campaign_id=snapshot.campaign_id,
                completed_count=len(snapshot.completed_task_ids),
                checkpoint_path=str(final_path),
            )
            return final_path
        except Exception as exc:
            _log.error(
                "checkpoint_save_failed",
                component="CheckpointManager",
                campaign_id=snapshot.campaign_id,
                error=str(exc),
            )
            raise InfrastructureFailure(f"Failed to write atomic checkpoint: {exc}") from exc

    def load_checkpoint(self, checkpoint_path: Path) -> QueueSnapshot:
        """Load and deserialize QueueSnapshot from disk.

        Args:
            checkpoint_path: Path to checkpoint.json file.

        Returns:
            Deserialized QueueSnapshot instance.
        """
        if not checkpoint_path.exists():
            raise InfrastructureFailure(f"Checkpoint file not found: {checkpoint_path}")

        try:
            content = checkpoint_path.read_text(encoding="utf-8")
            data = json.loads(content)

            fmt_ver = data.get("checkpoint_format_version", 1)
            if fmt_ver > self.checkpoint_format_version:
                _log.warning(
                    "checkpoint_version_higher_than_expected",
                    component="CheckpointManager",
                    file_version=fmt_ver,
                    expected_version=self.checkpoint_format_version,
                )

            # Reconstruct QueueSnapshot (converting lists back to tuples for frozen model)
            snapshot = QueueSnapshot(
                campaign_id=data["campaign_id"],
                configuration_hash=data["configuration_hash"],
                completed_task_ids=tuple(data.get("completed_task_ids", [])),
                failed_task_ids=tuple(data.get("failed_task_ids", [])),
                in_progress_task_ids=tuple(data.get("in_progress_task_ids", [])),
                pending_task_ids=tuple(data.get("pending_task_ids", [])),
                task_results=data.get("task_results", {}),
                last_event_sequence=data.get("last_event_sequence", 0),
            )

            _log.info(
                "checkpoint_loaded",
                component="CheckpointManager",
                campaign_id=snapshot.campaign_id,
                completed_count=len(snapshot.completed_task_ids),
            )
            return snapshot
        except Exception as exc:
            _log.error(
                "checkpoint_load_failed",
                component="CheckpointManager",
                path=str(checkpoint_path),
                error=str(exc),
            )
            raise InfrastructureFailure(f"Failed to load checkpoint: {exc}") from exc
