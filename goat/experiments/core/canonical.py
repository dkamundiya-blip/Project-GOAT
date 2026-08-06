"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Experiment Subsystem
"""

import hashlib
import json
from typing import Any


def serialize_canonical_json(data: Any) -> str:
    """Recursively convert arbitrary structure into canonical JSON string with sorted keys.

    Args:
        data: Structure to serialize (dict, list, tuple, set, Enum, primitive, Pydantic model).

    Returns:
        Canonical JSON string formatted with sorted keys and tight separators.
    """
    def _normalize(val: Any) -> Any:
        if isinstance(val, dict):
            return {str(k): _normalize(v) for k, v in sorted(val.items(), key=lambda x: str(x[0]))}
        elif isinstance(val, (list, tuple, set)):
            return [_normalize(item) for item in val]
        elif hasattr(val, "value"):  # Enum support
            return str(val.value)
        elif hasattr(val, "model_dump"):  # Pydantic v2 support
            return _normalize(val.model_dump())
        elif hasattr(val, "dict"):  # Pydantic v1 fallback
            return _normalize(val.dict())
        return val

    normalized = _normalize(data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_canonical_sha256(data: Any) -> str:
    """Compute 64-character uppercase SHA-256 hex digest of canonically serialized data."""
    canonical_json = serialize_canonical_json(data)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest().upper()


def compute_experiment_id(
    hypothesis_id: str = "",
    title: str = "",
    experiment_type: str = "SIMULATION",
    author: str = "",
    version: str = "1.0.0",
    name: str = "",
    fingerprint: str = "",
) -> tuple[str, str]:
    """Compute (experiment_id, canonical_hash) deterministically for ScientificExperiment.

    Returns:
        Tuple of (EXP_<HEX16>, SHA256_HEX64).
    """
    target_title = title or name or "UNTITLED"
    target_hyp = hypothesis_id or "HYP_0000000000000000"
    payload = {
        "author": str(author).strip(),
        "experiment_type": str(experiment_type).strip().upper(),
        "fingerprint": str(fingerprint).strip(),
        "hypothesis_id": str(target_hyp).strip(),
        "title": str(target_title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    experiment_id = f"EXP_{digest[:16].upper()}"
    return experiment_id, digest.upper()


def compute_manifest_id(
    experiment_id: str,
    hypothesis_id: str,
    evidence_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (manifest_id, canonical_hash) deterministically for ExperimentManifest.

    Returns:
        Tuple of (MAN_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "evidence_ids": sorted([str(e).strip() for e in evidence_ids]),
        "experiment_id": str(experiment_id).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    manifest_id = f"MAN_{digest[:16].upper()}"
    return manifest_id, digest.upper()


def compute_lifecycle_id(
    experiment_id: str,
    from_status: str,
    to_status: str,
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (lifecycle_id, canonical_hash) deterministically for ExperimentLifecycle.

    Returns:
        Tuple of (LFC_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "experiment_id": str(experiment_id).strip(),
        "from_status": str(from_status).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "to_status": str(to_status).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    lifecycle_id = f"LFC_{digest[:16].upper()}"
    return lifecycle_id, digest.upper()


def compute_replay_id(
    experiment_id: str,
    manifest_id: str,
    dataset_hash: str = "",
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (replay_id, canonical_hash) deterministically for ExperimentReplay.

    Returns:
        Tuple of (RPL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "dataset_hash": str(dataset_hash).strip(),
        "experiment_id": str(experiment_id).strip(),
        "manifest_id": str(manifest_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    replay_id = f"RPL_{digest[:16].upper()}"
    return replay_id, digest.upper()


def compute_schedule_id(
    experiment_id: str,
    priority: str,
    scheduled_timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (schedule_id, canonical_hash) deterministically for ExperimentSchedule.

    Returns:
        Tuple of (SCH_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "experiment_id": str(experiment_id).strip(),
        "priority": str(priority).strip().upper(),
        "scheduled_timestamp": str(scheduled_timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    schedule_id = f"SCH_{digest[:16].upper()}"
    return schedule_id, digest.upper()


def compute_summary_id(
    total_experiments: int,
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically for ExperimentSummary.

    Returns:
        Tuple of (SUM_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_experiments": int(total_experiments),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"SUM_{digest[:16].upper()}"
    return summary_id, digest.upper()
