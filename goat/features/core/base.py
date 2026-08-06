"""
Project GOAT v0.7 — Abstract Feature Hierarchy

Defines abstract base classes (BaseFeature, PrimitiveFeature, DerivedFeature, CompositeFeature)
governing feature computation, AST serialization, metadata management, Scientific Feature Fingerprints,
and Capability Contracts (Step 4.1B-R2).
"""

from __future__ import annotations

import abc
from datetime import datetime, timezone
from typing import Any

import numpy as np

from goat.features.core.context import MarketDataWindow
from goat.features.core.contracts import (
    ComputationalConstraints,
    ExecutionCostMetadata,
    FeatureCapabilityContract,
    FeatureInputContract,
    FeatureOutputContract,
)
from goat.features.core.enums import (
    DataType,
    DeprecationStatus,
    DeterminismClass,
    StationarityType,
    TaxonomyCategory,
)
from goat.features.core.fingerprint import (
    DEFAULT_FINGERPRINT_ALGORITHM,
    DEFAULT_FINGERPRINT_VERSION,
    compute_scientific_feature_fingerprint,
)
from goat.features.core.hash import compute_feature_canonical_hash
from goat.features.core.metadata import FeatureMetadata


class BaseFeature(abc.ABC):
    """Abstract base class for all features in Project GOAT v0.7."""

    def __init__(
        self,
        name: str,
        version: str,
        taxonomy_category: TaxonomyCategory,
        mathematical_definition: str,
        algorithmic_spec: str,
        parameters: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
        taxonomy_subcategory: str = "general",
        output_type: DataType = DataType.FLOAT64,
        value_range: tuple[float | None, float | None] = (None, None),
        expected_stationarity: StationarityType = StationarityType.STATIONARY,
        known_failure_modes: list[str] | None = None,
        provenance_generator: str = "human_author",
        capabilities: FeatureCapabilityContract | None = None,
        constraints: ComputationalConstraints | None = None,
        output_contract: FeatureOutputContract | None = None,
        input_contract: FeatureInputContract | None = None,
        cost_metadata: ExecutionCostMetadata | None = None,
    ) -> None:
        self._name = name
        self._version = version
        self._taxonomy_category = taxonomy_category
        self._mathematical_definition = mathematical_definition
        self._algorithmic_spec = algorithmic_spec
        self._parameters = parameters or {}
        self._dependencies = dependencies or []
        self._taxonomy_subcategory = taxonomy_subcategory
        self._output_type = output_type
        self._value_range = value_range
        self._expected_stationarity = expected_stationarity
        self._known_failure_modes = known_failure_modes or []
        self._provenance_generator = provenance_generator

        # Initialize default capability contracts if not provided
        self._capabilities = capabilities or self._build_default_capabilities()
        self._constraints = constraints or self._build_default_constraints()
        self._output_contract = output_contract or self._build_default_output_contract()
        self._input_contract = input_contract or self._build_default_input_contract()
        self._cost_metadata = cost_metadata or self._build_default_cost_metadata()

        # Compute deterministic Feature ID (FEAT_<HEX16>) & Canonical Hash
        ast_dict = self.to_ast_dict()
        feat_id, canon_hash = compute_feature_canonical_hash(
            name=self._name,
            version=self._version,
            parameters=self._parameters,
            ast_spec=ast_dict,
            dependencies=self._dependencies,
        )

        # Compute Scientific Feature Fingerprint (FPT_<HEX64>) - Step 4.1B-R1 & 4.1B-R2
        scientific_fp = compute_scientific_feature_fingerprint(
            mathematical_definition=self._mathematical_definition,
            parameters=self._parameters,
            dependencies=self._dependencies,
            version=self._version,
            input_requirements=self._get_input_requirements(),
            output_type=self._output_type.value if hasattr(self._output_type, "value") else str(self._output_type),
            determinism_class="ieee_754_strict",
            expected_stationarity=(
                self._expected_stationarity.value
                if hasattr(self._expected_stationarity, "value")
                else str(self._expected_stationarity)
            ),
            capabilities=self._capabilities.model_dump(mode="json"),
            input_contract=self._input_contract.model_dump(mode="json"),
            output_contract=self._output_contract.model_dump(mode="json"),
        )

        creation_time = datetime.now(timezone.utc).isoformat()

        self._metadata = FeatureMetadata(
            feature_id=feat_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=scientific_fp,
            fingerprint_version=DEFAULT_FINGERPRINT_VERSION,
            fingerprint_algorithm=DEFAULT_FINGERPRINT_ALGORITHM,
            fingerprint_timestamp=creation_time,
            fingerprint_verified=True,
            capabilities=self._capabilities,
            constraints=self._constraints,
            output_contract=self._output_contract,
            input_contract=self._input_contract,
            cost_metadata=self._cost_metadata,
            name=self._name,
            version=self._version,
            taxonomy_category=self._taxonomy_category,
            taxonomy_subcategory=self._taxonomy_subcategory,
            dependencies=self._dependencies,
            mathematical_definition=self._mathematical_definition,
            algorithmic_spec=self._algorithmic_spec,
            input_requirements=self._get_input_requirements(),
            output_type=self._output_type,
            value_range=self._value_range,
            computational_cost=self._get_computational_cost(),
            determinism_class=DeterminismClass.IEEE_754_STRICT,
            applicable_instruments=["ALL"],
            applicable_timeframes=["ALL"],
            creation_timestamp=creation_time,
            provenance_generator=self._provenance_generator,
            expected_stationarity=self._expected_stationarity,
            known_failure_modes=self._known_failure_modes,
            deprecation_status=DeprecationStatus.ACTIVE,
        )

    def _build_default_capabilities(self) -> FeatureCapabilityContract:
        return FeatureCapabilityContract(window_size_policy="fixed")

    def _build_default_constraints(self) -> ComputationalConstraints:
        return ComputationalConstraints(minimum_history=1, lookback_required=0)

    def _build_default_output_contract(self) -> FeatureOutputContract:
        return FeatureOutputContract(output_dimension="vector", dtype=self._output_type, shape_constraints="(N,)")

    def _build_default_input_contract(self) -> FeatureInputContract:
        req_cols = self._get_input_requirements().get("required_columns", ["close"])
        return FeatureInputContract(required_fields=req_cols)

    def _build_default_cost_metadata(self) -> ExecutionCostMetadata:
        return ExecutionCostMetadata()

    @property
    def metadata(self) -> FeatureMetadata:
        """Return frozen immutable FeatureMetadata."""
        return self._metadata

    @property
    def feature_id(self) -> str:
        """Return unique Feature ID (FEAT_<HEX16>)."""
        return self._metadata.feature_id

    @property
    def canonical_hash(self) -> str:
        """Return 64-char SHA-256 canonical hash digest."""
        return self._metadata.canonical_hash

    @property
    def scientific_fingerprint(self) -> str:
        """Return Scientific Feature Fingerprint (FPT_<HEX64>)."""
        return self._metadata.scientific_fingerprint

    @property
    def fingerprint_version(self) -> str:
        """Return Scientific Fingerprint specification version."""
        return self._metadata.fingerprint_version

    @property
    def fingerprint_algorithm(self) -> str:
        """Return Scientific Fingerprint hashing algorithm."""
        return self._metadata.fingerprint_algorithm

    @property
    def capabilities(self) -> FeatureCapabilityContract:
        """Return feature capability contract."""
        return self._metadata.capabilities

    @property
    def constraints(self) -> ComputationalConstraints:
        """Return computational constraints."""
        return self._metadata.constraints

    @property
    def output_contract(self) -> FeatureOutputContract:
        """Return feature output contract."""
        return self._metadata.output_contract

    @property
    def input_contract(self) -> FeatureInputContract:
        """Return feature input contract."""
        return self._metadata.input_contract

    @property
    def cost_metadata(self) -> ExecutionCostMetadata:
        """Return execution cost metadata."""
        return self._metadata.cost_metadata

    @property
    def name(self) -> str:
        """Return feature name."""
        return self._name

    @property
    def parameters(self) -> dict[str, Any]:
        """Return bound parameters dictionary."""
        return self._parameters.copy()

    @abc.abstractmethod
    def compute(self, context: MarketDataWindow) -> np.ndarray:
        """Compute feature output array over input market data window."""
        ...

    @abc.abstractmethod
    def to_ast_dict(self) -> dict[str, Any]:
        """Return Abstract Syntax Tree (AST) dictionary representation of feature logic."""
        ...

    @abc.abstractmethod
    def _get_input_requirements(self) -> dict[str, Any]:
        """Return dictionary specifying minimum history depth and required columns."""
        ...

    @abc.abstractmethod
    def _get_computational_cost(self) -> dict[str, Any]:
        """Return dictionary specifying complexity bounds (e.g. O(N))."""
        ...


