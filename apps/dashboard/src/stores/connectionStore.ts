/**
 * Project GOAT v1.0 — API & WebSocket Connection Telemetry Store
 */

import { create } from 'zustand';

interface ConnectionState {
  restStatus: 'CONNECTED' | 'DISCONNECTED' | 'RETRYING';
  wsStatus: 'OPEN' | 'CONNECTING' | 'CLOSED';
  latencyMs: number;
  reconnectCount: number;
  mode: 'LIVE' | 'REPLAY';
  setRestStatus: (status: 'CONNECTED' | 'DISCONNECTED' | 'RETRYING') => void;
  setWsStatus: (status: 'OPEN' | 'CONNECTING' | 'CLOSED') => void;
  setLatency: (ms: number) => void;
  incrementReconnectCount: () => void;
  setMode: (mode: 'LIVE' | 'REPLAY') => void;
}

export const useConnectionStore = create<ConnectionState>((set) => ({
  restStatus: 'CONNECTED',
  wsStatus: 'OPEN',
  latencyMs: 12.5,
  reconnectCount: 0,
  mode: 'LIVE',
  setRestStatus: (restStatus) => set({ restStatus }),
  setWsStatus: (wsStatus) => set({ wsStatus }),
  setLatency: (latencyMs) => set({ latencyMs }),
  incrementReconnectCount: () => set((state) => ({ reconnectCount: state.reconnectCount + 1 })),
  setMode: (mode) => set({ mode }),
}));
