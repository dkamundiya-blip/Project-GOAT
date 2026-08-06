"""
Project GOAT v0.9 — Edge Knowledge Graph Traversal Engine
"""

from typing import Any

from goat.knowledge.core.canonical import compute_scientific_path_id
from goat.knowledge.core.enums import PathValidity
from goat.knowledge.core.models import (
    KnowledgeGraph,
    KnowledgeNode,
    KnowledgeRelationship,
    ScientificPath,
)


class TraversalEngine:
    """Quantitative Sub-Engine for Deterministic Graph Traversal.

    Executes deterministic path-finding, lineage tracing, and ancestor/descendant
    extraction across the scientific knowledge graph.
    """

    def find_paths(
        self,
        nodes: list[KnowledgeNode],
        relationships: list[KnowledgeRelationship],
        source_node_id: str,
        target_node_id: str,
        max_depth: int = 10,
        metadata: dict[str, Any] | None = None,
    ) -> list[ScientificPath]:
        """Find all deterministic paths between source_node_id and target_node_id."""
        meta = dict(metadata or {})
        node_map = {n.node_id: n for n in nodes}

        if source_node_id not in node_map or target_node_id not in node_map:
            return []

        # Adjacency list: node_id -> list of (target_node_id, relationship_id)
        adj: dict[str, list[tuple[str, str]]] = {}
        for r in relationships:
            adj.setdefault(r.source_node_id, []).append((r.target_node_id, r.relationship_id))

        paths: list[ScientificPath] = []

        def _dfs(current: str, visited: set[str], path_nodes: list[str], path_rels: list[str]):
            if len(path_nodes) > max_depth:
                return
            if current == target_node_id:
                p_id, p_hash = compute_scientific_path_id(
                    source_node_id=source_node_id,
                    target_node_id=target_node_id,
                    node_chain=path_nodes,
                )
                validity = (
                    PathValidity.VALID_SCIENTIFIC_CHAIN
                    if len(path_nodes) >= 2
                    else PathValidity.INCOMPLETE_CHAIN
                )
                paths.append(
                    ScientificPath(
                        path_id=p_id,
                        source_node_id=source_node_id,
                        target_node_id=target_node_id,
                        node_chain=list(path_nodes),
                        relationship_chain=list(path_rels),
                        validity=validity,
                        path_length=len(path_nodes) - 1,
                        metadata=meta,
                        canonical_hash=p_hash,
                    )
                )
                return

            for nxt_node, rel_id in adj.get(current, []):
                if nxt_node not in visited:
                    visited.add(nxt_node)
                    path_nodes.append(nxt_node)
                    path_rels.append(rel_id)

                    _dfs(nxt_node, visited, path_nodes, path_rels)

                    path_nodes.pop()
                    path_rels.pop()
                    visited.remove(nxt_node)

        _dfs(source_node_id, {source_node_id}, [source_node_id], [])

        # Sort paths deterministically by length and node_chain
        paths.sort(key=lambda p: (p.path_length, "".join(p.node_chain)))
        return paths

    def get_ancestors(
        self,
        nodes: list[KnowledgeNode],
        relationships: list[KnowledgeRelationship],
        node_id: str,
    ) -> list[KnowledgeNode]:
        """Extract all ancestor nodes leading into node_id."""
        node_map = {n.node_id: n for n in nodes}
        if node_id not in node_map:
            return []

        # Reverse adjacency list: target -> sources
        rev_adj: dict[str, list[str]] = {}
        for r in relationships:
            rev_adj.setdefault(r.target_node_id, []).append(r.source_node_id)

        ancestors: set[str] = set()
        queue = [node_id]

        while queue:
            curr = queue.pop(0)
            for parent in rev_adj.get(curr, []):
                if parent not in ancestors:
                    ancestors.add(parent)
                    queue.append(parent)

        return [node_map[nid] for nid in sorted(list(ancestors)) if nid in node_map]

    def get_descendants(
        self,
        nodes: list[KnowledgeNode],
        relationships: list[KnowledgeRelationship],
        node_id: str,
    ) -> list[KnowledgeNode]:
        """Extract all descendant nodes originating from node_id."""
        node_map = {n.node_id: n for n in nodes}
        if node_id not in node_map:
            return []

        adj: dict[str, list[str]] = {}
        for r in relationships:
            adj.setdefault(r.source_node_id, []).append(r.target_node_id)

        descendants: set[str] = set()
        queue = [node_id]

        while queue:
            curr = queue.pop(0)
            for child in adj.get(curr, []):
                if child not in descendants:
                    descendants.add(child)
                    queue.append(child)

        return [node_map[nid] for nid in sorted(list(descendants)) if nid in node_map]
