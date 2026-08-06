/**
 * Project GOAT v1.0 — Live Market Data Zustand Store
 */

import { create } from 'zustand';
import { LiveQuoteDTO, IngestionTelemetryDTO } from '../types/marketData';

interface MarketDataState {
  quotes: Record<string, LiveQuoteDTO>;
  telemetry: IngestionTelemetryDTO | null;
  connectionState: 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING' | 'DEGRADED';
  isPolling: boolean;

  setQuotes: (quotes: LiveQuoteDTO[]) => void;
  setTelemetry: (telemetry: IngestionTelemetryDTO) => void;
  setConnectionState: (state: 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING' | 'DEGRADED') => void;
  setIsPolling: (isPolling: boolean) => void;
}

export const useMarketDataStore = create<MarketDataState>((set) => ({
  quotes: {},
  telemetry: null,
  connectionState: 'CONNECTED',
  isPolling: false,

  setQuotes: (quotesList) =>
    set((state) => {
      const map: Record<string, LiveQuoteDTO> = { ...state.quotes };
      for (const q of quotesList) {
        map[q.symbol] = q;
      }
      return { quotes: map };
    }),

  setTelemetry: (telemetry) => set({ telemetry }),
  setConnectionState: (connectionState) => set({ connectionState }),
  setIsPolling: (isPolling) => set({ isPolling }),
}));
