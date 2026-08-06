"""
Project GOAT v0.9 — Expectancy Assessment Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.statistics.core.canonical import compute_expectancy_id
from goat.statistics.core.models import ExpectancyAssessment


class ExpectancyAssessmentEngine:
    """Expectancy Assessment Engine for calculating mathematical expected value, win/loss ratios,

    profit factors, and risk-adjusted distribution summaries.

    IMPORTANT: This engine ONLY evaluates statistical expectancy.
    It SHALL NOT size positions or execute trades.
    """

    def __init__(self) -> None:
        self._assessments: dict[str, ExpectancyAssessment] = {}

    def calculate_expectancy(
        self,
        evaluation_id: str,
        returns_or_gains: Sequence[float],
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExpectancyAssessment:
        """Calculate mathematical expectancy and summary statistics from observation return values."""
        if not returns_or_gains:
            raise ValueError("Expectancy assessment requires non-empty returns sequence.")

        n = len(returns_or_gains)
        wins = [x for x in returns_or_gains if x > 0.0]
        losses = [abs(x) for x in returns_or_gains if x < 0.0]

        win_count = len(wins)
        loss_count = len(losses)

        win_rate = float(win_count) / float(n)
        loss_rate = float(loss_count) / float(n)

        avg_gain = (sum(wins) / float(win_count)) if win_count > 0 else 0.0
        avg_loss = (sum(losses) / float(loss_count)) if loss_count > 0 else 0.0

        # Mathematical expectancy = (win_rate * avg_gain) - (loss_rate * avg_loss)
        expected_val = (win_rate * avg_gain) - (loss_rate * avg_loss)

        total_gain = sum(wins)
        total_loss = sum(losses)
        profit_factor = (total_gain / total_loss) if total_loss > 0 else (999.0 if total_gain > 0 else 0.0)

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        exp_id, canonical_hash = compute_expectancy_id(
            evaluation_id=evaluation_id,
            expected_value=expected_val,
            sample_size=n,
        )

        assessment = ExpectancyAssessment(
            expectancy_id=exp_id,
            evaluation_id=evaluation_id.strip(),
            expected_value=expected_val,
            win_rate=win_rate,
            loss_rate=loss_rate,
            average_gain=avg_gain,
            average_loss=avg_loss,
            profit_factor=profit_factor,
            sample_size=n,
            timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._assessments[exp_id] = assessment
        return assessment

    def get_assessment(self, expectancy_id: str) -> ExpectancyAssessment | None:
        """Retrieve assessment by ID."""
        return self._assessments.get(expectancy_id)

    def list_all(self) -> list[ExpectancyAssessment]:
        """List all assessments sorted by timestamp."""
        return sorted(self._assessments.values(), key=lambda e: e.timestamp)
