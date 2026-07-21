"""Project GOAT — Research & Statistical Characterization Layer."""

from goat.research.dataset import DatasetManifest, ResearchDatasetBuilder
from goat.research.events import ImpulseCharacterization, PullbackCharacterization
from goat.research.fingerprint import MarketFingerprint, compare_market_fingerprints
from goat.research.outcomes import ForwardOutcomeTable
from goat.research.regimes import RegimeClassifier
from goat.research.report import ResearchReportGenerator
from goat.research.returns import calculate_returns
from goat.research.splitting import ChronologicalSplitter
from goat.research.stats import calculate_distribution_stats, calculate_serial_dependence
from goat.research.sufficiency import DatasetSufficiencyReport, evaluate_dataset_sufficiency

__all__ = [
    "DatasetManifest",
    "ResearchDatasetBuilder",
    "calculate_returns",
    "calculate_distribution_stats",
    "calculate_serial_dependence",
    "ImpulseCharacterization",
    "PullbackCharacterization",
    "ForwardOutcomeTable",
    "RegimeClassifier",
    "MarketFingerprint",
    "compare_market_fingerprints",
    "ChronologicalSplitter",
    "DatasetSufficiencyReport",
    "evaluate_dataset_sufficiency",
    "ResearchReportGenerator",
]
