"""
Project GOAT v0.5 — CLI Campaign Orchestrator

Launches, status-checks, resumes, cancels, and reports batch statistical campaigns.
"""

from __future__ import annotations

import argparse
import sys

from goat.config import GoatSettings
from goat.orchestration.campaign import CampaignDefinition
from goat.orchestration.scheduler import (
    ExperimentScheduler,
    compute_configuration_hash,
    generate_campaign_id,
)
from scripts.run_hypothesis_experiment import build_volatility_compression_grid


def main() -> None:
    parser = argparse.ArgumentParser(description="Project GOAT v0.5 — Campaign CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Launch command
    launch_parser = subparsers.add_parser("launch", help="Launch a new campaign")
    launch_parser.add_argument("--name", type=str, default="volatility_compression", help="Campaign name")
    launch_parser.add_argument("--symbols", nargs="+", default=["R_10"], help="Instrument symbol scope")
    launch_parser.add_argument("--timeframes", nargs="+", default=["M1"], help="Timeframe scope")
    launch_parser.add_argument("--workers", type=int, default=4, help="Worker thread count")
    launch_parser.add_argument("--seed", type=int, default=42, help="Master random seed")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check campaign status")
    status_parser.add_argument("--campaign-id", type=str, required=True, help="Campaign ID")

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a paused or interrupted campaign")
    resume_parser.add_argument("--campaign-id", type=str, required=True, help="Campaign ID")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a running campaign")
    cancel_parser.add_argument("--campaign-id", type=str, required=True, help="Campaign ID")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate report for a campaign")
    report_parser.add_argument("--campaign-id", type=str, required=True, help="Campaign ID")

    args = parser.parse_args()

    settings = GoatSettings()
    scheduler = ExperimentScheduler(settings=settings)

    if args.command == "launch":
        symbols = args.symbols
        timeframes = args.timeframes

        # Build volatility compression parameter grid
        grid = build_volatility_compression_grid(
            symbols=symbols,
            timeframes=timeframes,
        )

        cfg_hash = compute_configuration_hash(
            hypothesis_grid=grid,
            symbols=symbols,
            timeframes=timeframes,
            master_seed=args.seed,
            fdr_alpha=settings.fdr_alpha,
        )

        camp_id = generate_campaign_id(args.name)

        camp_def = CampaignDefinition(
            campaign_id=camp_id,
            configuration_hash=cfg_hash,
            name=args.name,
            description="CLI launched batch campaign",
            symbol_scope=symbols,
            timeframe_scope=timeframes,
            master_seed=args.seed,
            max_workers=args.workers,
            fdr_alpha=settings.fdr_alpha,
        )

        print("=" * 50)
        print("PROJECT GOAT v0.5 — EXPERIMENT CAMPAIGN LAUNCH")
        print("=" * 50)
        print(f"Campaign ID        : {camp_def.campaign_id}")
        print(f"Configuration Hash : {camp_def.configuration_hash}")
        print(f"Symbols            : {', '.join(symbols)}")
        print(f"Timeframes         : {', '.join(timeframes)}")
        print(f"Workers            : {args.workers}")
        print(f"Master Seed        : {args.seed}")
        print(f"Hypotheses Grid    : {len(grid)}")
        print("")

        output_dir = scheduler.run_campaign(
            campaign_def=camp_def,
            hypothesis_grid=grid,
            symbols=symbols,
            timeframes=timeframes,
        )

        print("=" * 50)
        print("CAMPAIGN EXECUTION COMPLETED")
        print("=" * 50)
        print(f"Artifacts output directory : {output_dir}")
        print(f"Markdown report path       : {output_dir / 'report.md'}")
        print(f"JSON report path           : {output_dir / 'report.json'}")

    elif args.command == "status":
        info = scheduler.get_status(args.campaign_id)
        print("=" * 50)
        print("PROJECT GOAT v0.5 — CAMPAIGN STATUS")
        print("=" * 50)
        print(f"Campaign ID        : {info.get('campaign_id')}")
        print(f"Status             : {info.get('status')}")
        print(f"Configuration Hash : {info.get('configuration_hash')}")
        print(f"Total Tasks        : {info.get('total_experiments')}")
        print(f"Completed Tasks    : {info.get('completed_experiments')}")
        print(f"Failed Tasks       : {info.get('failed_experiments')}")

    elif args.command == "resume":
        print("=" * 50)
        print("PROJECT GOAT v0.5 — CAMPAIGN RESUME")
        print("=" * 50)
        output_dir = scheduler.resume_campaign(args.campaign_id)
        print(f"Resumed campaign output directory : {output_dir}")

    elif args.command == "cancel":
        print("=" * 50)
        print("PROJECT GOAT v0.5 — CAMPAIGN CANCEL")
        print("=" * 50)
        output_dir = scheduler.cancel_campaign(args.campaign_id)
        print(f"Campaign cancelled cleanly. Output directory : {output_dir}")

    elif args.command == "report":
        print("=" * 50)
        print("PROJECT GOAT v0.5 — CAMPAIGN REPORT GENERATION")
        print("=" * 50)
        output_dir = scheduler.generate_reports(args.campaign_id)
        print(f"Reports regenerated cleanly in : {output_dir}")


if __name__ == "__main__":
    main()
