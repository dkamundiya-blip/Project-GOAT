"""
Project GOAT v0.6 — MultiplicityFamilyCoordinator Unit Tests
"""

import math

import pytest

from goat.research.edge.validation.exceptions import MultiplicityFamilyError
from goat.research.edge.validation.multiplicity import MultiplicityFamilyCoordinator


def test_multiplicity_coordinator_basic_fdr():
    coord = MultiplicityFamilyCoordinator("FAM_001", alpha=0.05)
    coord.register_candidate("cand_1", 0.001)
    coord.register_candidate("cand_2", 0.040)
    coord.register_candidate("cand_3", 0.800)

    coord.freeze_family()
    assert coord.is_frozen

    # Duplicate registration after freeze rejected
    with pytest.raises(MultiplicityFamilyError):
        coord.register_candidate("cand_4", 0.02)

    assert coord.is_significant("cand_1") is True
    assert coord.get_q_value("cand_1") <= 0.05


def test_multiplicity_coordinator_tie_breaking():
    # Candidates with duplicate p-values must sort deterministically by candidate_id
    coord1 = MultiplicityFamilyCoordinator("FAM_002", alpha=0.05)
    coord1.register_candidate("B_cand", 0.03)
    coord1.register_candidate("A_cand", 0.03)
    coord1.freeze_family()

    coord2 = MultiplicityFamilyCoordinator("FAM_002", alpha=0.05)
    coord2.register_candidate("A_cand", 0.03)
    coord2.register_candidate("B_cand", 0.03)
    coord2.freeze_family()

    assert coord1.get_q_value("A_cand") == coord2.get_q_value("A_cand")
    assert coord1.get_q_value("B_cand") == coord2.get_q_value("B_cand")


def test_multiplicity_coordinator_invalid_pvalues():
    coord = MultiplicityFamilyCoordinator("FAM_003")

    with pytest.raises(MultiplicityFamilyError):
        coord.register_candidate("c_nan", float("nan"))

    with pytest.raises(MultiplicityFamilyError):
        coord.register_candidate("c_inf", float("inf"))

    with pytest.raises(MultiplicityFamilyError):
        coord.register_candidate("c_neg", -0.01)

    with pytest.raises(MultiplicityFamilyError):
        coord.register_candidate("c_over", 1.05)


def test_multiplicity_coordinator_boundary_pvalues():
    coord = MultiplicityFamilyCoordinator("FAM_004", alpha=0.05)
    coord.register_candidate("c_zero", 0.0)
    coord.register_candidate("c_one", 1.0)
    coord.freeze_family()

    assert coord.is_significant("c_zero") is True
    assert coord.is_significant("c_one") is False
