"""
Project GOAT v0.7 — Canonical Hashing & Deterministic ID Generation for Simulation Engine

Provides deterministic canonical JSON serialization, SHA-256 digest computation,
and stable ID generation for Scientific Simulation and Walk-Forward entities.
"""

from typing import Any
from goat.integration.core.canonical import serialize_canonical_json
from goat.research.edge.canonical import compute_canonical_sha256


def compute_scenario_id(
    qualification_id: str,
    composite_id: str,
    dataset_reference: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (scenario_id, canonical_hash) deterministically for SimulationScenario.

    Returns:
        Tuple of (SIM_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "qualification_id": str(qualification_id).strip(),
        "composite_id": str(composite_id).strip(),
        "dataset_reference": str(dataset_reference).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    scenario_id = f"SIM_{digest[:16].upper()}"
    return scenario_id, digest.upper()


def compute_run_id(
    scenario_id: str,
    replay_seed: int,
    execution_timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (run_id, canonical_hash) deterministically for SimulationRun.

    Returns:
        Tuple of (SRN_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "scenario_id": str(scenario_id).strip(),
        "replay_seed": int(replay_seed),
        "execution_timestamp": str(execution_timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    run_id = f"SRN_{digest[:16].upper()}"
    return run_id, digest.upper()


def compute_result_id(
    run_id: str,
    validation_status: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (result_id, canonical_hash) deterministically for SimulationResult.

    Returns:
        Tuple of (SRS_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "run_id": str(run_id).strip(),
        "validation_status": str(validation_status).strip().upper(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    result_id = f"SRS_{digest[:16].upper()}"
    return result_id, digest.upper()


def compute_window_id(
    sequence_number: int,
    training_period: list[str],
    validation_period: list[str],
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (window_id, canonical_hash) deterministically for WalkForwardWindow.

    Returns:
        Tuple of (WFW_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "sequence_number": int(sequence_number),
        "training_period": [str(t).strip() for t in training_period],
        "validation_period": [str(v).strip() for v in validation_period],
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    window_id = f"WFW_{digest[:16].upper()}"
    return window_id, digest.upper()


def compute_attribution_id(
    result_id: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (attribution_id, canonical_hash) deterministically for PerformanceAttribution.

    Returns:
        Tuple of (PAT_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "result_id": str(result_id).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    attribution_id = f"PAT_{digest[:16].upper()}"
    return attribution_id, digest.upper()


def compute_simulation_report_id(
    report_type: str,
    timestamp: str,
    version: str = "1.0.0",
) -> tuple[str, str]:
    """Compute (report_id, canonical_hash) deterministically for Simulation reports.

    Returns:
        Tuple of (SSR_<HEX16>, SHA256_HEX64).
    """
    payload = {
        "report_type": str(report_type).strip().upper(),
        "timestamp": str(timestamp).strip(),
        "version": str(version).strip(),
    }
    digest = compute_canonical_sha256(payload)
    report_id = f"SSR_{digest[:16].upper()}"
    return report_id, digest.upper()
