# Project GOAT v0.6 — Edge Reporting, Evidence Packages & Scientific Audit Trail Architecture

**Authoritative Architecture Specification & Trust Contract**
* **Version**: v0.6.0-SPEC.4 (Reporting & Evidence Packaging)
* **Status**: FROZEN / CERTIFIED SPECIFICATION
* **Authoritative Baselines**: GOAT v0.5.0 (`c32fe497709e5bd03263ede3447a67cf8cc61cf9`), v0.6.0-SPEC.3, SQLite Schema v2

---

## 1. Executive Summary & Reporting Goals

The Project GOAT v0.6 Edge Reporting and Evidence Packaging Layer transforms persisted research artifacts and scientific evidence from the Edge Registry into deterministic, tamper-evident, machine-readable scientific evidence packages.

### Primary Goals
1. **DERIVED TRUTH**: The Edge Registry (`SQLiteEdgeRepository`) and persisted atomic evidence (`AtomicEvidenceRecord`) remain the sole authoritative scientific source of truth. Reports are strictly derived artifacts.
2. **ZERO RECOMPUTATION**: Report generation is 100% read-only. It MUST NOT rerun Stage A–G statistical tests, tune parameters, or recalculate p-values.
3. **DETERMINISTIC IDENTITY**: Every report has a canonical identifier (`RPT_<HEX16>`) derived strictly from frozen scientific identity payloads and canonical evidence records. Wall-clock generation time (`generated_at_utc`) is metadata only and MUST NOT alter report identity.
4. **HOLDOUT ISOLATION**: Report generation has ZERO capability to authorize `HoldoutAccessGate` or read real holdout data (`REAL_HOLDOUT_ACCESSED = NO`, `REAL_HOLDOUT_BYTES_READ = 0`).
5. **FAIL CLOSED**: Any missing evidence, hash mismatch, structural corruption, or identity inconsistency produces an explicit `ReportIntegrityError`.
6. **FULL AUDIT TRAIL**: Complete cryptographic provenance binding candidate edge identity (`EDGE_`), hypothesis version (`12-hex`), validation policy (`PLC_`), dataset fingerprint, context universe (`CTX_`), validation run (`VAL_`), atomic evidence (`EVD_`/`EVP_`), and confirmatory audit (`AUD_`).

---

## 2. Trust Boundaries & Authoritative Data Sources

