"""
Project GOAT v0.7 — Step 4.2 Feature Registry Test Suite
"""

from __future__ import annotations

import os
import tempfile
import pytest

from goat.features import (
    BarRange,
    BodyRatio,
    FeatureRegistryService,
    FeatureRegistryVerifier,
    LogReturn,
    RegistrationStatus,
    SQLiteFeatureRepository,
    TaxonomyCategory,
    ValidationStatus,
)


@pytest.fixture
def temp_db_service():
    """Fixture providing FeatureRegistryService backed by temporary SQLite DB file."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmp.name
    tmp.close()

    repo = SQLiteFeatureRepository(db_path)
    service = FeatureRegistryService(repo)
    yield service, repo, db_path

    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_feature_registration_and_lookup(temp_db_service):
    """Verify feature registration, retrieval by ID, fingerprint, and canonical hash."""
    service, repo, _ = temp_db_service

    feat = LogReturn()
    rec = service.register_feature(feat, provenance="unit_test", notes="Log return primitive")

    assert rec.feature_id == feat.feature_id
    assert rec.scientific_fingerprint == feat.scientific_fingerprint
    assert rec.canonical_hash == feat.canonical_hash
    assert rec.registration_status == RegistrationStatus.REGISTERED

    # Lookup by ID
    by_id = service.get_by_id(feat.feature_id)
    assert by_id is not None
    assert by_id.feature_id == feat.feature_id

    # Lookup by Fingerprint
    by_fp = service.get_by_fingerprint(feat.scientific_fingerprint)
    assert by_fp is not None
    assert by_fp.feature_id == feat.feature_id

    # Lookup by Canonical Hash
    by_hash = service.get_by_canonical_hash(feat.canonical_hash)
    assert by_hash is not None
    assert by_hash.feature_id == feat.feature_id


def test_duplicate_registration_fail_closed(temp_db_service):
    """Verify registry rejects duplicate feature registrations (fail-closed)."""
    service, _, _ = temp_db_service

    feat = LogReturn()
    service.register_feature(feat)

    # Re-registering identical feature must raise ValueError
    with pytest.raises(ValueError, match="already registered|already exists"):
        service.register_feature(feat)


def test_registry_query_apis(temp_db_service):
    """Verify multi-dimensional query APIs."""
    service, _, _ = temp_db_service

    feat1 = LogReturn()
    feat2 = BarRange()
    feat3 = BodyRatio()

    service.register_feature(feat1)
    service.register_feature(feat2)
    service.register_feature(feat3)

    # Query by taxonomy
    trend_recs = service.query_by_taxonomy(TaxonomyCategory.TREND)
    assert len(trend_recs) == 1
    assert trend_recs[0].feature_id == feat1.feature_id

    range_recs = service.query_by_taxonomy(TaxonomyCategory.RANGE)
    assert len(range_recs) == 1
    assert range_recs[0].feature_id == feat2.feature_id

    # Query by capability (vectorized=True)
    vec_recs = service.query_by_capability(vectorized=True)
    assert len(vec_recs) == 3


def test_audit_trail_logging(temp_db_service):
    """Verify append-only audit trail logging for registration and status updates."""
    service, repo, _ = temp_db_service

    feat = LogReturn()
    service.register_feature(feat)

    # Update validation status
    service.update_validation_status(feat.feature_id, ValidationStatus.PASSED, actor="quality_pipeline", notes="All 7 gates passed")

    audit = service.get_audit_trail(feat.feature_id)
    assert len(audit) == 2
    assert audit[0].event_type == "REGISTER"
    assert audit[1].event_type == "UPDATE_STATUS"
    assert audit[1].details["new_val_status"] == "passed"


def test_registry_verifier_and_snapshot(temp_db_service):
    """Verify FeatureRegistryVerifier and snapshot export/import."""
    service, repo, db_path = temp_db_service

    feat1 = LogReturn()
    feat2 = BarRange()
    service.register_feature(feat1)
    service.register_feature(feat2)

    # Verify DB integrity
    verifier = FeatureRegistryVerifier(repo)
    is_valid, errors = verifier.verify_integrity()
    assert is_valid is True
    assert len(errors) == 0

    # Export snapshot
    tmp_json = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    snapshot_path = tmp_json.name
    tmp_json.close()

    service.export_snapshot(snapshot_path)
    assert os.path.exists(snapshot_path)

    # Import into a new empty registry DB
    tmp_db2 = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path2 = tmp_db2.name
    tmp_db2.close()

    repo2 = SQLiteFeatureRepository(db_path2)
    service2 = FeatureRegistryService(repo2)

    count = service2.import_snapshot(snapshot_path)
    assert count == 2
    assert service2.get_by_id(feat1.feature_id) is not None

    repo2.close()
    if os.path.exists(snapshot_path):
        os.remove(snapshot_path)
    if os.path.exists(db_path2):
        os.remove(db_path2)
