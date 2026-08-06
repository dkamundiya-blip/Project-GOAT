"""
Project GOAT v0.7 — Step 4.1B-R2 Feature Capability Contracts Test Suite
"""

from __future__ import annotations

import json
import pytest
from pydantic import ValidationError

from goat.features import (
    BarRange,
    BodyRatio,
    ComputationalConstraints,
    ExecutionCostMetadata,
    FeatureCapabilityContract,
    FeatureInputContract,
    FeatureOutputContract,
    LogReturn,
    validate_feature_capability_contract,
    validate_scientific_feature_fingerprint,
)
from goat.research.edge.canonical import canonical_json


def test_capability_contract_immutability():
    """Verify FeatureCapabilityContract and contract models are frozen and immutable."""
    caps = FeatureCapabilityContract()
    assert caps.supports_vectorized_execution is True

    with pytest.raises(ValidationError):
        caps.supports_vectorized_execution = False  # Frozen check


def test_capability_contract_validation_pass():
    """Verify standard primitive features pass validate_feature_capability_contract."""
    feat = LogReturn()
    meta = feat.metadata

    assert validate_feature_capability_contract(meta) is True
    assert validate_scientific_feature_fingerprint(meta) is True


def test_capability_contract_validation_failures():
    """Verify fail-closed rejection of inconsistent capability contracts."""
    feat = LogReturn()
    meta = feat.metadata

    # Rule 1 Failure: Streaming + Complete History contradiction
    bad_caps1 = FeatureCapabilityContract(supports_streaming_execution=True, requires_complete_history=True)
    bad_meta1 = meta.model_copy(update={"capabilities": bad_caps1})
    with pytest.raises(ValueError, match="streaming execution cannot require complete history"):
        validate_feature_capability_contract(bad_meta1)

    # Rule 2 Failure: Rolling window without lookback
    bad_caps2 = FeatureCapabilityContract(window_size_policy="rolling")
    bad_constraints2 = ComputationalConstraints(lookback_required=0)
    bad_meta2 = meta.model_copy(update={"capabilities": bad_caps2, "constraints": bad_constraints2})
    with pytest.raises(ValueError, match="rolling window policy requires lookback_required > 0"):
        validate_feature_capability_contract(bad_meta2)

    # Rule 3 Failure: Scalar dimension with vector shape
    bad_out3 = FeatureOutputContract(output_dimension="scalar", shape_constraints="(N,)")
    bad_meta3 = meta.model_copy(update={"output_contract": bad_out3})
    with pytest.raises(ValueError, match="scalar output cannot have vector shape"):
        validate_feature_capability_contract(bad_meta3)

    # Rule 4 Failure: Requires fixed window without valid fixed_window count
    bad_caps4 = FeatureCapabilityContract(requires_fixed_window=True)
    bad_constraints4 = ComputationalConstraints(fixed_window=None)
    bad_meta4 = meta.model_copy(update={"capabilities": bad_caps4, "constraints": bad_constraints4})
    with pytest.raises(ValueError, match="requires_fixed_window requires valid fixed_window"):
        validate_feature_capability_contract(bad_meta4)


def test_contract_public_api():
    """Verify public contract property exposure on feature instances."""
    feat = BarRange()
    assert isinstance(feat.capabilities, FeatureCapabilityContract)
    assert isinstance(feat.constraints, ComputationalConstraints)
    assert isinstance(feat.output_contract, FeatureOutputContract)
    assert isinstance(feat.input_contract, FeatureInputContract)
    assert isinstance(feat.cost_metadata, ExecutionCostMetadata)

    assert feat.capabilities.supports_vectorized_execution is True
    assert feat.constraints.minimum_history == 1
    assert feat.output_contract.output_dimension == "vector"
    assert feat.input_contract.required_fields == ["high", "low"]


def test_contract_serialization_stability():
    """Verify contracts survive JSON and canonical serialization."""
    feat = BodyRatio()
    meta = feat.metadata

    # Pydantic JSON dump/load roundtrip
    json_str = meta.model_dump_json()
    loaded_dict = json.loads(json_str)
    assert loaded_dict["capabilities"]["supports_vectorized_execution"] is True
    assert loaded_dict["input_contract"]["required_fields"] == ["open", "high", "low", "close"]

    # Canonical JSON string check
    canon_str = canonical_json(meta)
    assert "capabilities" in canon_str
    assert "input_contract" in canon_str
