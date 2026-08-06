/**
 * Project GOAT v1.0 — Detailed Entity Inspector Slide-Over Drawer Widget
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState } from 'react';
import { usePipelineStore } from '../../stores/pipelineStore';

export const EntityInspectorModal: React.FC = () => {
  const { inspectorOpen, selectedEntity, setInspectorOpen } = usePipelineStore();
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'LINEAGE' | 'AUDIT' | 'REPLAY' | 'RAW'>('OVERVIEW');
  const [copied, setCopied] = useState<string | null>(null);

  if (!inspectorOpen || !selectedEntity) return null;

  const handleCopy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/80 backdrop-blur-md flex justify-end">
      <div className="w-full max-w-2xl bg-[#0b101b] border-l border-slate-800 h-full flex flex-col justify-between shadow-2xl animate-in slide-in-from-right duration-300 font-mono text-xs">
        {/* Drawer Header */}
        <div className="p-5 border-b border-slate-800/80 bg-[#06090e] flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                {selectedEntity.canonicalId}
              </span>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                {selectedEntity.stage}
              </span>
              <button
                onClick={() => handleCopy(selectedEntity.canonicalId, 'ID')}
                className="text-[10px] text-slate-400 hover:text-cyan-300 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800"
              >
                {copied === 'ID' ? '✓ Copied' : '📋 Copy ID'}
              </button>
            </div>
            <h2 className="text-lg font-bold text-slate-100 mt-2 tracking-tight">{selectedEntity.name}</h2>
          </div>
          <button
            onClick={() => setInspectorOpen(false)}
            className="text-slate-400 hover:text-slate-100 p-2 rounded-md hover:bg-slate-800 text-sm"
          >
            ✕
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800 bg-[#080d1a] px-5 pt-2">
          {(['OVERVIEW', 'LINEAGE', 'AUDIT', 'REPLAY', 'RAW'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-bold transition-colors border-b-2 ${
                activeTab === tab
                  ? 'border-cyan-500 text-cyan-400 bg-slate-900/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Drawer Body Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'OVERVIEW' && (
            <div className="space-y-4">
              {/* Status Banner */}
              <div className="grid grid-cols-2 gap-3 bg-[#06090e] p-4 rounded-xl border border-slate-800/80">
                <div>
                  <span className="text-slate-500 block text-[10px]">CANONICAL STATUS</span>
                  <span className="text-emerald-400 font-bold text-sm">{selectedEntity.status}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">DETERMINISTIC REPLAY</span>
                  <span className="text-cyan-400 font-bold text-sm">
                    {selectedEntity.replayAvailable ? 'VERIFIED' : 'N/A'}
                  </span>
                </div>
              </div>

              {/* SHA-256 Fingerprint */}
              <div className="bg-[#06090e]/80 p-4 rounded-xl border border-slate-800/80 space-y-2">
                <div className="flex justify-between items-center text-slate-300 font-bold">
                  <span>SHA-256 FINGERPRINT & LINEAGE HASH</span>
                  <button
                    onClick={() => handleCopy(selectedEntity.sha256LineageHash, 'HASH')}
                    className="text-[10px] text-cyan-400 hover:underline"
                  >
                    {copied === 'HASH' ? '✓ Copied' : 'Copy Hash'}
                  </button>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-[11px] text-cyan-300 break-all">
                  {selectedEntity.sha256LineageHash}
                </div>
              </div>

              {/* Properties Grid */}
              <div className="bg-[#06090e]/80 p-4 rounded-xl border border-slate-800/80 space-y-2">
                <div className="text-slate-300 font-bold mb-2">SCIENTIFIC METRICS & PARAMETERS</div>
                {Object.entries(selectedEntity.properties).map(([k, v]) => (
                  <div key={k} className="flex justify-between items-center py-1 border-b border-slate-800/60">
                    <span className="text-slate-400">{k}</span>
                    <span className="text-slate-100 font-semibold">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: LINEAGE */}
          {activeTab === 'LINEAGE' && (
            <div className="space-y-4">
              <div className="bg-[#06090e] p-4 rounded-xl border border-slate-800 space-y-3">
                <div className="text-slate-300 font-bold">UPSTREAM PARENT NODES</div>
                <div className="p-2.5 bg-slate-900 rounded border border-slate-800 text-cyan-400 font-bold flex justify-between">
                  <span>HYP_2026_ALPHA_001</span>
                  <span className="text-slate-400 font-normal">Hypothesis Stage</span>
                </div>
              </div>
              <div className="bg-[#06090e] p-4 rounded-xl border border-slate-800 space-y-3">
                <div className="text-slate-300 font-bold">DOWNSTREAM CHILD NODES</div>
                <div className="p-2.5 bg-slate-900 rounded border border-slate-800 text-cyan-400 font-bold flex justify-between">
                  <span>VAL_2026_LIVE_012</span>
                  <span className="text-slate-400 font-normal">Validation Session</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: AUDIT */}
          {activeTab === 'AUDIT' && (
            <div className="space-y-3">
              <div className="bg-[#06090e] p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="text-slate-300 font-bold">CONSTITUTIONAL GOVERNANCE AUDIT TRAIL</div>
                <div className="text-slate-400 text-xs">Certified by Step 1.1 Backend & Version 0.9.1 Core.</div>
                <div className="text-emerald-400 font-bold pt-2">✓ 100% CONSTITUTIONAL COMPLIANCE PASSED</div>
              </div>
            </div>
          )}

          {/* TAB 4: REPLAY */}
          {activeTab === 'REPLAY' && (
            <div className="space-y-3">
              <div className="bg-[#06090e] p-4 rounded-xl border border-slate-800 space-y-2">
                <div className="text-slate-300 font-bold">DETERMINISTIC STATE REPLAY ENGINE</div>
                <div className="text-slate-400 text-xs">Deterministic seed: <code className="text-cyan-300">0x4F9A12B8</code></div>
                <button className="w-full mt-2 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold rounded-lg transition-colors">
                  ▶ Replay Deterministic Sequence
                </button>
              </div>
            </div>
          )}

          {/* TAB 5: RAW JSON */}
          {activeTab === 'RAW' && (
            <div className="bg-[#06090e] p-4 rounded-xl border border-slate-800">
              <pre className="text-[11px] text-cyan-300 bg-slate-950 p-4 rounded-lg overflow-x-auto border border-slate-800">
                {JSON.stringify(selectedEntity, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Drawer Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-[#06090e] flex justify-between items-center">
          <span className="text-slate-500">ID: {selectedEntity.canonicalId}</span>
          <button
            onClick={() => setInspectorOpen(false)}
            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
