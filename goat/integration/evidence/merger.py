"""
Project GOAT v0.7 — Deterministic Evidence Merger

Provides deterministic aggregation of scientific evidence:
- Evidence accumulation
- Confidence accumulation
- Reproducibility accumulation
- Consensus accumulation
- Experiment references
- Study references
- Execution references
- Feature references
"""

from __future__ import annotations

import math
from typing import Any

from goat.integration.core.canonical import compute_evidence_merge_id, compute_canonical_sha256
from goat.integration.evidence.models import EvidenceMergeRecord


class EvidenceMerger:
    """Engine for deterministic evidence aggregation and reference tracking."""

    @staticmethod
    def accumulate_confidence(confidences: list[float]) -> float:
        """Deterministically aggregate confidence values using independent accumulation.

        Formula: 1 - prod(1 - c_i) for c_i in confidences.
        Returns float in range [0.0, 1.0] rounded to 6 decimal places for reproducibility.
        """
        if not confidences:
            return 0.0

        prod = 1.0
        for c in confidences:
            clamped = max(0.0, min(1.0, float(c)))
            prod *= (1.0 - clamped)

        res = 1.0 - prod
        return round(max(0.0, min(1.0, res)), 6)

    @staticmethod
    def accumulate_reproducibility(reproducibilities: list[float]) -> float:
        """Deterministically aggregate reproducibility scores using arithmetic mean."""
        if not reproducibilities:
            return 0.0

        clean = [max(0.0, min(1.0, float(r))) for r in reproducibilities]
        mean_val = sum(clean) / len(clean)
        return round(max(0.0, min(1.0, mean_val)), 6)

    @staticmethod
    def accumulate_consensus(support_count: int, total_count: int) -> float:
        """Deterministically calculate consensus score from support and total evidence counts."""
        if total_count <= 0:
            return 0.0

        ratio = float(support_count) / float(total_count)
        return round(max(0.0, min(1.0, ratio)), 6)

    def merge_evidence(
        self,
        evidence_items: list[dict[str, Any]],
        target_knowledge_id: str,
        timestamp: str,
    ) -> EvidenceMergeRecord:
        """Merge a collection of evidence dictionaries into an EvidenceMergeRecord deterministically.

        Args:
            evidence_items: List of evidence payloads or validation summaries.
            target_knowledge_id: Target IKN_<HEX16> ID.
            timestamp: ISO 8601 UTC timestamp.

        Returns:
            EvidenceMergeRecord object.
        """
        evidence_ids: set[str] = set()
        confidences: list[float] = []
        reproducibilities: list[float] = []
        experiment_refs: set[str] = set()
        study_refs: set[str] = set()
        execution_refs: set[str] = set()
        feature_refs: set[str] = set()

        support_count = 0
        total_count = len(evidence_items)

        for item in evidence_items:
            ev_id = str(item.get("evidence_id") or item.get("validation_id") or "").strip()
            if ev_id:
                evidence_ids.add(ev_id)

            if "confidence" in item:
                confidences.append(float(item["confidence"]))

            if "reproducibility" in item:
                reproducibilities.append(float(item["reproducibility"]))

            if item.get("status", "").upper() in ("SUPPORTED", "PASSED", "VALIDATED"):
                support_count += 1

            for exp in item.get("experiment_refs", []):
                if exp:
                    experiment_refs.add(str(exp).strip())

            for std in item.get("study_refs", []):
                if std:
                    study_refs.add(str(std).strip())

            for exe in item.get("execution_refs", []):
                if exe:
                    execution_refs.add(str(exe).strip())

            for feat in item.get("feature_refs", []):
                if feat:
                    feature_refs.add(str(feat).strip())

        sorted_evidence_ids = sorted(list(evidence_ids))
        merge_id, _ = compute_evidence_merge_id(sorted_evidence_ids, target_knowledge_id)

        accum_conf = self.accumulate_confidence(confidences)
        accum_repr = self.accumulate_reproducibility(reproducibilities)
        accum_cons = self.accumulate_consensus(support_count, total_count)

        payload = {
            "accumulated_confidence": accum_conf,
            "accumulated_consensus": accum_cons,
            "accumulated_reproducibility": accum_repr,
            "experiment_refs": sorted(list(experiment_refs)),
            "feature_refs": sorted(list(feature_refs)),
            "merge_id": merge_id,
            "source_evidence_ids": sorted_evidence_ids,
            "study_refs": sorted(list(study_refs)),
            "target_knowledge_id": target_knowledge_id,
            "timestamp": timestamp,
        }
        canonical_hash = compute_canonical_sha256(payload).upper()

        return EvidenceMergeRecord(
            merge_id=merge_id,
            source_evidence_ids=sorted_evidence_ids,
            target_knowledge_id=target_knowledge_id,
            accumulated_confidence=accum_conf,
            accumulated_reproducibility=accum_repr,
            accumulated_consensus=accum_cons,
            experiment_refs=sorted(list(experiment_refs)),
            study_refs=sorted(list(study_refs)),
            execution_refs=sorted(list(execution_refs)),
            feature_refs=sorted(list(feature_refs)),
            timestamp=timestamp,
            canonical_hash=canonical_hash,
        )
