"""
Project GOAT v0.4 — Research Edge Registry

Append-only registry preserving historical hypothesis evaluation records
and lifecycle state transitions across research iterations.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from goat.logging import get_logger
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.result import HypothesisResult

_log = get_logger("hypothesis.registry")

VALID_REGISTRY_STATUSES = {
    "EXPLORATORY",
    "TRAIN_SUPPORTED",
    "VALIDATION_SUPPORTED",
    "UNSTABLE",
    "REJECTED",
    "INSUFFICIENT_DATA",
    "HOLDOUT_EVALUATED",
}


class RegistryEntry(BaseModel):
    """Immutable entry in the research EdgeRegistry."""

    entry_id: str  # hypothesis_id:version
    hypothesis_id: str
    version: str
    status: str
    definition: dict[str, Any]
    latest_result: dict[str, Any] | None = None
    evaluation_history: list[dict[str, Any]] = Field(default_factory=list)


class EdgeRegistry:
    """Persistent append-only research registry for hypothesis lifecycle tracking."""

    def __init__(self, registry_path: Path) -> None:
        self.registry_path = Path(registry_path)
        self._entries: dict[str, RegistryEntry] = {}
        self._load()

    def _load(self) -> None:
        if self.registry_path.exists():
            try:
                raw_data = json.loads(self.registry_path.read_text(encoding="utf-8"))
                for entry_key, entry_dict in raw_data.items():
                    self._entries[entry_key] = RegistryEntry(**entry_dict)
            except Exception as e:
                _log.warning("error_loading_edge_registry", path=str(self.registry_path), error=str(e))

    def _save(self) -> None:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        export_dict = {k: v.model_dump(mode="json") for k, v in self._entries.items()}
        self.registry_path.write_text(json.dumps(export_dict, indent=2), encoding="utf-8")

    def register_hypothesis(
        self,
        definition: HypothesisDefinition,
        status: str = "EXPLORATORY",
    ) -> None:
        """Register a new or updated hypothesis in the registry."""
        if status not in VALID_REGISTRY_STATUSES:
            raise ValueError(f"Invalid registry status '{status}'. Must be one of {VALID_REGISTRY_STATUSES}")

        entry_key = f"{definition.hypothesis_id}:{definition.version}"
        if entry_key not in self._entries:
            entry = RegistryEntry(
                entry_id=entry_key,
                hypothesis_id=definition.hypothesis_id,
                version=definition.version,
                status=status,
                definition=definition.model_dump(mode="json"),
            )
            self._entries[entry_key] = entry
            self._save()
            _log.info("registered_new_hypothesis", entry_key=entry_key, status=status)

    def record_evaluation_result(
        self,
        result: HypothesisResult,
        new_status: str | None = None,
    ) -> None:
        """Record an evaluation result and append it to historical record."""
        entry_key = f"{result.hypothesis_id}:{result.version}"
        if entry_key not in self._entries:
            raise KeyError(f"Hypothesis {entry_key} must be registered before recording results.")

        entry = self._entries[entry_key]
        res_dict = result.model_dump(mode="json")
        entry.latest_result = res_dict
        entry.evaluation_history.append(res_dict)

        if new_status:
            if new_status not in VALID_REGISTRY_STATUSES:
                raise ValueError(f"Invalid registry status '{new_status}'")
            entry.status = new_status

        self._save()
        _log.info("recorded_evaluation_result", entry_key=entry_key, status=entry.status)

    def get_entry(self, hypothesis_id: str, version: str) -> RegistryEntry | None:
        return self._entries.get(f"{hypothesis_id}:{version}")

    def list_entries(self) -> list[RegistryEntry]:
        return list(self._entries.values())
