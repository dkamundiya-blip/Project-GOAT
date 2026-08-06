/**
 * Project GOAT v1.0 — Dashboard Domain Types
 */

export interface SystemOverviewMetrics {
  hypothesis_count: number;
  evidence_records_count: number;
  validated_edges_count: number;
  promoted_edges_count: number;
  knowledge_graph_nodes: number;
  intelligence_health_score: number;
  database_status: string;
}

export interface HypothesisSummaryItem {
  hypothesis_id: string;
  title: string;
  category: string;
  status: string;
  confidence_score: number;
  created_at: string;
}

export interface GovernanceDecisionItem {
  decision_id: string;
  edge_id: string;
  outcome: 'PROMOTE' | 'RETAIN' | 'PAUSE' | 'RETURN_TO_RESEARCH' | 'RETIRE';
  reason: string;
  decided_at: string;
}

export interface ActivityEventItem {
  id: string;
  timestamp: string;
  category: 'EVENT' | 'WARNING' | 'GOVERNANCE' | 'VALIDATION' | 'SYSTEM';
  title: string;
  description: string;
}
