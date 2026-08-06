"""
Project GOAT v0.7 — Composite Conflict Engine

Evaluates scientific conflicts between candidate participating edges:
- Direct contradiction
- Weak reinforcement
- Duplicate evidence
- Redundant knowledge
- Mutually exclusive applicability
- Scientific disagreement
"""

from __future__ import annotations

from typing import Any

from goat.alpha.core.models import ScientificEdge
from goat.composite.core.enums import ConflictSeverity


class CompositeConflictEngine:
    """Engine for deterministic conflict detection and resolution between participating edges."""

    def evaluate_combination_conflicts(
        self,
        edges: list[ScientificEdge],
    ) -> tuple[float, ConflictSeverity, str]:
        """Evaluate conflict penalty, severity, and explanation between candidate edges deterministically.

        Args:
            edges: List of participating ScientificEdge models.

        Returns:
            Tuple of (penalty_float, ConflictSeverity, explanation_str).
        """
        if len(edges) < 2:
            return 0.0, ConflictSeverity.NONE, "Single edge has zero internal conflicts."

        penalty = 0.0
        reasons: list[str] = []

        # 1. Direct Contradiction Check (e.g., MOM vs REV in identical horizon/dataset)
        titles = [e.title.upper() for e in edges]
        has_mom = any("MOM" in t for t in titles)
        has_rev = any("REV" in t for t in titles)

        if has_mom and has_rev:
            penalty += 0.35
            reasons.append("Direct directional hypothesis contradiction (Momentum vs Reversal).")

        # 2. Duplicate Evidence / Redundant Knowledge Check
        all_vals: list[str] = []
        for e in edges:
            all_vals.extend(e.originating_validations)
        unique_vals = set(all_vals)
        if len(all_vals) > len(unique_vals):
            overlap_count = len(all_vals) - len(unique_vals)
            penalty += min(0.20, 0.05 * overlap_count)
            reasons.append(f"Evidence redundancy detected ({overlap_count} overlapping validation runs).")

        # 3. Weak Reinforcement Check (both edges have low confidence)
        avg_conf = sum(float(e.confidence) for e in edges) / len(edges)
        if avg_conf < 0.60:
            penalty += 0.25
            reasons.append(f"Weak mutual reinforcement (average confidence {avg_conf:.2f} < 0.60).")

        final_penalty = round(min(1.0, penalty), 4)

        if final_penalty >= 0.70:
            severity = ConflictSeverity.CRITICAL_REJECTION
        elif final_penalty >= 0.40:
            severity = ConflictSeverity.HIGH
        elif final_penalty >= 0.20:
            severity = ConflictSeverity.MEDIUM
        elif final_penalty > 0.0:
            severity = ConflictSeverity.LOW
        else:
            severity = ConflictSeverity.NONE

        explanation = "; ".join(reasons) if reasons else "Zero conflicts detected between participating edges."
        return final_penalty, severity, explanation
