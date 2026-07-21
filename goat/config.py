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

    def get_raw_data_dir(self) -> Path:
        """Return the raw data directory, defaulting to ``data_dir/raw``."""
        return self.raw_data_dir or self.data_dir / "raw"

    def get_processed_data_dir(self) -> Path:
        """Return the processed data directory, defaulting to ``data_dir/processed``."""
        return self.processed_data_dir or self.data_dir / "processed"
