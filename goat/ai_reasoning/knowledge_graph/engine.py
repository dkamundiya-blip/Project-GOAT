"""
Project GOAT Phase 7 — Research Knowledge Graph (`goat.ai_reasoning.knowledge_graph`)

Constructs and queries an interconnected Research Knowledge Graph linking features, hypotheses, edges,
regimes, symbols, sessions, timeframes, and validation results.
"""

from __future__ import annotations

import threading
from typing import Sequence

from goat.ai_reasoning.models.graph import (
    EdgeType,
    NodeType,
    ResearchGraphEdge,
    ResearchGraphNode,
    compute_edge_id,
    compute_node_id,
)
from goat.edge_discovery.models.edge import DiscoveredEdge


class ResearchKnowledgeGraph:
    """Quantitative Research Knowledge Graph representing research entity relationships."""

    def __init__(self):
        self._nodes: dict[str, ResearchGraphNode] = {}
        self._edges_from: dict[str, list[ResearchGraphEdge]] = {}
        self._edges_to: dict[str, list[ResearchGraphEdge]] = {}
        self._lock = threading.RLock()

    def add_node(self, node: ResearchGraphNode) -> None:
        """Add a node to the knowledge graph."""
        with self._lock:
            self._nodes[node.node_id] = node
            if node.node_id not in self._edges_from:
                self._edges_from[node.node_id] = []
            if node.node_id not in self._edges_to:
                self._edges_to[node.node_id] = []

    def add_edge(self, edge: ResearchGraphEdge) -> None:
        """Add a directed edge to the knowledge graph."""
        with self._lock:
            if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
                return  # Guard against missing node references
            self._edges_from[edge.source_id].append(edge)
            self._edges_to[edge.target_id].append(edge)

    def get_node(self, node_id: str) -> ResearchGraphNode | None:
        """Fetch a node by node_id."""
        with self._lock:
            return self._nodes.get(node_id)

    def find_nodes_by_type(self, node_type: NodeType) -> list[ResearchGraphNode]:
        """Find all nodes matching a specific NodeType."""
        with self._lock:
            return [n for n in self._nodes.values() if n.node_type == node_type]

    def query_neighbors(
        self,
        node_id: str,
        edge_type: EdgeType | None = None,
        direction: str = "OUTGOING",
    ) -> list[ResearchGraphNode]:
        """Query neighbor nodes connected to target node_id."""
        with self._lock:
            neighbors: list[ResearchGraphNode] = []
            if direction == "OUTGOING" and node_id in self._edges_from:
                edges = self._edges_from[node_id]
                for e in edges:
                    if edge_type is None or e.edge_type == edge_type:
                        if e.target_id in self._nodes:
                            neighbors.append(self._nodes[e.target_id])
            elif direction == "INCOMING" and node_id in self._edges_to:
                edges = self._edges_to[node_id]
                for e in edges:
                    if edge_type is None or e.edge_type == edge_type:
                        if e.source_id in self._nodes:
                            neighbors.append(self._nodes[e.source_id])
            return neighbors

    def ingest_discovered_edge(self, edge: DiscoveredEdge) -> ResearchGraphNode:
        """Ingest a DiscoveredEdge and automatically wire relationship nodes & edges in the graph."""
        with self._lock:
            # 1. Create Edge Node
            e_nid, e_nhash = compute_node_id(NodeType.EDGE, edge.edge_id)
            e_node = ResearchGraphNode(
                node_id=e_nid,
                node_type=NodeType.EDGE,
                name=edge.edge_id,
                properties={
                    "composite_score": edge.composite_score,
                    "expected_value": edge.metrics.expected_value,
                    "hypothesis_id": edge.hypothesis_id,
                    "p_value": edge.p_value,
                    "sharpe_ratio": edge.metrics.sharpe_ratio,
                    "status": edge.status.value,
                },
                canonical_hash=e_nhash,
            )
            self.add_node(e_node)

            # 2. Create Hypothesis Node
            h_nid, h_nhash = compute_node_id(NodeType.HYPOTHESIS, edge.hypothesis_id)
            h_node = ResearchGraphNode(
                node_id=h_nid,
                node_type=NodeType.HYPOTHESIS,
                name=edge.hypothesis_id,
                properties={"hypothesis_id": edge.hypothesis_id},
                canonical_hash=h_nhash,
            )
            self.add_node(h_node)

            rel_id, rel_hash = compute_edge_id(e_nid, h_nid, EdgeType.EVALUATED_BY)
            self.add_edge(ResearchGraphEdge(edge_id=rel_id, source_id=e_nid, target_id=h_nid, edge_type=EdgeType.EVALUATED_BY, canonical_hash=rel_hash))

            # 3. Create Feature Nodes & Connect
            for feat_name in edge.feature_combination:
                f_nid, f_nhash = compute_node_id(NodeType.FEATURE, feat_name)
                f_node = ResearchGraphNode(node_id=f_nid, node_type=NodeType.FEATURE, name=feat_name, canonical_hash=f_nhash)
                self.add_node(f_node)

                fe_id, fe_hash = compute_edge_id(e_nid, f_nid, EdgeType.DERIVED_FROM)
                self.add_edge(ResearchGraphEdge(edge_id=fe_id, source_id=e_nid, target_id=f_nid, edge_type=EdgeType.DERIVED_FROM, canonical_hash=fe_hash))

            # 4. Create Symbol Nodes & Connect
            for sym in edge.supported_symbols:
                s_nid, s_nhash = compute_node_id(NodeType.SYMBOL, sym)
                s_node = ResearchGraphNode(node_id=s_nid, node_type=NodeType.SYMBOL, name=sym, canonical_hash=s_nhash)
                self.add_node(s_node)

                se_id, se_hash = compute_edge_id(e_nid, s_nid, EdgeType.APPLIES_TO)
                self.add_edge(ResearchGraphEdge(edge_id=se_id, source_id=e_nid, target_id=s_nid, edge_type=EdgeType.APPLIES_TO, canonical_hash=se_hash))

            # 5. Create Timeframe Nodes & Connect
            for tf in edge.supported_timeframes:
                t_nid, t_nhash = compute_node_id(NodeType.TIMEFRAME, tf)
                t_node = ResearchGraphNode(node_id=t_nid, node_type=NodeType.TIMEFRAME, name=tf, canonical_hash=t_nhash)
                self.add_node(t_node)

                te_id, te_hash = compute_edge_id(e_nid, t_nid, EdgeType.APPLIES_TO)
                self.add_edge(ResearchGraphEdge(edge_id=te_id, source_id=e_nid, target_id=t_nid, edge_type=EdgeType.APPLIES_TO, canonical_hash=te_hash))

            # 6. Create Regime Nodes & Connect
            for regime_name, metrics in edge.regime_performance.items():
                if metrics.get("sample_size", 0.0) > 0:
                    r_nid, r_nhash = compute_node_id(NodeType.REGIME, regime_name)
                    r_node = ResearchGraphNode(node_id=r_nid, node_type=NodeType.REGIME, name=regime_name, canonical_hash=r_nhash)
                    self.add_node(r_node)

                    re_id, re_hash = compute_edge_id(e_nid, r_nid, EdgeType.ACTIVE_IN)
                    self.add_edge(ResearchGraphEdge(edge_id=re_id, source_id=e_nid, target_id=r_nid, edge_type=EdgeType.ACTIVE_IN, canonical_hash=re_hash))

            return e_node

    def node_count(self) -> int:
        """Return total node count."""
        with self._lock:
            return len(self._nodes)

    def edge_count(self) -> int:
        """Return total edge count."""
        with self._lock:
            return sum(len(v) for v in self._edges_from.values())