class PrimitiveFeature(BaseFeature):
    """Abstract base class for Primitive Features ($f_{prim}$)."""

    def _build_default_capabilities(self) -> FeatureCapabilityContract:
        return FeatureCapabilityContract(window_size_policy="fixed")

    def _build_default_constraints(self) -> ComputationalConstraints:
        return ComputationalConstraints(minimum_history=1, lookback_required=0)

    def _get_computational_cost(self) -> dict[str, Any]:
        return {"time_complexity": "O(N)", "memory_bytes_per_bar": 8, "type": "primitive"}


class DerivedFeature(BaseFeature):
    """Abstract base class for Derived Features ($f_{deriv}$)."""

    def __init__(self, lookback_window: int, *args: Any, **kwargs: Any) -> None:
        if lookback_window <= 0:
            raise ValueError(f"lookback_window must be > 0, got {lookback_window}")
        self._lookback_window = lookback_window
        kwargs.setdefault("parameters", {})["lookback_window"] = lookback_window
        super().__init__(*args, **kwargs)

    @property
    def lookback_window(self) -> int:
        """Return lookback window depth N."""
        return self._lookback_window

    def _build_default_capabilities(self) -> FeatureCapabilityContract:
        return FeatureCapabilityContract(window_size_policy="rolling")

    def _build_default_constraints(self) -> ComputationalConstraints:
        return ComputationalConstraints(
            minimum_history=self._lookback_window,
            rolling_window=self._lookback_window,
            lookback_required=self._lookback_window - 1,
            warmup_period=self._lookback_window - 1,
        )

    def _get_computational_cost(self) -> dict[str, Any]:
        return {
            "time_complexity": f"O(N * {self._lookback_window})",
            "memory_bytes_per_bar": 8,
            "lookback_window": self._lookback_window,
            "type": "derived",
        }


class CompositeFeature(BaseFeature):
    """Abstract base class for Composite Features."""

    def __init__(self, upstream_features: list[BaseFeature], *args: Any, **kwargs: Any) -> None:
        if not upstream_features:
            raise ValueError("CompositeFeature requires at least one upstream feature")
        self._upstream_features = upstream_features
        upstream_ids = [feat.feature_id for feat in upstream_features]
        kwargs["dependencies"] = upstream_ids
        super().__init__(*args, **kwargs)

    @property
    def upstream_features(self) -> list[BaseFeature]:
        """Return list of upstream dependency feature instances."""
        return list(self._upstream_features)

    def _get_computational_cost(self) -> dict[str, Any]:
        return {
            "time_complexity": "O(N * M)",
            "upstream_count": len(self._upstream_features),
            "type": "composite",
        }
