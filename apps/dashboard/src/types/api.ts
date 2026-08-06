/**
 * Project GOAT v1.0 — Dashboard API & Telemetry TypeScript Types
 */

export interface TelemetryFramePayload {
  frame_id: string;
  channel: 'SYSTEM' | 'MICROSTRUCTURE' | 'HYPOTHESIS' | 'EVIDENCE' | 'GOVERNANCE' | 'INTELLIGENCE';
  sequence: number;
  timestamp: string;
  payload: Record<string, unknown>;
  cpu_percent?: number;
  memory_mb?: number;
}

export interface APIResponsePayload<T = unknown> {
  payload_id: string;
  route: string;
  status_code: number;
  timestamp: string;
  data: T;
  meta: Record<string, unknown>;
}

export interface DashboardHealthStatusPayload {
  status: 'RUNNING' | 'DEGRADED' | 'INITIALIZING' | 'STOPPED' | 'ERROR';
  uptime_seconds: number;
  active_ws_clients: number;
  system_memory_mb: number;
  database_status: string;
  frozen_backend_version: string;
}

export interface MarketSymbolStatus {
  symbol: string;
  status: 'STREAMING' | 'PAUSED' | 'OFFLINE';
  latency_ms: number;
  data_quality_score: number;
}
