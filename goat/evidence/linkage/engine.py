"""
Project GOAT v0.9 — Evidence Linkage Engine
"""

from datetime import datetime, timezone
from typing import Any, Sequence

from goat.evidence.core.canonical import compute_link_id
from goat.evidence.core.models import EvidenceLink


class EvidenceLinkageEngine:
    """Evidence Linkage Engine for creating and managing deterministic links between

    ScientificHypothesis IDs (HYP_) and EvidenceRecord (EVR_) or ScientificObservation (OBS_) IDs.

    IMPORTANT: This engine ONLY maintains relational provenance links.
    It DOES NOT evaluate, rate, score, or judge whether evidence supports or refutes a hypothesis.
    """

    def __init__(self) -> None:
        self._links: dict[str, EvidenceLink] = {}
        self._hypothesis_map: dict[str, set[str]] = {}
        self._target_map: dict[str, set[str]] = {}

    def create_link(
        self,
        hypothesis_id: str,
        target_id: str,
        link_type: str = "HYPOTHESIS_EVIDENCE_LINK",
        linker_id: str = "GOAT_LINKER",
        timestamp: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> EvidenceLink:
        """Create a deterministic evidence provenance link between a hypothesis and evidence/observation."""
        if not hypothesis_id or not hypothesis_id.startswith("HYP_"):
            raise ValueError(f"Hypothesis ID '{hypothesis_id}' must start with 'HYP_'.")
        if not target_id or not (target_id.startswith("EVR_") or target_id.startswith("OBS_") or target_id.startswith("COL_")):
            raise ValueError(f"Target ID '{target_id}' must start with 'EVR_', 'OBS_', or 'COL_'.")

        now_str = timestamp or datetime.now(timezone.utc).isoformat()
        lnk_id, canonical_hash = compute_link_id(
            hypothesis_id=hypothesis_id,
            target_id=target_id,
            link_type=link_type,
            timestamp=now_str,
        )

        if lnk_id in self._links:
            return self._links[lnk_id]

        link = EvidenceLink(
            link_id=lnk_id,
            hypothesis_id=hypothesis_id.strip(),
            target_id=target_id.strip(),
            link_type=link_type.strip().upper(),
            linker_id=linker_id.strip(),
            timestamp=now_str,
            metadata=metadata or {},
            canonical_hash=canonical_hash,
        )

        self._links[lnk_id] = link
        self._hypothesis_map.setdefault(hypothesis_id, set()).add(lnk_id)
        self._target_map.setdefault(target_id, set()).add(lnk_id)

        return link

    def get_link(self, link_id: str) -> EvidenceLink | None:
        """Retrieve a link by ID."""
        return self._links.get(link_id)

    def get_links_for_hypothesis(self, hypothesis_id: str) -> list[EvidenceLink]:
        """Retrieve all evidence links associated with a hypothesis ID."""
        lnk_ids = self._hypothesis_map.get(hypothesis_id, set())
        return sorted([self._links[lid] for lid in lnk_ids], key=lambda l: l.timestamp)

    def get_links_for_target(self, target_id: str) -> list[EvidenceLink]:
        """Retrieve all hypothesis links associated with a target evidence or observation ID."""
        lnk_ids = self._target_map.get(target_id, set())
        return sorted([self._links[lid] for lid in lnk_ids], key=lambda l: l.timestamp)

    def list_all_links(self) -> list[EvidenceLink]:
        """List all links in the registry sorted by timestamp."""
        return sorted(self._links.values(), key=lambda l: l.timestamp)
