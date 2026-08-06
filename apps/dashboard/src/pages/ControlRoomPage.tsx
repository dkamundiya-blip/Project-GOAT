import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { useSymbolStore } from '../stores/symbolStore';
import { useMarketData } from '../hooks/useMarketData';
import { TradingViewContainer } from '../charting/TradingViewContainer';
import { Play, Square, RefreshCw, Radio, RadioTower, CheckCircle2, ShieldAlert } from 'lucide-react';

export const ControlRoomPage: React.FC = () => {
  const { currentSymbol } = useSymbolStore();
  const { connectionState, connect, disconnect, reconnect, subscribe, unsubscribe } = useMarketData();
  const [log, setLog] = useState<string[]>([
    `[${new Date().toISOString()}] Control Room Ingestion Operator initialized.`,
    `[${new Date().toISOString()}] Non-execution safety protocol active (Amendments No.001 & No.002).`,
  ]);

  const addLog = (msg: string) => {
    setLog((prev) => [`[${new Date().toISOString()}] ${msg}`, ...prev.slice(0, 49)]);
  };

  const handleConnect = async () => {
    addLog('Operator command: CONNECT WebSocket Feed...');
    const res = await connect();
    addLog(`Feed connection status: ${res.connection_state}`);
  };

  const handleDisconnect = async () => {
    addLog('Operator command: DISCONNECT WebSocket Feed...');
    await disconnect();
    addLog('Feed disconnected by operator command.');
  };

  const handleReconnect = async () => {
    addLog('Operator command: RECONNECT WebSocket Feed...');
    const res = await reconnect();
    addLog(`Reconnected feed status: ${res.connection_state}`);
  };

  const handleSubscribeCurrent = async () => {
    addLog(`Operator command: SUBSCRIBE symbol ${currentSymbol}...`);
    await subscribe(currentSymbol);
    addLog(`Subscribed to stream: ${currentSymbol}`);
  };

  const handleUnsubscribeCurrent = async () => {
    addLog(`Operator command: UNSUBSCRIBE symbol ${currentSymbol}...`);
    await unsubscribe(currentSymbol);
    addLog(`Unsubscribed from stream: ${currentSymbol}`);
  };

  const handleRefreshStatus = () => {
    addLog('Operator command: REFRESH STATUS refreshed telemetry frame.');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            Operator Control Room
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                connectionState === 'CONNECTED' ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500 animate-ping'
              }`}
            />
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time operator command workstation, market stream controller, and feed status monitoring.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={connectionState === 'CONNECTED' ? 'success' : 'danger'}>
            {connectionState}
          </Badge>
          <Badge variant="primary">{currentSymbol}</Badge>
        </div>
      </div>

      {/* Control Actions Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Connection Commands */}
        <Card title="Feed Stream Controls" subtitle="Deriv WebSocket Feed Manager">
          <div className="mt-3 flex flex-wrap gap-2">
            <Button variant="primary" size="sm" onClick={handleConnect} className="gap-1.5">
              <Play className="w-3.5 h-3.5" /> Connect
            </Button>
            <Button variant="outline" size="sm" onClick={handleDisconnect} className="gap-1.5 text-rose-400 border-rose-800 hover:bg-rose-950">
              <Square className="w-3.5 h-3.5" /> Disconnect
            </Button>
            <Button variant="secondary" size="sm" onClick={handleReconnect} className="gap-1.5">
              <RefreshCw className="w-3.5 h-3.5" /> Reconnect
            </Button>
          </div>
        </Card>

        {/* Subscription Commands */}
        <Card title="Stream Subscription" subtitle={`Active Instrument: ${currentSymbol}`}>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button variant="secondary" size="sm" onClick={handleSubscribeCurrent} className="gap-1.5">
              <Radio className="w-3.5 h-3.5 text-emerald-400" /> Subscribe
            </Button>
            <Button variant="ghost" size="sm" onClick={handleUnsubscribeCurrent} className="gap-1.5">
              <RadioTower className="w-3.5 h-3.5 text-amber-400" /> Unsubscribe
            </Button>
          </div>
        </Card>

        {/* System Telemetry Actions */}
        <Card title="Operational Controls" subtitle="Telemetry & Diagnostic Control">
          <div className="mt-3 flex flex-wrap gap-2">
            <Button variant="secondary" size="sm" onClick={handleRefreshStatus} className="gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> Refresh Status
            </Button>
          </div>
        </Card>
      </div>

      {/* Operator Live Chart Preview */}
      <Card title="Operator Stream Live Chart Inspection" subtitle={`Instrument: ${currentSymbol}`}>
        <TradingViewContainer initialSymbol={currentSymbol} initialTimeframe="1M" className="h-[450px]" />
      </Card>

      {/* Safety Gate & Rules Notice */}
      <Card title="Production Governance & Execution Safety Gate" subtitle="Institutional Operating Constraints">
        <div className="flex items-start gap-3 p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1 text-slate-300">
            <div className="font-semibold text-slate-100">STRICT MARKET DATA INGESTION ONLY MODE</div>
            <p className="text-slate-400">
              This control room ONLY manages market price data streaming, WebSocket connection recovery, and ingestion persistence.
              Signal generation, trade execution, machine learning models, and automated order routing are strictly disabled per Constitutional Amendments No.001 & No.002.
            </p>
          </div>
        </div>
      </Card>

      {/* Operator Console Log */}
      <Card title="Operator Stream Log" subtitle="Real-time control event audit log">
        <div className="bg-[#04060a] p-4 rounded-lg font-mono text-xs text-slate-300 h-48 overflow-y-auto space-y-1.5 border border-slate-800">
          {log.map((entry, idx) => (
            <div key={idx} className="flex items-center gap-2">
              <span className="text-slate-500 font-bold">&gt;</span>
              <span className={entry.includes('CONNECTED') ? 'text-emerald-400' : entry.includes('DISCONNECT') ? 'text-rose-400' : 'text-slate-300'}>
                {entry}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
export default ControlRoomPage;
