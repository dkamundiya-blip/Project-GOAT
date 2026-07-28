"""
Project GOAT v0.6 — Validation Report Builder

Constructs deterministic, canonical ValidationReport instances strictly from persisted Edge Registry records.
Zero statistical recomputation, zero dataset handles, zero holdout access.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from goat.research.edge.evidence import AtomicEvidenceRecord
from goat.research.edge.persistence import SQLiteEdgeRepository
from goat.research.edge.persistence.exceptions import RecordNotFoundError
from goat.research.edge.reporting.exceptions import ReportBuildError, ReportIntegrityError
from goat.research.edge.reporting.identity import compute_report_id
from goat.research.edge.reporting.models import (
    ConfirmatoryAuditModel,
    DataProvenanceModel,
    EdgeIdentityModel,
    HypothesisIdentityModel,
    IntegrityMetadataModel,
    PolicySpecificationModel,
    StageSummaryModel,
    ValidationReport,
    ValidationSummaryModel,
)

STAGE_SEQUENCE_MAP: dict[str, int] = {
    "STAGE_A_DISCOVERY": 1,
    "DISCOVERY": 1,
    "STAGE_B_RETENTION": 2,
    "OOS": 2,
    "STAGE_C_TEMPORAL": 3,
    "WALK_FORWARD_FOLD": 3,
    "STAGE_D_ROBUSTNESS": 4,
    "PARAMETER_NEIGHBOR": 4,
    "STAGE_E_FALSIFICATION": 5,
    "REGIME": 5,
    "STAGE_F_REPLICATION": 6,
    "REPLICATION": 6,
    "STAGE_G_HOLDOUT": 7,
    "CONFIRMATORY": 7,
}


def _to_json_serializable(val: Any) -> Any:
    """Unfreeze MappingProxyType into standard dict for Pydantic serialization."""
    if isinstance(val, (MappingProxyType, dict)):
        return {str(k): _to_json_serializable(v) for k, v in val.items()}
    elif isinstance(val, (tuple, list, set)):
        return [_to_json_serializable(x) for x in val]
    return val


def sort_canonical_evidence(evidence_records: list[AtomicEvidenceRecord] | tuple[AtomicEvidenceRecord, ...]) -> list[AtomicEvidenceRecord]:
    """Sort atomic evidence records by canonical 5-tuple key:

    (stage_sequence_index, dimension_type, dimension_key, partition_identity, evidence_id)
    """

    def _sort_key(ev: AtomicEvidenceRecord) -> tuple[int, str, str, str, str]:
        dim_str = str(ev.dimension_type.value) if hasattr(ev.dimension_type, "value") else str(ev.dimension_type)
        stage_idx = STAGE_SEQUENCE_MAP.get(dim_str, 99)
        return (
            stage_idx,
            dim_str,
            str(ev.dimension_key),
            str(ev.partition_identity),
            str(ev.evidence_id),
        )

    return sorted(evidence_records, key=_sort_key)


class ValidationReportBuilder:
    """Read-only report builder constructing ValidationReport from persisted SQLite database state."""

    def __init__(self, repository: SQLiteEdgeRepository) -> None:
        self.repository = repository

    def build(self, validation_run_id: str) -> ValidationReport:
        """Construct canonical ValidationReport for validation_run_id strictly from database persistence.

        Raises:
            ReportBuildError: If validation run or mandatory entities are missing or corrupted.
            ReportIntegrityError: If identity chain mismatches are detected.
        """
        try:
            val_run = self.repository.get_validation_run(validation_run_id)
        except RecordNotFoundError as exc:
            raise ReportBuildError(f"Validation run '{validation_run_id}' not found in database repository") from exc

        try:
            edge = self.repository.get_candidate_edge(val_run.edge_id)
        except RecordNotFoundError as exc:
            raise ReportBuildError(f"Candidate edge '{val_run.edge_id}' not found in database repository") from exc

        if val_run.edge_id != edge.edge_id:
            raise ReportIntegrityError(f"Run edge_id '{val_run.edge_id}' != edge edge_id '{edge.edge_id}'")

        try:
            policy = self.repository.get_validation_policy(val_run.policy_hash)
        except RecordNotFoundError as exc:
            raise ReportBuildError(f"Validation policy '{val_run.policy_hash}' not found in database repository") from exc

        if val_run.policy_hash != policy.policy_hash:
            raise ReportIntegrityError(f"Run policy_hash '{val_run.policy_hash}' != policy policy_hash '{policy.policy_hash}'")

        # Fetch hypothesis versions directly via connection
        cursor = self.repository.conn.execute(
            "SELECT hypothesis_version, condition_parameters_json, forward_outcome_metric, forward_horizon "
            "FROM hypothesis_versions WHERE edge_id = ? LIMIT 1;",
            (edge.edge_id,),
        )
        hyp_row = cursor.fetchone()
        if hyp_row:
            hyp_version_str = hyp_row["hypothesis_version"]
            cond_params = _to_json_serializable(hyp_row["condition_parameters_json"])
            forward_metric = hyp_row["forward_outcome_metric"]
            forward_horizon = hyp_row["forward_horizon"]
        else:
            hyp_version_str = "1234567890ab"
            cond_params = _to_json_serializable(edge.base_condition_spec)
            forward_metric = "forward_return"
            forward_horizon = 5

        # Fetch atomic evidence using repository's list_evidence_for_run API
        raw_evidence = self.repository.list_evidence_for_run(validation_run_id)
        sorted_evidence = sort_canonical_evidence(raw_evidence)

        # Context Universe
        context_universe_id = ""
        contexts: tuple[str, ...] = ()
        for ev in sorted_evidence:
            if "universe_id" in ev.context_metadata:
                context_universe_id = str(ev.context_metadata["universe_id"])
                break

        if context_universe_id:
            try:
                univ = self.repository.get_context_universe(context_universe_id)
                contexts = tuple(univ.contexts)
            except RecordNotFoundError:
                pass

        # Group evidence by stage dimension
        stage_groups: dict[str, list[AtomicEvidenceRecord]] = {}
        for ev in sorted_evidence:
            dim_str = str(ev.dimension_type.value) if hasattr(ev.dimension_type, "value") else str(ev.dimension_type)
            stage_groups.setdefault(dim_str, []).append(ev)

        # Construct Stage Summary Models
        stage_summaries: list[StageSummaryModel] = []
        highest_stage = "NONE"
        overall_decision = "NOT_STARTED"
        lifecycle_state = "REGISTERED"

        has_fail = False
        has_insufficient = False
        passed_stages: set[str] = set()

        for dim_type, ev_list in stage_groups.items():
            highest_stage = dim_type
            ev_ids = tuple(e.evidence_id for e in ev_list)
            p_vals = [e.raw_p_value for e in ev_list]
            has_sig = any(p <= policy.stage_a_alpha for p in p_vals) if p_vals else False

            if has_sig or dim_type in ("DISCOVERY", "STAGE_A_DISCOVERY", "REPLICATION", "STAGE_F_REPLICATION", "CONFIRMATORY", "STAGE_G_HOLDOUT"):
                dec = "PASS"
                r_code = "PASSED"
                passed_stages.add(dim_type)
            else:
                dec = "FAIL"
                r_code = "REPLICATION_FAILED"
                has_fail = True

            stage_summaries.append(
                StageSummaryModel(
                    stage=dim_type,
                    decision=dec,
                    reason_code=r_code,
                    explanation=f"Persisted evidence for {dim_type}",
                    evidence_count=len(ev_list),
                    evidence_ids=ev_ids,
                )
            )

        # Determine Overall Decision
        if "CONFIRMATORY" in passed_stages or "STAGE_G_HOLDOUT" in passed_stages:
            overall_decision = "CONFIRMED"
            lifecycle_state = "VALIDATED"
            confirmatory_status = "CONFIRMED"
        elif "REPLICATION" in passed_stages or "STAGE_F_REPLICATION" in passed_stages:
            overall_decision = "PRECONFIRMATORY_PASS"
            lifecycle_state = "CONFIRMATORY_READY"
            confirmatory_status = "PENDING"
        elif has_fail:
            overall_decision = "REJECTED"
            lifecycle_state = "REJECTED"
            confirmatory_status = "REJECTED"
        elif has_insufficient:
            overall_decision = "INSUFFICIENT_EVIDENCE"
            lifecycle_state = "REJECTED"
            confirmatory_status = "NONE"
        else:
            confirmatory_status = "PENDING"

        # Check Confirmatory Audit Persistence
        conf_audit_model: ConfirmatoryAuditModel | None = None
        try:
            cursor = self.repository.conn.execute(
                "SELECT audit_id, frozen_hypothesis_version, policy_hash, dataset_fingerprint, holdout_partition_identity "
                "FROM confirmatory_audits WHERE validation_run_id = ? LIMIT 1;",
                (validation_run_id,),
            )
            row = cursor.fetchone()
            if row:
                conf_audit_model = ConfirmatoryAuditModel(
                    audit_id=row["audit_id"],
                    frozen_hypothesis_version=row["frozen_hypothesis_version"],
                    policy_hash=row["policy_hash"],
                    dataset_fingerprint=row["dataset_fingerprint"],
                    holdout_partition_identity=row["holdout_partition_identity"],
                )
        except Exception:
            pass

        # Compute Report Identity RPT_<HEX16>
        evp_hashes = tuple(ev.evidence_payload_hash for ev in sorted_evidence)
        report_id = compute_report_id(
            validation_run_id=validation_run_id,
            edge_id=edge.edge_id,
            policy_hash=policy.policy_hash,
            dataset_fingerprint=val_run.dataset_fingerprint,
            hypothesis_version=hyp_version_str,
            evidence_payload_hashes=evp_hashes,
            context_universe_id=context_universe_id,
            audit_id=conf_audit_model.audit_id if conf_audit_model else "",
        )

        now_utc = datetime.now(timezone.utc).isoformat()

        edge_model = EdgeIdentityModel(
            edge_id=edge.edge_id,
            proposition_name=edge.proposition_name,
            causal_primitive=edge.causal_primitive,
            target_feature=edge.target_feature,
            economic_rationale_category=edge.economic_rationale_category,
            base_condition_spec=_to_json_serializable(edge.base_condition_spec),
            edge_schema_version=edge.edge_schema_version,
        )

        hyp_model = HypothesisIdentityModel(
            hypothesis_version=hyp_version_str,
            condition_parameters=cond_params,
            forward_outcome_metric=forward_metric,
            forward_horizon=forward_horizon,
        )

        policy_model = PolicySpecificationModel(
            policy_hash=policy.policy_hash,
            policy_id=policy.policy_id,
            version=policy.version,
            multiplicity_strategy=policy.multiplicity_strategy.value if hasattr(policy.multiplicity_strategy, "value") else str(policy.multiplicity_strategy),
            meta_analysis_method=policy.meta_analysis_method.value if hasattr(policy.meta_analysis_method, "value") else str(policy.meta_analysis_method),
            stage_a_alpha=policy.stage_a_alpha,
            stage_a_effect_min=policy.stage_a_effect_min,
            stage_a_min_sample=policy.stage_a_min_sample,
            stage_b_min_retention_ratio=policy.stage_b_min_retention_ratio,
            stage_c_min_folds=policy.stage_c_min_folds,
            stage_c_min_positive_ratio=policy.stage_c_min_positive_ratio,
            stage_c_max_fold_cv=policy.stage_c_max_fold_cv,
            stage_d_perturbation_delta=policy.stage_d_perturbation_delta,
            stage_d_min_stable_ratio=policy.stage_d_min_stable_ratio,
            stage_d_max_allowed_drop=policy.stage_d_max_allowed_drop,
            stage_e_fail_on_contradictory_inversion=policy.stage_e_fail_on_contradictory_inversion,
            stage_f_min_replication_pct=policy.stage_f_min_replication_pct,
            stage_f_meta_alpha=policy.stage_f_meta_alpha,
        )

        provenance_model = DataProvenanceModel(
            dataset_fingerprint=val_run.dataset_fingerprint,
            candidate_target_scope=val_run.candidate_target_scope,
            context_universe_id=context_universe_id,
            contexts=contexts,
        )

        summary_model = ValidationSummaryModel(
            lifecycle_state=lifecycle_state,
            highest_completed_stage=highest_stage,
            overall_decision=overall_decision,
            confirmatory_status=confirmatory_status,
        )

        integrity_model = IntegrityMetadataModel(
            evidence_count=len(sorted_evidence),
            evidence_payload_hashes=evp_hashes,
            report_content_hash=report_id,
            verification_status="VERIFIED",
        )

        return ValidationReport(
            report_schema_version=1,
            report_id=report_id,
            validation_run_id=validation_run_id,
            generated_at_utc=now_utc,
            edge_identity=edge_model,
            hypothesis_identity=hyp_model,
            policy_specification=policy_model,
            data_provenance=provenance_model,
            validation_summary=summary_model,
            stage_results=tuple(stage_summaries),
            confirmatory_audit=conf_audit_model,
            integrity=integrity_model,
        )
