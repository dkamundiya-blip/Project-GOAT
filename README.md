# 🐐 Project GOAT

**Generative Opportunity Analysis & Trading**

A rigorous quantitative research platform for studying synthetic financial
markets, discovering recurring statistical price structures, and validating
potential edges.

---

## Current Version: v0.5 — Experiment Orchestrator

This release introduces the **deterministic experiment orchestration framework** capable of executing large batch campaigns of statistical hypothesis experiments while preserving scientific auditability, reproducibility, chronological integrity, train/freeze/validation workflow, and sealed holdout discipline.

### Capabilities Included

- ✅ **Three-Tier Identity System**: `campaign_id` (operational run), `configuration_hash` (research setup), and `experiment_id` (deterministic hypothesis definition hash).
- ✅ **Worker-Count Invariant Determinism**: Execution across 1, 2, 8, or 16 workers yields 100% byte-for-byte identical output files.
- ✅ **Six Independent Version Tags Hierarchy**: `manifest_schema_version`, `provenance_schema_version`, `experiment_hash_schema`, `checkpoint_format_version`, `log_schema_version`, and `report_schema_version`.
- ✅ **Queue vs Persistence Decoupling**: In-memory `ExperimentQueue` (zero file I/O) decoupled from `CheckpointManager` disk persistence via frozen `QueueSnapshot`.
- ✅ **Formally Defined State Machine**: 10-state `CampaignStatus` lifecycle matrix and 6-state `ExperimentStatus` lifecycle.
- ✅ **Structured Failure Taxonomy & Option A Graceful Cancellation**: `ValidationFailure`, `ExperimentFailure`, `InfrastructureFailure`, `WorkerFailure`, `CampaignFailure`.
- ✅ **Environment Metadata & Research Provenance**: Pre-flight data integrity verification aborts execution on fingerprint/version mismatches.
- ✅ **Structured Logging & Deterministic Event Sequencing**: Monotonic `event_sequence` counter preserved across checkpoints.
- ✅ **Modular Reporting & Output Abstraction Layer**: `BaseReportGenerator` separating artifact persistence from markdown (`report.md`) and JSON (`report.json`) report generation.

---

### Critical Scope Disclaimer & Boundaries

> **⚠️ Project GOAT is strictly a quantitative research and statistical edge discovery engine.**
>
> **The following are EXPLICITLY OUT OF SCOPE:**
>
> - BUY/SELL trading signals or trade execution
> - Live/simulated broker order routing
> - Stop-loss / take-profit order placement
> - Position sizing or portfolio management
> - Machine learning models or neural networks
> - AutoML or optimization against holdout data
>
> `goat/signals`, `goat/risk`, and `goat/models` remain completely untouched.

---

## Installation & Setup

```bash
# Clone the repository
git clone <repository-url>
cd project-goat

# Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies in development mode
pip install -e ".[dev]"
```

---

## Running Hypothesis Experiments & Campaigns

### 1. Build Research Dataset & Acquire History

```bash
python scripts/build_research_dataset.py --acquire-history --symbols R_10 --timeframes M1
```

### 2. Launch Batch Experiment Campaign via CLI

```bash
python scripts/run_campaign.py launch --name volatility_compression --symbols R_10 --timeframes M1 --workers 4
```

### 3. Inspect Campaign Status

```bash
python scripts/run_campaign.py status --campaign-id CMP-20260722T083015Z-7F3D21
```

---

## Canonical Output Directory Structure

Executing a campaign produces a self-contained output directory:

```
data/campaigns/<campaign_id>/
    ├── campaign_manifest.json        (6-section manifest, manifest_schema_version = 1)
    ├── checkpoint.json               (QueueSnapshot state, checkpoint_format_version = 1)
    ├── experiment_results.json       (Sorted array of HypothesisResult objects)
    ├── campaign_statistics.json      (Aggregated statistics & performance metrics)
    ├── campaign.log.jsonl            (Monotonic event_sequence JSON logs, log_schema_version = 1)
    ├── report.md                     (Rendered human-readable markdown report)
    └── report.json                   (Structured machine-readable report, report_schema_version = 1)
```

---

## Running Tests

```bash
# Run the complete deterministic test suite
pytest -v

# Run with coverage report
pytest -v --cov=goat --cov-report=term-missing
```

---

## Project Milestones

- **v0.1**: Quant Data Foundation (Immutable tick/candle schemas, Parquet storage, M1 aggregation).
- **v0.2**: Real Synthetic Market Data Acquisition (Deriv WebSocket integration, live tick ingestion).
- **v0.3**: Research Dataset Construction & Synthetic Market Fingerprinting (Causal features, regimes, sealed holdout).
- **v0.4**: Hypothesis Engine & Statistical Edge Discovery (Causal evaluator, Welch/Mann-Whitney/Permutation tests, FDR q-values, EdgeScore, EdgeRegistry).
- **v0.5**: Experiment Orchestrator (Worker-count invariant batch execution, 10-state lifecycle, deterministic checkpoints, structured logging, output abstraction).
