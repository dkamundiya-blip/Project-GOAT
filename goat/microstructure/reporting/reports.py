"""
Project GOAT v0.9 — Deriv Market Microstructure Report Generator
"""

import json
from typing import Any

from goat.microstructure.core.canonical import serialize_canonical_json
from goat.microstructure.core.models import (
    ExecutionProfile,
    JumpProfile,
    LiquidityProfile,
    MarketProfile,
    MicrostructureObservation,
    ResearchSummary,
    VolatilityProfile,
)


class MicrostructureReportGenerator:
    """Report Generator for Deriv Market Microstructure Research Engine.

    Generates Markdown and Canonical JSON representations of volatility, jump,
    liquidity, execution, market profile, and executive research summaries.
    """

    def generate_volatility_report(self, profile: VolatilityProfile) -> str:
        """Generate Markdown Volatility Report."""
        return (
            f"# DERIV VOLATILITY PROFILE REPORT\n"
            f"**Symbol**: `{profile.symbol}` | **Index Type**: `{profile.index_type.value}`\n"
            f"**Profile ID**: `{profile.profile_id}` | **Canonical Hash**: `{profile.canonical_hash}`\n\n"
            f"## Volatility Metrics\n"
            f"- **Realized Volatility**: `{profile.realized_volatility:.6f}`\n"
            f"- **Clustering Coefficient**: `{profile.volatility_clustering_coeff:.4f}`\n"
            f"- **Persistence Decay**: `{profile.volatility_persistence:.4f}`\n"
            f"- **Expansion Ratio**: `{profile.expansion_ratio:.4f}`\n"
            f"- **Contraction Ratio**: `{profile.contraction_ratio:.4f}`\n"
            f"- **Regime**: `{profile.regime.value}`\n\n"
            f"## Component Observations\n"
            f"Total Observations: `{len(profile.observation_ids)}`\n"
        )

    def generate_jump_report(self, profile: JumpProfile) -> str:
        """Generate Markdown Jump Profile Report."""
        return (
            f"# DERIV JUMP PROFILE REPORT\n"
            f"**Symbol**: `{profile.symbol}` | **Index Type**: `{profile.index_type.value}`\n"
            f"**Profile ID**: `{profile.profile_id}` | **Canonical Hash**: `{profile.canonical_hash}`\n\n"
            f"## Jump Dynamics\n"
            f"- **Jump Count**: `{profile.jump_count}`\n"
            f"- **Jump Frequency**: `{profile.jump_frequency:.4f} jumps/min`\n"
            f"- **Mean Jump Magnitude**: `{profile.mean_jump_magnitude:.6f}`\n"
            f"- **Max Jump Magnitude**: `{profile.max_jump_magnitude:.6f}`\n"
            f"- **Mean Spacing**: `{profile.mean_jump_spacing_sec:.2f} sec`\n"
            f"- **Clustering Index**: `{profile.jump_clustering_index:.4f}`\n"
            f"- **Dominant Direction**: `{profile.dominant_direction.value}`\n"
        )

    def generate_liquidity_report(self, profile: LiquidityProfile) -> str:
        """Generate Markdown Liquidity Report."""
        return (
            f"# DERIV LIQUIDITY PROFILE REPORT\n"
            f"**Symbol**: `{profile.symbol}` | **Index Type**: `{profile.index_type.value}`\n"
            f"**Profile ID**: `{profile.profile_id}` | **Canonical Hash**: `{profile.canonical_hash}`\n\n"
            f"## Liquidity Metrics\n"
            f"- **Average Spread**: `{profile.average_spread:.6f}`\n"
            f"- **Spread StDev**: `{profile.spread_stdev:.6f}`\n"
            f"- **Spread Stability**: `{profile.spread_stability:.4f}`\n"
            f"- **Quote Continuity**: `{profile.quote_continuity_score:.4f}`\n"
            f"- **Tick Rate**: `{profile.ticks_per_second:.2f} ticks/sec`\n"
            f"- **Tick Density**: `{profile.tick_density:.2f} ticks/min`\n"
            f"- **Activity Score**: `{profile.activity_score:.2f}`\n"
        )

    def generate_execution_report(self, profile: ExecutionProfile) -> str:
        """Generate Markdown Execution Quality Report."""
        return (
            f"# DERIV EXECUTION PROFILE REPORT\n"
            f"**Symbol**: `{profile.symbol}` | **Index Type**: `{profile.index_type.value}`\n"
            f"**Profile ID**: `{profile.profile_id}` | **Canonical Hash**: `{profile.canonical_hash}`\n\n"
            f"## Execution Metrics\n"
            f"- **Sample Count**: `{profile.sample_count}`\n"
            f"- **Mean Latency**: `{profile.mean_latency_ms:.2f} ms`\n"
            f"- **Median Latency**: `{profile.median_latency_ms:.2f} ms`\n"
            f"- **P95 Latency**: `{profile.p95_latency_ms:.2f} ms`\n"
            f"- **Fill Time**: `{profile.fill_time_ms:.2f} ms`\n"
            f"- **Consistency Score**: `{profile.consistency_score:.4f}`\n"
            f"- **Execution Rating**: `{profile.rating.value}`\n"
        )

    def generate_market_profile_report(self, profile: MarketProfile) -> str:
        """Generate Markdown Market Profile Report."""
        return (
            f"# DERIV MARKET PROFILE AGGREGATE REPORT\n"
            f"**Symbol**: `{profile.symbol}` | **Index Type**: `{profile.index_type.value}`\n"
            f"**Profile ID**: `{profile.profile_id}` | **Canonical Hash**: `{profile.canonical_hash}`\n\n"
            f"## Market Microstructure Summary\n"
            f"- **Volatility Profile**: `{profile.volatility_profile_id}`\n"
            f"- **Jump Profile**: `{profile.jump_profile_id}`\n"
            f"- **Liquidity Profile**: `{profile.liquidity_profile_id}`\n"
            f"- **Execution Profile**: `{profile.execution_profile_id}`\n"
            f"- **Observation Count**: `{profile.observation_count}`\n"
            f"- **Overall Health Score**: `{profile.overall_health_score:.2f}/100`\n"
        )

    def generate_executive_report(self, summary: ResearchSummary) -> str:
        """Generate Markdown Executive Research Report."""
        symbols_str = ", ".join([f"`{s}`" for s in summary.symbols_profiled]) or "None"
        return (
            f"# DERIV MARKET MICROSTRUCTURE EXECUTIVE RESEARCH SUMMARY\n"
            f"**Summary ID**: `{summary.summary_id}` | **Timestamp**: `{summary.timestamp}`\n"
            f"**Canonical Hash**: `{summary.canonical_hash}`\n\n"
            f"## Inventory Summary\n"
            f"- **Profiled Symbols**: {symbols_str}\n"
            f"- **Total Observations**: `{summary.total_observations}`\n"
            f"- **Volatility Profiles**: `{summary.total_volatility_profiles}`\n"
            f"- **Jump Profiles**: `{summary.total_jump_profiles}`\n"
            f"- **Liquidity Profiles**: `{summary.total_liquidity_profiles}`\n"
            f"- **Execution Profiles**: `{summary.total_execution_profiles}`\n"
            f"- **Market Profiles**: `{summary.total_market_profiles}`\n\n"
            f"## Category Breakdown\n"
            + "\n".join([f"- `{k}`: `{v}`" for k, v in summary.category_breakdown.items()])
        )

    def export_canonical_json(self, obj: Any) -> str:
        """Export model as canonical JSON string."""
        return serialize_canonical_json(obj)
