"""
Project GOAT v0.6 — ParameterPerturbationCore Unit Tests
"""

from goat.research.edge.validation.perturbation import ParameterPerturbationCore


def test_parameter_perturbation_grid_generation():
    baseline = {"period": 20, "threshold": 1.5, "use_filter": True, "type": "RSI"}
    grid = ParameterPerturbationCore.generate_perturbation_grid(
        baseline, delta_ratio=0.20, non_perturbable_keys=["type"]
    )

    assert len(grid) > 1
    # Check non-perturbable field preserved across all grid points
    for param_dict in grid:
        assert param_dict["type"] == "RSI"
        assert param_dict["use_filter"] in (True, False)
        assert isinstance(param_dict["period"], int)
        assert param_dict["period"] >= 1


def test_parameter_perturbation_deterministic_sorting():
    baseline = {"b_param": 10, "a_param": 5}

    grid1 = ParameterPerturbationCore.generate_perturbation_grid(baseline, delta_ratio=0.10)
    grid2 = ParameterPerturbationCore.generate_perturbation_grid(baseline, delta_ratio=0.10)

    assert len(grid1) == len(grid2)
    assert grid1 == grid2
