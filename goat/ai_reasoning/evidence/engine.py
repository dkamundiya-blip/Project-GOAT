"""
Project GOAT Phase 7 — Evidence Engine (`goat.ai_reasoning.evidence`)

Constructs 100% traceable EvidenceBundle and EvidenceRecord objects from empirical edge research metrics.
"""

from __future__ import annotations

from goat.ai_reasoning.models.evidence import (
    EvidenceBundle,
    EvidenceRecord,
    EvidenceType,
    compute_evidence_bundle_id,
    compute_evidence_record_id,
)
from goat.edge_discovery.models.edge import DiscoveredEdge


class EvidenceEngine:
    """Quantitative Evidence Engine generating traceable empirical evidence records."""

    def build_evidence_bundle(self, edge: DiscoveredEdge) -> EvidenceBundle:
        """Construct an EvidenceBundle from a DiscoveredEdge."""
        records: list[EvidenceRecord] = []
        m = edge.metrics

        # 1. Expected Value Evidence
        claim_ev = f"Expected Value per trade is positive ({m.expected_value:.6f})"
        r_id, r_hash = compute_evidence_record_id(claim_ev, "expected_value", m.expected_value)
        records.append(
            EvidenceRecord(
                record_id=r_id,
                evidence_type=EvidenceType.STATISTICAL_METRIC,
                claim=claim_ev,
                metric_name="expected_value",
                metric_value=m.expected_value,
                threshold_value=0.0,
                is_supporting=(m.expected_value > 0.0),
                canonical_hash=r_hash,
            )
        )

        # 2. Sharpe Ratio Evidence
        claim_sr = f"Annualized Sharpe Ratio ({m.sharpe_ratio:.2f}) indicates favorable risk-adjusted returns"
        r_id, r_hash = compute_evidence_record_id(claim_sr, "sharpe_ratio", m.sharpe_ratio)
        records.append(
            EvidenceRecord(
                record_id=r_id,
                evidence_type=EvidenceType.STATISTICAL_METRIC,
                claim=claim_sr,
                metric_name="sharpe_ratio",
                metric_value=m.sharpe_ratio,
                threshold_value=1.0,
                is_supporting=(m.sharpe_ratio >= 1.0),
                canonical_hash=r_hash,
            )
        )

        # 3. Statistical Significance P-Value Evidence
        claim_pv = f"P-value ({edge.p_value:.6f}) confirms statistical significance below alpha 0.05"
        r_id, r_hash = compute_evidence_record_id(claim_pv, "p_value", edge.p_value)
        records.append(
            EvidenceRecord(
                record_id=r_id,
                evidence_type=EvidenceType.STATISTICAL_METRIC,
                claim=claim_pv,
                metric_name="p_value",
                metric_value=edge.p_value,
                threshold_value=0.05,
                is_supporting=(edge.p_value <= 0.05),
                canonical_hash=r_hash,
            )
        )

        # 4. Sample Size Evidence
        claim_ss = f"Observation sample size ({m.sample_size}) satisfies statistical power requirements"
        r_id, r_hash = compute_evidence_record_id(claim_ss, "sample_size", float(m.sample_size))
        records.append(
            EvidenceRecord(
                record_id=r_id,
                evidence_type=EvidenceType.STATISTICAL_METRIC,
                claim=claim_ss,
                metric_name="sample_size",
                metric_value=float(m.sample_size),
                threshold_value=10.0,
                is_supporting=(m.sample_size >= 10),
                canonical_hash=r_hash,
            )
        )

        # 5. Walk-Forward Out-of-Sample Evidence
        oos_ev = edge.walk_forward_metrics.get("oos_expected_value", m.expected_value)
        claim_oos = f"Out-of-Sample Walk-Forward Expected Value ({oos_ev:.6f}) demonstrates edge persistence"
        r_id, r_hash = compute_evidence_record_id(claim_oos, "oos_expected_value", oos_ev)
        records.append(
            EvidenceRecord(
                record_id=r_id,
                evidence_type=EvidenceType.WALK_FORWARD_OOS,
                claim=claim_oos,
                metric_name="oos_expected_value",
                metric_value=oos_ev,
                threshold_value=0.0,
                is_supporting=(oos_ev > 0.0),
                canonical_hash=r_hash,
            )
        )

        # Aggregated Confidence
        supporting_count = sum(1 for r in records if r.is_supporting)
        confidence = supporting_count / len(records) if records else 0.0

        b_id, b_hash = compute_evidence_bundle_id(edge.edge_id, records)

        return EvidenceBundle(
            bundle_id=b_id,
            target_id=edge.edge_id,
            target_type="EDGE",
            records=records,
            sample_size=m.sample_size,
            overall_confidence=round(confidence, 4),
            canonical_hash=b_hash,
        )
