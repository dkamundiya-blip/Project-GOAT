/**
 * Project GOAT v1.0 — Dashboard Session State Store
 */

import { create } from 'zustand';

interface SessionState {
  sessionId: string;
  host: string;
  port: number;
  userRole: string;
  startTime: string;
  setSession: (sessionId: string, host: string, port: number, userRole?: string) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: 'DSH_DEFAULT_SESSION',
  host: '127.0.0.1',
  port: 8000,
  userRole: 'CHIEF_QUANTITATIVE_OFFICER',
  startTime: new Date().toISOString(),
  setSession: (sessionId, host, port, userRole = 'CHIEF_QUANTITATIVE_OFFICER') =>
    set({ sessionId, host, port, userRole }),
}));
