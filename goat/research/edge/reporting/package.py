"""
Project GOAT v0.6 — Scientific Evidence Package Atomic Filesystem Persistence

Implements EvidencePackageWriter for generating deterministic, atomic, crash-resistant,
and tamper-evident scientific evidence packages under data/edge_reports/<val_run_id>/<report_id>/.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Sequence
import uuid

from goat.research.edge.canonical import canonical_json
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.reporting.builder import sort_canonical_evidence
from goat.research.edge.reporting.exceptions import (
    PackageCollisionError,
    PackageIntegrityError,
    SecurityViolationError,
)
from goat.research.edge.reporting.identity import compute_report_id
from goat.research.edge.reporting.integrity import ReportIntegrityVerifier
from goat.research.edge.reporting.models import ValidationReport
from goat.research.edge.reporting.package_integrity import (
    PACKAGE_SCHEMA_VERSION,
    EvidencePackageVerifier,
    compute_file_sha256,
    validate_path_component,
)
from goat.research.edge.reporting.serializer import render_report_markdown, serialize_report_to_json


class EvidencePackageWriter:
    """Atomic filesystem writer for scientific evidence packages."""

    def __init__(self, root_dir: Path | str = "data/edge_reports") -> None:
        self.root_dir = Path(root_dir).resolve()

    def _ensure_containment(self, target_path: Path) -> None:
        """Verify resolved target_path is strictly contained within self.root_dir."""
        try:
            target_path.resolve().relative_to(self.root_dir)
        except ValueError as exc:
            raise SecurityViolationError(
                f"Security violation: Target path '{target_path}' escapes root directory '{self.root_dir}'"
            ) from exc

    def write_package(
        self,
        report: ValidationReport,
        evidence_records: Sequence[AtomicEvidenceRecord],
    ) -> Path:
        """Atomically generate and publish evidence package for report and evidence_records.

        Returns:
            Path pointing to published package directory data/edge_reports/<val_run_id>/<report_id>/.

        Raises:
            SecurityViolationError: If path components contain invalid characters or attempt path traversal.
            ReportIntegrityError: If report verification fails before writing.
            PackageCollisionError: If an existing package at the target path is conflicting or corrupted.
            PackageIntegrityError: If temporary package fails integrity verification.
        """
        # 1. Path Component Validation
        val_run_id = validate_path_component("validation_run_id", report.validation_run_id)
        report_id = validate_path_component("report_id", report.report_id)

        # 2. Verify Report Integrity Before Filesystem Operations
        verifier = ReportIntegrityVerifier()
        verifier.verify_report(report, evidence_records)

        # 3. Determine Target Directory
        run_dir = self.root_dir / val_run_id
        final_pkg_dir = run_dir / report_id

        self.root_dir.mkdir(parents=True, exist_ok=True)
        run_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_containment(final_pkg_dir)

        # 4. Handle Existing Package (Idempotent vs Collision)
        pkg_verifier = EvidencePackageVerifier()
        if final_pkg_dir.exists():
            try:
                pkg_verifier.verify_package(final_pkg_dir, report_verifier=verifier)
                # Verified identical package exists: Return idempotently
                return final_pkg_dir
            except Exception as exc:
                raise PackageCollisionError(
                    f"Target package directory '{final_pkg_dir}' already exists and contains conflicting or corrupted data"
                ) from exc

        # 5. Create Sibling Temporary Directory
        tmp_dir_name = f".tmp_{uuid.uuid4().hex}"
        tmp_dir = run_dir / tmp_dir_name
        self._ensure_containment(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=False)

        try:
            # 6. Write validation_report.json
            report_json_path = tmp_dir / "validation_report.json"
            report_json_content = serialize_report_to_json(report)
            with open(report_json_path, "w", encoding="utf-8") as f:
                f.write(report_json_content)

            # 7. Write validation_report.md
            report_md_path = tmp_dir / "validation_report.md"
            report_md_content = render_report_markdown(report)
            with open(report_md_path, "w", encoding="utf-8") as f:
                f.write(report_md_content)

            # 8. Write evidence.json
            sorted_evidence = sort_canonical_evidence(evidence_records)
            ev_dict_list = [ev.model_dump(mode="json") for ev in sorted_evidence]
            evidence_json_path = tmp_dir / "evidence.json"
            evidence_json_content = json.dumps(ev_dict_list, indent=2, sort_keys=True, ensure_ascii=False)
            with open(evidence_json_path, "w", encoding="utf-8") as f:
                f.write(evidence_json_content)

            # Compute file SHA-256 digests for artifacts
            sha_report_json = compute_file_sha256(report_json_path)
            sha_report_md = compute_file_sha256(report_md_path)
            sha_evidence_json = compute_file_sha256(evidence_json_path)

            # 9. Build and Write manifest.json
            now_iso = datetime.now(timezone.utc).isoformat()
            audit_id_str = report.confirmatory_audit.audit_id if report.confirmatory_audit else ""

            manifest_data = {
                "package_schema_version": PACKAGE_SCHEMA_VERSION,
                "report_schema_version": report.report_schema_version,
                "report_id": report.report_id,
                "validation_run_id": report.validation_run_id,
                "edge_id": report.edge_identity.edge_id,
                "policy_hash": report.policy_specification.policy_hash,
                "dataset_fingerprint": report.data_provenance.dataset_fingerprint,
                "hypothesis_version": report.hypothesis_identity.hypothesis_version,
                "context_universe_id": report.data_provenance.context_universe_id,
                "audit_id": audit_id_str,
                "generated_at_utc": now_iso,
                "artifacts": {
                    "validation_report.json": {
                        "size_bytes": report_json_path.stat().st_size,
                        "sha256": sha_report_json,
                    },
                    "validation_report.md": {
                        "size_bytes": report_md_path.stat().st_size,
                        "sha256": sha_report_md,
                    },
                    "evidence.json": {
                        "size_bytes": evidence_json_path.stat().st_size,
                        "sha256": sha_evidence_json,
                    },
                },
            }

            manifest_json_path = tmp_dir / "manifest.json"
            with open(manifest_json_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2, sort_keys=True, ensure_ascii=False)

            sha_manifest_json = compute_file_sha256(manifest_json_path)

            # 10. Build and Write integrity.json
            integrity_data = {
                "integrity_schema_version": 1,
                "report_id": report.report_id,
                "files": {
                    "manifest.json": sha_manifest_json,
                    "validation_report.json": sha_report_json,
                    "validation_report.md": sha_report_md,
                    "evidence.json": sha_evidence_json,
                },
            }

            integrity_json_path = tmp_dir / "integrity.json"
            with open(integrity_json_path, "w", encoding="utf-8") as f:
                json.dump(integrity_data, f, indent=2, sort_keys=True, ensure_ascii=False)

            # 11. Verify Temporary Package Before Publishing
            pkg_verifier.verify_package(tmp_dir, report_verifier=verifier)

            # 12. Atomic Publish (Path.replace) with concurrent collision handling
            try:
                tmp_dir.replace(final_pkg_dir)
            except (FileExistsError, OSError, PermissionError) as replace_exc:
                if final_pkg_dir.exists():
                    try:
                        pkg_verifier.verify_package(final_pkg_dir, report_verifier=verifier)
                        shutil.rmtree(tmp_dir, ignore_errors=True)
                        return final_pkg_dir
                    except Exception as verify_exc:
                        raise PackageCollisionError(
                            f"Concurrent package publish collision at '{final_pkg_dir}': verification failed"
                        ) from verify_exc
                raise replace_exc

            # 13. Verify Final Directory Existence
            if not final_pkg_dir.exists():
                raise PackageIntegrityError(f"Atomic package publish failed for '{final_pkg_dir}'")

            return final_pkg_dir

        except Exception:
            # Clean up temporary directory on failure
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