```
+-----------------------------------------------------------------------------------+
|                            AUTHORITATIVE PERSISTENCE LAYER                        |
|                                SQLiteEdgeRepository (v2)                          |
|                                                                                   |
|  [candidate_edges]  [hypothesis_versions]  [validation_policies]                  |
|  [validation_context_universes]  [validation_runs]  [atomic_evidence]             |
|  [confirmatory_audits]                                                            |
+-----------------------------------------------------------------------------------+
                                         │
                                         │ READ-ONLY QUERY (NO RECOMPUTATION)
                                         ▼
+-----------------------------------------------------------------------------------+
|                           EDGE REPORTING ENGINE (v0.6)                            |
|                                                                                   |
|   1. Canonical Evidence Sorting                                                   |
|   2. ValidationReport Model Assembly                                              |
|   3. Report Identity Computation (RPT_<HEX16>)                                    |
|   4. Integrity Proof Generation                                                   |
|   5. Markdown Presentation Rendering                                              |
+-----------------------------------------------------------------------------------+
                                         │
                                         │ ATOMIC PERSISTENCE
                                         ▼
+-----------------------------------------------------------------------------------+
|                        CANONICAL EVIDENCE PACKAGE ARTIFACTS                       |
|           data/edge_reports/<validation_run_id>/<report_id>/                      |
|                                                                                   |
|   - manifest.json          (Package manifest & SHA-256 hashes)                    |
|   - validation_report.json (Authoritative machine-readable report)                |
|   - validation_report.md   (Human-readable presentation)                          |
|   - evidence.json          (Canonical ordered atomic evidence list)               |
|   - integrity.json         (Independent verification proof)                       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Canonical ValidationReport Model Schema

The machine-readable `ValidationReport` schema (`report_schema_version = 1`) contains 9 structured sections:

```json
{
  "report_schema_version": 1,
  "report_id": "RPT_7A8B9C0D1E2F3456",
  "validation_run_id": "VAL_061DC6057ECC260E",
  "generated_at_utc": "2026-07-28T18:45:00Z",
  "edge_identity": {
    "edge_id": "EDGE_9A8B7C6D5E4F3210",
    "proposition_name": "Momentum Breakout Edge",
    "causal_primitive": "greater_than",
    "target_feature": "close",
    "economic_rationale_category": "momentum",
    "base_condition_spec": {"period": 20},
    "edge_schema_version": 1
  },
  "hypothesis_identity": {
    "hypothesis_version": "1234567890ab",
    "condition_parameters": {"period": 20, "threshold": 0.02},
    "forward_outcome_metric": "log_return",
    "forward_horizon": 5
  },
  "policy_specification": {
    "policy_hash": "PLC_1234567890ABCDEF",
    "policy_id": "P1_PRODUCTION",
    "version": "1.0.0",
    "multiplicity_strategy": "BENJAMINI_HOCHBERG",
    "meta_analysis_method": "FISHER_COMBINED_PROBABILITY",
    "stage_a_alpha": 0.05,
    "stage_a_effect_min": 0.15,
    "stage_a_min_sample": 100,
    "stage_b_min_retention_ratio": 0.50,
    "stage_c_min_folds": 5,
    "stage_c_min_positive_ratio": 0.70,
    "stage_c_max_fold_cv": 1.00,
    "stage_d_perturbation_delta": 0.20,
    "stage_d_min_stable_ratio": 0.65,
    "stage_d_max_allowed_drop": 0.60,
    "stage_e_fail_on_contradictory_inversion": true,
    "stage_f_min_replication_pct": 0.60,
    "stage_f_meta_alpha": 0.01
  },
  "data_provenance": {
    "dataset_fingerprint": "DS_FP_SYNTHETIC_9999",
    "candidate_target_scope": "UNIVERSAL",
    "context_universe_id": "CTX_1122334455667788",
    "contexts": ["AAPL", "GOOGL", "MSFT"]
  },
  "validation_summary": {
    "lifecycle_state": "CONFIRMATORY_READY",
    "highest_completed_stage": "STAGE_F_REPLICATION",
    "overall_decision": "PRECONFIRMATORY_PASS",
    "confirmatory_status": "PENDING"
  },
  "stage_results": [
    {
      "stage": "STAGE_A_DISCOVERY",
      "decision": "PASS",
      "reason_code": "PASSED",
      "explanation": "Stage A discovery significance passed",
      "evidence_count": 1,
      "evidence_ids": ["EVD_1111111111111111"]
    }
  ],
  "confirmatory_audit": {
    "audit_id": "AUD_A1B2C3D4E5F67890",
    "frozen_hypothesis_version": "1234567890ab",
    "policy_hash": "PLC_1234567890ABCDEF",
    "dataset_fingerprint": "DS_FP_SYNTHETIC_9999",
    "holdout_partition_identity": "holdout_sealed_v1"
  },
  "software_provenance": {
    "goat_version": "v0.6.0",
    "python_version": "3.14.0",
    "git_commit": "c32fe497709e5bd03263ede3447a67cf8cc61cf9"
  },
  "integrity": {
    "evidence_count": 12,
    "evidence_payload_hashes": ["EVP_AAA", "EVP_BBB"],
    "report_content_hash": "RPT_7A8B9C0D1E2F3456",
    "verification_status": "VERIFIED"
  }
}
```

---

## 4. Report Identity Contract (`RPT_<HEX16>`)

Report identity is calculated using canonical SHA-256 hashing (`compute_canonical_sha256`, length 16):

```python
def compute_report_id(
    validation_run_id: str,
    edge_id: str,
    policy_hash: str,
    dataset_fingerprint: str,
    hypothesis_version: str,
    evidence_payload_hashes: Sequence[str],
    context_universe_id: str = "",
    audit_id: str = "",
    report_schema_version: int = 1,
) -> str:
    """Compute deterministic report identity RPT_<HEX16>. Excludes timestamps."""
    sorted_evp = sorted([str(h).strip() for h in evidence_payload_hashes])
    payload = {
        "audit_id": str(audit_id).strip(),
        "context_universe_id": str(context_universe_id).strip(),
        "dataset_fingerprint": str(dataset_fingerprint).strip(),
        "edge_id": str(edge_id).strip(),
        "evidence_payload_hashes": sorted_evp,
        "hypothesis_version": str(hypothesis_version).strip(),
        "policy_hash": str(policy_hash).strip(),
        "report_schema_version": int(report_schema_version),
        "validation_run_id": str(validation_run_id).strip(),
    }
    digest = compute_canonical_sha256(payload, length=16)
    return f"RPT_{digest.upper()}"
