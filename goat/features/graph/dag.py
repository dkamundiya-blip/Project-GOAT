"""
Project GOAT v0.7 — Feature Dependency Graph (DAG Engine)

Implements FeatureDependencyGraph for directed acyclic graph construction using explicit GraphNode
and GraphEdge models, static DFS cycle detection, topological sorting, graph validation,
recursive ancestor/descendant traversal, and deterministic graph hashing.
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from typing import Any

from goat.features.graph.edge import GraphEdge, compute_edge_id
from goat.features.graph.node import GraphNode, compute_node_id
from goat.features.registry.model import RegistryRecord
from goat.research.edge.canonical import compute_canonical_sha256


class CircularDependencyError(ValueError):
    """Raised when a circular dependency is detected in the feature graph."""
    pass


class GraphValidationError(ValueError):
    """Raised when dependency graph validation fails (missing node, self dependency, etc.)."""
    pass


class FeatureDependencyGraph:
    """Directed Acyclic Graph (DAG) representing feature dependency relationships G = (V, E)."""

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}  # feature_id -> GraphNode
        self._edges: dict[tuple[str, str], GraphEdge] = {}  # (parent, child) -> GraphEdge
        self._adj_out: dict[str, set[str]] = defaultdict(set)  # parent -> set of child IDs
        self._adj_in: dict[str, set[str]] = defaultdict(set)  # child -> set of parent IDs
        self._records: dict[str, RegistryRecord] = {}  # feature_id -> RegistryRecord for backwards compatibility

    @property
    def nodes(self) -> dict[str, GraphNode]:
        """Return node map (Feature ID -> GraphNode)."""
        return dict(self._nodes)

    @property
    def edges(self) -> list[GraphEdge]:
        """Return list of graph edges."""
        return list(self._edges.values())

    def add_node(self, node_or_record: GraphNode | RegistryRecord) -> GraphNode:
        """Add a feature node to the graph.

        Args:
            node_or_record: GraphNode instance or RegistryRecord.

        Returns:
            Added GraphNode instance.
        """
        if isinstance(node_or_record, RegistryRecord):
            record = node_or_record
            fid = record.feature_id
            if fid in self._nodes:
                raise GraphValidationError(f"Duplicate node registration detected: Feature ID '{fid}' already exists in graph")

            depth = self._calculate_depth(record)
            node_id = compute_node_id(fid, record.scientific_fingerprint, depth)

            node = GraphNode(
                node_id=node_id,
                feature_id=fid,
                scientific_fingerprint=record.scientific_fingerprint,
                canonical_hash=record.canonical_hash,
                node_version=record.semantic_version,
                dependency_depth=depth,
                topological_index=0,
                node_provenance=record.registry_provenance,
            )
            self._records[fid] = record
            deps = record.dependency_spec
        elif isinstance(node_or_record, GraphNode):
            node = node_or_record
            fid = node.feature_id
            if fid in self._nodes:
                raise GraphValidationError(f"Duplicate node registration detected: Feature ID '{fid}' already exists in graph")
            deps = []
        else:
            raise TypeError(f"Expected GraphNode or RegistryRecord, got '{type(node_or_record).__name__}'")

        self._nodes[fid] = node

        # Process dependency edges
        for dep_id in deps:
            if dep_id == fid:
                raise GraphValidationError(f"Self-dependency edge detected: Feature '{fid}' depends on itself")

            edge_id, edge_hash = compute_edge_id(dep_id, fid, "required")
            edge = GraphEdge(
                edge_id=edge_id,
                parent_feature_id=dep_id,
                child_feature_id=fid,
                dependency_type="required",
                is_required=True,
                edge_hash=edge_hash,
            )
            edge_key = (dep_id, fid)
            if edge_key in self._edges:
                raise GraphValidationError(f"Duplicate edge detected between parent '{dep_id}' and child '{fid}'")

            self._edges[edge_key] = edge
            self._adj_out[dep_id].add(fid)
            self._adj_in[fid].add(dep_id)

        return node

    def _calculate_depth(self, record: RegistryRecord) -> int:
        """Calculate dependency depth for a record based on existing nodes."""
        if not record.dependency_spec:
            return 0
        max_parent_depth = 0
        for dep_id in record.dependency_spec:
            if dep_id in self._nodes:
                max_parent_depth = max(max_parent_depth, self._nodes[dep_id].dependency_depth + 1)
        return max_parent_depth

    def build_from_records(self, records: list[RegistryRecord]) -> None:
        """Build DAG deterministically from a list of RegistryRecords regardless of input ordering.

        Args:
            records: List of RegistryRecords.
        """
        record_map = {r.feature_id: r for r in records}
        added: set[str] = set()

        def add_rec(rec: RegistryRecord, path: set[str]) -> None:
            if rec.feature_id in added:
                return
            if rec.feature_id in path:
                cycle_str = " -> ".join(sorted(path) + [rec.feature_id])
                raise CircularDependencyError(f"Circular dependency detected in graph: {cycle_str}")
            path.add(rec.feature_id)

            for dep_id in sorted(rec.dependency_spec):
                if dep_id in record_map:
                    add_rec(record_map[dep_id], path)

            path.remove(rec.feature_id)
            self.add_node(rec)
            added.add(rec.feature_id)

        for r in sorted(records, key=lambda x: x.feature_id):
            add_rec(r, set())

        # Validate graph integrity and cycles
        self.validate_graph()

    def validate_graph(self) -> bool:
        """Validate structural graph integrity.

        Fail-closed rules:
        - All declared upstream dependencies must exist in the graph.
        - All edges must reference existing parent and child nodes.
        - No circular dependencies allowed.
        - No self-edges allowed.
        """
        # Check invalid edge references
        for (parent_id, child_id), edge in self._edges.items():
            if parent_id not in self._nodes:
                raise GraphValidationError(f"Edge references non-existent parent node '{parent_id}'")
            if child_id not in self._nodes:
                raise GraphValidationError(f"Edge references non-existent child node '{child_id}'")
            if parent_id == child_id:
                raise GraphValidationError(f"Self-edge detected on node '{parent_id}'")

        # Check missing upstream nodes declared in records
        for fid, record in self._records.items():
            for dep_id in record.dependency_spec:
                if dep_id not in self._nodes:
                    raise GraphValidationError(
                        f"Graph integrity failure: Feature '{fid}' requires missing upstream feature '{dep_id}'"
                    )

        # Check cycles via DFS
        self._detect_cycles()
        return True

    def _detect_cycles(self) -> None:
        """Detect circular dependencies using 3-color DFS traversal."""
        visited: dict[str, int] = {fid: 0 for fid in self._nodes}  # 0=unvisited, 1=visiting, 2=visited

        def dfs(node: str, path: list[str]) -> None:
            visited[node] = 1
            path.append(node)

            for child in sorted(self._adj_out.get(node, set())):
                if visited[child] == 1:
                    cycle_str = " -> ".join(path[path.index(child):] + [child])
                    raise CircularDependencyError(f"Circular dependency detected in graph: {cycle_str}")
                elif visited[child] == 0:
                    dfs(child, path)

            path.pop()
            visited[node] = 2

        for fid in sorted(self._nodes.keys()):
            if visited[fid] == 0:
                dfs(fid, [])

    def topological_sort(self) -> list[str]:
        """Compute deterministic topological ordering of Feature IDs for evaluation.

        Uses Kahn's algorithm with lexicographical tie-breaking for 100% determinism.

        Returns:
            List of Feature IDs ordered from root dependencies to downstream composite features.
        """
        self.validate_graph()

        in_deg = {fid: len(self._adj_in.get(fid, set())) for fid in self._nodes}

        # Zero in-degree queue (roots)
        zero_in = [fid for fid, deg in in_deg.items() if deg == 0]
        zero_in.sort()  # Lexicographical sort for determinism

        result: list[str] = []
        queue = deque(zero_in)

        while queue:
            node = queue.popleft()
            result.append(node)

            # Process children
            children = sorted(self._adj_out.get(node, set()))
            for child in children:
                in_deg[child] -= 1
                if in_deg[child] == 0:
                    queue.append(child)

        if len(result) != len(self._nodes):
            raise CircularDependencyError("Graph contains hidden circular dependency during topological sort")

        return result

    def get_node(self, feature_id: str) -> GraphNode:
        """Retrieve GraphNode by Feature ID."""
        if feature_id not in self._nodes:
            raise KeyError(f"Feature ID '{feature_id}' not found in graph")
        return self._nodes[feature_id]

    def get_edge(self, parent_feature_id: str, child_feature_id: str) -> GraphEdge:
        """Retrieve GraphEdge by parent and child Feature IDs."""
        key = (parent_feature_id, child_feature_id)
        if key not in self._edges:
            raise KeyError(f"Edge from parent '{parent_feature_id}' to child '{child_feature_id}' not found in graph")
        return self._edges[key]

    def get_ancestors(self, feature_id: str) -> list[str]:
        """Retrieve recursive list of all upstream ancestor Feature IDs."""
        ancestors: set[str] = set()
        visited: set[str] = set()

        def dfs(curr: str) -> None:
            visited.add(curr)
            for parent in self._adj_in.get(curr, set()):
                ancestors.add(parent)
                if parent not in visited:
                    dfs(parent)

        dfs(feature_id)
        return sorted(ancestors)

    def get_descendants(self, feature_id: str) -> list[str]:
        """Retrieve recursive list of all downstream descendant Feature IDs."""
        descendants: set[str] = set()
        visited: set[str] = set()

        def dfs(curr: str) -> None:
            visited.add(curr)
            for child in self._adj_out.get(curr, set()):
                descendants.add(child)
                if child not in visited:
                    dfs(child)

        dfs(feature_id)
        return sorted(descendants)

    def get_dependency_depth(self, feature_id: str) -> int:
        """Get calculated dependency depth for a node in the graph."""
        node = self.get_node(feature_id)
        return node.dependency_depth

    def get_topological_index(self, feature_id: str) -> int:
        """Get topological ordering index for a node."""
        top_order = self.topological_sort()
        if feature_id not in top_order:
            raise KeyError(f"Feature ID '{feature_id}' not found in topological ordering")
        return top_order.index(feature_id)

    def get_graph_statistics(self) -> dict[str, Any]:
        """Compute structural statistics of the graph."""
        top_order = self.topological_sort()
        node_count = len(self._nodes)
        edge_count = len(self._edges)

        roots = [fid for fid in self._nodes if len(self._adj_in.get(fid, set())) == 0]
        leaves = [fid for fid in self._nodes if len(self._adj_out.get(fid, set())) == 0]
        max_depth = max([n.dependency_depth for n in self._nodes.values()], default=0)

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "max_depth": max_depth,
            "root_count": len(roots),
            "leaf_count": len(leaves),
            "root_feature_ids": sorted(roots),
            "leaf_feature_ids": sorted(leaves),
            "graph_hash": self.compute_graph_hash(),
        }

    def compute_graph_hash(self) -> str:
        """Compute deterministic SHA-256 hash digest of the dependency graph topology."""
        top_order = self.topological_sort()

        edges_list = []
        for (parent, child), edge in sorted(self._edges.items(), key=lambda item: item[0]):
            edges_list.append({
                "child": child,
                "edge_hash": edge.edge_hash,
                "edge_id": edge.edge_id,
                "parent": parent,
            })

        nodes_list = []
        for fid in top_order:
            node = self._nodes[fid]
            nodes_list.append({
                "feature_id": fid,
                "node_id": node.node_id,
                "scientific_fingerprint": node.scientific_fingerprint,
                "version": node.node_version,
            })

        payload = {
            "edges": edges_list,
            "nodes": nodes_list,
            "topological_order": top_order,
        }

        return compute_canonical_sha256(payload)

    def export_graph(self) -> dict[str, Any]:
        """Export graph topological structure as a dictionary."""
        top_order = self.topological_sort()
        return {
            "graph_hash": self.compute_graph_hash(),
            "graph_statistics": self.get_graph_statistics(),
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "nodes": [self._nodes[fid].model_dump(mode="json") for fid in top_order],
            "edges": [edge.model_dump(mode="json") for edge in sorted(self._edges.values(), key=lambda e: e.edge_id)],
            "topological_order": top_order,
        }
