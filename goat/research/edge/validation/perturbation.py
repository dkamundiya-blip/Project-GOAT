"""
Project GOAT v0.6 — Parameter Perturbation Core

Generates deterministic parameter perturbation grids for Stage D parameter surface robustness evaluation.
"""

from __future__ import annotations

import itertools
from typing import Any, Sequence

from goat.research.edge.canonical import canonical_json, freeze_structure


class ParameterPerturbationCore:
    """Generates deterministic neighborhood parameter perturbation grids without performance searching."""

    @staticmethod
    def generate_perturbation_grid(
        baseline_params: dict[str, Any],
        delta_ratio: float = 0.20,
        non_perturbable_keys: Sequence[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Generate deterministic list of perturbed parameter dicts.

        Args:
            baseline_params: Baseline condition parameter mapping.
            delta_ratio: Perturbation ratio (e.g. 0.20 for +/- 20%).
            non_perturbable_keys: Sequence of parameter keys that must remain fixed.

        Returns:
            List of perturbed parameter dicts including baseline, sorted deterministically by canonical JSON.
        """
        if not baseline_params:
            return [{}]

        fixed_keys = set(non_perturbable_keys or [])
        sorted_keys = sorted(baseline_params.keys())

        key_variants: list[tuple[str, list[Any]]] = []

        for key in sorted_keys:
            val = baseline_params[key]
            if key in fixed_keys:
                key_variants.append((key, [val]))
                continue

            if isinstance(val, bool):
                # Boolean toggles both True and False
                key_variants.append((key, [True, False]))

            elif isinstance(val, int) and not isinstance(val, bool):
                # Integer parameter: baseline, floor(val*(1-delta)), ceil(val*(1+delta))
                val_min = max(1, int(round(val * (1.0 - delta_ratio))))
                val_max = max(val_min + 1, int(round(val * (1.0 + delta_ratio))))
                variants = sorted(list(set([val_min, val, val_max])))
                key_variants.append((key, variants))

            elif isinstance(val, (float, int)):
                # Continuous parameter
                f_val = float(val)
                v_low = round(f_val * (1.0 - delta_ratio), 6)
                v_high = round(f_val * (1.0 + delta_ratio), 6)
                variants = sorted(list(set([v_low, round(f_val, 6), v_high])))
                key_variants.append((key, variants))

            else:
                # Categorical or non-numeric: fixed
                key_variants.append((key, [val]))

        # Product of variants across keys
        keys = [kv[0] for kv in key_variants]
        values_lists = [kv[1] for kv in key_variants]

        grid: list[dict[str, Any]] = []
        seen_jsons: set[str] = set()

        for combo in itertools.product(*values_lists):
            param_dict = {k: v for k, v in zip(keys, combo)}
            c_json = canonical_json(param_dict)
            if c_json not in seen_jsons:
                seen_jsons.add(c_json)
                grid.append(param_dict)

        # Sort grid deterministically by canonical JSON
        grid.sort(key=canonical_json)
        return grid
