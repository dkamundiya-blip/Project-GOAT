"""
Project GOAT v0.9 — Canonical Hashing & Deterministic ID Generation for Statistical Evaluation Subsystem
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


def compute_statistical_evaluation_id(
    experiment_id: str,
    hypothesis_id: str,
    evaluator: str = "STATISTICAL_ENGINE",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (evaluation_id, canonical_hash) deterministically for StatisticalEvaluation.

    Returns:
        Tuple of (STE_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "evaluator": str(evaluator).strip(),
        "experiment_id": str(experiment_id).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    evaluation_id = f"STE_{digest[:16].upper()}"
    return evaluation_id, digest.upper()


def compute_confidence_id(
    evaluation_id: str,
    confidence_level: float,
    margin_of_error: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (confidence_id, canonical_hash) deterministically for ConfidenceAssessment.

    Returns:
        Tuple of (CON_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "confidence_level": float(confidence_level),
        "evaluation_id": str(evaluation_id).strip(),
        "margin_of_error": float(margin_of_error),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    confidence_id = f"CON_{digest[:16].upper()}"
    return confidence_id, digest.upper()


def compute_significance_id(
    evaluation_id: str,
    p_value: float,
    test_statistic: float,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (significance_id, canonical_hash) deterministically for SignificanceAssessment.

    Returns:
        Tuple of (SIG_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "evaluation_id": str(evaluation_id).strip(),
        "p_value": float(p_value),
        "test_statistic": float(test_statistic),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    significance_id = f"SIG_{digest[:16].upper()}"
    return significance_id, digest.upper()


def compute_expectancy_id(
    evaluation_id: str,
    expected_value: float,
    sample_size: int,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (expectancy_id, canonical_hash) deterministically for ExpectancyAssessment.

    Returns:
        Tuple of (EXP_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "evaluation_id": str(evaluation_id).strip(),
        "expected_value": float(expected_value),
        "sample_size": int(sample_size),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    expectancy_id = f"EXP_{digest[:16].upper()}"
    return expectancy_id, digest.upper()


def compute_decision_id(
    evaluation_id: str,
    decision: str,
    hypothesis_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (decision_id, canonical_hash) deterministically for EvaluationDecision.

    Returns:
        Tuple of (EVD_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "decision": str(decision).strip().upper(),
        "evaluation_id": str(evaluation_id).strip(),
        "hypothesis_id": str(hypothesis_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    decision_id = f"EVD_{digest[:16].upper()}"
    return decision_id, digest.upper()


def compute_summary_id(
    total_evaluations: int,
    total_decisions: int,
    timestamp: str = "",
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (summary_id, canonical_hash) deterministically for EvaluationSummary.

    Returns:
        Tuple of (SUM_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "timestamp": str(timestamp).strip(),
        "total_decisions": int(total_decisions),
        "total_evaluations": int(total_evaluations),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    summary_id = f"SUM_{digest[:16].upper()}"
    return summary_id, digest.upper()
