"""
Project GOAT v0.7 — Knowledge Registry Service Layer

Implements KnowledgeRegistry service for candidate registration, duplicate rejection,
deterministic query APIs, audit trail management, and snapshot import/export.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

from goat.knowledge.enums import KnowledgeStatus, KnowledgeType
from goat.knowledge.evidence import EvidenceReference
from goat.knowledge.model import KnowledgeObject
from goat.knowledge.registry.model import KnowledgeAuditEvent, KnowledgeRegistryRecord
from goat.knowledge.registry.sqlite import SQLiteKnowledgeRepository
from goat.research.edge.canonical import compute_canonical_sha256


class KnowledgeValidationError(ValueError):
    """Raised when Knowledge Object validation or registration fails."""
    pass


class KnowledgeRegistry:
    """Authoritative scientific registry service for Knowledge Objects."""

    def __init__(self, repo: SQLiteKnowledgeRepository) -> None:
        self._repo = repo

    def register_knowledge(
        self,
        knowledge_object: KnowledgeObject,
        evidence_references: list[EvidenceReference] | None = None,
        provenance: str = "system",
        notes: str = "",
    ) -> KnowledgeRegistryRecord:
        """Register a KnowledgeObject into the registry with fail-closed validation.

        Args:
            knowledge_object: KnowledgeObject instance.
            evidence_references: List of supporting EvidenceReferences.
            provenance: Provenance attribution.
            notes: Registration commentary notes.

        Returns:
            Registered KnowledgeRegistryRecord.
        """
        kid = knowledge_object.knowledge_id
        fp = knowledge_object.scientific_fingerprint

        # Fail-closed duplicate checks
        if self._repo.get_by_id(kid) is not None:
            raise KnowledgeValidationError(f"Duplicate Knowledge ID registration: '{kid}' already exists")
        if self._repo.get_by_fingerprint(fp) is not None:
            raise KnowledgeValidationError(f"Duplicate Scientific Fingerprint registration: '{fp}' already exists")

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        evd_list = evidence_references or []

        record = KnowledgeRegistryRecord(
            knowledge_id=kid,
            scientific_fingerprint=fp,
            canonical_hash=knowledge_object.canonical_hash,
            semantic_version=knowledge_object.semantic_version,
            knowledge_type=knowledge_object.knowledge_type,
            knowledge_status=knowledge_object.knowledge_status,
            title=knowledge_object.title,
            knowledge_object=knowledge_object,
            evidence_references=evd_list,
            registration_timestamp=timestamp,
            provenance=provenance,
            notes=notes,
        )

        self._repo.save(record)

        # Log audit event
        event_hash = compute_canonical_sha256({"id": kid, "timestamp": timestamp, "type": "REGISTER"})
        audit_event = KnowledgeAuditEvent(
            event_id=f"AUD_{event_hash[:16].upper()}",
            knowledge_id=kid,
            event_type="REGISTER",
            timestamp=timestamp,
            previous_state="",
            new_state=knowledge_object.knowledge_status.value,
            provenance=provenance,
            notes=f"Registered Knowledge Object '{knowledge_object.title}'",
        )
        self._repo.log_audit_event(audit_event)

        return record

    def get_by_id(self, knowledge_id: str) -> KnowledgeRegistryRecord:
        """Retrieve KnowledgeRegistryRecord by Knowledge ID."""
        rec = self._repo.get_by_id(knowledge_id)
        if rec is None:
            raise KeyError(f"Knowledge ID '{knowledge_id}' not found in KnowledgeRegistry")
        return rec

    def get_by_fingerprint(self, scientific_fingerprint: str) -> KnowledgeRegistryRecord:
        """Retrieve KnowledgeRegistryRecord by Scientific Fingerprint."""
        rec = self._repo.get_by_fingerprint(scientific_fingerprint)
        if rec is None:
            raise KeyError(f"Scientific Fingerprint '{scientific_fingerprint}' not found in KnowledgeRegistry")
        return rec

    def query_by_type(self, knowledge_type: KnowledgeType) -> list[KnowledgeRegistryRecord]:
        """Query Knowledge records by taxonomy KnowledgeType."""
        all_recs = self._repo.list_all()
        return [r for r in all_recs if r.knowledge_type == knowledge_type]

    def query_by_status(self, status: KnowledgeStatus) -> list[KnowledgeRegistryRecord]:
        """Query Knowledge records by KnowledgeStatus."""
        all_recs = self._repo.list_all()
        return [r for r in all_recs if r.knowledge_status == status]

    def update_status(self, knowledge_id: str, new_status: KnowledgeStatus, notes: str = "") -> None:
        """Update Knowledge status with audit trail logging."""
        rec = self.get_by_id(knowledge_id)
        old_status = rec.knowledge_status.value

        self._repo.update_status(knowledge_id, new_status)

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        event_hash = compute_canonical_sha256({"id": knowledge_id, "new": new_status.value, "timestamp": timestamp})
        audit_event = KnowledgeAuditEvent(
            event_id=f"AUD_{event_hash[:16].upper()}",
            knowledge_id=knowledge_id,
            event_type="STATUS_CHANGE",
            timestamp=timestamp,
            previous_state=old_status,
            new_state=new_status.value,
            provenance="system",
            notes=notes or f"Updated status to '{new_status.value}'",
        )
        self._repo.log_audit_event(audit_event)

    def get_audit_trail(self, knowledge_id: str) -> list[KnowledgeAuditEvent]:
        """Retrieve audit log history for a Knowledge ID."""
        return self._repo.get_audit_trail(knowledge_id)

    def list_all_records(self) -> list[KnowledgeRegistryRecord]:
        """List all registered KnowledgeRegistryRecords."""
        return self._repo.list_all()

    def export_snapshot(self, file_path: str | Path) -> None:
        """Export full registry snapshot to JSON file."""
        records = [r.model_dump(mode="json") for r in self._repo.list_all()]
        snapshot_data = {
            "export_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "record_count": len(records),
            "records": records,
            "version": "1.0.0",
        }
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snapshot_data, indent=2), encoding="utf-8")

    def import_snapshot(self, file_path: str | Path) -> int:
        """Import registry snapshot from JSON file.

        Returns:
            Count of newly imported records.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot file '{file_path}' not found")

        content = json.loads(path.read_text(encoding="utf-8"))
        records_data = content.get("records", [])
        imported_count = 0

        for r_dict in records_data:
            rec = KnowledgeRegistryRecord(**r_dict)
            if self._repo.get_by_id(rec.knowledge_id) is None:
                self.register_knowledge(
                    knowledge_object=rec.knowledge_object,
                    evidence_references=rec.evidence_references,
                    provenance=rec.provenance,
                    notes=f"Imported from snapshot '{path.name}'",
                )
                imported_count += 1

        return imported_count
