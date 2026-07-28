"""
Project GOAT v0.6 — Multiplicity Family Coordinator

Manages candidate hypothesis families, enforces deterministic tie-breaking for FDR correction,
and prevents post-hoc candidate filtering or family mutation after freeze.
"""

from __future__ import annotations

import math
from typing import Mapping

import numpy as np

from goat.research.hypothesis.multiple_testing import benjamini_hochberg_fdr
from goat.research.edge.validation.exceptions import MultiplicityFamilyError


class MultiplicityFamilyCoordinator:
    """Coordinates multiple-testing FDR correction across a registered candidate family."""

    def __init__(self, family_id: str, alpha: float = 0.05) -> None:
        if not family_id.strip():
            raise MultiplicityFamilyError("family_id must be a non-empty string")
        if not (0.0 < alpha < 1.0):
            raise MultiplicityFamilyError(f"alpha must be in range (0, 1), got {alpha}")

        self.family_id = family_id.strip()
        self.alpha = alpha
        self._members: dict[str, float] = {}
        self._is_frozen = False
        self._q_values: dict[str, float] | None = None
        self._rejections: dict[str, bool] | None = None

    @property
    def is_frozen(self) -> bool:
        return self._is_frozen

    @property
    def member_count(self) -> int:
        return len(self._members)

    def register_candidate(self, candidate_id: str, raw_p_value: float) -> None:
        """Register candidate identifier and raw p-value in the family."""
        if self._is_frozen:
            raise MultiplicityFamilyError(f"Cannot register candidate '{candidate_id}': family '{self.family_id}' is frozen")

        cand_id = candidate_id.strip()
        if not cand_id:
            raise MultiplicityFamilyError("candidate_id must be a non-empty string")

        if cand_id in self._members:
            raise MultiplicityFamilyError(f"Candidate '{cand_id}' already registered in family '{self.family_id}'")

        # Strict p-value validation
        if not isinstance(raw_p_value, (int, float)) or math.isnan(raw_p_value) or math.isinf(raw_p_value):
            raise MultiplicityFamilyError(f"Invalid non-finite p-value '{raw_p_value}' for candidate '{cand_id}'")

        p_val = float(raw_p_value)
        if not (0.0 <= p_val <= 1.0):
            raise MultiplicityFamilyError(f"p-value out of bounds [0, 1]: {p_val} for candidate '{cand_id}'")

        self._members[cand_id] = p_val

    def freeze_family(self) -> None:
        """Freeze family membership and compute Benjamini-Hochberg FDR q-values."""
        if self._is_frozen:
            return

        if not self._members:
            raise MultiplicityFamilyError(f"Cannot freeze empty family '{self.family_id}'")

        # Deterministic sorting: sort by p-value ascending, secondary by candidate_id ascending
        sorted_pairs = sorted(self._members.items(), key=lambda item: (item[1], item[0]))
        sorted_cand_ids = [pair[0] for pair in sorted_pairs]
        sorted_pvals = [pair[1] for pair in sorted_pairs]

        # Apply Benjamini-Hochberg FDR procedure
        q_arr, reject_arr = benjamini_hochberg_fdr(sorted_pvals, alpha=self.alpha)

        self._q_values = {cand_id: float(q) for cand_id, q in zip(sorted_cand_ids, q_arr)}
        self._rejections = {cand_id: bool(r) for cand_id, r in zip(sorted_cand_ids, reject_arr)}
        self._is_frozen = True

    def get_q_value(self, candidate_id: str) -> float:
        """Retrieve FDR adjusted q-value for candidate."""
        if not self._is_frozen:
            self.freeze_family()
        assert self._q_values is not None
        if candidate_id not in self._q_values:
            raise MultiplicityFamilyError(f"Candidate '{candidate_id}' not found in family '{self.family_id}'")
        return self._q_values[candidate_id]

    def is_significant(self, candidate_id: str) -> bool:
        """Retrieve significance rejection decision for candidate."""
        if not self._is_frozen:
            self.freeze_family()
        assert self._rejections is not None
        if candidate_id not in self._rejections:
            raise MultiplicityFamilyError(f"Candidate '{candidate_id}' not found in family '{self.family_id}'")
        return self._rejections[candidate_id]
