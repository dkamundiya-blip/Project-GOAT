"""
Project GOAT v0.9 — Hypothesis Validation Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.research.core.canonical import compute_validation_id
from goat.research.core.models import (
    HypothesisRevision,
    HypothesisValidation,
    ScientificHypothesis,
)


class HypothesisValidationEngine:
    """Validation Engine for evaluating ScientificHypothesis entities against scientific,

    constitutional, and protocol standards.
    """

    def validate_hypothesis(
        self,
        hypothesis: ScientificHypothesis,
        existing_hypotheses: Sequence[ScientificHypothesis] | None = None,
        reviewer: str = "GOAT_VALIDATION_ENGINE",
        timestamp: str | None = None,
    ) -> HypothesisValidation:
        """Perform comprehensive validation on a ScientificHypothesis instance."""
        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        errors: list[str] = []
        warnings: list[str] = []
        rule_results: list[dict[str, Any]] = []

        # Rule 1: Required Field Validation
        field_errors = self.validate_field_integrity(hypothesis)
        rule_results.append({
            "rule_id": "VAL_001_FIELD_INTEGRITY",
            "passed": len(field_errors) == 0,
            "errors": field_errors,
        })
        errors.extend(field_errors)

        # Rule 2: Protocol Compliance
        protocol_errors = self.validate_protocol_compliance(hypothesis)
        rule_results.append({
            "rule_id": "VAL_002_PROTOCOL_COMPLIANCE",
            "passed": len(protocol_errors) == 0,
            "errors": protocol_errors,
        })
        errors.extend(protocol_errors)

        # Rule 3: Constitution Compliance
        const_errors = self.validate_constitution_compliance(hypothesis)
        rule_results.append({
            "rule_id": "VAL_003_CONSTITUTION_COMPLIANCE",
            "passed": len(const_errors) == 0,
            "errors": const_errors,
        })
        errors.extend(const_errors)

        # Rule 4: Duplicate Check
        if existing_hypotheses:
            dup_errors = self.validate_uniqueness(hypothesis, existing_hypotheses)
            rule_results.append({
                "rule_id": "VAL_004_UNIQUENESS",
                "passed": len(dup_errors) == 0,
                "errors": dup_errors,
            })
            errors.extend(dup_errors)

        # Rule 5: Identifier Format Check
        id_errors = self.validate_identifier_format(hypothesis)
        rule_results.append({
            "rule_id": "VAL_005_IDENTIFIER_FORMAT",
            "passed": len(id_errors) == 0,
            "errors": id_errors,
        })
        errors.extend(id_errors)

        is_valid = len(errors) == 0
        validation_id, canonical_hash = compute_validation_id(
            hypothesis_id=hypothesis.hypothesis_id,
            reviewer=reviewer,
            timestamp=now_str,
            is_valid=is_valid,
        )

        return HypothesisValidation(
            validation_id=validation_id,
            hypothesis_id=hypothesis.hypothesis_id,
            is_valid=is_valid,
            validation_rule_results=rule_results,
            validation_errors=errors,
            validation_warnings=warnings,
            reviewer=reviewer,
            timestamp=now_str,
            canonical_hash=canonical_hash,
        )

    def validate_field_integrity(self, hypothesis: ScientificHypothesis) -> list[str]:
        """Validate required non-empty string fields and collection dimensions."""
        errors: list[str] = []
        if not hypothesis.title or len(hypothesis.title.strip()) < 3:
            errors.append("Title must be at least 3 non-whitespace characters.")
        if not hypothesis.research_question or len(hypothesis.research_question.strip()) < 5:
            errors.append("Research question must be at least 5 non-whitespace characters.")
        if not hypothesis.null_hypothesis or len(hypothesis.null_hypothesis.strip()) < 5:
            errors.append("Null hypothesis (H0) must be at least 5 non-whitespace characters.")
        if not hypothesis.alternative_hypothesis or len(hypothesis.alternative_hypothesis.strip()) < 5:
            errors.append("Alternative hypothesis (H1) must be at least 5 non-whitespace characters.")
        if not hypothesis.expected_behaviour or len(hypothesis.expected_behaviour.strip()) < 5:
            errors.append("Expected behaviour must be at least 5 non-whitespace characters.")
        return errors

    def validate_protocol_compliance(self, hypothesis: ScientificHypothesis) -> list[str]:
        """Validate compliance with PRSP v1.0 protocol standards."""
        errors: list[str] = []
        # Check that success criteria or failure criteria are defined
        if not hypothesis.success_criteria and not hypothesis.failure_criteria:
            errors.append("Hypothesis must specify at least one quantitative success or failure criterion.")
        if not hypothesis.author or len(hypothesis.author.strip()) == 0:
            errors.append("Hypothesis author/agent must be specified.")
        return errors

    def validate_constitution_compliance(self, hypothesis: ScientificHypothesis) -> list[str]:
        """Validate compliance with Strategic Constitution rules (e.g. banning forbidden ML/discretionary keywords)."""
        errors: list[str] = []
        text_content = f"{hypothesis.title} {hypothesis.research_question} {hypothesis.expected_behaviour}".lower()
        forbidden = ["discretionary feeling", "intuitive gut", "magic indicator", "guaranteed profit"]
        for term in forbidden:
            if term in text_content:
                errors.append(f"Forbidden term '{term}' violates scientific explainability rules.")
        return errors

    def validate_uniqueness(
        self,
        hypothesis: ScientificHypothesis,
        existing_hypotheses: Sequence[ScientificHypothesis],
    ) -> list[str]:
        """Check for duplicate hypothesis_id or duplicate title/H0 combination."""
        errors: list[str] = []
        for existing in existing_hypotheses:
            if existing.hypothesis_id == hypothesis.hypothesis_id:
                # Check if it's the exact same object (updating) vs duplicate registration
                if existing.revision_number == hypothesis.revision_number:
                    errors.append(f"Duplicate hypothesis_id '{hypothesis.hypothesis_id}' already registered.")
            elif (
                existing.title.strip().lower() == hypothesis.title.strip().lower()
                and existing.null_hypothesis.strip().lower() == hypothesis.null_hypothesis.strip().lower()
            ):
                errors.append(f"Duplicate hypothesis content matching title '{hypothesis.title}'.")
        return errors

    def validate_identifier_format(self, hypothesis: ScientificHypothesis) -> list[str]:
        """Validate hypothesis_id prefix and hex format."""
        errors: list[str] = []
        if not hypothesis.hypothesis_id.startswith("HYP_"):
            errors.append(f"Hypothesis ID '{hypothesis.hypothesis_id}' must start with 'HYP_'.")
        return errors

    def validate_revision_consistency(
        self,
        hypothesis: ScientificHypothesis,
        revisions: Sequence[HypothesisRevision],
    ) -> list[str]:
        """Validate that revision numbers increase monotonically and previous hashes match."""
        errors: list[str] = []
        if not revisions:
            return errors

        sorted_revs = sorted(revisions, key=lambda r: r.revision_number)
        if hypothesis.revision_number != sorted_revs[-1].revision_number:
            errors.append(
                f"Hypothesis revision number ({hypothesis.revision_number}) does not match latest revision ({sorted_revs[-1].revision_number})."
            )

        for i in range(1, len(sorted_revs)):
            if sorted_revs[i].revision_number != sorted_revs[i - 1].revision_number + 1:
                errors.append(
                    f"Non-sequential revision numbers detected: {sorted_revs[i-1].revision_number} -> {sorted_revs[i].revision_number}."
                )
        return errors
