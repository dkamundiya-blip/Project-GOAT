"""
Project GOAT v0.7 — Feature Registry Service

Authoritative scientific catalog manager providing fail-closed registration, duplicate detection,
multi-dimensional querying, snapshot import/export, and audit tracking.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from goat.features.core.base import BaseFeature
from goat.features.core.contracts import validate_feature_capability_contract
from goat.features.core.enums import TaxonomyCategory
from goat.features.core.fingerprint import validate_scientific_feature_fingerprint
from goat.features.registry.model import (
    RegistrationStatus,
    RegistryAuditEvent,
    RegistryRecord,
    ValidationStatus,
)
from goat.features.registry.sqlite import SQLiteFeatureRepository


class FeatureRegistryService:
    """Service layer coordinating scientific Feature registration, search, and integrity."""

    def __init__(self, repo: SQLiteFeatureRepository) -> None:
        """Initialize registry service.

        Args:
            repo: Instantiated SQLiteFeatureRepository instance.
        """
        self._repo = repo

    def register_feature(
        self,
        feature: BaseFeature,
        provenance: str = "system",
        notes: str = "",
    ) -> RegistryRecord:
        """Register a candidate feature into the Registry.

        Fail-closed validation rules:
        - Must pass validate_feature_capability_contract(metadata).
        - Must pass validate_scientific_feature_fingerprint(metadata).
        - Must not collide with an existing Feature ID, Scientific Fingerprint, or Canonical Hash.

        Args:
            feature: BaseFeature instance.
            provenance: Author or subroutine string.
            notes: Scientific audit notes.

        Returns:
            Immutable RegistryRecord.
        """
        meta = feature.metadata

        # 1. Contract Validation
        validate_feature_capability_contract(meta)

        # 2. Fingerprint Validation
        validate_scientific_feature_fingerprint(meta)

        # 3. Duplicate Prevention (Fail-Closed)
        if self._repo.get_by_id(meta.feature_id) is not None:
            raise ValueError(f"Registration failed: Feature ID '{meta.feature_id}' already registered")

        if self._repo.get_by_fingerprint(meta.scientific_fingerprint) is not None:
            raise ValueError(
                f"Registration failed: Scientific Feature Fingerprint '{meta.scientific_fingerprint}' "
                f"already exists in registry"
            )

        if self._repo.get_by_canonical_hash(meta.canonical_hash) is not None:
            raise ValueError(
                f"Registration failed: Canonical AST Hash '{meta.canonical_hash}' already exists in registry"
            )

        # Construct RegistryRecord
        record = RegistryRecord(
            feature_id=meta.feature_id,
            scientific_fingerprint=meta.scientific_fingerprint,
            canonical_hash=meta.canonical_hash,
            semantic_version=meta.version,
            feature_metadata=meta,
            capability_contract=meta.capabilities,
            input_contract=meta.input_contract,
            output_contract=meta.output_contract,
            execution_constraints=meta.constraints,
            dependency_spec=meta.dependencies,
            registration_timestamp=meta.creation_timestamp,
            registry_version="1.0.0",
            registration_status=RegistrationStatus.REGISTERED,
            deprecation_state=meta.deprecation_status,
            validation_status=ValidationStatus.UNVALIDATED,
            registry_provenance=provenance,
            registry_notes=notes,
        )

        self._repo.save(record)
        return record

    def get_by_id(self, feature_id: str) -> RegistryRecord | None:
        """Lookup record by Feature ID."""
        return self._repo.get_by_id(feature_id)

    def get_by_fingerprint(self, fingerprint: str) -> RegistryRecord | None:
        """Lookup record by Scientific Feature Fingerprint."""
        return self._repo.get_by_fingerprint(fingerprint)

    def get_by_canonical_hash(self, canonical_hash: str) -> RegistryRecord | None:
        """Lookup record by Canonical AST Hash."""
        return self._repo.get_by_canonical_hash(canonical_hash)

    def query_by_taxonomy(self, category: TaxonomyCategory) -> list[RegistryRecord]:
        """Query features belonging to a specific taxonomy category."""
        all_recs = self._repo.list_all()
        return [r for r in all_recs if r.feature_metadata.taxonomy_category == category]

    def query_by_status(
        self,
        registration_status: RegistrationStatus | None = None,
        validation_status: ValidationStatus | None = None,
    ) -> list[RegistryRecord]:
        """Query features matching registration or validation status."""
        all_recs = self._repo.list_all()
        results = all_recs
        if registration_status is not None:
            results = [r for r in results if r.registration_status == registration_status]
        if validation_status is not None:
            results = [r for r in results if r.validation_status == validation_status]
        return results

    def query_by_capability(
        self,
        vectorized: bool | None = None,
        streaming: bool | None = None,
    ) -> list[RegistryRecord]:
        """Query features matching capability flags."""
        all_recs = self._repo.list_all()
        results = all_recs
        if vectorized is not None:
            results = [r for r in results if r.capability_contract.supports_vectorized_execution == vectorized]
        if streaming is not None:
            results = [r for r in results if r.capability_contract.supports_streaming_execution == streaming]
        return results

    def update_validation_status(
        self,
        feature_id: str,
        validation_status: ValidationStatus,
        actor: str = "system",
        notes: str = "",
    ) -> RegistryRecord:
        """Update quality gate validation status."""
        return self._repo.update_status(
            feature_id=feature_id,
            validation_status=validation_status,
            actor=actor,
            notes=notes,
        )

    def update_registration_status(
        self,
        feature_id: str,
        registration_status: RegistrationStatus,
        actor: str = "system",
        notes: str = "",
    ) -> RegistryRecord:
        """Update registration lifecycle status (e.g. DEPRECATED)."""
        return self._repo.update_status(
            feature_id=feature_id,
            registration_status=registration_status,
            actor=actor,
            notes=notes,
        )

    def get_audit_trail(self, feature_id: str | None = None) -> list[RegistryAuditEvent]:
        """Retrieve audit trail records."""
        return self._repo.get_audit_trail(feature_id)

    def export_snapshot(self, filepath: str | Path) -> str:
        """Export full registry snapshot to JSON file."""
        records = self._repo.list_all()
        snapshot = {
            "snapshot_version": "1.0.0",
            "record_count": len(records),
            "records": [r.model_dump(mode="json") for r in records],
        }
        json_str = json.dumps(snapshot, indent=2, sort_keys=True)
        Path(filepath).write_text(json_str, encoding="utf-8")
        return json_str

    def import_snapshot(self, filepath: str | Path) -> int:
        """Import registry snapshot from JSON file.

        Returns:
            Number of imported records.
        """
        content = Path(filepath).read_text(encoding="utf-8")
        snapshot = json.loads(content)
        records_data = snapshot.get("records", [])

        imported_count = 0
        for rec_data in records_data:
            rec = RegistryRecord(**rec_data)
            if self._repo.get_by_id(rec.feature_id) is None:
                self._repo.save(rec)
                imported_count += 1
        return imported_count
