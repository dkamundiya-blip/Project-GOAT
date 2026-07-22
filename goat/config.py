"""
Project GOAT v0.1 — Configuration

Loads application settings from environment variables using pydantic-settings.
Secrets and provider-specific credentials must be supplied via environment
variables or a .env file — they are NEVER hard-coded.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class GoatSettings(BaseSettings):
    """Application-wide settings loaded from environment variables.

    All fields use the ``GOAT_`` prefix when reading from the environment.
    For example, ``GOAT_DATA_DIR`` maps to ``data_dir``.

    Attributes:
        data_dir: Root directory for all data storage.
        raw_data_dir: Override directory for raw tick data (Parquet).
                      Defaults to ``data_dir / "raw"`` if not set.
        processed_data_dir: Override directory for processed candle data.
                            Defaults to ``data_dir / "processed"`` if not set.
        log_level: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """

    model_config = {"env_prefix": "GOAT_"}

    data_dir: Path = Path("data")
    raw_data_dir: Path | None = None
    processed_data_dir: Path | None = None
    log_level: str = "INFO"

    # Provider settings (v0.2 Market Data Acquisition)
    deriv_ws_endpoint: str = "wss://ws.derivws.com/websockets/v3"
    deriv_app_id: int = 1089
    collection_symbols: list[str] = ["R_10", "R_50", "R_75"]
    reconnect_max_retries: int = 10
    reconnect_base_delay: float = 1.0
    reconnect_max_delay: float = 60.0
    connection_timeout: float = 10.0
    heartbeat_interval: float = 30.0

    # Research settings (v0.3 Quantitative Research)
    research_data_dir: Path | None = None
    research_symbols: list[str] = ["R_10", "R_50", "R_75"]
    research_timeframes: list[str] = ["M1", "M5", "M15"]
    rolling_windows: list[int] = [10, 20, 50, 100]
    autocorr_lags: list[int] = [1, 2, 3, 5, 10]
    forward_horizons: list[int] = [1, 3, 5, 10, 20]
    # Hypothesis engine settings (v0.4 Hypothesis & Edge Discovery)
    fdr_alpha: float = 0.05
    min_hypothesis_sample_size: int = 100
    default_permutation_samples: int = 1000
    permutation_random_seed: int = 42
    edge_registry_path: Path | None = None
    holdout_audit_log_path: Path | None = None

    def get_raw_data_dir(self) -> Path:
        """Return the raw data directory, defaulting to ``data_dir/raw``."""
        return self.raw_data_dir or self.data_dir / "raw"

    def get_processed_data_dir(self) -> Path:
        """Return the processed data directory, defaulting to ``data_dir/processed``."""
        return self.processed_data_dir or self.data_dir / "processed"

    def get_research_data_dir(self) -> Path:
        """Return the research data directory, defaulting to ``data_dir/research``."""
        return self.research_data_dir or self.data_dir / "research"

    def get_edge_registry_path(self) -> Path:
        """Return the edge registry file path, defaulting to ``data_dir/research/edge_registry.json``."""
        return self.edge_registry_path or self.get_research_data_dir() / "edge_registry.json"

    def get_holdout_audit_log_path(self) -> Path:
        """Return the holdout audit log file path, defaulting to ``data_dir/research/holdout_audit_log.json``."""
        return self.holdout_audit_log_path or self.get_research_data_dir() / "holdout_audit_log.json"
