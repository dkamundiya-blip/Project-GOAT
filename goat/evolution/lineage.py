"""
Project GOAT v0.7 — Knowledge Lineage Graph

Defines KnowledgeLineageGraph for building acyclic directed graphs of knowledge version relationships and ancestry.
"""

from __future__ import annotations

from goat.evolution.version import KnowledgeVersion


class KnowledgeLineageGraph:
    """Acyclic directed graph connecting KnowledgeVersions and preserving scientific lineage."""

    def __init__(self) -> None:
        self._nodes: dict[str, KnowledgeVersion] = {}  # version_id -> KnowledgeVersion
        self._parents: dict[str, str] = {}              # version_id -> parent_version_id
        self._children: dict[str, list[str]] = {}       # version_id -> list of child_version_ids

    def add_version(self, version: KnowledgeVersion) -> None:
        """Add a KnowledgeVersion to the lineage graph.

        Args:
            version: KnowledgeVersion instance.
        """
        vid = version.version_id
        if vid in self._nodes:
            raise ValueError(f"Version ID '{vid}' already exists in KnowledgeLineageGraph")

        # Cycle check: if candidate parent has vid in its ancestor chain or is vid itself
        if version.parent_version_id:
            if version.parent_version_id == vid or self._is_ancestor(vid, version.parent_version_id):
                raise ValueError(f"Cycle detected: '{vid}' is an ancestor of parent '{version.parent_version_id}'")

        self._nodes[vid] = version
        if version.parent_version_id:
            p_id = version.parent_version_id
            self._parents[vid] = p_id
            if p_id not in self._children:
                self._children[p_id] = []
            if vid not in self._children[p_id]:
                self._children[p_id].append(vid)

    def get_ancestors(self, version_id: str) -> list[str]:
        """Retrieve ordered list of parent/ancestor version IDs back to root."""
        ancestors: list[str] = []
        curr = version_id
        while curr in self._parents:
            parent = self._parents[curr]
            ancestors.append(parent)
            curr = parent
        return ancestors

    def get_descendants(self, version_id: str) -> list[str]:
        """Retrieve list of descendant version IDs."""
        descendants: list[str] = []
        stack = list(self._children.get(version_id, []))
        while stack:
            curr = stack.pop(0)
            descendants.append(curr)
            stack.extend(self._children.get(curr, []))
        return descendants

    def get_root(self, version_id: str) -> str:
        """Retrieve the root version ID for a version lineage branch."""
        ancestors = self.get_ancestors(version_id)
        return ancestors[-1] if ancestors else version_id

    def _is_ancestor(self, target_id: str, candidate_parent_id: str) -> bool:
        """Check if target_id is an ancestor of candidate_parent_id."""
        ancestors = self.get_ancestors(candidate_parent_id)
        return target_id in ancestors or target_id == candidate_parent_id
