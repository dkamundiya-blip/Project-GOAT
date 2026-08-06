"""
Project GOAT v0.8 — Test Suite: Public API Export Validation for Step 7.1
"""

import pytest
import goat.marketstate as ms


def test_public_api_exports():
    expected_exports = [
        # Enums
        "TrendState",
        "VolatilityState",
        "LiquidityState",
        "SpreadState",
        "ActivityState",
        "StructureState",
        "QualityState",
        # Core Models
        "MarketState",
        "VolatilityAssessment",
        "LiquidityAssessment",
        "StructureAssessment",
        "MarketQualityAssessment",
        # Identifiers
        "compute_market_state_id",
        "compute_volatility_id",
        "compute_liquidity_id",
        "compute_structure_id",
        "compute_quality_id",
        "compute_report_id",
        # Assessment Engines & Coordinators
        "MarketStateEngine",
        "VolatilityAssessmentEngine",
        "LiquidityAssessmentEngine",
        "StructureAssessmentEngine",
        "MarketQualityEngine",
        "MarketClassificationEngine",
        # Persistence
        "init_marketstate_db",
        "MarketStateRepository",
        "VolatilityRepository",
        "LiquidityRepository",
        "StructureRepository",
        "QualityRepository",
        "MarketStateReportRepository",
        # Reporting
        "MarketStateReport",
        "VolatilityReport",
        "LiquidityReport",
        "StructureReport",
        "QualityReport",
        "MarketStateExecutiveReport",
    ]

    for export_name in expected_exports:
        assert hasattr(ms, export_name), f"Missing public export: {export_name}"
        assert export_name in ms.__all__, f"{export_name} missing from __all__"
