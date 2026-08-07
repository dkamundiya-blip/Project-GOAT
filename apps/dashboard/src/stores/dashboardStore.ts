/**
 * Project GOAT v1.0 — Dashboard Overview State Store
 *
 * Initialized with null summary to prevent shadowing live WebSocket telemetry.
 * Zero static mock metrics.
 */

import { create } from 'zustand';
import { GovernanceDecisionItem, HypothesisSummaryItem, SystemOverviewMetrics } from '../types/dashboard';

interface DashboardState {
  summary: SystemOverviewMetrics | null;
  hypotheses: HypothesisSummaryItem[];
  governanceDecisions: GovernanceDecisionItem[];
  isLoading: boolean;
  error: string | null;
  setSummary: (summary: SystemOverviewMetrics | null) => void;
  setHypotheses: (hypotheses: HypothesisSummaryItem[]) => void;
  setGovernanceDecisions: (decisions: GovernanceDecisionItem[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  summary: null,
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
