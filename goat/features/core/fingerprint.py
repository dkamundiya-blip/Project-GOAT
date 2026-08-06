"""
Project GOAT v0.7 — Scientific Feature Fingerprint & Validation Engine

Implements the Scientific Feature Fingerprint (FPT_<HEX64>) representing a feature's
immutable scientific identity, distinct from registry identity (FEAT_<HEX16>).
"""

from __future__ import annotations

from typing import Any

from goat.research.edge.canonical import compute_canonical_sha256

DEFAULT_FINGERPRINT_ALGORITHM = "SHA256_CANONICAL_V1"
DEFAULT_FINGERPRINT_VERSION = "1.0.0"
DEFAULT_DEPENDENCY_GRAPH_VERSION = "1.0.0"


def compute_scientific_feature_fingerprint(
    mathematical_definition: str,
    parameters: dict[str, Any],
    dependencies: list[str] | None = None,
    dependency_graph_version: str = DEFAULT_DEPENDENCY_GRAPH_VERSION,
    version: str = "1.0.0",
    input_requirements: dict[str, Any] | None = None,
    output_type: str = "float64",
    determinism_class: str = "ieee_754_strict",
    expected_stationarity: str = "stationary",
    capabilities: dict[str, Any] | None = None,
    input_contract: dict[str, Any] | None = None,
    output_contract: dict[str, Any] | None = None,
) -> str:
    """Compute deterministic Scientific Feature Fingerprint (FPT_<HEX64>).

    The Scientific Feature Fingerprint uniquely represents the scientific definition
    of a feature. It is generated ONLY from normalized scientific definition attributes and capability contracts.
    It intentionally excludes runtime state, file paths, author names, creation timestamps,
    or memory addresses.

    Returns:
        String formatted as 'FPT_' + 64-character upper-case SHA-256 hex digest.
    """
    math_def = str(mathematical_definition).strip()
    if not math_def:
        raise ValueError("Cannot compute Scientific Feature Fingerprint for empty mathematical_definition")

    deps = sorted([str(d).strip() for d in (dependencies or [])])
    input_reqs = input_requirements or {}
    params = parameters or {}
    caps = capabilities or {}
    in_contract = input_contract or {}
    out_contract = output_contract or {}

    payload = {
        "capabilities": caps,
        "dependency_graph_version": str(dependency_graph_version).strip(),
        "dependencies": deps,
        "determinism_declaration": str(determinism_class).strip().lower(),
        "feature_semantic_version": str(version).strip(),
        "input_contract": in_contract,
        "input_schema": input_reqs,
        "mathematical_definition": math_def,
        "normalized_parameter_schema": params,
        "output_contract": out_contract,
        "output_schema": str(output_type).strip().lower(),
        "stationarity_declaration": str(expected_stationarity).strip().lower(),
    }

    digest = compute_canonical_sha256(payload)
    return f"FPT_{digest.upper()}"


def validate_scientific_feature_fingerprint(metadata: Any) -> bool:
    """Validate the integrity and correctness of a FeatureMetadata's Scientific Fingerprint.

    Fail-closed validation rules:
    - Required scientific fields must be present and non-empty.
    - Algorithm must be supported ('SHA256_CANONICAL_V1').
    - Fingerprint format must match 'FPT_<HEX64>'.
    - Computed fingerprint must strictly match stored scientific_fingerprint.

    Returns:
        True if valid. Raises ValueError or returns False if invalid.
    """
    if not hasattr(metadata, "scientific_fingerprint") or not metadata.scientific_fingerprint:
        raise ValueError("Missing scientific_fingerprint in FeatureMetadata")

    if getattr(metadata, "fingerprint_algorithm", None) != DEFAULT_FINGERPRINT_ALGORITHM:
        raise ValueError(
            f"Unsupported fingerprint algorithm '{getattr(metadata, 'fingerprint_algorithm', None)}'. "
            f"Expected '{DEFAULT_FINGERPRINT_ALGORITHM}'"
        )

    fp_str = metadata.scientific_fingerprint
    if not fp_str.startswith("FPT_") or len(fp_str) != 68:
        raise ValueError(f"Invalid scientific_fingerprint format '{fp_str}'. Expected 'FPT_<HEX64>'")

    caps_dict = metadata.capabilities.model_dump(mode="json") if hasattr(metadata, "capabilities") else {}
    in_contract_dict = metadata.input_contract.model_dump(mode="json") if hasattr(metadata, "input_contract") else {}
    out_contract_dict = (
        metadata.output_contract.model_dump(mode="json") if hasattr(metadata, "output_contract") else {}
    )

    # Re-compute fingerprint from scientific metadata
    expected_fp = compute_scientific_feature_fingerprint(
        mathematical_definition=metadata.mathematical_definition,
        parameters=getattr(metadata, "parameters", metadata.input_requirements.get("parameters", {})),
        dependencies=metadata.dependencies,
        version=metadata.version,
        input_requirements=metadata.input_requirements,
        output_type=str(metadata.output_type.value if hasattr(metadata.output_type, "value") else metadata.output_type),
        determinism_class=str(
            metadata.determinism_class.value
            if hasattr(metadata.determinism_class, "value")
            else metadata.determinism_class
        ),
        expected_stationarity=str(
            metadata.expected_stationarity.value
            if hasattr(metadata.expected_stationarity, "value")
            else metadata.expected_stationarity
        ),
        capabilities=caps_dict,
        input_contract=in_contract_dict,
        output_contract=out_contract_dict,
    )

    if fp_str != expected_fp:
        raise ValueError(
            f"Scientific Feature Fingerprint mismatch! Stored: '{fp_str}', Re-computed: '{expected_fp}'"
        )

    return True
