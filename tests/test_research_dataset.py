"""
Project GOAT v0.3 — Unit Tests for Research Dataset Builder & Manifest

Tests Amendment Requirements E, F, G, H:
- Deterministic dataset fingerprinting (Same input + config -> same fingerprint; different input -> different fingerprint).
- Historical truncation tracking in DatasetManifest.
- Exclusion of TEST provenance from genuine research datasets.
"""

from datetime import datetime, timezone

import pandas as pd
import pytest

from goat.research.dataset import ResearchDatasetBuilder


def test_dataset_builder_provenance_exclusion_rejects_test_data() -> None:
    """Amendment H: TEST provenance cannot enter genuine research datasets."""
    df = pd.DataFrame([
        {"symbol": "R_75", "timestamp": "2024-07-22T00:00:00Z", "price": 100.0, "source": "test"},
        {"symbol": "R_75", "timestamp": "2024-07-22T00:01:00Z", "price": 101.0, "source": "test"},
    ])
    builder = ResearchDatasetBuilder()
    with pytest.raises(ValueError, match="contains only TEST observations"):
        builder.build_dataset(df, symbol="R_75")


def test_dataset_builder_deterministic_fingerprint_reproducibility() -> None:
    """Amendment E & F: Same canonical dataset + config -> same fingerprint; different input -> different fingerprint."""
    df1 = pd.DataFrame([
        {"symbol": "R_75", "timestamp": "2024-07-22T00:00:00Z", "price": 100.0, "source": "live"},
        {"symbol": "R_75", "timestamp": "2024-07-22T00:01:00Z", "price": 101.0, "source": "live"},
    ])
    df2 = pd.DataFrame([
        {"symbol": "R_75", "timestamp": "2024-07-22T00:00:00Z", "price": 100.0, "source": "live"},
        {"symbol": "R_75", "timestamp": "2024-07-22T00:01:00Z", "price": 105.0, "source": "live"},  # Price changed
    ])

    builder = ResearchDatasetBuilder()
    clean1, manifest1 = builder.build_dataset(df1, symbol="R_75", config_str="config_v1")
    clean1_again, manifest1_again = builder.build_dataset(df1, symbol="R_75", config_str="config_v1")
    clean2, manifest2 = builder.build_dataset(df2, symbol="R_75", config_str="config_v1")

    # Same input -> same dataset_id
    assert manifest1.dataset_id == manifest1_again.dataset_id
    assert manifest1.canonical_checksum == manifest1_again.canonical_checksum

    # Different input -> different dataset_id & checksum
    assert manifest1.dataset_id != manifest2.dataset_id
    assert manifest1.canonical_checksum != manifest2.canonical_checksum


def test_dataset_builder_truncation_tracking() -> None:
    """Amendment G: Historical truncation is correctly represented in DatasetManifest."""
    df = pd.DataFrame([
        {"symbol": "R_10", "timestamp": "2024-07-22T04:00:00Z", "price": 50.0, "source": "historical"},
        {"symbol": "R_10", "timestamp": "2024-07-22T05:00:00Z", "price": 51.0, "source": "historical"},
    ])
    requested_start = datetime(2024, 7, 22, 0, 0, 0, tzinfo=timezone.utc)

    builder = ResearchDatasetBuilder()
    _, manifest = builder.build_dataset(df, symbol="R_10", requested_start=requested_start)

    assert manifest.history_truncated is True
    assert manifest.truncation_reason is not None
    assert "Requested start" in manifest.truncation_reason
    assert manifest.actual_start_timestamp == datetime(2024, 7, 22, 4, 0, 0, tzinfo=timezone.utc)
