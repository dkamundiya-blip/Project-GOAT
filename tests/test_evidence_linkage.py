"""
Project GOAT v0.9 — Dedicated Unit Tests for Evidence Linkage Engine
"""

import pytest

from goat.evidence.linkage.engine import EvidenceLinkageEngine


@pytest.fixture
def linkage_engine():
    return EvidenceLinkageEngine()


@pytest.mark.parametrize("idx", range(1, 15))
def test_create_link_success(linkage_engine: EvidenceLinkageEngine, idx: int):
    hyp_id = f"HYP_{idx:016X}"
    evr_id = f"EVR_{idx:016X}"

    link = linkage_engine.create_link(
        hypothesis_id=hyp_id,
        target_id=evr_id,
        link_type="HYPOTHESIS_EVIDENCE_LINK",
        linker_id="GOAT_LINKER",
    )

    assert link.link_id.startswith("LNK_")
    assert link.hypothesis_id == hyp_id
    assert link.target_id == evr_id
    assert linkage_engine.get_link(link.link_id) is not None


@pytest.mark.parametrize("invalid_hyp_id", ["INVALID_HYP", "OBS_1234567890ABCDEF", "EVR_1234567890ABCDEF"])
def test_create_link_invalid_hypothesis_prefix(linkage_engine: EvidenceLinkageEngine, invalid_hyp_id: str):
    with pytest.raises(ValueError):
        linkage_engine.create_link(
            hypothesis_id=invalid_hyp_id,
            target_id="EVR_1234567890ABCDEF",
        )


@pytest.mark.parametrize("invalid_target_id", ["INVALID_TARGET", "HYP_1234567890ABCDEF", "123_456"])
def test_create_link_invalid_target_prefix(linkage_engine: EvidenceLinkageEngine, invalid_target_id: str):
    with pytest.raises(ValueError):
        linkage_engine.create_link(
            hypothesis_id="HYP_1234567890ABCDEF",
            target_id=invalid_target_id,
        )


@pytest.mark.parametrize("link_count", range(1, 10))
def test_hypothesis_multi_link_retrieval(linkage_engine: EvidenceLinkageEngine, link_count: int):
    hyp_id = "HYP_1000000000000000"
    for k in range(link_count):
        evr_id = f"EVR_{k:016X}"
        linkage_engine.create_link(
            hypothesis_id=hyp_id,
            target_id=evr_id,
            timestamp=f"2026-08-04T12:{k:02d}:00Z",
        )

    links = linkage_engine.get_links_for_hypothesis(hyp_id)
    assert len(links) == link_count
    assert all(l.hypothesis_id == hyp_id for l in links)


def test_target_multi_hypothesis_link_retrieval(linkage_engine: EvidenceLinkageEngine):
    evr_id = "EVR_5555555555555555"
    for h in range(5):
        hyp_id = f"HYP_{h:016X}"
        linkage_engine.create_link(
            hypothesis_id=hyp_id,
            target_id=evr_id,
            timestamp=f"2026-08-04T12:{h:02d}:00Z",
        )

    links = linkage_engine.get_links_for_target(evr_id)
    assert len(links) == 5
    assert all(l.target_id == evr_id for l in links)
