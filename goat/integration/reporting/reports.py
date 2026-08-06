"""
Project GOAT v0.7 — Knowledge Integration Reports

Provides immutable, deterministic report models and renderers:
- KnowledgeIntegrationReport
- ConflictReport
- KnowledgeGraphReport
- EvidenceMergeReport
- KnowledgeEvolutionReport
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from goat.integration.core.canonical import serialize_canonical_json
from goat.integration.core.models import ConflictRecord, IntegratedKnowledge
from goat.integration.evidence.models import EvidenceMergeRecord
from goat.integration.graph.engine import ScientificKnowledgeGraph
from goat.integration.versioning import KnowledgeStateVersion


class KnowledgeIntegrationReport(BaseModel):
    """Report summarizing a full scientific knowledge integration event."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    integrated_knowledge: IntegratedKnowledge = Field(..., description="Target IntegratedKnowledge model")
    node_count: int = Field(..., ge=0, description="Total nodes in updated graph")
    edge_count: int = Field(..., ge=0, description="Total edges in updated graph")
    conflict_count: int = Field(..., ge=0, description="Number of detected conflicts")
    evidence_merge_id: str = Field(default="", description="Associated EvidenceMergeRecord ID")
    version_id: str = Field(default="", description="Associated KnowledgeStateVersion ID")
    summary_notes: str = Field(default="", description="Narrative summary")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        """Render report as canonical JSON string."""
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        """Render report as structured Markdown string."""
        ik = self.integrated_knowledge
        lines = [
            f"# Scientific Knowledge Integration Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Integrated Knowledge ID**: `{ik.knowledge_id}`",
            f"- **Version**: `{ik.version}`",
            f"- **Overall Confidence**: `{ik.overall_confidence:.4f}`",
            f"- **Reproducibility**: `{ik.reproducibility:.4f}`",
            f"- **Consensus Strength**: `{ik.consensus_strength:.4f}`",
            f"- **Conflict Score**: `{ik.conflict_score:.4f}`",
            "",
            "## Graph Statistics",
            f"- **Nodes**: {self.node_count}",
            f"- **Edges**: {self.edge_count}",
            f"- **Conflicts Detected**: {self.conflict_count}",
            "",
            "## Provenance",
            f"- **Participating Validations**: {len(ik.participating_validations)}",
            f"- **Participating Hypotheses**: {len(ik.participating_hypotheses)}",
            f"- **Participating Experiments**: {len(ik.participating_experiments)}",
            f"- **Evidence Merge Record**: `{self.evidence_merge_id}`",
            f"- **State Version**: `{self.version_id}`",
            "",
            "## Summary Notes",
            self.summary_notes or "Knowledge integration completed deterministically.",
        ]
        return "\n".join(lines)


class ConflictReport(BaseModel):
    """Report detailing detected scientific conflicts and contradictions."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC creation timestamp")
    conflicts: list[ConflictRecord] = Field(default_factory=list, description="List of detected conflicts")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Conflict Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Conflicts**: {len(self.conflicts)}",
            "",
            "| Conflict ID | Validation A | Validation B | Type | Severity | Explanation |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for c in sorted(self.conflicts, key=lambda x: x.conflict_id):
            lines.append(
                f"| `{c.conflict_id}` | `{c.validation_a}` | `{c.validation_b}` | `{c.conflict_type}` | `{c.severity}` | {c.explanation} |"
            )
        return "\n".join(lines)


class KnowledgeGraphReport(BaseModel):
    """Report detailing structural state and relationships of ScientificKnowledgeGraph."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    total_nodes: int = Field(..., ge=0)
    total_edges: int = Field(..., ge=0)
    node_types_breakdown: dict[str, int] = Field(default_factory=dict)
    relationship_types_breakdown: dict[str, int] = Field(default_factory=dict)

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Scientific Knowledge Graph Report ({self.report_id})",
            "",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Nodes**: {self.total_nodes}",
            f"- **Total Edges**: {self.total_edges}",
            "",
            "## Node Types Breakdown",
        ]
        for k in sorted(self.node_types_breakdown.keys()):
            lines.append(f"- **{k}**: {self.node_types_breakdown[k]}")

        lines.extend(["", "## Relationship Types Breakdown"])
        for k in sorted(self.relationship_types_breakdown.keys()):
            lines.append(f"- **{k}**: {self.relationship_types_breakdown[k]}")

        return "\n".join(lines)


class EvidenceMergeReport(BaseModel):
    """Report summarizing evidence aggregation."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    merge_record: EvidenceMergeRecord = Field(..., description="Underlying EvidenceMergeRecord")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        mr = self.merge_record
        lines = [
            f"# Evidence Merge Report ({self.report_id})",
            "",
            f"- **Merge ID**: `{mr.merge_id}`",
            f"- **Target Knowledge ID**: `{mr.target_knowledge_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Accumulated Confidence**: `{mr.accumulated_confidence:.4f}`",
            f"- **Accumulated Reproducibility**: `{mr.accumulated_reproducibility:.4f}`",
            f"- **Accumulated Consensus**: `{mr.accumulated_consensus:.4f}`",
            "",
            "## References Summary",
            f"- **Source Evidence Artifacts**: {len(mr.source_evidence_ids)}",
            f"- **Experiments Referenced**: {len(mr.experiment_refs)}",
            f"- **Studies Referenced**: {len(mr.study_refs)}",
            f"- **Executions Referenced**: {len(mr.execution_refs)}",
            f"- **Features Referenced**: {len(mr.feature_refs)}",
        ]
        return "\n".join(lines)


class KnowledgeEvolutionReport(BaseModel):
    """Report summarizing knowledge evolution versions and history."""

    report_id: str = Field(..., description="Unique report identifier")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp")
    knowledge_id: str = Field(..., description="Target Integrated Knowledge ID")
    versions: list[KnowledgeStateVersion] = Field(default_factory=list, description="Version history snapshots")

    class Config:
        frozen = True
        extra = "forbid"

    def to_json(self) -> str:
        return serialize_canonical_json(self.dict())

    def to_markdown(self) -> str:
        lines = [
            f"# Knowledge Evolution Report ({self.report_id})",
            "",
            f"- **Target Knowledge ID**: `{self.knowledge_id}`",
            f"- **Timestamp**: `{self.timestamp}`",
            f"- **Total Versions Recorded**: {len(self.versions)}",
            "",
            "| Version ID | Version # | State Hash | Parent Version ID | Created Timestamp |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for v in sorted(self.versions, key=lambda x: x.version_number):
            lines.append(
                f"| `{v.version_id}` | {v.version_number} | `{v.state_hash[:16]}...` | `{v.parent_version_id or 'NONE'}` | `{v.timestamp}` |"
            )
        return "\n".join(lines)
