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
  status: 'INITIALIZING',
  uptimeSeconds: 0.0,
  memoryMb: 0.0,
  databaseStatus: 'UNKNOWN',
  frozenBackendVersion: 'v1.2.0',
  setHealth: (health) =>
    set({
      status: health.status,
      uptimeSeconds: health.uptime_seconds,
      memoryMb: health.system_memory_mb,
      databaseStatus: health.database_status,
      frozenBackendVersion: health.frozen_backend_version,
    }),
}));
