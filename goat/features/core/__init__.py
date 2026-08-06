"""
Project GOAT v0.7 — Feature Core Module

Exposes domain enums, metadata model, market data context, canonical hash calculator,
Scientific Feature Fingerprint engine, capability contracts, and abstract base classes.
"""

from goat.features.core.base import (
    BaseFeature,
    CompositeFeature,
    DerivedFeature,
    PrimitiveFeature,
)
from goat.features.core.context import MarketDataWindow
from goat.features.core.contracts import (
    ComputationalConstraints,
    ExecutionCostMetadata,
    FeatureCapabilityContract,
    FeatureInputContract,
    FeatureOutputContract,
    validate_feature_capability_contract,
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
    validate_scientific_feature_fingerprint,
)
from goat.features.core.hash import compute_feature_canonical_hash
from goat.features.core.metadata import FeatureMetadata

__all__ = [
    "TaxonomyCategory",
    "DataType",
    "DeterminismClass",
    "StationarityType",
    "DeprecationStatus",
    "FeatureMetadata",
    "MarketDataWindow",
    "compute_feature_canonical_hash",
    "compute_scientific_feature_fingerprint",
    "validate_scientific_feature_fingerprint",
    "DEFAULT_FINGERPRINT_ALGORITHM",
    "DEFAULT_FINGERPRINT_VERSION",
    "FeatureCapabilityContract",
    "ComputationalConstraints",
    "FeatureOutputContract",
    "FeatureInputContract",
    "ExecutionCostMetadata",
    "validate_feature_capability_contract",
    "BaseFeature",
    "PrimitiveFeature",
    "DerivedFeature",
    "CompositeFeature",
]
