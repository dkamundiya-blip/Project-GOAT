"""
Project GOAT v0.6 — SQLite Persistence Repository Implementation

Implements relational storage, transaction isolation, append-only evidence guarantees,
and deterministic query retrieval according to SPEC.3 architecture.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import sqlite3
from typing import Any, Generator

from goat.research.edge.canonical import canonical_json, freeze_structure
from goat.research.edge.definition import CandidateEdge, compute_hypothesis_version
from goat.research.edge.enums import EdgeLifecycleStatus, EdgeScope, EvidenceDimensionType, MetaAnalysisMethod, MultiplicityStrategy
from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.models import (
    ValidationContextUniverse,
    ValidationRunInfo,
    compute_confirmatory_audit_id,
)
from goat.research.edge.persistence.exceptions import (
    EdgePersistenceError,
    EvidenceConflictError,
    IdentityConflictError,
    PersistenceIntegrityError,
    RecordNotFoundError,
)
from goat.research.edge.persistence.schema import initialize_database
from goat.research.edge.policy import ValidationPolicy


class SQLiteEdgeRepository:
    """Production-grade SQLite persistence layer for Project GOAT v0.6 research artifacts."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        initialize_database(self.conn)

    def __enter__(self) -> SQLiteEdgeRepository:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close SQLite database connection cleanly."""
        if self.conn:
            self.conn.close()

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager enforcing ACID transaction isolation and rollback on error."""
        try:
            yield self.conn
            self.conn.commit()
        except EdgePersistenceError:
            self.conn.rollback()
            raise
        except Exception as exc:
            self.conn.rollback()
            raise PersistenceIntegrityError(f"Transaction rolled back due to failure: {exc}") from exc

    # -------------------------------------------------------------------------
    # Candidate Edge Persistence
    # -------------------------------------------------------------------------

    def save_candidate_edge(self, edge: CandidateEdge) -> CandidateEdge:
        """Save CandidateEdge. Idempotent for identical payload; updates metadata if unchanged ID."""
        now_iso = datetime.now(timezone.utc).isoformat()
        base_cond_json = canonical_json(edge.base_condition_spec)
        labels_json = canonical_json(edge.display_labels)
        hypotheses_json = canonical_json(edge.hypothesis_ids)

        with self.transaction() as conn:
            cursor = conn.execute(
                "SELECT edge_id, edge_schema_version, causal_primitive, target_feature, "
                "economic_rationale_category, base_condition_spec_json FROM candidate_edges WHERE edge_id = ?;",
                (edge.edge_id,),
            )
            existing = cursor.fetchone()

            if existing:
                # Check identity payload equivalence
                if (
                    existing["edge_schema_version"] != edge.edge_schema_version
                    or existing["causal_primitive"] != edge.causal_primitive.lower()
                    or existing["target_feature"] != edge.target_feature.lower()
                    or existing["economic_rationale_category"] != edge.economic_rationale_category.lower()
                    or existing["base_condition_spec_json"] != base_cond_json
                ):
                    raise IdentityConflictError(
                        f"Cannot overwrite CandidateEdge '{edge.edge_id}' with non-identical statistical identity payload"
                    )

                # Update metadata fields
                conn.execute(
                    """
                    UPDATE candidate_edges SET
                        proposition_name = ?, description = ?, notes = ?,
                        display_labels_json = ?, hypothesis_ids_json = ?, lifecycle_state = ?, updated_at_utc = ?
                    WHERE edge_id = ?;
                    """,
                    (
                        edge.proposition_name,
                        edge.description,
                        edge.notes,
                        labels_json,
                        hypotheses_json,
                        edge.lifecycle_state.value,
                        now_iso,
                        edge.edge_id,
                    ),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO candidate_edges (
                        edge_id, edge_schema_version, causal_primitive, target_feature,
                        economic_rationale_category, base_condition_spec_json, proposition_name,
                        description, notes, display_labels_json, hypothesis_ids_json,
                        lifecycle_state, created_at_utc, updated_at_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        edge.edge_id,
                        edge.edge_schema_version,
                        edge.causal_primitive.lower(),
                        edge.target_feature.lower(),
                        edge.economic_rationale_category.lower(),
                        base_cond_json,
                        edge.proposition_name,
                        edge.description,
                        edge.notes,
                        labels_json,
                        hypotheses_json,
                        edge.lifecycle_state.value,
                        now_iso,
                        now_iso,
                    ),
                )

        return self.get_candidate_edge(edge.edge_id)

    def get_candidate_edge(self, edge_id: str) -> CandidateEdge:
        """Retrieve CandidateEdge by edge_id."""
        cursor = self.conn.execute("SELECT * FROM candidate_edges WHERE edge_id = ?;", (edge_id,))
        row = cursor.fetchone()
        if not row:
            raise RecordNotFoundError(f"CandidateEdge '{edge_id}' not found")

        return CandidateEdge(
            edge_id=row["edge_id"],
            edge_schema_version=row["edge_schema_version"],
            causal_primitive=row["causal_primitive"],
            target_feature=row["target_feature"],
            economic_rationale_category=row["economic_rationale_category"],
            base_condition_spec=json.loads(row["base_condition_spec_json"]),
            proposition_name=row["proposition_name"],
            description=row["description"],
            notes=row["notes"],
            display_labels=tuple(json.loads(row["display_labels_json"])),
            hypothesis_ids=tuple(json.loads(row["hypothesis_ids_json"])),
            lifecycle_state=EdgeLifecycleStatus(row["lifecycle_state"]),
        )

    # -------------------------------------------------------------------------
    # Hypothesis Version Persistence
    # -------------------------------------------------------------------------

    def save_hypothesis_version(
        self,
        edge_id: str,
        condition_parameters: dict[str, Any],
        forward_outcome_metric: str,
        forward_horizon: int,
    ) -> str:
        """Save parameterization hypothesis version string (12 hex chars). Returns hypothesis_version."""
        version_hash = compute_hypothesis_version(
            edge_id=edge_id,
            condition_parameters=condition_parameters,
            forward_outcome_metric=forward_outcome_metric,
            forward_horizon=forward_horizon,
        )
        params_json = canonical_json(condition_parameters)
        now_iso = datetime.now(timezone.utc).isoformat()

        with self.transaction() as conn:
            cursor = conn.execute(
                "SELECT hypothesis_version FROM hypothesis_versions WHERE hypothesis_version = ?;",
                (version_hash,),
            )
            if cursor.fetchone():
                return version_hash

            conn.execute(
                """
                INSERT INTO hypothesis_versions (
                    hypothesis_version, edge_id, condition_parameters_json,
                    forward_outcome_metric, forward_horizon, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    version_hash,
                    edge_id,
                    params_json,
                    forward_outcome_metric,
                    forward_horizon,
                    now_iso,
                ),
            )
        return version_hash

    def get_hypothesis_version(self, hypothesis_version: str) -> dict[str, Any]:
        """Retrieve hypothesis version details by hypothesis_version string."""
        cursor = self.conn.execute(
            "SELECT * FROM hypothesis_versions WHERE hypothesis_version = ?;", (hypothesis_version,)
        )
        row = cursor.fetchone()
        if not row:
            raise RecordNotFoundError(f"HypothesisVersion '{hypothesis_version}' not found")

        return {
            "hypothesis_version": row["hypothesis_version"],
            "edge_id": row["edge_id"],
            "condition_parameters": json.loads(row["condition_parameters_json"]),
            "forward_outcome_metric": row["forward_outcome_metric"],
            "forward_horizon": row["forward_horizon"],
            "created_at_utc": row["created_at_utc"],
        }

    # -------------------------------------------------------------------------
    # Validation Policy Persistence
    # -------------------------------------------------------------------------

    def save_validation_policy(self, policy: ValidationPolicy) -> ValidationPolicy:
        """Save ValidationPolicy. Idempotent for policy_hash."""
        now_iso = datetime.now(timezone.utc).isoformat()

        with self.transaction() as conn:
            cursor = conn.execute(
                "SELECT policy_hash FROM validation_policies WHERE policy_hash = ?;",
                (policy.policy_hash,),
            )
            if cursor.fetchone():
                return policy

            conn.execute(
                """
                INSERT INTO validation_policies (
                    policy_hash, policy_id, version, description, multiplicity_strategy, meta_analysis_method,
                    stage_a_alpha, stage_a_effect_min, stage_a_min_sample,
                    stage_b_min_retention_ratio, stage_c_min_folds, stage_c_min_positive_ratio,
                    stage_c_max_fold_cv, stage_d_perturbation_delta, stage_d_min_stable_ratio,
                    stage_d_max_allowed_drop, stage_e_fail_on_contradictory_inversion,
                    stage_f_min_replication_pct, stage_f_meta_alpha, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    policy.policy_hash,
                    policy.policy_id,
                    policy.version,
                    policy.description,
                    policy.multiplicity_strategy.value,
                    policy.meta_analysis_method.value,
                    policy.stage_a_alpha,
                    policy.stage_a_effect_min,
                    policy.stage_a_min_sample,
                    policy.stage_b_min_retention_ratio,
                    policy.stage_c_min_folds,
                    policy.stage_c_min_positive_ratio,
                    policy.stage_c_max_fold_cv,
                    policy.stage_d_perturbation_delta,
                    policy.stage_d_min_stable_ratio,
                    policy.stage_d_max_allowed_drop,
                    1 if policy.stage_e_fail_on_contradictory_inversion else 0,
                    policy.stage_f_min_replication_pct,
                    policy.stage_f_meta_alpha,
                    now_iso,
                ),
            )
        return policy

    def get_validation_policy(self, policy_hash: str) -> ValidationPolicy:
        """Retrieve ValidationPolicy by policy_hash."""
        cursor = self.conn.execute(
            "SELECT * FROM validation_policies WHERE policy_hash = ?;", (policy_hash,)
        )
        row = cursor.fetchone()
        if not row:
            raise RecordNotFoundError(f"ValidationPolicy '{policy_hash}' not found")

        meta_method = row["meta_analysis_method"] if "meta_analysis_method" in row.keys() else "FISHER_COMBINED_PROBABILITY"

        return ValidationPolicy(
            policy_hash=row["policy_hash"],
            policy_id=row["policy_id"],
            version=row["version"],
            description=row["description"],
            multiplicity_strategy=MultiplicityStrategy(row["multiplicity_strategy"]),
            meta_analysis_method=MetaAnalysisMethod(meta_method),
            stage_a_alpha=row["stage_a_alpha"],
            stage_a_effect_min=row["stage_a_effect_min"],
            stage_a_min_sample=row["stage_a_min_sample"],
            stage_b_min_retention_ratio=row["stage_b_min_retention_ratio"],
            stage_c_min_folds=row["stage_c_min_folds"],
            stage_c_min_positive_ratio=row["stage_c_min_positive_ratio"],
            stage_c_max_fold_cv=row["stage_c_max_fold_cv"],
            stage_d_perturbation_delta=row["stage_d_perturbation_delta"],
            stage_d_min_stable_ratio=row["stage_d_min_stable_ratio"],
            stage_d_max_allowed_drop=row["stage_d_max_allowed_drop"],
            stage_e_fail_on_contradictory_inversion=bool(row["stage_e_fail_on_contradictory_inversion"]),
            stage_f_min_replication_pct=row["stage_f_min_replication_pct"],
            stage_f_meta_alpha=row["stage_f_meta_alpha"],
        )

    # -------------------------------------------------------------------------
    # Context Universe Persistence
    # -------------------------------------------------------------------------

    def save_context_universe(self, universe: ValidationContextUniverse) -> ValidationContextUniverse:
        """Save ValidationContextUniverse. Idempotent for universe_id."""
        now_iso = datetime.now(timezone.utc).isoformat()
        contexts_json = canonical_json(universe.contexts)

        with self.transaction() as conn:
            cursor = conn.execute(
                "SELECT universe_id FROM validation_context_universes WHERE universe_id = ?;",
                (universe.universe_id,),
            )
            if cursor.fetchone():
                return universe

            conn.execute(
                """
                INSERT INTO validation_context_universes (
                    universe_id, universe_schema_version, contexts_json, description, created_at_utc
                ) VALUES (?, ?, ?, ?, ?);
                """,
                (
                    universe.universe_id,
                    universe.universe_schema_version,
                    contexts_json,
                    universe.description,
                    now_iso,
                ),
            )
        return universe

    def get_context_universe(self, universe_id: str) -> ValidationContextUniverse:
        """Retrieve ValidationContextUniverse by universe_id."""
        cursor = self.conn.execute(
            "SELECT * FROM validation_context_universes WHERE universe_id = ?;", (universe_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise RecordNotFoundError(f"ValidationContextUniverse '{universe_id}' not found")

        return ValidationContextUniverse(
            universe_id=row["universe_id"],
            universe_schema_version=row["universe_schema_version"],
            contexts=tuple(json.loads(row["contexts_json"])),
            description=row["description"],
        )

    # -------------------------------------------------------------------------
    # Validation Run Persistence
    # -------------------------------------------------------------------------

    def save_validation_run(self, run: ValidationRunInfo) -> ValidationRunInfo:
        """Save ValidationRunInfo. Idempotent for validation_run_id."""
        with self.transaction() as conn:
            cursor = conn.execute(
                "SELECT validation_run_id FROM validation_runs WHERE validation_run_id = ?;",
                (run.validation_run_id,),
            )
            if cursor.fetchone():
                return run

            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """
                INSERT INTO validation_runs (
                    validation_run_id, edge_id, policy_hash, dataset_fingerprint,
                    candidate_target_scope, goat_version, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run.validation_run_id,
                    run.edge_id,
                    run.policy_hash,
                    run.dataset_fingerprint,
                    run.candidate_target_scope.value,
                    run.goat_version,
                    now_iso,
                ),
            )
        return run

    def get_validation_run(self, validation_run_id: str) -> ValidationRunInfo:
        """Retrieve ValidationRunInfo by validation_run_id."""
        cursor = self.conn.execute(
            "SELECT * FROM validation_runs WHERE validation_run_id = ?;", (validation_run_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise RecordNotFoundError(f"ValidationRunInfo '{validation_run_id}' not found")

        return ValidationRunInfo(
            validation_run_id=row["validation_run_id"],
            edge_id=row["edge_id"],
            policy_hash=row["policy_hash"],
            dataset_fingerprint=row["dataset_fingerprint"],
            candidate_target_scope=EdgeScope(row["candidate_target_scope"]),
            goat_version=row["goat_version"],
        )

    # -------------------------------------------------------------------------
    # Atomic Evidence Record Persistence
    # -------------------------------------------------------------------------

    def save_evidence_record(self, record: AtomicEvidenceRecord) -> AtomicEvidenceRecord:
        """Save AtomicEvidenceRecord according to SPEC.3 append-only & conflict rules."""
        now_iso = datetime.now(timezone.utc).isoformat()
        ci_json = canonical_json(record.confidence_interval) if record.confidence_interval is not None else None
        meta_json = canonical_json(record.context_metadata)

        with self.transaction() as conn:
            cursor = conn.execute(
                "SELECT evidence_id, evidence_payload_hash FROM atomic_evidence WHERE evidence_id = ?;",
                (record.evidence_id,),
            )
            existing = cursor.fetchone()

            if existing:
                # Append-only Conflict Rule: If evidence_id exists, evidence_payload_hash MUST be identical!
                if existing["evidence_payload_hash"] != record.evidence_payload_hash:
                    raise EvidenceConflictError(
                        f"Append-only evidence conflict for evidence_id '{record.evidence_id}': "
                        f"existing payload hash '{existing['evidence_payload_hash']}' != new payload hash '{record.evidence_payload_hash}'"
                    )
                return record

            conn.execute(
                """
                INSERT INTO atomic_evidence (
                    evidence_id, evidence_payload_hash, validation_run_id, edge_id,
                    dimension_type, dimension_key, partition_identity, sample_count,
                    effect_size, effect_size_type, raw_p_value, adjusted_q_value,
                    statistic_value, confidence_interval_json, context_metadata_json, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    record.evidence_id,
                    record.evidence_payload_hash,
                    record.validation_run_id,
                    record.edge_id,
                    record.dimension_type.value,
                    record.dimension_key,
                    record.partition_identity,
                    record.sample_count,
                    record.effect_size,
                    record.effect_size_type,
                    record.raw_p_value,
                    record.adjusted_q_value,
                    record.statistic_value,
                    ci_json,
                    meta_json,
                    now_iso,
                ),
            )

        return record

    def save_evidence(self, record: AtomicEvidenceRecord) -> AtomicEvidenceRecord:
        return self.save_evidence_record(record)

    def get_evidence_record(self, evidence_id: str) -> AtomicEvidenceRecord:
        """Retrieve AtomicEvidenceRecord by evidence_id."""
        cursor = self.conn.execute("SELECT * FROM atomic_evidence WHERE evidence_id = ?;", (evidence_id,))
        row = cursor.fetchone()
        if not row:
            raise RecordNotFoundError(f"AtomicEvidenceRecord '{evidence_id}' not found")

        ci_val = json.loads(row["confidence_interval_json"]) if row["confidence_interval_json"] else None
        meta_val = json.loads(row["context_metadata_json"])

        return AtomicEvidenceRecord(
            evidence_id=row["evidence_id"],
            evidence_payload_hash=row["evidence_payload_hash"],
            validation_run_id=row["validation_run_id"],
            edge_id=row["edge_id"],
            dimension_type=EvidenceDimensionType(row["dimension_type"]),
            dimension_key=row["dimension_key"],
            partition_identity=row["partition_identity"],
            sample_count=row["sample_count"],
            effect_size=row["effect_size"],
            effect_size_type=row["effect_size_type"],
            raw_p_value=row["raw_p_value"],
            adjusted_q_value=row["adjusted_q_value"],
            statistic_value=row["statistic_value"],
            confidence_interval=ci_val,
            context_metadata=meta_val,
        )

    def get_evidence(self, evidence_id: str) -> AtomicEvidenceRecord:
        return self.get_evidence_record(evidence_id)

    def list_evidence_for_run(self, validation_run_id: str) -> list[AtomicEvidenceRecord]:
        """Retrieve all AtomicEvidenceRecord instances for a validation_run_id."""
        cursor = self.conn.execute(
            "SELECT * FROM atomic_evidence WHERE validation_run_id = ? ORDER BY created_at_utc ASC;",
            (validation_run_id,),
        )
        rows = cursor.fetchall()
        records: list[AtomicEvidenceRecord] = []
        for row in rows:
            ci_val = json.loads(row["confidence_interval_json"]) if row["confidence_interval_json"] else None
            meta_val = json.loads(row["context_metadata_json"])
            records.append(
                AtomicEvidenceRecord(
                    evidence_id=row["evidence_id"],
                    evidence_payload_hash=row["evidence_payload_hash"],
                    validation_run_id=row["validation_run_id"],
                    edge_id=row["edge_id"],
                    dimension_type=EvidenceDimensionType(row["dimension_type"]),
                    dimension_key=row["dimension_key"],
                    partition_identity=row["partition_identity"],
                    sample_count=row["sample_count"],
                    effect_size=row["effect_size"],
                    effect_size_type=row["effect_size_type"],
                    raw_p_value=row["raw_p_value"],
                    adjusted_q_value=row["adjusted_q_value"],
                    statistic_value=row["statistic_value"],
                    confidence_interval=ci_val,
                    context_metadata=meta_val,
                )
            )
        return records

    # -------------------------------------------------------------------------
    # Confirmatory Audit Identity Persistence
    # -------------------------------------------------------------------------

    def save_confirmatory_audit(
        self,
        validation_run_id: str,
        frozen_hypothesis_version: str,
        dataset_fingerprint: str,
        policy_hash: str,
        holdout_partition_identity: str = "holdout_sealed_v1",
    ) -> str:
        """Save ConfirmatoryAudit metadata. Returns audit_id (AUD_<HEX16>)."""
        audit_id = compute_confirmatory_audit_id(
            validation_run_id=validation_run_id,
            frozen_hypothesis_version=frozen_hypothesis_version,
            dataset_fingerprint=dataset_fingerprint,
            policy_hash=policy_hash,
            holdout_partition_identity=holdout_partition_identity,
        )
        now_iso = datetime.now(timezone.utc).isoformat()

        with self.transaction() as conn:
            cursor = conn.execute(
                "SELECT audit_id FROM confirmatory_audits WHERE audit_id = ?;", (audit_id,)
            )
            if cursor.fetchone():
                return audit_id

            conn.execute(
                """
                INSERT INTO confirmatory_audits (
                    audit_id, validation_run_id, frozen_hypothesis_version,
                    dataset_fingerprint, policy_hash, holdout_partition_identity, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    audit_id,
                    validation_run_id,
                    frozen_hypothesis_version,
                    dataset_fingerprint,
                    policy_hash,
                    holdout_partition_identity,
                    now_iso,
                ),
            )
        return audit_id

    def get_confirmatory_audit(self, audit_id: str) -> dict[str, Any]:
        """Retrieve ConfirmatoryAudit metadata by audit_id."""
        cursor = self.conn.execute(
            "SELECT * FROM confirmatory_audits WHERE audit_id = ?;", (audit_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise RecordNotFoundError(f"ConfirmatoryAudit '{audit_id}' not found")

        return {
            "audit_id": row["audit_id"],
            "validation_run_id": row["validation_run_id"],
            "frozen_hypothesis_version": row["frozen_hypothesis_version"],
            "dataset_fingerprint": row["dataset_fingerprint"],
            "policy_hash": row["policy_hash"],
            "holdout_partition_identity": row["holdout_partition_identity"],
            "created_at_utc": row["created_at_utc"],
        }
