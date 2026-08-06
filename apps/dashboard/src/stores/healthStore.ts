/**
 * Project GOAT v1.0 — System Health State Store
 */

import { create } from 'zustand';
import { DashboardHealthStatusPayload } from '../types/api';

interface HealthState {
  status: 'RUNNING' | 'DEGRADED' | 'INITIALIZING' | 'STOPPED' | 'ERROR';
  uptimeSeconds: number;
  memoryMb: number;
  databaseStatus: string;
  frozenBackendVersion: string;
  setHealth: (health: DashboardHealthStatusPayload) => void;
}

export const useHealthStore = create<HealthState>((set) => ({
  status: 'RUNNING',
  uptimeSeconds: 120.0,
  memoryMb: 128.5,
  databaseStatus: 'HEALTHY',
  frozenBackendVersion: 'v0.9.1',
  setHealth: (health) =>
    set({
      status: health.status,
      uptimeSeconds: health.uptime_seconds,
      memoryMb: health.system_memory_mb,
      databaseStatus: health.database_status,
      frozenBackendVersion: health.frozen_backend_version,
    }),
}));
