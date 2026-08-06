/**
 * Project GOAT v1.1 — Market Data Service Layer
 *
 * Production market data service consuming live Deriv feeds from the backend API gateway.
 * ABSOLUTE RULE: Zero mock or fallback payloads. Network failures trigger degraded UI states.
 */

import { LiveQuoteDTO, IngestionTelemetryDTO } from '../../types/marketData';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    throw new Error(`API Request failed (${res.status} ${res.statusText})`);
  }
  const payload = await res.json();
  if (payload && payload.data !== undefined) {
    return payload.data as T;
  }
  return payload as T;
}

export const marketDataApi = {
  async getSymbols(): Promise<{ symbols: LiveQuoteDTO[]; count: number }> {
    return await fetchJson<{ symbols: LiveQuoteDTO[]; count: number }>('/api/v1/market-data/symbols');
  },

  async getMetrics(): Promise<IngestionTelemetryDTO> {
    return await fetchJson<IngestionTelemetryDTO>('/api/v1/market-data/metrics');
  },

  async postConnect(): Promise<{ success: boolean; connection_state: string }> {
    return await fetchJson<{ success: boolean; connection_state: string }>('/api/v1/market-data/connect', { method: 'POST' });
  },

  async postDisconnect(): Promise<{ success: boolean; connection_state: string }> {
    return await fetchJson<{ success: boolean; connection_state: string }>('/api/v1/market-data/disconnect', { method: 'POST' });
  },

  async postReconnect(): Promise<{ success: boolean; connection_state: string }> {
    return await fetchJson<{ success: boolean; connection_state: string }>('/api/v1/market-data/reconnect', { method: 'POST' });
  },

  async postSubscribe(symbol_id: string): Promise<{ symbol: string; success: boolean }> {
    return await fetchJson<{ symbol: string; success: boolean }>(`/api/v1/market-data/subscribe/${symbol_id}`, { method: 'POST' });
  },

  async postUnsubscribe(symbol_id: string): Promise<{ symbol: string; success: boolean }> {
    return await fetchJson<{ symbol: string; success: boolean }>(`/api/v1/market-data/unsubscribe/${symbol_id}`, { method: 'POST' });
  },
};
