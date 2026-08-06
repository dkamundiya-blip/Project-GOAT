import React from 'react';
import { Card } from '../components/ui/Card';
import { Table } from '../components/ui/Table';
import { Badge } from '../components/ui/Badge';
import { KPICard } from '../components/ui/KPICard';
import { useMarketData } from '../hooks/useMarketData';
import { LiveQuoteDTO } from '../types/marketData';
import { TradingViewContainer } from '../charting/TradingViewContainer';
import { OrderTicketWidget } from '../components/widgets/OrderTicketWidget';

export const MarketsPage: React.FC = () => {
  const { quotes, telemetry } = useMarketData(1500);

  const getIndexType = (symbol: string) => {
    if (symbol.startsWith('BOOM') || symbol.startsWith('CRASH')) return 'SPIKE INDEX';
    if (symbol.includes('STEP')) return 'STEP INDEX';
    return 'VOLATILITY INDEX';
  };

  const columns: any = [
    {
      key: 'symbol',
      header: 'Symbol',
      render: (row: LiveQuoteDTO) => (
        <div className="flex flex-col">
          <span className="font-mono font-bold text-slate-100">{row.symbol}</span>
          <span className="text-[10px] text-slate-400 font-mono">Deriv: {row.deriv_ws_symbol}</span>
        </div>
      ),
    },
    {
      key: 'indexType',
      header: 'Index Type',
      render: (row: LiveQuoteDTO) => (
        <span className="text-xs font-semibold text-cyan-400">{getIndexType(row.symbol)}</span>
      ),
    },
    {
      key: 'live_price',
      header: 'Live Price',
      render: (row: LiveQuoteDTO) => (
        <div className="flex flex-col">
          <span className="font-mono font-bold text-indigo-400 tabular-nums">
            {row.live_price > 0 ? row.live_price.toFixed(4) : '—'}
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            B: {row.bid.toFixed(2)} | A: {row.ask.toFixed(2)}
          </span>
        </div>
      ),
    },
    {
      key: 'connection_status',
      header: 'Connection',
      render: (row: LiveQuoteDTO) => (
        <Badge variant={row.connection_status === 'CONNECTED' ? 'success' : 'warning'}>
          {row.connection_status}
        </Badge>
      ),
    },
    {
      key: 'latency_ms',
      header: 'Latency',
      render: (row: LiveQuoteDTO) => (
        <span className="font-mono text-xs text-slate-300 tabular-nums">
          {row.latency_ms > 0 ? `${row.latency_ms.toFixed(1)} ms` : '—'}
        </span>
      ),
    },
    {
      key: 'tick_frequency',
      header: 'Tick Frequency',
      render: (row: LiveQuoteDTO) => (
        <span className="font-mono text-xs text-emerald-400 tabular-nums font-semibold">
          {row.tick_frequency.toFixed(1)} t/s
        </span>
      ),
    },
    {
      key: 'streaming_status',
      header: 'Streaming Status',
      render: (row: LiveQuoteDTO) => (
        <div className="flex items-center gap-1.5">
          <span
            className={`w-2 h-2 rounded-full ${
              row.streaming_status === 'STREAMING' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
            }`}
          />
          <span className="text-xs font-medium text-slate-200">{row.streaming_status}</span>
        </div>
      ),
    },
    {
      key: 'last_tick_time',
      header: 'Last Tick Time',
      render: (row: LiveQuoteDTO) => (
        <span className="font-mono text-[11px] text-slate-400">
          {row.last_tick_time ? row.last_tick_time.substring(11, 19) + ' UTC' : '—'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          Deriv Live Market Data & Charting Workspace
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Institutional multi-timeframe TradingView charting, real-time tick streaming, and feed metrics for Deriv synthetic indices.
        </p>
      </div>

      {/* KPI Overview Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <KPICard
          title="Total Ticks Ingested"
          value={telemetry?.total_ticks_received.toLocaleString() || '0'}
          subValue="LIVE INGESTION"
          icon="📊"
        />
        <KPICard
          title="Throughput Rate"
          value={`${telemetry?.ticks_per_second.toFixed(1) || '0.0'} t/s`}
          subValue="STREAM FREQUENCY"
          icon="⚡"
        />
        <KPICard
          title="WebSocket Uptime"
          value={`${((telemetry?.websocket_uptime_seconds || 0) / 60).toFixed(1)} m`}
          subValue="CONNECTED"
          icon="📡"
        />
        <KPICard
          title="Dropped Packets"
          value={telemetry?.dropped_packets.toString() || '0'}
          subValue="PACKET INTEGRITY"
          icon="📦"
        />
        <KPICard
          title="Reconnect Count"
          value={telemetry?.reconnect_count.toString() || '0'}
          subValue="RESILIENCE OK"
          icon="🔄"
        />
      </div>

      {/* Institutional TradingView Charting Engine */}
      <Card title="Institutional TradingView Interactive Chart" subtitle="Multi-timeframe streaming charting engine">
        <TradingViewContainer initialSymbol="VOLATILITY_100" initialTimeframe="1M" />
      </Card>

      {/* Institutional Order Execution & Position Panel */}
      <OrderTicketWidget />

      {/* Synthetic Instruments Table */}
      <Card title="Live Synthetic Instruments Catalogue" subtitle="Real-time quotes & stream metrics">
        <Table columns={columns} data={quotes as any} />
      </Card>
    </div>
  );
};
export default MarketsPage;
