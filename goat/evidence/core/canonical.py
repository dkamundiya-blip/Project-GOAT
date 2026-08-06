"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Evidence Subsystem
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


def compute_observation_id(
    metric_name: str,
    metric_value: Any,
    timestamp: str,
    source: str = "LIVE_MARKET",
    instrument: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (observation_id, canonical_hash) deterministically for ScientificObservation.

    Returns:
        Tuple of (OBS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "instrument": str(instrument).strip().upper(),
        "metric_name": str(metric_name).strip(),
        "metric_value": str(metric_value).strip(),
        "source": str(source).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    observation_id = f"OBS_{digest[:16].upper()}"
    return observation_id, digest.upper()


def compute_evidence_record_id(
    category: str,
    observation_ids: list[str],
    source: str = "LIVE_MARKET",
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (evidence_id, canonical_hash) deterministically for EvidenceRecord.

    Returns:
        Tuple of (EVR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "category": str(category).strip().upper(),
        "observation_ids": sorted([str(o).strip() for o in observation_ids]),
        "source": str(source).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    evidence_id = f"EVR_{digest[:16].upper()}"
    return evidence_id, digest.upper()


def compute_collection_id(
    collection_name: str,
    observation_ids: list[str],
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (collection_id, canonical_hash) deterministically for ObservationCollection.

    Returns:
        Tuple of (COL_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "collection_name": str(collection_name).strip(),
        "observation_ids": sorted([str(o).strip() for o in observation_ids]),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    collection_id = f"COL_{digest[:16].upper()}"
    return collection_id, digest.upper()


def compute_link_id(
    hypothesis_id: str,
    target_id: str,
    link_type: str = "HYPOTHESIS_EVIDENCE_LINK",
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (link_id, canonical_hash) deterministically for EvidenceLink.

    Returns:
        Tuple of (LNK_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "hypothesis_id": str(hypothesis_id).strip(),
        "link_type": str(link_type).strip().upper(),
        "target_id": str(target_id).strip(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    link_id = f"LNK_{digest[:16].upper()}"
    return link_id, digest.upper()


def compute_summary_id(
    total_observations: int,
    total_evidence_records: int,
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically for EvidenceSummary.

    Returns:
        Tuple of (EVS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_evidence_records": int(total_evidence_records),
        "total_observations": int(total_observations),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"EVS_{digest[:16].upper()}"
    return summary_id, digest.upper()
