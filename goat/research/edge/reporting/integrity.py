"""
Project GOAT v0.6 — Report Cryptographic Integrity Verifier

Independently verifies ValidationReport cryptographic identity, evidence payload hashes,
confirmatory audit identity, and scientific chain continuity.
"""

from __future__ import annotations

from typing import Sequence

from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.models import compute_confirmatory_audit_id
from goat.research.edge.reporting.builder import sort_canonical_evidence
from goat.research.edge.reporting.exceptions import EvidenceIntegrityError, ReportIntegrityError
from goat.research.edge.reporting.identity import compute_report_id
from goat.research.edge.reporting.models import ValidationReport


class ReportIntegrityVerifier:
    """Independent verifier validating cryptographic proof and scientific continuity of ValidationReport."""

    def verify_report(
        self,
        report: ValidationReport,
        evidence_records: Sequence[AtomicEvidenceRecord],
    ) -> bool:
        """Verify report content hash, atomic evidence payload hashes, and identity chain integrity.

        Returns:
            True if all cryptographic and continuity checks pass cleanly.

        Raises:
            ReportIntegrityError: If any hash mismatch, broken chain, or evidence corruption is detected.
            EvidenceIntegrityError: If atomic evidence payload hash verification fails.
        """
        # 1. Verify Schema Version
        if report.report_schema_version != 1:
            raise ReportIntegrityError(f"Unsupported report_schema_version '{report.report_schema_version}'")

        # 2. Verify Evidence Count
        if len(evidence_records) != report.integrity.evidence_count:
            raise ReportIntegrityError(
                f"Evidence count mismatch: report states {report.integrity.evidence_count}, but passed {len(evidence_records)}"
            )

        # 3. Verify Atomic Evidence Payload Hashes (EVP_)
        sorted_evidence = sort_canonical_evidence(evidence_records)
        recomputed_evp = tuple(ev.evidence_payload_hash for ev in sorted_evidence)

        for ev in sorted_evidence:
            computed_evp = ev.compute_payload_hash()
            if computed_evp != ev.evidence_payload_hash:
                raise EvidenceIntegrityError(
                    f"Evidence '{ev.evidence_id}' payload hash mismatch: computed '{computed_evp}' != recorded '{ev.evidence_payload_hash}'"
                )

        if recomputed_evp != report.integrity.evidence_payload_hashes:
            raise ReportIntegrityError("Sorted evidence payload hashes do not match report integrity metadata")

        # 4. Verify Confirmatory Audit Identity (AUD_) if present
        audit_id_str = ""
        if report.confirmatory_audit is not None:
            computed_aud = compute_confirmatory_audit_id(
                validation_run_id=report.validation_run_id,
                frozen_hypothesis_version=report.confirmatory_audit.frozen_hypothesis_version,
                dataset_fingerprint=report.confirmatory_audit.dataset_fingerprint,
                policy_hash=report.confirmatory_audit.policy_hash,
                holdout_partition_identity=report.confirmatory_audit.holdout_partition_identity,
            )
            if computed_aud != report.confirmatory_audit.audit_id:
                raise ReportIntegrityError(
                    f"Confirmatory audit ID mismatch: computed '{computed_aud}' != report audit_id '{report.confirmatory_audit.audit_id}'"
                )
            audit_id_str = report.confirmatory_audit.audit_id

        # 5. Verify Report Identity (RPT_) Recomputation
        recomputed_rpt = compute_report_id(
            validation_run_id=report.validation_run_id,
            edge_id=report.edge_identity.edge_id,
            policy_hash=report.policy_specification.policy_hash,
            dataset_fingerprint=report.data_provenance.dataset_fingerprint,
            hypothesis_version=report.hypothesis_identity.hypothesis_version,
            evidence_payload_hashes=recomputed_evp,
            context_universe_id=report.data_provenance.context_universe_id,
            audit_id=audit_id_str,
            report_schema_version=report.report_schema_version,
        )

        if recomputed_rpt != report.report_id:
            raise ReportIntegrityError(
                f"Report ID mismatch: recomputed '{recomputed_rpt}' != report_id '{report.report_id}'"
            )

        return True
