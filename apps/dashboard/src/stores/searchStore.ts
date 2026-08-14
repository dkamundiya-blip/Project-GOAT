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

const INDEX: SearchResultItem[] = [];

export const useSearchStore = create<SearchState>((set) => ({
  searchOpen: false,
  query: '',
  results: [],
  history: [],
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
