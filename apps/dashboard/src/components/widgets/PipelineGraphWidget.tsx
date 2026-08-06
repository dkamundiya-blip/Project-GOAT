/**
 * Project GOAT v1.0 — Institutional 8-Stage Research Pipeline Visualizer
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState } from 'react';
import { PipelineStage } from '../../types/pipeline';
import { usePipelineStore } from '../../stores/pipelineStore';

interface PipelineStageNode {
  stage: PipelineStage;
  label: string;
  sublabel: string;
  icon: string;
  count: number;
  health: number;
  throughput: string;
  status: 'NOMINAL' | 'ACTIVE' | 'ELEVATED';
}

const STAGES: PipelineStageNode[] = [
  { stage: 'HYPOTHESIS', label: 'Research', sublabel: 'Formulation', icon: '🔬', count: 142, health: 99.2, throughput: '14/hr', status: 'NOMINAL' },
  { stage: 'EVIDENCE', label: 'Evidence', sublabel: 'Ingestion', icon: '📑', count: 12850, health: 100, throughput: '1.4 MB/s', status: 'NOMINAL' },
  { stage: 'EXPERIMENT', label: 'Experiments', sublabel: 'Execution', icon: '🧪', count: 840, health: 98.6, throughput: '60/min', status: 'ACTIVE' },
  { stage: 'STATISTICAL_EVALUATION', label: 'Statistics', sublabel: 'Evaluation', icon: '📈', count: 412, health: 99.5, throughput: '12/min', status: 'NOMINAL' },
  { stage: 'LIVE_VALIDATION', label: 'Validation', sublabel: 'Holdout Test', icon: '⚡', count: 48, health: 100, throughput: '3 active', status: 'ACTIVE' },
  { stage: 'GOVERNANCE', label: 'Governance', sublabel: 'Audit & Vote', icon: '⚖️', count: 18, health: 100, throughput: '2 pending', status: 'NOMINAL' },
  { stage: 'ARCHIVE', label: 'Archive', sublabel: 'Immutability', icon: '📦', count: 4500, health: 100, throughput: '0.2 MB/s', status: 'NOMINAL' },
  { stage: 'RESEARCH_INTELLIGENCE', label: 'Intelligence', sublabel: 'Synthesis', icon: '💡', count: 86, health: 98.9, throughput: 'Real-time', status: 'NOMINAL' },
];

export const PipelineGraphWidget: React.FC = () => {
  const { selectedEdgeId, edges, setSelectedEdge, filterStage, setFilterStage } = usePipelineStore();
  const selectedEdge = edges.find((e) => e.edgeId === selectedEdgeId);
  const [hoveredStage, setHoveredStage] = useState<PipelineStage | null>(null);

  return (
    <div className="bg-[#0b101b]/90 border border-slate-800/80 rounded-xl p-6 shadow-xl backdrop-blur-md">
      {/* Widget Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-cyan-400 animate-ping" />
            <h3 className="text-base font-bold text-slate-100 font-mono tracking-tight flex items-center gap-2">
              SCIENTIFIC RESEARCH PIPELINE VISUALIZATION ENGINE
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Deterministic 8-stage lineage graph tracking hypotheses through empirical evidence to governance promotion.
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="text-slate-500">FILTER STAGE:</span>
          <span className="text-cyan-400 font-bold bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
            {filterStage}
          </span>
          {filterStage !== 'ALL' && (
            <button
              onClick={() => setFilterStage('ALL')}
              className="text-slate-400 hover:text-slate-200 underline text-[11px]"
            >
              Reset Filter
            </button>
          )}
        </div>
      </div>

      {/* Interactive 8-Stage Pipeline Flow */}
      <div className="relative mb-8">
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {STAGES.map((node, index) => {
            const isActive = selectedEdge?.currentStage === node.stage;
            const isFiltered = filterStage === node.stage;
            const isHovered = hoveredStage === node.stage;

            return (
              <div
                key={node.stage}
                onMouseEnter={() => setHoveredStage(node.stage)}
                onMouseLeave={() => setHoveredStage(null)}
                className="relative"
              >
                <button
                  onClick={() => setFilterStage(filterStage === node.stage ? 'ALL' : node.stage)}
                  className={`w-full flex flex-col items-center p-3.5 rounded-xl border text-center transition-all duration-300 ${
                    isActive
                      ? 'bg-cyan-950/90 border-cyan-400 shadow-lg shadow-cyan-500/20 ring-2 ring-cyan-500/50 scale-105'
                      : isFiltered
                      ? 'bg-slate-800 border-cyan-500 text-cyan-300 shadow-md'
                      : isHovered
                      ? 'bg-slate-800/80 border-slate-700 text-slate-100 scale-[1.02]'
                      : 'bg-[#06090e]/80 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <span className="text-2xl mb-1.5 filter drop-shadow">{node.icon}</span>
                  <span className="text-xs font-mono font-bold tracking-tight text-slate-100">{node.label}</span>
                  <span className="text-[10px] font-mono text-slate-500 mb-2">{node.sublabel}</span>

                  <div className="w-full flex items-center justify-between font-mono text-[10px] bg-slate-950/80 px-2 py-1 rounded border border-slate-800/80">
                    <span className="text-cyan-400 font-bold">{node.count.toLocaleString()}</span>
                    <span className="text-emerald-400 font-semibold">{node.health}%</span>
                  </div>
                </button>

                {/* Connected Flow Arrow Indicator */}
                {index < STAGES.length - 1 && (
                  <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 pointer-events-none">
                    <span className="text-cyan-500 text-xs animate-pulse">▶</span>
                  </div>
                )}

                {/* Hover Detail Tooltip */}
                {isHovered && (
                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-48 bg-[#0e1626] border border-cyan-500/50 p-3 rounded-lg shadow-2xl z-30 font-mono text-[11px] space-y-1">
                    <div className="text-cyan-400 font-bold border-b border-slate-800 pb-1">{node.label} Stage Details</div>
                    <div className="flex justify-between text-slate-400">
                      <span>Total Entities:</span>
                      <span className="text-slate-200">{node.count}</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Throughput:</span>
                      <span className="text-slate-200">{node.throughput}</span>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Integrity Health:</span>
                      <span className="text-emerald-400">{node.health}%</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Active Edges Stream */}
      <div className="border-t border-slate-800/80 pt-5">
        <div className="flex items-center justify-between mb-3">
          <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider">
            CANONICAL CANDIDATE EDGES IN PIPELINE ({edges.length})
          </div>
          {selectedEdgeId && (
            <button
              onClick={() => setSelectedEdge('')}
              className="text-[11px] font-mono text-slate-400 hover:text-slate-200 underline"
            >
              Deselect Edge
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {edges.map((edge) => (
            <div
              key={edge.edgeId}
              onClick={() => setSelectedEdge(edge.edgeId)}
              className={`p-4 rounded-xl border cursor-pointer transition-all duration-200 ${
                selectedEdgeId === edge.edgeId
                  ? 'bg-slate-800/90 border-cyan-500 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-500/40'
                  : 'bg-[#06090e]/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/40'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-mono font-bold text-cyan-300 tracking-wider">{edge.symbol}</span>
                <span
                  className={`text-[9.5px] font-mono font-bold px-2 py-0.5 rounded border uppercase ${
                    edge.status === 'PROMOTED'
                      ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                      : 'bg-cyan-950/80 text-cyan-300 border-cyan-800'
                  }`}
                >
                  {edge.currentStage}
                </span>
              </div>
              <div className="text-xs text-slate-400 font-mono mb-3 truncate">{edge.edgeId}</div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800 mb-2">
                <div
                  className="bg-gradient-to-r from-cyan-500 via-blue-500 to-emerald-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${edge.progressPercent}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[10.5px] text-slate-400 font-mono">
                <span>Sharpe: <strong className="text-slate-200">{edge.sharpeRatio.toFixed(2)}</strong></span>
                <span>p-val: <strong className="text-slate-200">{edge.pValue}</strong></span>
                <span className="text-cyan-400 font-semibold">{edge.progressPercent}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
