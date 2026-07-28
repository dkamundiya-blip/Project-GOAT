"""
Project GOAT v0.6 — Evidence Package Cryptographic Verifier

Independently verifies filesystem scientific evidence packages according to SPEC.4 architecture.
Validates file presence, cryptographic digests, manifest consistency, and canonical evidence integrity.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Sequence

from goat.research.edge.canonical import canonicalize_structure
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.reporting.builder import sort_canonical_evidence
from goat.research.edge.reporting.exceptions import (
    PackageIntegrityError,
    ReportIntegrityError,
    SecurityViolationError,
    UnsupportedReportSchemaError,
)
from goat.research.edge.reporting.identity import compute_report_id
from goat.research.edge.reporting.integrity import ReportIntegrityVerifier
from goat.research.edge.reporting.models import ValidationReport

PACKAGE_SCHEMA_VERSION = 1
SAFE_PATH_COMPONENT_REGEX = re.compile(r"^[A-Za-z0-9_-]+$")
TMP_DIR_REGEX = re.compile(r"^\.tmp_[a-f0-9]{32}$")

REQUIRED_PACKAGE_FILES = (
    "manifest.json",
    "validation_report.json",
    "validation_report.md",
    "evidence.json",
    "integrity.json",
)


def validate_path_component(component_name: str, value: str) -> str:
    """Validate dynamic path component against strict ^[A-Za-z0-9_-]+$ security regex.

    Raises:
        SecurityViolationError: If value contains path traversal, slashes, dots, whitespace, or invalid characters.
    """
    val_str = str(value).strip()
    if not val_str:
        raise SecurityViolationError(f"Path component '{component_name}' cannot be empty")
    if ".." in val_str or "/" in val_str or "\\" in val_str or ":" in val_str or "\x00" in val_str:
        raise SecurityViolationError(f"Security violation: Path component '{component_name}' contains illegal path characters")
    if not SAFE_PATH_COMPONENT_REGEX.match(val_str):
        raise SecurityViolationError(
            f"Security violation: Path component '{component_name}' value '{val_str}' fails security regex ^[A-Za-z0-9_-]+$"
        )
    return val_str


def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA-256 digest of a filesystem artifact."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class EvidencePackageVerifier:
    """Independent filesystem verifier for scientific evidence packages."""

    def verify_package(
        self,
        package_dir: Path | str,
        report_verifier: ReportIntegrityVerifier | None = None,
    ) -> dict[str, Any]:
        """Verify completeness, file digests, manifest structure, and canonical scientific integrity of package_dir.

        Returns:
            Dict containing verification manifest summary.

        Raises:
            PackageIntegrityError: If file is missing, checksum fails, or structure is tampered with.
            SecurityViolationError: If directory path components fail security validation.
            ReportIntegrityError: If report identity or evidence payload hash fails validation.
        """
        pkg_path = Path(package_dir).resolve()
        if not pkg_path.is_dir():
            raise PackageIntegrityError(f"Evidence package directory '{pkg_path}' does not exist or is not a directory")

        report_id = pkg_path.name
        val_run_id = pkg_path.parent.name

        if report_id.startswith(".tmp_"):
            if not TMP_DIR_REGEX.match(report_id):
                raise SecurityViolationError(
                    f"Security violation: Temporary directory name '{report_id}' fails temporary security regex"
                )
        else:
            validate_path_component("report_id", report_id)

        validate_path_component("validation_run_id", val_run_id)

        # 1. Verify File Inventory
        existing_files = {f.name for f in pkg_path.iterdir() if f.is_file()}
        for req in REQUIRED_PACKAGE_FILES:
            if req not in existing_files:
                raise PackageIntegrityError(f"Package '{pkg_path.name}' missing mandatory artifact '{req}'")

        # Reject temporary or extraneous files inside final package
        for filename in existing_files:
            if filename not in REQUIRED_PACKAGE_FILES:
                raise PackageIntegrityError(
                    f"Package '{pkg_path.name}' contains unexpected/unauthorized artifact '{filename}'"
                )

        # 2. Parse manifest.json
        manifest_path = pkg_path / "manifest.json"
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as exc:
            raise PackageIntegrityError(f"Failed to parse manifest.json in package '{pkg_path.name}'") from exc

        if manifest.get("package_schema_version") != PACKAGE_SCHEMA_VERSION:
            raise UnsupportedReportSchemaError(
                f"Package schema version '{manifest.get('package_schema_version')}' unsupported (expected {PACKAGE_SCHEMA_VERSION})"
            )

        if not report_id.startswith(".tmp_") and manifest.get("report_id") != report_id:
            raise PackageIntegrityError(
                f"Manifest report_id '{manifest.get('report_id')}' != directory report_id '{report_id}'"
            )

        if manifest.get("validation_run_id") != val_run_id:
            raise PackageIntegrityError(
                f"Manifest validation_run_id '{manifest.get('validation_run_id')}' != parent directory '{val_run_id}'"
            )

        # 3. Parse integrity.json
        integrity_path = pkg_path / "integrity.json"
        try:
            with open(integrity_path, "r", encoding="utf-8") as f:
                integrity_doc = json.load(f)
        except Exception as exc:
            raise PackageIntegrityError(f"Failed to parse integrity.json in package '{pkg_path.name}'") from exc

        if not report_id.startswith(".tmp_") and integrity_doc.get("report_id") != report_id:
            raise PackageIntegrityError(
                f"Integrity report_id '{integrity_doc.get('report_id')}' != directory report_id '{report_id}'"
            )

        # 4. Verify Cryptographic File Checksums
        manifest_inventory = manifest.get("artifacts", {})
        integrity_files = integrity_doc.get("files", {})

        for filename in REQUIRED_PACKAGE_FILES:
            file_p = pkg_path / filename
            actual_sha = compute_file_sha256(file_p)

            # Verify against manifest inventory
            if filename in manifest_inventory:
                expected_sha = manifest_inventory[filename].get("sha256")
                if actual_sha != expected_sha:
                    raise PackageIntegrityError(
                        f"Checksum mismatch for '{filename}' in manifest: actual '{actual_sha}' != expected '{expected_sha}'"
                    )

            # Verify against integrity.json
            if filename in integrity_files:
                expected_sha = integrity_files[filename]
                if actual_sha != expected_sha:
                    raise PackageIntegrityError(
                        f"Checksum mismatch for '{filename}' in integrity.json: actual '{actual_sha}' != expected '{expected_sha}'"
                    )

        # 5. Deserialize & Verify validation_report.json
        report_path = pkg_path / "validation_report.json"
        with open(report_path, "r", encoding="utf-8") as f:
            report_dict = json.load(f)

        try:
            report = ValidationReport.model_validate(report_dict)
        except Exception as exc:
            raise PackageIntegrityError(f"ValidationReport deserialization failed in '{pkg_path.name}'") from exc

        if not report_id.startswith(".tmp_") and report.report_id != report_id:
            raise PackageIntegrityError(
                f"ValidationReport report_id '{report.report_id}' != package report_id '{report_id}'"
            )

        # 6. Deserialize & Verify evidence.json
        evidence_path = pkg_path / "evidence.json"
        with open(evidence_path, "r", encoding="utf-8") as f:
            raw_ev_list = json.load(f)

        evidence_records: list[AtomicEvidenceRecord] = []
        for raw_ev in raw_ev_list:
            try:
                ev = AtomicEvidenceRecord(
                    evidence_id=raw_ev["evidence_id"],
                    evidence_payload_hash=raw_ev["evidence_payload_hash"],
                    validation_run_id=raw_ev["validation_run_id"],
                    edge_id=raw_ev["edge_id"],
                    dimension_type=raw_ev["dimension_type"],
                    dimension_key=raw_ev["dimension_key"],
                    partition_identity=raw_ev["partition_identity"],
                    sample_count=raw_ev["sample_count"],
                    effect_size=raw_ev["effect_size"],
                    effect_size_type=raw_ev["effect_size_type"],
                    raw_p_value=raw_ev["raw_p_value"],
                    adjusted_q_value=raw_ev.get("adjusted_q_value"),
                    statistic_value=raw_ev["statistic_value"],
                    confidence_interval=raw_ev.get("confidence_interval"),
                    context_metadata=raw_ev.get("context_metadata", {}),
                )
                evidence_records.append(ev)
            except Exception as exc:
                raise PackageIntegrityError(f"Failed to deserialize atomic evidence in evidence.json: {exc}") from exc

        # Verify Canonical Evidence Sorting
        sorted_ev = sort_canonical_evidence(evidence_records)
        if tuple(e.evidence_id for e in sorted_ev) != tuple(e.evidence_id for e in evidence_records):
            raise PackageIntegrityError("evidence.json records are not in canonical 5-tuple sorted order")

        # 7. Execute Report Integrity Verifier
        verifier = report_verifier or ReportIntegrityVerifier()
        verifier.verify_report(report, evidence_records)

        return {
            "package_path": str(pkg_path),
            "report_id": report.report_id,
            "validation_run_id": val_run_id,
            "verification_status": "VERIFIED",
            "evidence_count": len(evidence_records),
        }
