/**
 * Project GOAT v1.0 — Connection & Subsystem Health Monitor
 */

export interface SubsystemHealthMetrics {
  connectionStatus: 'ONLINE' | 'DEGRADED' | 'OFFLINE';
  latencyMs: number;
  reconnectCount: number;
  heartbeatAgeMs: number;
  lastSyncTimestamp: string;
}

export class HealthMonitor {
  private metrics: SubsystemHealthMetrics = {
    connectionStatus: 'ONLINE',
    latencyMs: 12,
    reconnectCount: 0,
    heartbeatAgeMs: 150,
    lastSyncTimestamp: new Date().toISOString(),
  };

  getMetrics(): SubsystemHealthMetrics {
    return { ...this.metrics };
  }

  recordLatency(ms: number): void {
    this.metrics.latencyMs = ms;
  }

  recordHeartbeat(): void {
    this.metrics.heartbeatAgeMs = 0;
    this.metrics.lastSyncTimestamp = new Date().toISOString();
  }

  recordReconnect(): void {
    this.metrics.reconnectCount += 1;
  }
}

export const healthMonitor = new HealthMonitor();
