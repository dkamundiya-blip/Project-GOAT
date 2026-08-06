"""
Project GOAT v0.7 — Knowledge Graph Engine

Implements KnowledgeGraph for directed graph construction, cycle detection, topological sorting,
ancestor/descendant traversal, relationship querying, graph statistics, and deterministic graph hashing.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from goat.knowledge.enums import KnowledgeRelationshipType
from goat.knowledge.graph.edge import KnowledgeEdge, compute_knowledge_edge_id
from goat.knowledge.graph.node import KnowledgeNode, compute_knowledge_node_id
from goat.knowledge.model import KnowledgeObject
from goat.research.edge.canonical import compute_canonical_sha256


class CircularKnowledgeDependencyError(ValueError):
    """Raised when a circular dependency is detected in the Knowledge Graph."""
    pass


class KnowledgeGraphValidationError(ValueError):
    """Raised when Knowledge Graph validation fails (missing node, self edge, etc.)."""
    pass


class KnowledgeGraph:
    """Directed graph representing scientific knowledge relationships G_K = (V_K, E_K)."""

    def __init__(self) -> None:
        self._nodes: dict[str, KnowledgeNode] = {}  # knowledge_id -> KnowledgeNode
        self._edges: dict[tuple[str, str, str], KnowledgeEdge] = {}  # (parent, child, rel_type) -> KnowledgeEdge
        self._adj_out: dict[str, set[str]] = defaultdict(set)  # parent -> set of child IDs
        self._adj_in: dict[str, set[str]] = defaultdict(set)  # child -> set of parent IDs
        self._objects: dict[str, KnowledgeObject] = {}

    @property
    def nodes(self) -> dict[str, KnowledgeNode]:
        """Return node map (Knowledge ID -> KnowledgeNode)."""
        return dict(self._nodes)

    @property
    def edges(self) -> list[KnowledgeEdge]:
        """Return list of knowledge edges."""
        return list(self._edges.values())

    def add_node(self, node_or_obj: KnowledgeNode | KnowledgeObject) -> KnowledgeNode:
        """Add a Knowledge Node or Object to the graph.

        Args:
            node_or_obj: KnowledgeNode instance or KnowledgeObject.

        Returns:
            Added KnowledgeNode instance.
        """
        if isinstance(node_or_obj, KnowledgeObject):
            obj = node_or_obj
            kid = obj.knowledge_id
            if kid in self._nodes:
                raise KnowledgeGraphValidationError(f"Duplicate node registration detected for Knowledge ID '{kid}'")

            depth = self._calculate_depth(obj)
            node_id = compute_knowledge_node_id(kid, obj.scientific_fingerprint, depth)

            node = KnowledgeNode(
                node_id=node_id,
                knowledge_id=kid,
                scientific_fingerprint=obj.scientific_fingerprint,
                canonical_hash=obj.canonical_hash,
                knowledge_type=obj.knowledge_type.value,
                depth=depth,
                topological_index=0,
            )
            self._objects[kid] = obj
            parents = obj.parent_knowledge_ids
        elif isinstance(node_or_obj, KnowledgeNode):
            node = node_or_obj
            kid = node.knowledge_id
            if kid in self._nodes:
                raise KnowledgeGraphValidationError(f"Duplicate node registration detected for Knowledge ID '{kid}'")
            parents = []
        else:
            raise TypeError(f"Expected KnowledgeNode or KnowledgeObject, got '{type(node_or_obj).__name__}'")

        self._nodes[kid] = node

        # Process implicit parent dependency edges
        for pid in parents:
            if pid == kid:
                raise KnowledgeGraphValidationError(f"Self-edge detected on Knowledge Object '{kid}'")

            rel_type = KnowledgeRelationshipType.DEPENDS_ON.value
            edge_id, edge_hash = compute_knowledge_edge_id(pid, kid, rel_type)
            edge = KnowledgeEdge(
                edge_id=edge_id,
                parent_knowledge_id=pid,
                child_knowledge_id=kid,
                relationship_type=KnowledgeRelationshipType.DEPENDS_ON,
                edge_hash=edge_hash,
            )
            self.add_edge(edge)

        return node

    def add_edge(self, edge: KnowledgeEdge) -> None:
        """Add an explicit relationship edge to the Knowledge Graph.

        Args:
            edge: KnowledgeEdge instance.
        """
        pid = edge.parent_knowledge_id
        cid = edge.child_knowledge_id
        rel = edge.relationship_type.value

        if pid == cid:
            raise KnowledgeGraphValidationError(f"Self-edge relationship detected between parent '{pid}' and child '{cid}'")

        key = (pid, cid, rel)
        if key in self._edges:
            return  # Idempotent registration

        self._edges[key] = edge
        self._adj_out[pid].add(cid)
        self._adj_in[cid].add(pid)

    def _calculate_depth(self, obj: KnowledgeObject) -> int:
        """Calculate depth based on existing parent nodes."""
        if not obj.parent_knowledge_ids:
            return 0
        max_parent_depth = 0
        for pid in obj.parent_knowledge_ids:
            if pid in self._nodes:
                max_parent_depth = max(max_parent_depth, self._nodes[pid].depth + 1)
        return max_parent_depth

    def validate_graph(self) -> bool:
        """Validate Knowledge Graph integrity.

        Fail-closed rules:
        - All edges must reference existing parent and child nodes.
        - No self-edges.
        - No circular dependencies.
        """
        for (pid, cid, rel), edge in self._edges.items():
            if pid not in self._nodes:
                raise KnowledgeGraphValidationError(f"Edge references non-existent parent Knowledge node '{pid}'")
            if cid not in self._nodes:
                raise KnowledgeGraphValidationError(f"Edge references non-existent child Knowledge node '{cid}'")
            if pid == cid:
                raise KnowledgeGraphValidationError(f"Self-edge detected on Knowledge node '{pid}'")

        self._detect_cycles()
        return True

    def _detect_cycles(self) -> None:
        """Detect circular dependencies using 3-color DFS traversal."""
        visited: dict[str, int] = {kid: 0 for kid in self._nodes}

        def dfs(node: str, path: list[str]) -> None:
            visited[node] = 1
            path.append(node)

            for child in sorted(self._adj_out.get(node, set())):
                if visited[child] == 1:
                    cycle_str = " -> ".join(path[path.index(child):] + [child])
                    raise CircularKnowledgeDependencyError(f"Circular dependency detected in Knowledge Graph: {cycle_str}")
                elif visited[child] == 0:
                    dfs(child, path)

            path.pop()
            visited[node] = 2

        for kid in sorted(self._nodes.keys()):
            if visited[kid] == 0:
                dfs(kid, [])

    def topological_sort(self) -> list[str]:
        """Compute deterministic topological ordering of Knowledge IDs using Kahn's algorithm."""
        self.validate_graph()

        in_deg = {kid: len(self._adj_in.get(kid, set())) for kid in self._nodes}
        zero_in = sorted([kid for kid, deg in in_deg.items() if deg == 0])

        result: list[str] = []
        queue = deque(zero_in)

        while queue:
            node = queue.popleft()
            result.append(node)

            for child in sorted(self._adj_out.get(node, set())):
                in_deg[child] -= 1
                if in_deg[child] == 0:
                    queue.append(child)

        if len(result) != len(self._nodes):
            raise CircularKnowledgeDependencyError("Knowledge Graph contains hidden circular dependency")

        return result

    def get_ancestors(self, knowledge_id: str) -> list[str]:
        """Retrieve recursive list of all upstream ancestor Knowledge IDs."""
        ancestors: set[str] = set()
        visited: set[str] = set()

        def dfs(curr: str) -> None:
            visited.add(curr)
            for parent in self._adj_in.get(curr, set()):
                ancestors.add(parent)
                if parent not in visited:
                    dfs(parent)

        dfs(knowledge_id)
        return sorted(ancestors)

    def get_descendants(self, knowledge_id: str) -> list[str]:
        """Retrieve recursive list of all downstream descendant Knowledge IDs."""
        descendants: set[str] = set()
        visited: set[str] = set()

        def dfs(curr: str) -> None:
            visited.add(curr)
            for child in self._adj_out.get(curr, set()):
                descendants.add(child)
                if child not in visited:
                    dfs(child)

        dfs(knowledge_id)
        return sorted(descendants)

    def query_relationships(
        self, relationship_type: KnowledgeRelationshipType | None = None
    ) -> list[KnowledgeEdge]:
        """Query relationship edges filtered optionally by relationship type."""
        if relationship_type is None:
            return list(self._edges.values())
        return [e for e in self._edges.values() if e.relationship_type == relationship_type]

    def get_graph_statistics(self) -> dict[str, Any]:
        """Compute structural statistics of Knowledge Graph."""
        top_order = self.topological_sort()
        node_count = len(self._nodes)
        edge_count = len(self._edges)

        roots = [kid for kid in self._nodes if len(self._adj_in.get(kid, set())) == 0]
        leaves = [kid for kid in self._nodes if len(self._adj_out.get(kid, set())) == 0]
        max_depth = max([n.depth for n in self._nodes.values()], default=0)

        rel_counts: dict[str, int] = defaultdict(int)
        for e in self._edges.values():
            rel_counts[e.relationship_type.value] += 1

        return {
            "edge_count": edge_count,
            "graph_hash": self.compute_knowledge_graph_hash(),
            "leaf_count": len(leaves),
            "max_depth": max_depth,
            "node_count": node_count,
            "relationship_counts": dict(rel_counts),
            "root_count": len(roots),
        }

    def compute_knowledge_graph_hash(self) -> str:
        """Compute deterministic SHA-256 hash digest of Knowledge Graph topology."""
        top_order = self.topological_sort()

        edges_list = []
        for (pid, cid, rel), edge in sorted(self._edges.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
            edges_list.append({
                "child": cid,
                "edge_hash": edge.edge_hash,
                "edge_id": edge.edge_id,
                "parent": pid,
                "relationship": rel,
            })

        nodes_list = []
        for kid in top_order:
            node = self._nodes[kid]
            nodes_list.append({
                "knowledge_id": kid,
                "node_id": node.node_id,
                "scientific_fingerprint": node.scientific_fingerprint,
                "type": node.knowledge_type,
            })

        payload = {
            "edges": edges_list,
            "nodes": nodes_list,
            "topological_order": top_order,
        }

        return compute_canonical_sha256(payload)

    def export_graph(self) -> dict[str, Any]:
        """Export Knowledge Graph topological structure as a dictionary."""
        top_order = self.topological_sort()
        return {
            "edge_count": len(self._edges),
            "edges": [e.model_dump(mode="json") for e in sorted(self._edges.values(), key=lambda e: e.edge_id)],
            "graph_hash": self.compute_knowledge_graph_hash(),
            "graph_statistics": self.get_graph_statistics(),
            "node_count": len(self._nodes),
            "nodes": [self._nodes[kid].model_dump(mode="json") for kid in top_order],
            "topological_order": top_order,
        }
