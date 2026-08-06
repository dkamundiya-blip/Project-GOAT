"""
Project GOAT v0.7 — Scientific Knowledge Graph Engine

Provides deterministic in-memory graph representation and graph algorithms:
- Node & Edge management
- Lookup operations
- Neighborhood queries
- Deterministic traversal (BFS / DFS)
- Canonical JSON serialization
- Deterministic Replay
"""

from __future__ import annotations

from collections import deque
from typing import Any

from goat.integration.core.canonical import serialize_canonical_json
from goat.integration.core.models import KnowledgeEdge, KnowledgeNode


class ScientificKnowledgeGraph:
    """Deterministic scientific knowledge graph."""

    def __init__(self) -> None:
        self._nodes: dict[str, KnowledgeNode] = {}
        self._edges: dict[str, KnowledgeEdge] = {}
        self._outgoing: dict[str, dict[str, KnowledgeEdge]] = {}  # node_id -> {edge_id: edge}
        self._incoming: dict[str, dict[str, KnowledgeEdge]] = {}  # node_id -> {edge_id: edge}

    def add_node(self, node: KnowledgeNode) -> None:
        """Add a KnowledgeNode to the graph.

        Raises:
            ValueError: If node_id already exists with conflicting data.
        """
        if node.node_id in self._nodes:
            existing = self._nodes[node.node_id]
            if existing != node:
                raise ValueError(
                    f"Node ID '{node.node_id}' already exists with different contents."
                )
            return

        self._nodes[node.node_id] = node
        self._outgoing[node.node_id] = {}
        self._incoming[node.node_id] = {}

    def add_edge(self, edge: KnowledgeEdge) -> None:
        """Add a KnowledgeEdge to the graph.

        Raises:
            KeyError: If source or destination node does not exist in graph.
            ValueError: If edge_id already exists with conflicting data.
        """
        if edge.source_node not in self._nodes:
            raise KeyError(f"Source node '{edge.source_node}' not found in graph.")
        if edge.destination_node not in self._nodes:
            raise KeyError(f"Destination node '{edge.destination_node}' not found in graph.")

        if edge.edge_id in self._edges:
            existing = self._edges[edge.edge_id]
            if existing != edge:
                raise ValueError(
                    f"Edge ID '{edge.edge_id}' already exists with different contents."
                )
            return

        self._edges[edge.edge_id] = edge
        self._outgoing[edge.source_node][edge.edge_id] = edge
        self._incoming[edge.destination_node][edge.edge_id] = edge

    def remove_edge(self, edge_id: str) -> bool:
        """Remove an edge by ID.

        Returns:
            True if removed, False if not found.
        """
        if edge_id not in self._edges:
            return False

        edge = self._edges.pop(edge_id)
        if edge.source_node in self._outgoing:
            self._outgoing[edge.source_node].pop(edge_id, None)
        if edge.destination_node in self._incoming:
            self._incoming[edge.destination_node].pop(edge_id, None)
        return True

    def lookup_node(self, node_id: str) -> KnowledgeNode | None:
        """Lookup a node by ID."""
        return self._nodes.get(node_id)

    def lookup_edge(self, edge_id: str) -> KnowledgeEdge | None:
        """Lookup an edge by ID."""
        return self._edges.get(edge_id)

    def lookup_evidence(self, target_id: str) -> list[str]:
        """Lookup evidence associated with a node or edge.

        Returns:
            Sorted list of unique evidence IDs.
        """
        evidence_set: set[str] = set()

        if target_id in self._nodes:
            node = self._nodes[target_id]
            if "evidence_ids" in node.metadata and isinstance(node.metadata["evidence_ids"], list):
                evidence_set.update(node.metadata["evidence_ids"])
            if node.originating_validation:
                evidence_set.add(node.originating_validation)

        if target_id in self._edges:
            edge = self._edges[target_id]
            evidence_set.update(edge.supporting_evidence)

        return sorted(list(evidence_set))

    def lookup_relationships(
        self, node_id: str, direction: str = "both"
    ) -> list[KnowledgeEdge]:
        """Lookup connected edges for a node in specified direction ('outgoing', 'incoming', 'both').

        Returns:
            Sorted list of KnowledgeEdge objects ordered by edge_id.
        """
        if node_id not in self._nodes:
            return []

        result_edges: dict[str, KnowledgeEdge] = {}
        dir_lower = direction.lower()

        if dir_lower in ("outgoing", "both"):
            for e in self._outgoing[node_id].values():
                result_edges[e.edge_id] = e

        if dir_lower in ("incoming", "both"):
            for e in self._incoming[node_id].values():
                result_edges[e.edge_id] = e

        return sorted(list(result_edges.values()), key=lambda e: e.edge_id)

    def neighborhood_queries(
        self, node_id: str, depth: int = 1
    ) -> dict[str, list[Any]]:
        """Perform neighborhood query around a node up to specified hop depth.

        Returns:
            Dict containing sorted list of 'nodes' and 'edges'.
        """
        if node_id not in self._nodes or depth < 0:
            return {"nodes": [], "edges": []}

        visited_nodes: set[str] = {node_id}
        collected_edges: set[str] = set()
        current_layer: set[str] = {node_id}

        for _ in range(depth):
            next_layer: set[str] = set()
            for current in sorted(current_layer):
                for edge in self._outgoing.get(current, {}).values():
                    collected_edges.add(edge.edge_id)
                    if edge.destination_node not in visited_nodes:
                        visited_nodes.add(edge.destination_node)
                        next_layer.add(edge.destination_node)
                for edge in self._incoming.get(current, {}).values():
                    collected_edges.add(edge.edge_id)
                    if edge.source_node not in visited_nodes:
                        visited_nodes.add(edge.source_node)
                        next_layer.add(edge.source_node)
            current_layer = next_layer
            if not current_layer:
                break

        res_nodes = [self._nodes[nid] for nid in sorted(visited_nodes) if nid in self._nodes]
        res_edges = [self._edges[eid] for eid in sorted(collected_edges) if eid in self._edges]

        return {"nodes": res_nodes, "edges": res_edges}

    def traversal(
        self, start_node_id: str, max_depth: int = 5, mode: str = "bfs"
    ) -> list[str]:
        """Perform deterministic traversal starting from start_node_id.

        Args:
            start_node_id: Starting node ID.
            max_depth: Maximum path depth.
            mode: 'bfs' or 'dfs'.

        Returns:
            List of visited node IDs in traversal order.
        """
        if start_node_id not in self._nodes:
            return []

        mode_lower = mode.lower()
        visited: set[str] = set()
        traversal_order: list[str] = []

        if mode_lower == "bfs":
            queue: deque[tuple[str, int]] = deque([(start_node_id, 0)])
            visited.add(start_node_id)

            while queue:
                curr_node, curr_depth = queue.popleft()
                traversal_order.append(curr_node)

                if curr_depth < max_depth:
                    # Collect neighbor nodes deterministically sorted by node_id
                    neighbors: set[str] = set()
                    for edge in self._outgoing.get(curr_node, {}).values():
                        neighbors.add(edge.destination_node)
                    for nbr in sorted(neighbors):
                        if nbr not in visited and nbr in self._nodes:
                            visited.add(nbr)
                            queue.append((nbr, curr_depth + 1))

        elif mode_lower == "dfs":
            stack: list[tuple[str, int]] = [(start_node_id, 0)]

            while stack:
                curr_node, curr_depth = stack.pop()
                if curr_node in visited:
                    continue
                visited.add(curr_node)
                traversal_order.append(curr_node)

                if curr_depth < max_depth:
                    neighbors: set[str] = set()
                    for edge in self._outgoing.get(curr_node, {}).values():
                        neighbors.add(edge.destination_node)
                    # Push onto stack in reverse sorted order so smallest node_id popped first
                    for nbr in sorted(neighbors, reverse=True):
                        if nbr not in visited and nbr in self._nodes:
                            stack.append((nbr, curr_depth + 1))
        else:
            raise ValueError(f"Unsupported traversal mode '{mode}'. Use 'bfs' or 'dfs'.")

        return traversal_order

    def get_nodes(self) -> list[KnowledgeNode]:
        """Return all nodes in graph sorted by node_id."""
        return [self._nodes[k] for k in sorted(self._nodes.keys())]

    def get_edges(self) -> list[KnowledgeEdge]:
        """Return all edges in graph sorted by edge_id."""
        return [self._edges[k] for k in sorted(self._edges.keys())]

    def to_dict(self) -> dict[str, Any]:
        """Convert graph state into canonical dict."""
        return {
            "nodes": [n.dict() for n in self.get_nodes()],
            "edges": [e.dict() for e in self.get_edges()],
        }

    def serialize(self) -> str:
        """Serialize graph to canonical JSON string."""
        return serialize_canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScientificKnowledgeGraph:
        """Construct ScientificKnowledgeGraph from dict representation."""
        graph = cls()
        for nd in data.get("nodes", []):
            graph.add_node(KnowledgeNode(**nd))
        for ed in data.get("edges", []):
            graph.add_edge(KnowledgeEdge(**ed))
        return graph

    @classmethod
    def deserialize(cls, json_str: str) -> ScientificKnowledgeGraph:
        """Construct graph from canonical JSON string."""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)

    def replay_events(self, events: list[dict[str, Any]]) -> None:
        """Replay sequence of graph modification events deterministically."""
        for event in events:
            ev_type = event.get("event_type", "").upper()
            payload = event.get("payload", {})
            if ev_type == "ADD_NODE":
                self.add_node(KnowledgeNode(**payload))
            elif ev_type == "ADD_EDGE":
                self.add_edge(KnowledgeEdge(**payload))
            elif ev_type == "REMOVE_EDGE":
                self.remove_edge(payload.get("edge_id", ""))
            else:
                raise ValueError(f"Unknown graph event type: '{ev_type}'")
