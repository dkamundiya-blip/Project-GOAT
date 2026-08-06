"""
Project GOAT v0.7 — Deterministic Conflict Detector

Implements rule-based deterministic conflict evaluation across validation findings:
- SUPPORTED
- PARTIALLY_SUPPORTED
- CONTRADICTED
- DUPLICATED
- SUPERSEDED
- INSUFFICIENT_EVIDENCE
"""

from __future__ import annotations

from typing import Any

from goat.integration.core.canonical import compute_conflict_id, compute_canonical_sha256
from goat.integration.core.enums import ConflictSeverity, ConflictType
from goat.integration.core.models import ConflictRecord


class ConflictDetector:
    """Engine for deterministic conflict detection and classification between validation runs."""

    def evaluate_conflict(
        self,
        val_a: dict[str, Any],
        val_b: dict[str, Any],
        timestamp: str = "",
    ) -> ConflictRecord:
        """Evaluate conflict between two validation findings deterministically.

        Args:
            val_a: First validation summary dict.
            val_b: Second validation summary dict.
            timestamp: Optional timestamp string.

        Returns:
            ConflictRecord object.
        """
        id_a = str(val_a.get("validation_id") or val_a.get("id") or "VAL_A").strip()
        id_b = str(val_b.get("validation_id") or val_b.get("id") or "VAL_B").strip()

        conf_a = float(val_a.get("confidence", 0.0))
        conf_b = float(val_b.get("confidence", 0.0))

        status_a = str(val_a.get("status") or val_a.get("decision") or "").upper()
        status_b = str(val_b.get("status") or val_b.get("decision") or "").upper()

        effect_a = val_a.get("effect_direction") or val_a.get("effect")
        effect_b = val_b.get("effect_direction") or val_b.get("effect")

        ver_a = str(val_a.get("version", "1.0.0"))
        ver_b = str(val_b.get("version", "1.0.0"))

        ev_a = val_a.get("supporting_evidence", [])
        ev_b = val_b.get("supporting_evidence", [])
        supporting_evidence = sorted(list(set(ev_a + ev_b + [id_a, id_b])))

        # Deterministic Classification Rules
        conflict_type: ConflictType
        severity: ConflictSeverity
        explanation: str

        if conf_a < 0.30 or conf_b < 0.30:
            conflict_type = ConflictType.INSUFFICIENT_EVIDENCE
            severity = ConflictSeverity.LOW
            explanation = f"Validation confidence below threshold: conf_a={conf_a:.2f}, conf_b={conf_b:.2f}."

        elif status_a == status_b and effect_a == effect_b and conf_a == conf_b and ver_a == ver_b:
            conflict_type = ConflictType.DUPLICATED
            severity = ConflictSeverity.NONE
            explanation = "Validations are identical in status, effect direction, confidence, and version."

        elif status_a in ("PASSED", "VALIDATED", "SUPPORTED") and status_b in ("FAILED", "REJECTED", "CONTRADICTED"):
            conflict_type = ConflictType.CONTRADICTED
            severity = ConflictSeverity.HIGH if (conf_a > 0.70 and conf_b > 0.70) else ConflictSeverity.MEDIUM
            explanation = f"Contradictory findings: '{id_a}' is {status_a} while '{id_b}' is {status_b}."

        elif status_b in ("PASSED", "VALIDATED", "SUPPORTED") and status_a in ("FAILED", "REJECTED", "CONTRADICTED"):
            conflict_type = ConflictType.CONTRADICTED
            severity = ConflictSeverity.HIGH if (conf_a > 0.70 and conf_b > 0.70) else ConflictSeverity.MEDIUM
            explanation = f"Contradictory findings: '{id_b}' is {status_b} while '{id_a}' is {status_a}."

        elif val_b.get("supersedes_id") == id_a or (ver_b > ver_a and status_b in ("PASSED", "VALIDATED", "SUPPORTED")):
            conflict_type = ConflictType.SUPERSEDED
            severity = ConflictSeverity.LOW
            explanation = f"Validation '{id_b}' (v{ver_b}) supersedes earlier validation '{id_a}' (v{ver_a})."

        elif val_a.get("supersedes_id") == id_b or (ver_a > ver_b and status_a in ("PASSED", "VALIDATED", "SUPPORTED")):
            conflict_type = ConflictType.SUPERSEDED
            severity = ConflictSeverity.LOW
            explanation = f"Validation '{id_a}' (v{ver_a}) supersedes earlier validation '{id_b}' (v{ver_b})."

        elif status_a in ("PASSED", "VALIDATED", "SUPPORTED") and status_b in ("PASSED", "VALIDATED", "SUPPORTED"):
            if abs(conf_a - conf_b) > 0.35:
                conflict_type = ConflictType.PARTIALLY_SUPPORTED
                severity = ConflictSeverity.MEDIUM
                explanation = f"Both validated but confidence discrepancy exceeds threshold: {conf_a:.2f} vs {conf_b:.2f}."
            else:
                conflict_type = ConflictType.SUPPORTED
                severity = ConflictSeverity.NONE
                explanation = f"Both validations confirm the finding with aligned confidence levels."

        else:
            conflict_type = ConflictType.PARTIALLY_SUPPORTED
            severity = ConflictSeverity.LOW
            explanation = f"Partial alignment between validation '{id_a}' ({status_a}) and '{id_b}' ({status_b})."

        conflict_id, _ = compute_conflict_id(id_a, id_b, conflict_type.value)

        payload = {
            "conflict_id": conflict_id,
            "conflict_type": conflict_type.value,
            "explanation": explanation,
            "severity": severity.value,
            "supporting_evidence": supporting_evidence,
            "validation_a": min(id_a, id_b),
            "validation_b": max(id_a, id_b),
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return ConflictRecord(
            conflict_id=conflict_id,
            validation_a=id_a,
            validation_b=id_b,
            conflict_type=conflict_type,
            severity=severity,
            explanation=explanation,
            supporting_evidence=supporting_evidence,
            canonical_hash=canonical_hash,
            timestamp=timestamp,
        )

    def detect_all_conflicts(
        self,
        validations: list[dict[str, Any]],
        timestamp: str = "",
    ) -> list[ConflictRecord]:
        """Run pairwise conflict detection across a list of validations deterministically.

        Returns:
            List of ConflictRecord objects sorted by conflict_id.
        """
        conflicts: list[ConflictRecord] = []
        sorted_vals = sorted(
            validations,
            key=lambda x: str(x.get("validation_id") or x.get("id") or ""),
        )

        for i in range(len(sorted_vals)):
            for j in range(i + 1, len(sorted_vals)):
                rec = self.evaluate_conflict(sorted_vals[i], sorted_vals[j], timestamp=timestamp)
                conflicts.append(rec)

        return sorted(conflicts, key=lambda c: c.conflict_id)
