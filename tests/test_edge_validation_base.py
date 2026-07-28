"""
Project GOAT v0.6 — BaseStageValidator Unit Tests
"""

from typing import Any

from goat.research.edge.definition import CandidateEdge
from goat.research.edge.evidence import EvidenceDimensionType
from goat.research.edge.models import ValidationRunInfo
from goat.research.edge.policy import ValidationPolicy
from goat.research.edge.validation.models import (
    ReasonCode,
    StageDecision,
    StageResult,
    ValidationStage,
)
from goat.research.edge.validation.stages.base import BaseStageValidator


class DummyStageValidator(BaseStageValidator):
    @property
    def stage(self) -> ValidationStage:
        return ValidationStage.STAGE_A_DISCOVERY

    @property
    def prerequisite_stage(self) -> ValidationStage | None:
        return None

    def evaluate(
        self,
        candidate_edge: CandidateEdge,
        hypothesis_version: str,
        policy: ValidationPolicy,
        validation_run: ValidationRunInfo,
        dataset_partitions: dict[str, Any],
        **kwargs: Any,
    ) -> StageResult:
        ev = self.create_evidence_record(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            dimension_type=EvidenceDimensionType.DISCOVERY,
            dimension_key="dummy_metric",
            partition_identity="train",
            sample_count=100,
            effect_size=0.25,
            raw_p_value=0.001,
            statistic_value=3.5,
        )
        return StageResult(
            validation_run_id=validation_run.validation_run_id,
            edge_id=candidate_edge.edge_id,
            stage=self.stage,
            decision=StageDecision.PASS,
            reason_code=ReasonCode.PASSED,
            evidence_ids=(ev.evidence_id,),
            policy_hash=policy.policy_hash,
        )


def test_base_stage_validator_contract():
    validator = DummyStageValidator()
    assert validator.stage == ValidationStage.STAGE_A_DISCOVERY
    assert validator.prerequisite_stage is None

    edge = CandidateEdge(
        proposition_name="Dummy Edge",
        causal_primitive="greater_than",
        target_feature="close",
        economic_rationale_category="momentum",
        base_condition_spec={"p": 1},
    )
    pol = ValidationPolicy(policy_id="P1")
    run = ValidationRunInfo(
        edge_id=edge.edge_id,
        policy_hash=pol.policy_hash,
        dataset_fingerprint="ds_fp",
        candidate_target_scope="UNIVERSAL",
    )

    res = validator.evaluate(
        candidate_edge=edge,
        hypothesis_version="123",
        policy=pol,
        validation_run=run,
        dataset_partitions={},
    )

    assert res.decision == StageDecision.PASS
    assert len(res.evidence_ids) == 1
    assert res.evidence_ids[0].startswith("EVD_")
