"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Edge Knowledge Graph Subsystem
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
        elif isinstance(val, float):
            return round(val, 8)
        return val

    normalized = _normalize(data)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_canonical_sha256(data: Any) -> str:
    """Compute 64-character uppercase SHA-256 hex digest of canonically serialized data."""
    canonical_json = serialize_canonical_json(data)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest().upper()


def compute_knowledge_node_id(
    node_type: str,
    entity_id: str,
    label: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (node_id, canonical_hash) for KnowledgeNode (Prefix: KND_)."""
    payload = {
        "entity_id": str(entity_id).strip(),
        "label": str(label).strip(),
        "node_type": str(node_type).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    node_id = f"KND_{digest[:16].upper()}"
    return node_id, digest.upper()


def compute_knowledge_relationship_id(
    source_node_id: str,
    target_node_id: str,
    relationship_type: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (relationship_id, canonical_hash) for KnowledgeRelationship (Prefix: REL_)."""
    payload = {
        "relationship_type": str(relationship_type).strip().upper(),
        "source_node_id": str(source_node_id).strip(),
        "target_node_id": str(target_node_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    rel_id = f"REL_{digest[:16].upper()}"
    return rel_id, digest.upper()


def compute_knowledge_graph_id(
    graph_name: str,
    node_ids: list[str],
    relationship_ids: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (graph_id, canonical_hash) for KnowledgeGraph (Prefix: KGR_)."""
    payload = {
        "graph_name": str(graph_name).strip(),
        "node_ids": sorted([str(n).strip() for n in node_ids]),
        "relationship_ids": sorted([str(r).strip() for r in relationship_ids]),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    graph_id = f"KGR_{digest[:16].upper()}"
    return graph_id, digest.upper()


def compute_scientific_path_id(
    source_node_id: str,
    target_node_id: str,
    node_chain: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (path_id, canonical_hash) for ScientificPath (Prefix: PTH_)."""
    payload = {
        "node_chain": [str(n).strip() for n in node_chain],
        "source_node_id": str(source_node_id).strip(),
        "target_node_id": str(target_node_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    path_id = f"PTH_{digest[:16].upper()}"
    return path_id, digest.upper()


def compute_relationship_validation_id(
    graph_id: str,
    status: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (validation_id, canonical_hash) for RelationshipValidation (Prefix: VAL_)."""
    payload = {
        "graph_id": str(graph_id).strip(),
        "status": str(status).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    val_id = f"VAL_{digest[:16].upper()}"
    return val_id, digest.upper()


def compute_knowledge_summary_id(
    timestamp: str,
    total_nodes: int,
    total_relationships: int,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) for KnowledgeSummary (Prefix: KSM_)."""
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_nodes": int(total_nodes),
        "total_relationships": int(total_relationships),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"KSM_{digest[:16].upper()}"
    return summary_id, digest.upper()
