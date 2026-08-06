"""
Project GOAT v0.7 — Research Priority Rule Engine

Defines ResearchPriorityRuleEngine for deterministically evaluating research opportunities and assigning priority scores.
"""

from __future__ import annotations

from typing import Any

from goat.prioritization.enums import PriorityLevel, ResearchOpportunityType


class ResearchPriorityRuleEngine:
    """Rule engine evaluating scientific opportunities deterministically without statistical inference or machine learning."""

    def evaluate_opportunity(self, opportunity_data: dict[str, Any]) -> dict[str, Any]:
        """Evaluate an opportunity dictionary and assign priority score, priority level, opportunity type, and justification.

        Args:
            opportunity_data: Dictionary containing 'conflict_ids', 'consensus_status', 'replication_strength', 'maturity', etc.

        Returns:
            Dictionary containing 'score', 'level', 'opportunity_type', 'justification'.
        """
        conflicts = opportunity_data.get("conflict_ids", [])
        consensus_status = str(opportunity_data.get("consensus_status", "")).lower()
        rep_strength = float(opportunity_data.get("replication_strength", 0.0))
        maturity = str(opportunity_data.get("maturity", "early")).lower()
        validated_count = int(opportunity_data.get("validated_count", 0))

        # Rule 1: Unresolved Conflict (Critical)
        if conflicts:
            return {
                "score": 0.95,
                "level": PriorityLevel.CRITICAL,
                "opportunity_type": ResearchOpportunityType.CONFLICT_RESOLUTION,
                "justification": f"Unresolved scientific evidence conflict ({len(conflicts)} conflicts) requires critical experimental resolution.",
            }

        # Rule 2: Independent Replication Required (High)
        if validated_count >= 1 and rep_strength == 0.0:
            return {
                "score": 0.85,
                "level": PriorityLevel.HIGH,
                "opportunity_type": ResearchOpportunityType.REPLICATION_REQUIRED,
                "justification": "Positive exploratory findings require independent replication across additional synthetic market regimes.",
            }

        # Rule 3: Insufficient Evidence (High)
        if consensus_status in ["insufficient_evidence", "emerging"]:
            return {
                "score": 0.75,
                "level": PriorityLevel.HIGH,
                "opportunity_type": ResearchOpportunityType.INSUFFICIENT_EVIDENCE,
                "justification": f"Consensus status '{consensus_status}' indicates insufficient evidence to establish scientific consensus.",
            }

        # Rule 4: Early Maturity Knowledge Validation (Moderate)
        if maturity == "early":
            return {
                "score": 0.60,
                "level": PriorityLevel.MODERATE,
                "opportunity_type": ResearchOpportunityType.KNOWLEDGE_VALIDATION,
                "justification": "Early-stage research maturity requires additional multi-experiment studies to strengthen confidence.",
            }

        # Rule 5: Knowledge Expansion / Refinement (Low)
        if maturity == "intermediate":
            return {
                "score": 0.40,
                "level": PriorityLevel.LOW,
                "opportunity_type": ResearchOpportunityType.KNOWLEDGE_REFINEMENT,
                "justification": "Intermediate research maturity offers refinement and scope expansion opportunities.",
            }

        # Default: Routine Consensus Review (Low)
        return {
            "score": 0.20,
            "level": PriorityLevel.LOW,
            "opportunity_type": ResearchOpportunityType.CONSENSUS_REVIEW,
            "justification": "Mature consensus-backed knowledge subject to routine periodic review.",
        }
