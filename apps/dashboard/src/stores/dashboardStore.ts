/**
 * Project GOAT v1.0 — Dashboard Overview State Store
 */

import { create } from 'zustand';
import { GovernanceDecisionItem, HypothesisSummaryItem, SystemOverviewMetrics } from '../types/dashboard';

interface DashboardState {
  summary: SystemOverviewMetrics | null;
  hypotheses: HypothesisSummaryItem[];
  governanceDecisions: GovernanceDecisionItem[];
  isLoading: boolean;
  error: string | null;
  setSummary: (summary: SystemOverviewMetrics) => void;
  setHypotheses: (hypotheses: HypothesisSummaryItem[]) => void;
  setGovernanceDecisions: (decisions: GovernanceDecisionItem[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  summary: {
    hypothesis_count: 42,
    evidence_records_count: 1250,
    validated_edges_count: 18,
    promoted_edges_count: 5,
    knowledge_graph_nodes: 156,
    intelligence_health_score: 94.5,
    database_status: 'ONLINE_READ_ONLY',
  },
  hypotheses: [],
  governanceDecisions: [],
  isLoading: false,
  error: null,
  setSummary: (summary) => set({ summary }),
  setHypotheses: (hypotheses) => set({ hypotheses }),
  setGovernanceDecisions: (governanceDecisions) => set({ governanceDecisions }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}));
