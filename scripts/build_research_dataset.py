"""
Project GOAT v0.3 — Research Dataset Construction CLI Script

Executes research dataset construction, statistical fingerprinting,
and research report generation for configured synthetic instruments.

NO TRADING DISCLAIMER:
----------------------
This script performs QUANTITATIVE RESEARCH ONLY.
It contains NO trading strategies, signals, buy/sell recommendations, or execution code.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from goat.config import GoatSettings
from goat.data.collector.deriv import DerivMarketDataCollector
from goat.data.historical import DerivHistoricalImporter
from goat.data.processing.aggregation import aggregate_ticks_to_candles
from goat.data.schemas import Timeframe
from goat.data.storage.parquet import ParquetStorage
from goat.logging import configure_logging, get_logger
from goat.research.dataset import ResearchDatasetBuilder
from goat.research.fingerprint import compare_market_fingerprints, generate_market_fingerprint
from goat.research.outcomes import ForwardOutcomeTable
from goat.research.report import ResearchReportGenerator
from goat.research.splitting import ChronologicalSplitter

_log = get_logger("script.research")


async def main_async(args: argparse.Namespace) -> None:
    settings = GoatSettings()
    configure_logging(level=settings.log_level)

    symbols = args.symbols or settings.research_symbols
    timeframes = args.timeframes or settings.research_timeframes
    output_dir = Path(args.output_dir) if args.output_dir else settings.get_research_data_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("PROJECT GOAT v0.3 — RESEARCH DATASET CONSTRUCTION")
    print("==================================================")
    print(f"Symbols    : {', '.join(symbols)}")
    print(f"Timeframes : {', '.join(timeframes)}")
    print(f"Output Dir : {output_dir}\n")

    storage = ParquetStorage(
        raw_dir=settings.get_raw_data_dir(),
        processed_dir=settings.get_processed_data_dir(),
    )

    # 1. Historical data acquisition if requested
    if args.acquire_history:
        print("Acquiring historical tick data from Deriv API...")
        collector = DerivMarketDataCollector(settings=settings)
        async with collector:
            importer = DerivHistoricalImporter(collector=collector, storage=storage)
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=args.history_days)

            for sym in symbols:
                print(f"  Fetching historical ticks for {sym} ({args.history_days} days)...")
                await importer.fetch_historical_ticks(sym, start, end)

    builder = ResearchDatasetBuilder()
    report_gen = ResearchReportGenerator()
    fingerprints = []

    for sym in symbols:
        for tf_str in timeframes:
            print(f"\nProcessing {sym} ({tf_str})...")

            # Load raw tick data or candles from storage
            if tf_str == "Tick":
                df = storage.read_ticks(sym)
            else:
                tf_enum = Timeframe(tf_str)
                df = storage.read_candles(sym, tf_enum)
                if df.empty:
                    # Aggregate from raw ticks if candles not directly saved
                    ticks_df = storage.read_ticks(sym)
                    if not ticks_df.empty:
                        df = aggregate_ticks_to_candles(ticks_df, tf_enum, source="historical")

            if df.empty:
                print(f"  [WARNING] No observation data found for {sym} ({tf_str}). Skipping.")
                continue

            # Build research dataset & manifest
            research_df, manifest = builder.build_dataset(
                df,
                symbol=sym,
                timeframe=tf_str,
            )

            # Generate forward outcomes separately
            fwd_generator = ForwardOutcomeTable()
            outcomes_df = fwd_generator.compute_outcomes(research_df)

            # Save forward outcomes separately
            outcomes_dir = output_dir / sym / "outcomes"
            outcomes_dir.mkdir(parents=True, exist_ok=True)
            outcomes_path = outcomes_dir / f"{sym}_{tf_str}_forward_outcomes.parquet"
            outcomes_df.to_parquet(outcomes_path, index=False)

            # Generate market fingerprint & reports
            fingerprint = generate_market_fingerprint(research_df, symbol=sym, timeframe=tf_str)
            fingerprints.append(fingerprint)

            m_path, f_path, r_path = report_gen.save_report_artifacts(
                output_dir=output_dir / sym,
                manifest=manifest,
                fingerprint=fingerprint,
            )

            print(f"  [OK] Manifest saved : {m_path.name}")
            print(f"  [OK] Fingerprint ID : {manifest.dataset_id[:16]}...")
            print(f"  [OK] Outcomes saved : {outcomes_path.name} (CLASSIFICATION: FORWARD_NON_CAUSAL)")
            print(f"  [OK] Report saved   : {r_path.name}")

    if len(fingerprints) > 1:
        comp_df = compare_market_fingerprints(fingerprints)
        comp_path = output_dir / "market_comparison.parquet"
        comp_df.to_parquet(comp_path, index=False)
        print(f"\n[OK] Saved Cross-Market Comparison to {comp_path.name}")

    print("\n==================================================")
    print("RESEARCH DATASET CONSTRUCTION COMPLETE")
    print("==================================================")


import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Project GOAT v0.3 — Research Dataset Construction & Fingerprinting"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Symbols to process (e.g. R_10 R_50 R_75)",
    )
    parser.add_argument(
        "--timeframes",
        nargs="+",
        help="Timeframes to process (e.g. M1 M5 M15)",
    )
    parser.add_argument(
        "--acquire-history",
        action="store_true",
        help="Acquire historical tick data from Deriv API before building dataset",
    )
    parser.add_argument(
        "--history-days",
        type=int,
        default=1,
        help="Number of historical days to acquire if --acquire-history is set",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Override output directory for research artifacts",
    )

    args = parser.parse_args()

    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
