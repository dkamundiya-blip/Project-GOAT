"""
Project GOAT v0.6 — Validation Policy Model

Defines versioned, immutable ValidationPolicy configuration according to SPEC.3.
All threshold values are explicitly documented as PROVISIONAL_DEFAULT settings.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from goat.research.edge.canonical import compute_canonical_sha256
from goat.research.edge.enums import MetaAnalysisMethod, MultiplicityStrategy


class ValidationPolicy(BaseModel):
    """Immutable versioned validation policy specification."""

    model_config = {"frozen": True}

    policy_id: str
    version: str = "1.0.0"
    description: str = ""
    policy_hash: str = ""

    multiplicity_strategy: MultiplicityStrategy = MultiplicityStrategy.BENJAMINI_HOCHBERG
    meta_analysis_method: MetaAnalysisMethod = MetaAnalysisMethod.FISHER_COMBINED_PROBABILITY

    # PROVISIONAL_DEFAULT Stage A: Discovery Evidence Thresholds
    stage_a_alpha: float = Field(
        default=0.05,
        description="PROVISIONAL_DEFAULT: Significance alpha threshold for discovery",
    )
    stage_a_effect_min: float = Field(
        default=0.15,
        description="PROVISIONAL_DEFAULT: Minimum effect size threshold for discovery",
    )
    stage_a_min_sample: int = Field(
        default=100,
        description="PROVISIONAL_DEFAULT: Minimum sample requirement for discovery",
    )

    # PROVISIONAL_DEFAULT Stage B: OOS Validation Thresholds
    stage_b_min_retention_ratio: float = Field(
        default=0.50,
        description="PROVISIONAL_DEFAULT: Minimum OOS/train effect retention ratio",
    )

    # PROVISIONAL_DEFAULT Stage C: Walk-Forward Thresholds
    stage_c_min_folds: int = Field(
        default=5,
        description="PROVISIONAL_DEFAULT: Minimum number of walk-forward folds",
    )
    stage_c_min_positive_ratio: float = Field(
        default=0.70,
        description="PROVISIONAL_DEFAULT: Minimum ratio of positive effect folds",
    )
    stage_c_max_fold_cv: float = Field(
        default=1.00,
        description="PROVISIONAL_DEFAULT: Maximum coefficient of variation across fold effects",
    )

    # PROVISIONAL_DEFAULT Stage D: Robustness Surface Thresholds
    stage_d_perturbation_delta: float = Field(
        default=0.20,
        description="PROVISIONAL_DEFAULT: Parameter perturbation delta (+/- 20%)",
    )
    stage_d_min_stable_ratio: float = Field(
        default=0.65,
        description="PROVISIONAL_DEFAULT: Minimum ratio of stable neighborhood grid points",
    )
    stage_d_max_allowed_drop: float = Field(
        default=0.60,
        description="PROVISIONAL_DEFAULT: Maximum allowed effect drop ratio before cliff flag",
    )

    # PROVISIONAL_DEFAULT Stage E: Regime Breakdown Thresholds
    stage_e_fail_on_contradictory_inversion: bool = Field(
        default=True,
        description="PROVISIONAL_DEFAULT: Flag whether contradictory regime inversion fails stage",
    )

    # PROVISIONAL_DEFAULT Stage F: Cross-Market Replication Thresholds
    stage_f_min_replication_pct: float = Field(
        default=0.60,
        description="PROVISIONAL_DEFAULT: Minimum cross-symbol replication percentage",
    )
    stage_f_meta_alpha: float = Field(
        default=0.01,
        description="PROVISIONAL_DEFAULT: Meta-analysis significance alpha threshold",
    )

    @field_validator("policy_id", "version")
    @classmethod
    def _validate_non_empty(cls, v: str, info: Any) -> str:
        if not str(v).strip():
            raise ValueError(f"Field '{info.field_name}' must be a non-empty string")
        return str(v).strip()

    @field_validator("stage_a_alpha", "stage_f_meta_alpha")
    @classmethod
    def _validate_alpha_range(cls, v: float, info: Any) -> float:
        if not (0.0 < v < 1.0):
            raise ValueError(f"Field '{info.field_name}' must be strictly between 0 and 1, got {v}")
        return float(v)

    @field_validator("stage_a_min_sample", "stage_c_min_folds")
    @classmethod
    def _validate_min_count(cls, v: int, info: Any) -> int:
        if v < 1:
            raise ValueError(f"Field '{info.field_name}' must be >= 1, got {v}")
        return int(v)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        computed = self.compute_policy_hash()
        if self.policy_hash and self.policy_hash != computed:
            raise ValueError(f"Supplied policy_hash '{self.policy_hash}' does not match computed '{computed}'")
        object.__setattr__(self, "policy_hash", computed)

    def compute_policy_hash(self) -> str:
        """Compute deterministic SHA-256 policy identity hash string: PLC_<HEX16>.

        Fields INCLUDED in policy_hash (scientifically authoritative):
        - meta_analysis_method
        - multiplicity_strategy
        - version
        - stage_a_alpha
        - stage_a_effect_min
        - stage_a_min_sample
        - stage_b_min_retention_ratio
        - stage_c_min_folds
        - stage_c_min_positive_ratio
        - stage_c_max_fold_cv
        - stage_d_perturbation_delta
        - stage_d_min_stable_ratio
        - stage_d_max_allowed_drop
        - stage_e_fail_on_contradictory_inversion
        - stage_f_min_replication_pct
        - stage_f_meta_alpha

        Fields EXCLUDED from policy_hash (display metadata):
        - policy_id
        - description
        """
        payload = {
            "meta_analysis_method": self.meta_analysis_method.value if isinstance(self.meta_analysis_method, MetaAnalysisMethod) else str(self.meta_analysis_method),
            "multiplicity_strategy": self.multiplicity_strategy.value if isinstance(self.multiplicity_strategy, MultiplicityStrategy) else str(self.multiplicity_strategy),
            "stage_a_alpha": float(self.stage_a_alpha),
            "stage_a_effect_min": float(self.stage_a_effect_min),
            "stage_a_min_sample": int(self.stage_a_min_sample),
            "stage_b_min_retention_ratio": float(self.stage_b_min_retention_ratio),
            "stage_c_max_fold_cv": float(self.stage_c_max_fold_cv),
            "stage_c_min_folds": int(self.stage_c_min_folds),
            "stage_c_min_positive_ratio": float(self.stage_c_min_positive_ratio),
            "stage_d_max_allowed_drop": float(self.stage_d_max_allowed_drop),
            "stage_d_min_stable_ratio": float(self.stage_d_min_stable_ratio),
            "stage_d_perturbation_delta": float(self.stage_d_perturbation_delta),
            "stage_e_fail_on_contradictory_inversion": bool(self.stage_e_fail_on_contradictory_inversion),
            "stage_f_meta_alpha": float(self.stage_f_meta_alpha),
            "stage_f_min_replication_pct": float(self.stage_f_min_replication_pct),
        }
        digest = compute_canonical_sha256(payload, length=16)
        return f"PLC_{digest.upper()}"
