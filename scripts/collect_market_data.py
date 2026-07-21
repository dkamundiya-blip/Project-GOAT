"""
Project GOAT v0.2 — Live Synthetic Market Data Collection Script

Invokes live market data collection from Deriv WebSocket API.

NO TRADING DISCLAIMER:
----------------------
This script performs MARKET DATA ACQUISITION ONLY.
It does NOT connect to trading accounts, authorization endpoints, or contract purchasing.
"""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
from pathlib import Path

# Add project root to sys.path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from goat.config import GoatSettings
from goat.data.collector.deriv import DerivMarketDataCollector
from goat.data.collector.discovery import DerivSymbolDiscovery
from goat.data.collector.session import CollectionSessionManager
from goat.logging import configure_logging, get_logger

_log = get_logger("script.collect")


async def main_async(args: argparse.Namespace) -> None:
    settings = GoatSettings()
    configure_logging(level=settings.log_level)

    endpoint = args.endpoint or settings.deriv_ws_endpoint
    app_id = args.app_id or settings.deriv_app_id

    collector = DerivMarketDataCollector(
        settings=settings,
        ws_endpoint=endpoint,
        app_id=app_id,
    )

    if args.discover:
        print("Connecting to Deriv for Symbol Discovery...")
        async with collector:
            discovery = DerivSymbolDiscovery(collector)
            symbols = await discovery.fetch_active_symbols(allowlist=args.symbols)
            print("\n==================================================")
            print("DISCOVERED SYNTHETIC INSTRUMENTS")
            print("==================================================")
            for s in symbols:
                print(
                    f"Symbol: {s.symbol:<12} Name: {s.display_name:<25} "
                    f"Submarket: {s.submarket:<15} Pip Size: {s.pip_size}"
                )
            print("==================================================\n")
        return

    collection_symbols = args.symbols or settings.collection_symbols
    print(f"Starting Data Collection Session for symbols: {', '.join(collection_symbols)}")
    print("Press Ctrl+C to stop collection gracefully.\n")

    session = CollectionSessionManager(collector=collector, settings=settings)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _sig_handler() -> None:
        print("\nShutdown signal received. Stopping collection session...")
        stop_event.set()

    if sys.platform != "win32":
        try:
            loop.add_signal_handler(signal.SIGINT, _sig_handler)
            loop.add_signal_handler(signal.SIGTERM, _sig_handler)
        except NotImplementedError:
            pass

    session_task = asyncio.create_task(
        session.run_session(symbols=collection_symbols, duration_seconds=args.duration)
    )

    try:
        if args.duration:
            await session_task
        else:
            await stop_event.wait()
            session_task.cancel()
            try:
                await session_task
            except asyncio.CancelledError:
                pass
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Stopping session...")
        session_task.cancel()
        try:
            await session_task
        except asyncio.CancelledError:
            pass
    finally:
        print("\n" + session.format_summary_text())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Project GOAT v0.2 — Live Synthetic Market Data Acquisition"
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        help="Synthetic symbols to collect (e.g. R_10 R_50 R_75)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        help="Run duration in seconds (if omitted, runs until Ctrl+C)",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Discover available synthetic symbols and exit",
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        help="Override WebSocket endpoint URL",
    )
    parser.add_argument(
        "--app-id",
        type=int,
        help="Override Deriv App ID",
    )

    args = parser.parse_args()

    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