```

---

## 5. Canonical Evidence Ordering Contract

To eliminate non-deterministic SQLite row retrieval differences, all evidence records MUST be sorted using a canonical 5-tuple key before report packaging:

$$\text{SortKey} = (\text{stage\_sequence\_index}, \text{dimension\_type}, \text{dimension\_key}, \text{partition\_identity}, \text{evidence\_id})$$

Where `stage_sequence_index` maps:
* `STAGE_A_DISCOVERY` $\rightarrow$ 1
* `STAGE_B_RETENTION` $\rightarrow$ 2
* `STAGE_C_TEMPORAL` $\rightarrow$ 3
* `STAGE_D_ROBUSTNESS` $\rightarrow$ 4
* `STAGE_E_FALSIFICATION` $\rightarrow$ 5
* `STAGE_F_REPLICATION` $\rightarrow$ 6
* `STAGE_G_HOLDOUT` $\rightarrow$ 7

---

## 6. Overall Edge Decision Derivation Matrix

Overall report decision is derived mechanically from persisted stage outcomes without second-guessing or overriding scientific state:

| Highest Completed Stage | Stage Decision | Validation Lifecycle State | Overall Report Decision |
| :--- | :--- | :--- | :--- |
| None | N/A | `REGISTERED` | `NOT_STARTED` |
| Stage A | `FAIL` | `REJECTED` | `REJECTED` |
| Stage A | `INSUFFICIENT_EVIDENCE` | `REJECTED` | `INSUFFICIENT_EVIDENCE` |
| Stage B | `FAIL` | `REJECTED` | `REJECTED` |
| Stage C | `FAIL` | `REJECTED` | `REJECTED` |
| Stage D | `FAIL` | `REJECTED` | `REJECTED` |
| Stage E | `FAIL` | `REJECTED` | `REJECTED` |
| Stage F | `FAIL` | `REJECTED` | `REJECTED` |
| Stage F | `PASS` | `CONFIRMATORY_READY` | `PRECONFIRMATORY_PASS` |
| Stage G | `PASS` | `VALIDATED` | `CONFIRMED` |
| Stage G | `FAIL` | `REJECTED` | `CONFIRMATORY_FAILED` |

---

## 7. Evidence Package Directory & File Contract

Every certified validation run produces an immutable directory package:

$$\text{Path: } \texttt{data/edge\_reports/<validation\_run\_id>/<report\_id>/}$$

### Package Artifacts
1. `manifest.json`: Cryptographic manifest containing file basenames, byte sizes, SHA-256 checksums, and package schema version (`evidence_package_schema_version = 1`).
2. `validation_report.json`: Authoritative machine-readable `ValidationReport` document.
3. `validation_report.md`: Human-readable Markdown presentation rendered strictly from `validation_report.json`.
4. `evidence.json`: Complete canonically-sorted list of atomic evidence payloads.
5. `integrity.json`: Cryptographic proof containing recomputed `RPT_`, `EVP_`, `AUD_` hashes, and integrity verification timestamp.

---

## 8. Integrity Verifier Specification

The `ReportIntegrityVerifier` independently validates an existing report package without external state assumptions:

```python
class ReportIntegrityVerifier:
    """Independent cryptographic verifier for validation reports and evidence packages."""

    def verify_package(self, package_dir: Path) -> IntegrityVerificationResult:
        """Validate package manifest checksums, RPT_ recomputation, EVP_ hashes, and AUD_ hashes."""
