/**
 * Project GOAT v1.0 — Real-Time Telemetry State Store
 */

import { create } from 'zustand';
import { TelemetryFramePayload } from '../types/api';

interface TelemetryState {
  frames: TelemetryFramePayload[];
  activeWSClients: number;
  lastFrameTimestamp: string | null;
  addFrame: (frame: TelemetryFramePayload) => void;
  setActiveWSClients: (count: number) => void;
  clearFrames: () => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  frames: [],
  activeWSClients: 0,
  lastFrameTimestamp: null,
  addFrame: (frame) =>
    set((state) => ({
      frames: [frame, ...state.frames].slice(0, 100),
      lastFrameTimestamp: frame.timestamp,
    })),
  setActiveWSClients: (activeWSClients) => set({ activeWSClients }),
  clearFrames: () => set({ frames: [], lastFrameTimestamp: null }),
}));
