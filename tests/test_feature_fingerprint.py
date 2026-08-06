"""
Project GOAT v0.7 — Step 4.1B-R1 Scientific Feature Fingerprint & Identity Test Suite
"""

from __future__ import annotations

import json
import pytest
from pydantic import ValidationError

from goat.features import (
    BarRange,
    BaseFeature,
    BodyRatio,
    FeatureMetadata,
    LogReturn,
    compute_scientific_feature_fingerprint,
    validate_scientific_feature_fingerprint,
)
from goat.research.edge.canonical import canonical_json


def test_fingerprint_bit_reproducibility():
    """Verify repeated fingerprint calculations on identical scientific definitions yield bitwise identical output."""
    fp1 = compute_scientific_feature_fingerprint(
        mathematical_definition=r"r_t = \ln(C_t / C_{t-1})",
        parameters={"alpha": 0.5},
        dependencies=["FEAT_1234567890ABCDEF"],
        version="1.0.0",
    )
    fp2 = compute_scientific_feature_fingerprint(
        mathematical_definition=r"r_t = \ln(C_t / C_{t-1})",
        parameters={"alpha": 0.5},
        dependencies=["FEAT_1234567890ABCDEF"],
        version="1.0.0",
    )

    assert fp1 == fp2
    assert fp1.startswith("FPT_")
    assert len(fp1) == 68  # 'FPT_' + 64 hex chars


def test_fingerprint_ignores_non_scientific_metadata():
    """Verify non-scientific metadata (provenance author, timestamp) does NOT change the Scientific Fingerprint."""
    feat1 = LogReturn()
    feat2 = LogReturn()

    # Even if instantiated at different timestamps/runtimes, scientific_fingerprint is 100% identical
    assert feat1.scientific_fingerprint == feat2.scientific_fingerprint


def test_fingerprint_sensitivity_to_scientific_changes():
    """Verify modifying any scientific attribute changes the Scientific Fingerprint."""
    base_fp = compute_scientific_feature_fingerprint(
        mathematical_definition="x_t = P_t",
        parameters={"w": 10},
        version="1.0.0",
    )

    # Change math definition
    math_changed = compute_scientific_feature_fingerprint(
        mathematical_definition="x_t = P_t * 2",
        parameters={"w": 10},
        version="1.0.0",
    )
    assert base_fp != math_changed

    # Change parameters
    param_changed = compute_scientific_feature_fingerprint(
        mathematical_definition="x_t = P_t",
        parameters={"w": 20},
        version="1.0.0",
    )
    assert base_fp != param_changed

    # Change version
    version_changed = compute_scientific_feature_fingerprint(
        mathematical_definition="x_t = P_t",
        parameters={"w": 10},
        version="2.0.0",
    )
    assert base_fp != version_changed

    # Change dependencies
    dep_changed = compute_scientific_feature_fingerprint(
        mathematical_definition="x_t = P_t",
        parameters={"w": 10},
        dependencies=["FEAT_ABCDEF1234567890"],
        version="1.0.0",
    )
    assert base_fp != dep_changed


def test_fingerprint_fail_closed_validation():
    """Verify validate_scientific_feature_fingerprint passes valid metadata and fails closed on tampering."""
    feat = BarRange()
    meta = feat.metadata

    # Valid metadata must pass
    assert validate_scientific_feature_fingerprint(meta) is True

    # Tampered fingerprint must raise ValueError
    tampered_dict = meta.model_dump()
    tampered_dict["scientific_fingerprint"] = "FPT_" + "0" * 64
    tampered_meta = FeatureMetadata(**tampered_dict)

    with pytest.raises(ValueError, match="Scientific Feature Fingerprint mismatch"):
        validate_scientific_feature_fingerprint(tampered_meta)


def test_fingerprint_public_api():
    """Verify public API property exposure on BaseFeature instances."""
    feat = BodyRatio()
    assert hasattr(feat, "scientific_fingerprint")
    assert hasattr(feat, "fingerprint_version")
    assert hasattr(feat, "fingerprint_algorithm")

    assert feat.scientific_fingerprint.startswith("FPT_")
    assert feat.fingerprint_version == "1.0.0"
    assert feat.fingerprint_algorithm == "SHA256_CANONICAL_V1"


def test_fingerprint_serialization_stability():
    """Verify Scientific Fingerprint survives JSON & canonical serialization roundtrips."""
    feat = LogReturn()
    meta = feat.metadata

    # Pydantic JSON dump/load
    json_str = meta.model_dump_json()
    loaded_dict = json.loads(json_str)
    reconstructed_meta = FeatureMetadata(**loaded_dict)

    assert reconstructed_meta.scientific_fingerprint == feat.scientific_fingerprint
    assert validate_scientific_feature_fingerprint(reconstructed_meta) is True

    # Canonical JSON string check
    canon_str = canonical_json(meta)
    assert "FPT_" in canon_str
