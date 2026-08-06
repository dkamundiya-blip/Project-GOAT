/**
 * Project GOAT v1.0 — Real-Time Telemetry Stream & Resource Widget
 */

import React from 'react';
import { useTelemetryStore } from '../../stores/telemetryStore';
import { useHealthStore } from '../../stores/healthStore';

export const LiveTelemetryChart: React.FC = () => {
  const frames = useTelemetryStore((state) => state.frames);
  const health = useHealthStore();

  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4 mb-6 shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan-400">
          Real-Time System Telemetry Feed
        </h3>
        <div className="flex items-center space-x-4 text-xs text-slate-400">
          <span>Uptime: {health.uptimeSeconds.toFixed(1)}s</span>
          <span>Memory: {health.memoryMb.toFixed(1)} MB</span>
          <span>Status: <strong className="text-emerald-400">{health.status}</strong></span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider">
            <tr>
              <th className="py-2 px-3">Frame ID</th>
              <th className="py-2 px-3">Channel</th>
              <th className="py-2 px-3">Sequence</th>
              <th className="py-2 px-3">Timestamp</th>
              <th className="py-2 px-3">Payload Summary</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {frames.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-4 text-center text-slate-500">
                  Telemetry stream connected. Awaiting frame updates from Step 1.1 backend...
                </td>
              </tr>
            ) : (
              frames.slice(0, 5).map((frame) => (
                <tr key={frame.frame_id} className="hover:bg-slate-850">
                  <td className="py-2 px-3 font-mono text-cyan-400">{frame.frame_id}</td>
                  <td className="py-2 px-3"><span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">{frame.channel}</span></td>
                  <td className="py-2 px-3">{frame.sequence}</td>
                  <td className="py-2 px-3 text-slate-400">{new Date(frame.timestamp).toLocaleTimeString()}</td>
                  <td className="py-2 px-3 font-mono text-slate-400 truncate max-w-xs">
                    {JSON.stringify(frame.payload)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
