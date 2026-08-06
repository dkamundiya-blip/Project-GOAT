/**
 * Project GOAT v1.0 — Global Canonical Search Zustand Store
 */

import { create } from 'zustand';
import { SearchResultItem } from '../types/pipeline';

interface SearchState {
  searchOpen: boolean;
  query: string;
  results: SearchResultItem[];
  history: string[];
  filterStage: string;

  // Actions
  setSearchOpen: (open: boolean) => void;
  setQuery: (query: string) => void;
  executeSearch: (q: string) => void;
  clearSearch: () => void;
}

const INDEX: SearchResultItem[] = [
  { id: 'HYP_VOL10_001', canonicalId: 'HYP_VOL10_001', title: 'Volatility 10 Microstructure Momentum Hypothesis', stage: 'HYPOTHESIS', matchField: 'canonicalId', snippet: 'Formulated statistical momentum anomaly hypothesis' },
  { id: 'EVI_VOL10_001', canonicalId: 'EVI_VOL10_001', title: 'Volatility 10 High-Frequency Tick Dataset Evidence', stage: 'EVIDENCE', matchField: 'canonicalId', snippet: '10,000,000 tick samples collected across 90 days' },
  { id: 'EXP_VOL10_001', canonicalId: 'EXP_VOL10_001', title: 'Volatility 10 Cross-Validation Experiment Run', stage: 'EXPERIMENT', matchField: 'canonicalId', snippet: '10-fold cross-validation with noise perturbation' },
  { id: 'VAL_VOL10_001', canonicalId: 'VAL_VOL10_001', title: 'Volatility 10 Live Paper Session Validation', stage: 'LIVE_VALIDATION', matchField: 'canonicalId', snippet: 'Paper trading session with zero fill slippage' },
  { id: 'GOV_BOOM500_002', canonicalId: 'GOV_BOOM500_002', title: 'Boom 500 Reversion Governance Approval Certificate', stage: 'GOVERNANCE', matchField: 'canonicalId', snippet: 'Quorum approval granted by Chief Quantitative Officer' },
  { id: 'ARC_CRASH1000_003', canonicalId: 'ARC_CRASH1000_003', title: 'Crash 1000 Regime Switching Archive Record', stage: 'ARCHIVE', matchField: 'canonicalId', snippet: 'Archived snapshot stored in SQLite cold storage' },
  { id: 'KNO_VOL10_001', canonicalId: 'KNO_VOL10_001', title: 'Knowledge Node: Volatility Microstructure Anomaly', stage: 'RESEARCH_INTELLIGENCE', matchField: 'canonicalId', snippet: 'Semantic node linked to 4 derivative hypotheses' },
  { id: 'INT_VOL10_001', canonicalId: 'INT_VOL10_001', title: 'Institutional Research Intelligence Insights Report', stage: 'RESEARCH_INTELLIGENCE', matchField: 'canonicalId', snippet: 'Cross-market alpha correlation and decay prediction' },
];

export const useSearchStore = create<SearchState>((set) => ({
  searchOpen: false,
  query: '',
  results: [],
  history: ['HYP_VOL10_001', 'VAL_VOL10_001', 'GOV_BOOM500_002'],
  filterStage: 'ALL',

  setSearchOpen: (open) => set({ searchOpen: open }),

  setQuery: (query) => {
    set({ query });
    if (!query.trim()) {
      set({ results: [] });
      return;
    }
    const q = query.trim().toUpperCase();
    const matched = INDEX.filter(
      (item) =>
        item.canonicalId.toUpperCase().includes(q) ||
        item.title.toUpperCase().includes(q) ||
        item.snippet.toUpperCase().includes(q)
    );
    set({ results: matched });
  },

  executeSearch: (q) => {
    const term = q.trim().toUpperCase();
    if (!term) return;
    const matched = INDEX.filter(
      (item) =>
        item.canonicalId.toUpperCase().includes(term) ||
        item.title.toUpperCase().includes(term) ||
        item.snippet.toUpperCase().includes(term)
    );
    set((state) => ({
      results: matched,
      history: [term, ...state.history.filter((h) => h !== term)].slice(0, 5),
    }));
  },

  clearSearch: () => set({ query: '', results: [] }),
}));
