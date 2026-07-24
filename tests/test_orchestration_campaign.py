"""
Project GOAT v0.5 — Unit Tests for Campaign Enums, Schemas, and Failure Taxonomy
"""

import pytest

from goat.orchestration.campaign import (
    CampaignDefinition,
    CampaignLifecycleLogEntry,
    CampaignManifest,
    CampaignStatus,
    ExperimentStatus,
    InfrastructureFailure,
    OrchestrationError,
    ProvenanceMismatchError,
    QueueSnapshot,
    ValidationFailure,
    WorkerFailure,
)


def test_status_enums() -> None:
    """Test strongly typed status enum values."""
    assert ExperimentStatus.PENDING == "PENDING"
    assert ExperimentStatus.RUNNING == "RUNNING"
    assert ExperimentStatus.COMPLETED == "COMPLETED"
    assert ExperimentStatus.FAILED == "FAILED"
    assert ExperimentStatus.SKIPPED == "SKIPPED"
    assert ExperimentStatus.CANCELLED == "CANCELLED"

    assert CampaignStatus.CREATED == "CREATED"
    assert CampaignStatus.VALIDATING == "VALIDATING"
    assert CampaignStatus.QUEUED == "QUEUED"
    assert CampaignStatus.RUNNING == "RUNNING"
    assert CampaignStatus.PAUSING == "PAUSING"
    assert CampaignStatus.PAUSED == "PAUSED"
    assert CampaignStatus.RESUMING == "RESUMING"
    assert CampaignStatus.COMPLETED == "COMPLETED"
    assert CampaignStatus.FAILED == "FAILED"
    assert CampaignStatus.CANCELLED == "CANCELLED"


def test_failure_taxonomy_inheritance() -> None:
    """Test failure taxonomy exception hierarchy."""
    assert issubclass(ValidationFailure, OrchestrationError)
    assert issubclass(ProvenanceMismatchError, ValidationFailure)
    assert issubclass(InfrastructureFailure, OrchestrationError)
    assert issubclass(WorkerFailure, OrchestrationError)


def test_queue_snapshot_immutability() -> None:
    """Test QueueSnapshot is frozen and cannot be mutated."""
    snapshot = QueueSnapshot(
        campaign_id="CMP-TEST",
        configuration_hash="cfg_test",
        completed_task_ids=("task1", "task2"),
    )
    assert snapshot.campaign_id == "CMP-TEST"
    assert len(snapshot.completed_task_ids) == 2

    with pytest.raises(Exception):
        # Frozen pydantic model must reject mutation
        snapshot.campaign_id = "MUTATED"  # type: ignore[misc]


def test_campaign_manifest_serialization() -> None:
    """Test 6-section CampaignManifest serialization."""
    manifest = CampaignManifest(
        campaign={"campaign_id": "CMP-001", "status": "COMPLETED"},
        configuration={"fdr_alpha": 0.05},
        environment={"python_version": "3.14.0"},
        research_provenance={"dataset_fingerprint": "fp123"},
        execution_configuration={"master_seed": 42},
        validation={"preflight_integrity_verified": True},
    )
    data = manifest.model_dump(mode="json")
    assert data["manifest_schema_version"] == 1
    assert data["provenance_schema_version"] == 1
    assert data["campaign"]["campaign_id"] == "CMP-001"
    assert data["validation"]["preflight_integrity_verified"] is True