```

### Verification Checks
1. **Manifest File Hashes**: Every file in `manifest.json` matches its actual SHA-256 file content hash.
2. **Report Identity Match**: Recomputed `compute_report_id(...)` matches `report_id`.
3. **Evidence Payload Hashes**: Every `AtomicEvidenceRecord.evidence_payload_hash` in `evidence.json` matches recomputed `compute_evidence_payload_hash(...)`.
4. **Confirmatory Audit Hash**: If `confirmatory_audit` is present, `compute_confirmatory_audit_id(...)` matches `audit_id`.
5. **Chain Continuity**: `validation_run_id`, `edge_id`, `policy_hash`, `dataset_fingerprint`, `hypothesis_version`, and `context_universe_id` are identical across report, evidence, and audit records.

---

## 9. Atomic Package Generation & Path Security

### Atomic Generation Pattern
1. Create temporary directory: `data/edge_reports/<validation_run_id>/.tmp_<uuid>/`.
2. Generate all report files (`validation_report.json`, `validation_report.md`, `evidence.json`, `integrity.json`, `manifest.json`).
3. Execute `ReportIntegrityVerifier.verify_package()` on the temporary directory.
4. Atomically rename temporary directory to destination path `data/edge_reports/<validation_run_id>/<report_id>/` using `Path.replace()`.

### Path Safety & Traversal Protection
All path components (`validation_run_id`, `report_id`) are validated against regex `^[A-Za-z0-9_\-]+$`. Any input containing `..`, `/`, `\`, or null bytes is rejected immediately with a `SecurityViolationError`.

---

## 10. Adversarial Threat Matrix & Fail-Closed Behaviors

| # | Threat / Adversarial Failure Mode | Expected Fail-Closed Behavior |
| :--- | :--- | :--- |
| 1 | Evidence inserted in different database order | Canonical 5-tuple sorting produces byte-identical `evidence.json` and `RPT_` ID. |
| 2 | Missing Stage C evidence between B and D | `verify_package()` detects broken stage chain gap and raises `ReportIntegrityError`. |
| 3 | EVD_ evidence ID mismatch | Recomputation of `compute_evidence_id()` fails; raises `ReportIntegrityError`. |
| 4 | EVP_ payload hash mismatch | Recomputation of payload SHA-256 fails; raises `ReportIntegrityError`. |
| 5 | Mismatched policy_hash | Policy hash mismatch across evidence records raises `ReportIntegrityError`. |
| 6 | Mismatched dataset_fingerprint | Fingerprint mismatch raises `ReportIntegrityError`. |
| 7 | Mismatched edge_id | Candidate edge ID mismatch raises `ReportIntegrityError`. |
| 8 | Mismatched context_universe_id | Universe ID mismatch raises `ReportIntegrityError`. |
| 9 | Duplicate evidence records | Duplicate `evidence_id` with conflicting payload hash raises `EvidenceConflictError`. |
| 10 | Conflicting evidence records | Conflicting evidence payload hash raises `ReportIntegrityError`. |
| 11 | Forged confirmatory audit | Recomputed `AUD_<HEX16>` hash fails to match `audit_id`; raises `ReportIntegrityError`. |
| 12 | Stage G evidence without A-F history | Prerequisite chain check fails; raises `ReportIntegrityError`. |
| 13 | Partial/corrupted report package | Manifest file checksum verification fails; raises `ReportIntegrityError`. |
| 14 | Modified report JSON after generation | Manifest checksum and recomputed `RPT_` hash fail; raises `ReportIntegrityError`. |
| 15 | Modified evidence JSON after generation | Manifest checksum and `EVP_` hashes fail; raises `ReportIntegrityError`. |
| 16 | Regeneration at different wall-clock time | `RPT_<HEX16>` identity excludes timestamps; produces identical `RPT_` ID. |
| 17 | Path traversal attack (`../`) | Path component sanitizer rejects traversal characters with `SecurityViolationError`. |
| 18 | Existing package collision | Atomic rename checks existence; identical package is verified, conflicting is rejected. |
| 19 | Unknown future schema version | Schema version check fails with `IncompatibleReportSchemaError`. |
| 20 | Real holdout data access attempt | Reporting module contains zero holdout access APIs; gate remains `SEALED`. |

---

## 11. Proposed Package & Test Directory Structure

### Production Package (`goat/research/edge/reporting/`)
* `__init__.py`: Package exports (`ValidationReportBuilder`, `ReportIntegrityVerifier`, `ValidationEvidencePackage`).
* `exceptions.py`: Reporting taxonomy (`EdgeReportingError`, `ReportIntegrityError`, `IncompatibleReportSchemaError`, `SecurityViolationError`).
* `models.py`: Pydantic models for `ValidationReport`, `StageSummary`, `IntegrityProof`, `PackageManifest`.
* `identity.py`: Deterministic report ID generator (`compute_report_id`).
* `builder.py`: Report builder querying `SQLiteEdgeRepository` and constructing `ValidationReport`.
* `integrity.py`: Cryptographic package verifier (`ReportIntegrityVerifier`).
* `serializer.py`: Canonical JSON serializer and Markdown presentation renderer.
* `package.py`: Atomic filesystem package writer (`ValidationEvidencePackage`).

### Test Package (`tests/`)
* `test_edge_reporting_models.py`: Pydantic schema validation tests.
* `test_edge_reporting_identity.py`: Deterministic `RPT_<HEX16>` computation tests.
* `test_edge_reporting_builder.py`: Report builder query & assembly tests.
* `test_edge_reporting_integrity.py`: Adversarial integrity verification tests.
* `test_edge_reporting_package.py`: Atomic package filesystem writer tests.
* `test_edge_reporting_determinism.py`: Evidence sorting and order-invariance tests.
* `test_edge_reporting_failures.py`: Failed and insufficient edge reporting tests.
* `test_edge_reporting_security.py`: Path traversal and injection defense tests.
* `test_edge_reporting_holdout_isolation.py`: Zero holdout access verification tests.
