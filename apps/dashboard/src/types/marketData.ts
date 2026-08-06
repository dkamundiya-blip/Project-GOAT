/**
 * Project GOAT v1.0 — Market Data Subsystem Types
 */

export interface LiveQuoteDTO {
  symbol: string;
  deriv_ws_symbol: string;
  live_price: number;
  bid: number;
  ask: number;
  spread: number;
  connection_status: 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING' | 'DEGRADED';
  latency_ms: number;
  tick_frequency: number;
  streaming_status: 'STREAMING' | 'PAUSED' | 'IDLE' | 'ERROR';
  last_tick_time: string;
  total_ticks: number;
}

export interface IngestionTelemetryDTO {
  total_ticks_received: number;
  ticks_per_second: number;
  websocket_uptime_seconds: number;
  dropped_packets: number;
  reconnect_count: number;
  cpu_usage_percent: number;
  memory_usage_mb: number;
  queue_size: number;
  buffer_size: number;
  database_writes_per_second: number;
  average_latency_ms: number;
  maximum_latency_ms: number;
  timestamp: string;
}

export interface LiveTickDTO {
  tick_id: string;
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  spread: number;
  epoch_timestamp: number;
  arrival_timestamp: string;
  sequence_number: number;
  connection_id: string;
  latency_ms: number;
  checksum: string;
  canonical_hash: string;
}
