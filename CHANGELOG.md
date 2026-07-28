# Changelog

All notable changes to Project GOAT (Generative Opportunity Analysis & Trading) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-07-29

### Added
- **Deterministic Scientific Identity Layer (Step 3.1)**:
  - Domain models for `CandidateEdge`, `HypothesisIdentity`, `ValidationPolicy`, and `ValidationRunInfo`.
  - Canonical JSON serializer (`canonical_json`) with sorted keys, standardized floats, and UTF-8 encoding.
  - Deterministic SHA-256 identity calculation for `hypothesis_version`, `policy_hash`, `validation_run_id`, and `evidence_payload_hash`.
- **Edge Registry & SQLite Persistence (Step 3.2)**:
  - Relational SQLite storage backend (`SQLiteEdgeRepository`) with foreign key enforcement and transactional durability.
  - SQLite Schema v2 (`CURRENT_SCHEMA_VERSION = 2`) with transactional v1 -> v2 schema migration.
  - Read-only integrity verification (`EdgePersistenceVerifier`) detecting unauthorized database tampering.
- **Multi-Stage Edge Validation Engine (Step 3.3)**:
  - Fail-closed `ValidationStateMachine` coordinating Stage A through Stage G execution.
  - **Stage A (Discovery Validation)**: Sample size, effect size, raw alpha filtering, and Benjamini-Hochberg FDR control.
  - **Stage B (Retention Validation)**: OOS partition performance retention ratio verification.
  - **Stage C (Temporal Stability)**: Multi-fold walk-forward cross-validation, fold coefficient of variation (CV) bounds, and positive fold ratio enforcement.
  - **Stage D (Parameter Robustness)**: Anti-optimization parameter perturbation grid, neighbor stability ratio, and max allowed performance drop enforcement.
  - **Stage E (Causal Falsification)**: Anti-p-hacking contradictory condition testing and inversion checks.
  - **Stage F (Cross-Context Replication)**: Multi-market replication family pre-registration, context universe lock, and Fisher's combined probability meta-analysis ($p_{\text{meta}} \le 0.01$).
  - **Stage G (Confirmatory Holdout Validation)**: One-shot holdout validation logic certified with synthetic test fixtures.
- **Holdout Isolation Architecture**:
  - `HoldoutAccessGate` enforcing strict single-use confirmatory holdout consumption.
  - Zero access to real confirmatory holdout datasets during development, testing, or reporting (`REAL_HOLDOUT_ACCESSED = NO`, `REAL_HOLDOUT_BYTES_READ = 0`).
- **Canonical Reporting & Evidence Packaging (Step 3.4)**:
  - Domain-level `ValidationReport` construction without statistical recomputation.
  - Deterministic report identity calculation (`compute_report_id` $\rightarrow$ `RPT_<HEX16>`).
  - Canonical JSON and presentation Markdown (`render_report_markdown`) generator.
  - Atomic filesystem evidence packaging (`EvidencePackageWriter`) under `data/edge_reports/<val_run_id>/<report_id>/`.
  - Package integrity verifier (`EvidencePackageVerifier`) with 5-tuple canonical evidence ordering and SHA-256 artifact manifest checksums.
  - Fail-closed path traversal and containment security validation (`^[A-Za-z0-9_-]+$`).
- **Release Hardening & Version Harmonization (Step 3.5)**:
  - Harmonized package version in `pyproject.toml` and runtime version in `goat.__version__` to `0.6.0`.
  - Hardened top-level public API exports across persistence, engine, stages, reporting, and evidence packaging.
  - Added release version metadata and public API regression test suites.

### Disclosures & Scientific Scope
- **Real Holdout Status**: The real confirmatory holdout dataset has NOT been accessed or consumed (`REAL_HOLDOUT_ACCESSED = NO`, `REAL_HOLDOUT_BYTES_READ = 0`). Stage G has been verified exclusively using synthetic test fixtures.
- **Scope**: This release certifies the scientific validation engine infrastructure, persistence architecture, and tamper-evident reporting pipeline. It does not make commercial profitability or live market trading claims.

---

## [0.5.0] - 2026-06-15

### Added
- Experiment Orchestration engine with campaign queue, checkpointing, and seed reproducibility.
