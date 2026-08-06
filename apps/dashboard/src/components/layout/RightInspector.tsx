/**
 * Project GOAT v1.0 — Institutional Right Inspector & Activity Drawer
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState } from 'react';
import { usePipelineStore } from '../../stores/pipelineStore';

export const RightInspector: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'EVENTS' | 'INSPECTOR' | 'TELEMETRY'>('EVENTS');
  const { selectedEntity } = usePipelineStore();

  const events = [
    { type: 'GOVERNANCE', text: 'Candidate HYP_001 promoted to Stage 6 Governance', time: '14:22 UTC', hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' },
    { type: 'VALIDATION', text: 'Live validation session VAL_012 passed stage G anti-cherrypicking check', time: '14:15 UTC', hash: '4f8d92a1c80b91e23f548e69d0c3b2f1e60a28f87140e9d12a9c40026e10b100' },
    { type: 'WARNING', text: 'Telemetry latency spike on websocket stream (34ms)', time: '14:02 UTC', hash: '12a9f8b4c5021e89f07a21c900e12f34b8c91a029e8172f561a09802e19b021e' },
    { type: 'SYSTEM', text: 'Step 1.1 Backend REST & WS telemetry feed synchronized', time: '13:45 UTC', hash: '90827361aefb0927e1029384c7162b901a293847510293847561928374615243' },
  ];

  return (
    <aside className="w-80 bg-[#06090e]/95 backdrop-blur-xl border-l border-slate-800/80 p-4 flex flex-col justify-between overflow-y-auto select-none font-mono text-xs z-20">
      <div>
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 mb-4 pb-1">
          <button
            onClick={() => setActiveTab('EVENTS')}
            className={`flex-1 py-1 text-center font-bold transition-colors ${
              activeTab === 'EVENTS' ? 'text-cyan-400 border-b-2 border-cyan-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            EVENTS
          </button>
          <button
            onClick={() => setActiveTab('INSPECTOR')}
            className={`flex-1 py-1 text-center font-bold transition-colors ${
              activeTab === 'INSPECTOR' ? 'text-cyan-400 border-b-2 border-cyan-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            INSPECTOR
          </button>
          <button
            onClick={() => setActiveTab('TELEMETRY')}
            className={`flex-1 py-1 text-center font-bold transition-colors ${
              activeTab === 'TELEMETRY' ? 'text-cyan-400 border-b-2 border-cyan-500' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            METRICS
          </button>
        </div>

        {/* Tab 1: Events Log */}
        {activeTab === 'EVENTS' && (
          <div className="space-y-3">
            <div className="flex justify-between items-center text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-2">
              <span>REAL-TIME AUDIT LOG</span>
              <span className="text-emerald-400">● LIVE</span>
            </div>
            {events.map((ev, idx) => (
              <div key={idx} className="bg-slate-900/80 border border-slate-800 p-2.5 rounded-md hover:border-slate-700 transition-all">
                <div className="flex justify-between items-center mb-1">
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                      ev.type === 'GOVERNANCE'
                        ? 'bg-purple-950 text-purple-300 border border-purple-800'
                        : ev.type === 'WARNING'
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : ev.type === 'VALIDATION'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                    }`}
                  >
                    {ev.type}
                  </span>
                  <span className="text-[10px] text-slate-500">{ev.time}</span>
                </div>
                <div className="text-slate-300 text-[11px] font-sans mb-1">{ev.text}</div>
                <div className="text-[9px] text-slate-600 truncate">SHA-256: {ev.hash}</div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 2: Entity Inspector Details */}
        {activeTab === 'INSPECTOR' && (
          <div>
            {selectedEntity ? (
              <div className="space-y-3 bg-slate-900/80 border border-slate-800 p-3 rounded-md">
                <div className="text-cyan-400 font-bold text-sm">{selectedEntity.canonicalId}</div>
                <div className="text-slate-300 font-medium font-sans text-xs">{selectedEntity.title}</div>
                <div className="text-[10px] text-slate-500">STAGE: <span className="text-slate-200">{selectedEntity.stage}</span></div>
                <div className="text-[10px] text-slate-500">STATUS: <span className="text-emerald-400">{selectedEntity.status}</span></div>
                <div className="border-t border-slate-800 pt-2 text-[10px] text-slate-400">
                  <div className="font-bold text-slate-300 mb-1">METADATA</div>
                  <pre className="text-[9px] bg-slate-950 p-2 rounded border border-slate-800 overflow-x-auto text-cyan-300">
                    {JSON.stringify(selectedEntity.metadata || {}, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs">
                SELECT AN ENTITY IN PIPELINE GRAPH OR DATA GRID TO INSPECT LINEAGE AND METADATA
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Telemetry Quick Metrics */}
        {activeTab === 'TELEMETRY' && (
          <div className="space-y-3">
            <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-md space-y-2">
              <div className="text-xs font-bold text-slate-200">RESEARCH ENGINE TELEMETRY</div>
              <div className="flex justify-between text-slate-400">
                <span>CPU Load:</span>
                <span className="text-cyan-400">14.2%</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>RAM Usage:</span>
                <span className="text-cyan-400">412 MB / 8 GB</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>WS Frame Rate:</span>
                <span className="text-emerald-400">60 FPS</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>SQLite Connections:</span>
                <span className="text-emerald-400">8 Idle / 2 Active</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-6 pt-3 border-t border-slate-800/80 text-[10px] text-slate-500 font-mono flex justify-between">
        <span>INSPECTOR BUS: ONLINE</span>
        <span className="text-emerald-400">100% DETERMINISTIC</span>
      </div>
    </aside>
  );
};
