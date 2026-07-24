"""
Project GOAT v0.5 — Unit Tests for ExperimentScheduler & Campaign Lifecycle
"""

import pytest

from goat.orchestration.campaign import (
    CampaignDefinition,
    CampaignStatus,
    ProvenanceMismatchError,
)
from goat.orchestration.scheduler import (
    ExperimentScheduler,
    compute_configuration_hash,
    generate_campaign_id,
)
from goat.research.hypothesis.definition import HypothesisDefinition


def test_generate_campaign_id_and_config_hash() -> None:
    """Test campaign_id and configuration_hash generation format."""
    camp_id = generate_campaign_id("volatility_compression")
    assert camp_id.startswith("CMP-")
    assert len(camp_id) > 20

    hyp = HypothesisDefinition(
        hypothesis_id="HYP-CFG-1",
        version="1.0.0",
        name="Name",
        description="Desc",
        causal_condition={"primitive": "greater_than", "feature": "close"},
        condition_parameters={"threshold": 100.0},
    )

    hash1 = compute_configuration_hash(
        hypothesis_grid=[hyp],
        symbols=["R_10"],
        timeframes=["M1"],
        master_seed=42,
        fdr_alpha=0.05,
    )
    hash2 = compute_configuration_hash(
        hypothesis_grid=[hyp],
        symbols=["R_10"],
        timeframes=["M1"],
        master_seed=42,
        fdr_alpha=0.05,
    )
    assert hash1.startswith("cfg_")
    assert hash1 == hash2  # Deterministic configuration hash


def test_campaign_status_transition_guards() -> None:
    """Test ExperimentScheduler enforces legal CampaignStatus transition matrix."""
    scheduler = ExperimentScheduler()
    assert scheduler.status == CampaignStatus.CREATED

    # Legal transition: CREATED -> VALIDATING -> QUEUED -> RUNNING -> COMPLETED
    scheduler._transition_status(CampaignStatus.VALIDATING, "Preflight start")
    assert scheduler.status == CampaignStatus.VALIDATING

    scheduler._transition_status(CampaignStatus.QUEUED, "Validation passed")
    assert scheduler.status == CampaignStatus.QUEUED

    scheduler._transition_status(CampaignStatus.RUNNING, "Workers active")
    assert scheduler.status == CampaignStatus.RUNNING

    scheduler._transition_status(CampaignStatus.COMPLETED, "Execution complete")
    assert scheduler.status == CampaignStatus.COMPLETED

    # Illegal transition: COMPLETED -> RUNNING raises ValueError
    with pytest.raises(ValueError):
        scheduler._transition_status(CampaignStatus.RUNNING, "Illegal restart")


def test_preflight_verification_missing_data(tmp_path) -> None:
    """Test pre-flight verification raises ProvenanceMismatchError when market data is missing."""
    from goat.config import GoatSettings
    settings = GoatSettings(raw_data_dir=tmp_path / "raw", processed_data_dir=tmp_path / "processed")

    scheduler = ExperimentScheduler(settings=settings)
    with pytest.raises(ProvenanceMismatchError):
        scheduler.perform_preflight_verification(symbols=["NON_EXISTENT_SYM"], timeframes=["M1"])
