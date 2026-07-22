"""
Project GOAT v0.4 — Hypothesis Experiment Runner CLI Script

Executes hypothesis testing experiments, applies Benjamini-Hochberg FDR control,
updates the EdgeRegistry, and compiles research reports.

NO TRADING DISCLAIMER:
----------------------
This script performs STATISTICAL EDGE RESEARCH ONLY.
It contains NO trading strategies, signals, buy/sell recommendations, or execution code.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from goat.config import GoatSettings
from goat.data.schemas import Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.logging import configure_logging, get_logger
from goat.research.dataset import ResearchDatasetBuilder
from goat.research.hypothesis.definition import HypothesisDefinition
from goat.research.hypothesis.experiment import ExperimentRunner
from goat.research.hypothesis.registry import EdgeRegistry
from goat.research.hypothesis.report import HypothesisReportGenerator
from goat.research.outcomes import ForwardOutcomeTable

_log = get_logger("script.hypothesis")


def build_volatility_compression_grid(
    symbols: list[str],
    timeframes: list[str],
) -> list[HypothesisDefinition]:
    """Generate a parameter grid family for Volatility Compression hypotheses."""
    grid = []
    thresholds = [0.10, 0.20, 0.30]
    horizons = [1, 3, 5, 10]

    for thresh in thresholds:
        for k in horizons:
            hyp_id = f"HYP-VOL-COMPRESS-q{int(thresh*100)}-k{k}"
            hyp = HypothesisDefinition(
                hypothesis_id=hyp_id,
                version="1.0.0",
                name=f"Volatility Compression (q={thresh}, k={k})",
                description="Tests whether trailing low-volatility quantile predicts larger forward absolute returns.",
                symbol_scope=symbols,
                timeframe_scope=timeframes,
                causal_condition={
                    "primitive": "quantile_membership",
                    "feature": "close",
                },
                condition_parameters={
                    "lookback": 50,
                    "quantile_lower": 0.0,
                    "quantile_upper": thresh,
                },
                required_causal_features=["close"],
                forward_outcome_metric=f"fwd_return_{k}",
                forward_horizon=k,
                baseline_definition="unconditional",
                event_spacing_bars=k,  # Embargo spacing equal to horizon k
                statistical_test="welch_ttest",
                effect_size_method="cohens_d",
                min_sample_requirement=50,
            )
            grid.append(hyp)

    return grid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Project GOAT v0.4 — Hypothesis Experiment Runner"
    )
    parser.add_argument(
        "--family",
        type=str,
        default="volatility_compression",
        help="Hypothesis family to test (default: volatility_compression)",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=["R_10"],
        help="Symbols to process (e.g. R_10 R_50 R_75)",
    )
    parser.add_argument(
        "--timeframes",
        nargs="+",
        default=["M1"],
        help="Timeframes to process (e.g. M1 M5)",
    )
    parser.add_argument(
        "--allow-holdout",
        action="store_true",
        help="Explicitly audit sealed HOLDOUT partition (logs audit entry)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Override output directory for experiment reports",
    )

    args = parser.parse_args()

    settings = GoatSettings()
    configure_logging(level=settings.log_level)

    print("==================================================")
    print("PROJECT GOAT v0.4 — HYPOTHESIS ENGINE EXPERIMENT")
    print("==================================================")
    print(f"Family     : {args.family}")
    print(f"Symbols    : {', '.join(args.symbols)}")
    print(f"Timeframes : {', '.join(args.timeframes)}")
    print(f"Holdout    : {'UNSEALED (AUDITED)' if args.allow_holdout else 'SEALED (PROTECTED)'}\n")

    storage = ParquetStorage(
        raw_dir=settings.get_raw_data_dir(),
        processed_dir=settings.get_processed_data_dir(),
    )
    output_dir = Path(args.output_dir) if args.output_dir else settings.get_research_data_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    registry = EdgeRegistry(settings.get_edge_registry_path())
    runner = ExperimentRunner(settings=settings)
    builder = ResearchDatasetBuilder()
    fwd_gen = ForwardOutcomeTable(horizons=[1, 3, 5, 10, 20])
    report_gen = HypothesisReportGenerator()

    # Build hypothesis parameter grid family
    grid = build_volatility_compression_grid(args.symbols, args.timeframes)

    for sym in args.symbols:
        for tf_str in args.timeframes:
            print(f"Processing hypothesis family on {sym} ({tf_str})...")

            if tf_str == "Tick":
                df_raw = storage.read_ticks(sym)
            else:
                tf_enum = Timeframe(tf_str)
                df_raw = storage.read_candles(sym, tf_enum)
                if df_raw.empty:
                    ticks_df = storage.read_ticks(sym)
                    if not ticks_df.empty:
                        from goat.data.processing.aggregation import aggregate_ticks_to_candles
                        df_raw = aggregate_ticks_to_candles(ticks_df, tf_enum, source="historical")

            if df_raw.empty:
                print(f"  [WARNING] No market data found for {sym} ({tf_str}). Skipping.")
                continue

            research_df, manifest = builder.build_dataset(df_raw, symbol=sym, timeframe=tf_str)
            outcomes_df = fwd_gen.compute_outcomes(research_df)

            experiment = runner.run_experiment_family(
                family_name=f"{args.family}_{sym}_{tf_str}",
                hypotheses=grid,
                df=research_df,
                outcomes_df=outcomes_df,
                manifest=manifest,
                allow_holdout=args.allow_holdout,
            )

            # Register hypotheses & results in EdgeRegistry
            for hyp in grid:
                registry.register_hypothesis(hyp, status="EXPLORATORY")

            for res in experiment.results:
                new_status = "TRAIN_SUPPORTED" if res.adjusted_q_value is not None and res.adjusted_q_value <= 0.05 else "REJECTED"
                if res.stability_status == "STATISTICALLY_SUPPORTED_BUT_PRACTICALLY_WEAK":
                    new_status = "UNSTABLE"
                registry.record_evaluation_result(res, new_status=new_status)

            json_p, md_p = report_gen.save_experiment_artifacts(output_dir / sym, experiment)
            print(f"  [OK] Experiment report saved : {md_p.name}")
            print(f"  [OK] Supported hypotheses    : {experiment.supported_count} / {len(grid)}")

    print("\n==================================================")
    print("HYPOTHESIS EXPERIMENT COMPLETED")
    print("==================================================")


if __name__ == "__main__":
    main()
