/**
 * Project GOAT v1.0 — System Monitoring Workspace
 */

import React from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { KPICard } from '../components/ui/KPICard';
import { Card } from '../components/ui/Card';
import { TradingViewWidget } from '../charting/TradingViewWidget';
import { Layers, HardDrive, Clock, Server } from 'lucide-react';

export const MonitoringPage: React.FC = () => {
  const { telemetry } = useMarketData(2000);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Server className="w-5 h-5 text-cyan-400" />
            <span>SYSTEM TELEMETRY & INGESTION MONITORING</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time process resources, buffer queue capacity, SQLite write throughput, and network latency monitoring.
          </p>
        </div>
      </div>

      {/* Resource Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          title="CPU Usage"
          value={`${telemetry?.cpu_usage_percent.toFixed(1) || '0.0'}%`}
          subValue="PROCESS CONSUMPTION"
          icon="🖥️"
        />
        <KPICard
          title="Memory Consumption"
          value={`${telemetry?.memory_usage_mb.toFixed(1) || '0.0'} MB`}
          subValue="RAM ALLOCATION"
          icon="💾"
        />
        <KPICard
          title="Database Writes / sec"
          value={`${telemetry?.database_writes_per_second.toFixed(1) || '0.0'} w/s`}
          subValue="SQLITE BATCH WRITE"
          icon="🗄️"
        />
        <KPICard
          title="Average Latency"
          value={`${telemetry?.average_latency_ms.toFixed(1) || '0.0'} ms`}
          subValue={`MAX: ${telemetry?.maximum_latency_ms.toFixed(1) || '0.0'} ms`}
          icon="📈"
        />
      </div>

      {/* Live Chart Stream Verification */}
      <Card title="Live Stream Interactive Frequency Inspection" subtitle="Monitoring Volatility 100 1-Minute tick stream">
        <div className="h-80 w-full overflow-hidden rounded-lg">
          <TradingViewWidget symbol="VOLATILITY_100" timeframe="1M" chartStyle="candlestick" height={320} />
        </div>
      </Card>

      {/* Buffer & Queue Capacity Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Ingestion Queue Size" subtitle="Async message buffer">
          <div className="mt-2 flex items-center justify-between">
            <div className="text-2xl font-bold text-slate-100 tabular-nums">{telemetry?.queue_size || 0}</div>
            <Layers className="w-6 h-6 text-slate-500" />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">Zero pending queue indicates zero backpressure.</p>
        </Card>

        <Card title="Persistence Buffer Size" subtitle="Un-flushed batch queue">
          <div className="mt-2 flex items-center justify-between">
            <div className="text-2xl font-bold text-slate-100 tabular-nums">{telemetry?.buffer_size || 0}</div>
            <HardDrive className="w-6 h-6 text-slate-500" />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">Maximum batch capacity: 50 ticks / 2s timer flush.</p>
        </Card>

        <Card title="WebSocket Feed Uptime" subtitle="Continuous connection duration">
          <div className="mt-2 flex items-center justify-between">
            <div className="text-2xl font-bold text-emerald-400 tabular-nums">
              {((telemetry?.websocket_uptime_seconds || 0) / 60).toFixed(1)} min
            </div>
            <Clock className="w-6 h-6 text-emerald-500" />
          </div>
          <p className="text-[11px] text-slate-400 mt-2">Active heartbeats verified every 20s.</p>
        </Card>
      </div>
    </div>
  );
};
export default MonitoringPage;
