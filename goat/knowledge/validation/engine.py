"""
Project GOAT v0.9 — Edge Knowledge Graph Validation Engine
"""

from typing import Any

from goat.knowledge.core.canonical import compute_relationship_validation_id
from goat.knowledge.core.enums import ValidationStatus
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
    RelationshipValidation,
)


class ValidationEngine:
    """Quantitative Sub-Engine for Knowledge Graph Validation.

    Performs scientific integrity checks across the knowledge graph, detecting
    orphan nodes, broken scientific chains, missing evidence, circular cycles,
    and duplicate relationships.
    """

    def validate_graph(
        self,
        graph_id: str,
        nodes: list[KnowledgeNode],
        relationships: list[KnowledgeRelationship],
        timestamp_str: str = "2026-01-01T00:00:00Z",
        metadata: dict[str, Any] | None = None,
    ) -> RelationshipValidation:
        """Validate knowledge graph for structural and scientific integrity."""
        meta = dict(metadata or {})
        violations: list[str] = []

        node_map = {n.node_id: n for n in nodes}
        connected_node_ids: set[str] = set()

        # 1. Duplicate Relationships & Connected Node Tracking
        seen_rel_keys: set[tuple[str, str, str]] = set()
        duplicate_count = 0

        for r in relationships:
            connected_node_ids.add(r.source_node_id)
            connected_node_ids.add(r.target_node_id)

            rel_key = (r.source_node_id, r.target_node_id, r.relationship_type.value)
            if rel_key in seen_rel_keys:
                duplicate_count += 1
                violations.append(f"Duplicate relationship: {r.source_node_id} -> {r.target_node_id} ({r.relationship_type.value})")
            seen_rel_keys.add(rel_key)

        # 2. Orphan Nodes Detection
        orphan_count = 0
        for n in nodes:
            if n.node_id not in connected_node_ids:
                orphan_count += 1
                violations.append(f"Orphan node with zero relationships: {n.node_id} ({n.label})")

        # 3. Cycle Detection (DFS for back-edges)
        adj: dict[str, list[str]] = {}
        for r in relationships:
            adj.setdefault(r.source_node_id, []).append(r.target_node_id)

        cycle_count = 0
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def _dfs_cycle(curr: str):
            nonlocal cycle_count
            visited.add(curr)
            rec_stack.add(curr)

            for nxt in adj.get(curr, []):
                if nxt not in visited:
                    _dfs_cycle(nxt)
                elif nxt in rec_stack:
                    cycle_count += 1
                    violations.append(f"Circular dependency cycle detected containing node: {nxt}")

            rec_stack.remove(curr)

        for n in nodes:
            if n.node_id not in visited:
                _dfs_cycle(n.node_id)

        # 4. Broken Chains & Missing Evidence Detection
        broken_chain_count = 0
        for n in nodes:
            if n.node_type.value in ("DISCOVERED_EDGE", "GOVERNANCE_DECISION"):
                # Must have incoming relationships
                has_incoming = any(r.target_node_id == n.node_id for r in relationships)
                if not has_incoming:
                    broken_chain_count += 1
                    violations.append(f"Broken scientific chain: Entity {n.node_id} ({n.node_type.value}) lacks upstream lineage")

        # Overall Status
        if cycle_count > 0:
            status = ValidationStatus.CYCLE_DETECTED
            is_valid = False
        elif broken_chain_count > 0:
            status = ValidationStatus.BROKEN_CHAIN
            is_valid = False
        elif orphan_count > 0:
            status = ValidationStatus.ORPHAN_NODE
            is_valid = False
        elif duplicate_count > 0:
            status = ValidationStatus.DUPLICATE_RELATIONSHIP
            is_valid = False
        else:
            status = ValidationStatus.VALID
            is_valid = True

        val_id, v_hash = compute_relationship_validation_id(
            graph_id=graph_id,
            status=status.value,
            timestamp=timestamp_str,
        )

        return RelationshipValidation(
            validation_id=val_id,
            graph_id=graph_id,
            status=status,
            is_valid=is_valid,
            broken_chain_count=broken_chain_count,
            orphan_node_count=orphan_count,
            cycle_count=cycle_count,
            duplicate_count=duplicate_count,
            violations=violations,
            timestamp=timestamp_str,
            metadata=meta,
            canonical_hash=v_hash,
        )
