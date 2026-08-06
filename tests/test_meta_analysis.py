"""
Project GOAT v0.9 — Dedicated Tests for Meta-Analysis Engine
"""

import pytest

from goat.intelligence.meta.engine import MetaAnalysisEngine
from goat.microstructure.core.enums import SyntheticIndexType

INDICES = list(SyntheticIndexType)


@pytest.mark.parametrize("index_type", INDICES)
def test_meta_analysis_pooled_effect(index_type: SyntheticIndexType) -> None:
    meta_engine = MetaAnalysisEngine()
    studies = [
        {"effect_size": 0.10, "sample_size": 50, "symbol": index_type.value},
        {"effect_size": 0.20, "sample_size": 50, "symbol": index_type.value},
        {"effect_size": 0.15, "sample_size": 100, "symbol": index_type.value},
    ]

    res = meta_engine.perform_meta_analysis(f"Meta Analysis {index_type.value}", studies)
    assert res.meta_analysis_id.startswith("MTA_")
    assert res.sample_size == 3
    assert 0.10 <= res.pooled_effect_size <= 0.20
    assert 0.0 <= res.heterogeneity_i2 <= 100.0
    assert 0.0 <= res.p_value <= 1.0


@pytest.mark.parametrize("index_type", INDICES[:10])
def test_meta_analysis_edge_longevity(index_type: SyntheticIndexType) -> None:
    meta_engine = MetaAnalysisEngine()
    survival_records = [
        {"longevity_days": 100, "is_active": True},
        {"longevity_days": 200, "is_active": True},
        {"longevity_days": 300, "is_active": False},
    ]

    res = meta_engine.analyze_edge_family_longevity(index_type.value, survival_records)
    assert res["edge_family"] == index_type.value
    assert res["mean_longevity_days"] == 200.0
    assert res["survival_rate"] == 0.6667
