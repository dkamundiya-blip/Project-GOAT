"""
Project GOAT v0.9 — Experiment Manifest Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.experiments.core.canonical import compute_manifest_id
from goat.experiments.core.models import ExperimentManifest, ScientificExperiment


class ExperimentManifestEngine:
    """Experiment Manifest Engine for generating, associating, and validating immutable ExperimentManifests (MAN_<HEX16>)."""

    def __init__(self) -> None:
        self._manifests: dict[str, ExperimentManifest] = {}
        self._experiment_manifest_map: dict[str, str] = {}

    def generate_manifest(
        self,
        experiment: ScientificExperiment,
        dataset_fingerprint: str = "",
        configuration_params: dict[str, Any] | None = None,
        software_version: str = "1.0.0",
        author: str = "QUANT_RESEARCHER",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExperimentManifest:
        """Generate an immutable ExperimentManifest for a target experiment."""
        exp_id = experiment.experiment_id
        hyp_id = experiment.hypothesis_id
        ev_ids = experiment.evidence_ids
        now_str = timestamp or datetime.now(timezone.utc).isoformat()

        man_id, canonical_hash = compute_manifest_id(
            experiment_id=exp_id,
            hypothesis_id=hyp_id,
            evidence_ids=ev_ids,
        )

        if man_id in self._manifests:
            return self._manifests[man_id]

        manifest = ExperimentManifest(
            manifest_id=man_id,
            experiment_id=exp_id,
            hypothesis_id=hyp_id,
            evidence_ids=ev_ids,
            dataset_fingerprint=dataset_fingerprint.strip(),
            configuration_params=configuration_params or {},
            software_version=software_version.strip(),
            author=author.strip(),
            created_timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._manifests[man_id] = manifest
        self._experiment_manifest_map[exp_id] = man_id

        return manifest

    def get_manifest(self, manifest_id: str) -> ExperimentManifest | None:
        """Get manifest by ID."""
        return self._manifests.get(manifest_id)

    def get_manifest_for_experiment(self, experiment_id: str) -> ExperimentManifest | None:
        """Get manifest associated with experiment ID."""
        man_id = self._experiment_manifest_map.get(experiment_id)
        if not man_id:
            return None
        return self._manifests.get(man_id)

    def list_all_manifests(self) -> list[ExperimentManifest]:
        """List all generated manifests sorted by creation timestamp."""
        return sorted(self._manifests.values(), key=lambda m: m.created_timestamp)
