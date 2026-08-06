"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Knowledge Nodes, Edges, Integrated Knowledge, and Conflict Records.
"""

import json
from typing import Any
from goat.research.edge.canonical import compute_canonical_sha256


def serialize_canonical_json(data: Any) -> str:
    """Recursively convert data into canonical JSON string with sorted keys.

    Args:
        data: Arbitrary structure (dict, list, primitive, Enum).

    Returns:
        Canonical JSON string.
    """
    def _normalize(val: Any) -> Any:
        if isinstance(val, dict):
            return {str(k): _normalize(v) for k, v in sorted(val.items(), key=lambda x: str(x[0]))}
        elif isinstance(val, (list, tuple, set)):
            return [_normalize(item) for item in val]
        elif hasattr(val, "value"):  # Enum support
            return str(val.value)
        elif hasattr(val, "dict"):   # Pydantic v1/v2 support
            return _normalize(val.dict())
        return val

    normalized = _normalize(data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_node_fingerprint(
    title: str,
    node_type: str,
    originating_validation: str,
    version: str = "1.0.0",
) -> str:
    """Compute deterministic Knowledge Node Fingerprint (NDFP_<HEX64>)."""
    payload = {
        "node_type": str(node_type).strip().upper(),
        "originating_validation": str(originating_validation).strip(),
        "title": str(title).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    return f"NDFP_{digest.upper()}"


def compute_node_id(title: str, node_type: str, originating_validation: str, version: str = "1.0.0") -> tuple[str, str, str]:
    """Compute (node_id, canonical_hash, fingerprint) deterministically.

    Returns:
        Tuple of (KND_<HEX16>, SHA256_HEX64, NDFP_<HEX64>).
    """
    fingerprint = compute_node_fingerprint(title, node_type, originating_validation, version)
    payload = {
        "fingerprint": fingerprint,
        "originating_validation": str(originating_validation).strip(),
        "title": str(title).strip(),
    }
    digest = compute_canonical_sha256(payload)
    node_id = f"KND_{digest[:16].upper()}"
    return node_id, digest.upper(), fingerprint


def compute_edge_id(
    source_node: str,
    destination_node: str,
    relationship: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (edge_id, canonical_hash) deterministically.

    Returns:
        Tuple of (KED_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "destination_node": str(destination_node).strip(),
        "relationship": str(relationship).strip().upper(),
        "source_node": str(source_node).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    edge_id = f"KED_{digest[:16].upper()}"
    return edge_id, digest.upper()


def compute_integrated_knowledge_id(
    participating_validations: list[str],
    participating_hypotheses: list[str],
    participating_experiments: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (knowledge_id, canonical_hash) deterministically.

    Returns:
        Tuple of (IKN_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "participating_experiments": sorted([str(e).strip() for e in participating_experiments]),
        "participating_hypotheses": sorted([str(h).strip() for h in participating_hypotheses]),
        "participating_validations": sorted([str(v).strip() for v in participating_validations]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    knowledge_id = f"IKN_{digest[:16].upper()}"
    return knowledge_id, digest.upper()


def compute_conflict_id(
    validation_a: str,
    validation_b: str,
    conflict_type: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (conflict_id, canonical_hash) deterministically.

    Returns:
        Tuple of (CFL_<HEX16>, SHA256_HEX64).
    """
    val_a = str(validation_a).strip()
    val_b = str(validation_b).strip()
    # Sort validation IDs to guarantee symmetry if needed, but preserve order if distinct roles
    payload = {
        "conflict_type": str(conflict_type).strip().upper(),
        "validation_a": min(val_a, val_b),
        "validation_b": max(val_a, val_b),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    conflict_id = f"CFL_{digest[:16].upper()}"
    return conflict_id, digest.upper()


def compute_evidence_merge_id(
    source_evidence_ids: list[str],
    target_knowledge_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (merge_id, canonical_hash) deterministically.

    Returns:
        Tuple of (EMG_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "source_evidence_ids": sorted([str(e).strip() for e in source_evidence_ids]),
        "target_knowledge_id": str(target_knowledge_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    merge_id = f"EMG_{digest[:16].upper()}"
    return merge_id, digest.upper()


def compute_version_id(
    knowledge_id: str,
    state_hash: str,
    version_number: int,
) -> tuple[str, str]:
    """Compute (version_id, canonical_hash) deterministically for knowledge evolution states.

    Returns:
        Tuple of (KVR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "knowledge_id": str(knowledge_id).strip(),
        "state_hash": str(state_hash).strip(),
        "version_number": int(version_number),
    }
    digest = compute_canonical_sha256(payload)
    version_id = f"KVR_{digest[:16].upper()}"
    return version_id, digest.upper()
