"""
Project GOAT v0.7 — Feature Identity Hashing

Provides deterministic SHA-256 canonical hashing for features, producing stable Feature IDs (FEAT_<HEX16>)
and cryptographic canonical hashes conforming to Part 1 and Part 5 of v0.7 architecture specification.
"""

from __future__ import annotations

from typing import Any

from goat.research.edge.canonical import compute_canonical_sha256


def compute_feature_canonical_hash(
    name: str,
    version: str,
    parameters: dict[str, Any],
    ast_spec: dict[str, Any],
    dependencies: list[str] | None = None,
) -> tuple[str, str]:
    """Compute deterministic Feature ID (FEAT_<HEX16>) and SHA-256 canonical hash.

    Args:
        name: Feature name identifier.
        version: Semantic version string.
        parameters: Bound hyper-parameter dictionary.
        ast_spec: Abstract Syntax Tree representation dictionary.
        dependencies: Optional list of upstream Feature IDs.

    Returns:
        Tuple of (feature_id, canonical_hash) where:
          - feature_id is 'FEAT_' + first 16 chars of SHA-256 digest.
          - canonical_hash is full 64-char hex digest of the canonical AST payload.
    """
    deps = sorted(dependencies) if dependencies else []
    payload = {
        "ast_spec": ast_spec,
        "dependencies": deps,
        "name": str(name).strip(),
        "parameters": parameters,
        "version": str(version).strip(),
    }
    canonical_hash = compute_canonical_sha256(payload)
    feature_id = f"FEAT_{canonical_hash[:16].upper()}"
    return feature_id, canonical_hash
