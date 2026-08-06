/**
 * Project GOAT v1.0 — Institutional Knowledge Graph & Relationship Viewer Widget
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState } from 'react';
import { usePipelineStore } from '../../stores/pipelineStore';

export const RelationshipViewerWidget: React.FC = () => {
  const { relationships, selectedEntity, inspectEntityById } = usePipelineStore();
  const [zoomLevel, setZoomLevel] = useState(100);
  const [highlightedId, setHighlightedId] = useState<string | null>(null);

  const graphNodes = [
    { id: 'HYP_001', label: 'Hypothesis 001', x: 80, y: 120, stage: 'HYPOTHESIS' },
    { id: 'EVI_001', label: 'Evidence 001', x: 220, y: 80, stage: 'EVIDENCE' },
    { id: 'EXP_001', label: 'Experiment 001', x: 360, y: 140, stage: 'EXPERIMENT' },
    { id: 'VAL_001', label: 'Validation 001', x: 500, y: 100, stage: 'LIVE_VALIDATION' },
    { id: 'GOV_001', label: 'Governance 001', x: 640, y: 120, stage: 'GOVERNANCE' },
  ];

  return (
    <div className="bg-[#0b101b]/90 border border-slate-800/80 rounded-xl p-5 shadow-xl backdrop-blur-md font-mono">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <span>🕸️</span>
            <span>KNOWLEDGE GRAPH & PARENT-CHILD LINEAGE VISUALIZER</span>
          </h3>
          <p className="text-xs text-slate-400 font-sans mt-0.5">
            Trace upstream hypotheses and downstream validation sessions with deterministic edge linkages.
          </p>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setZoomLevel((z) => Math.max(z - 10, 50))}
            className="px-2.5 py-1 bg-slate-900 border border-slate-800 rounded hover:bg-slate-800 text-slate-300"
          >
            - Zoom
          </button>
          <span className="text-cyan-400 font-bold px-2">{zoomLevel}%</span>
          <button
            onClick={() => setZoomLevel((z) => Math.min(z + 10, 200))}
            className="px-2.5 py-1 bg-slate-900 border border-slate-800 rounded hover:bg-slate-800 text-slate-300"
          >
            + Zoom
          </button>
          <button
            onClick={() => setZoomLevel(100)}
            className="px-2.5 py-1 bg-slate-900 border border-slate-800 rounded hover:bg-slate-800 text-slate-400"
          >
            Fit Canvas
          </button>
        </div>
      </div>

      {/* Interactive SVG Canvas Viewport */}
      <div className="relative bg-[#06090e] border border-slate-800/80 rounded-lg h-72 overflow-hidden mb-4 flex items-center justify-center">
        <svg
          className="w-full h-full transition-transform duration-300"
          style={{ transform: `scale(${zoomLevel / 100})` }}
          viewBox="0 0 750 240"
        >
          {/* Connector Lines */}
          <line x1="120" y1="120" x2="220" y2="80" stroke="#3b82f6" strokeWidth="2" strokeDasharray="4" />
          <line x1="260" y1="80" x2="360" y2="140" stroke="#00f0ff" strokeWidth="2" />
          <line x1="400" y1="140" x2="500" y2="100" stroke="#10b981" strokeWidth="2" />
          <line x1="540" y1="100" x2="640" y2="120" stroke="#a855f7" strokeWidth="2" />

          {/* Node Circles */}
          {graphNodes.map((node) => {
            const isHovered = highlightedId === node.id;
            const isSelected = selectedEntity?.canonicalId === node.id;

            return (
              <g
                key={node.id}
                onMouseEnter={() => setHighlightedId(node.id)}
                onMouseLeave={() => setHighlightedId(null)}
                onClick={() => inspectEntityById(node.id)}
                className="cursor-pointer"
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={isHovered || isSelected ? "24" : "18"}
                  fill={isSelected ? '#00f0ff' : isHovered ? '#3b82f6' : '#0f172a'}
                  stroke={isSelected ? '#ffffff' : '#00f0ff'}
                  strokeWidth="2"
                  className="transition-all duration-200"
                />
                <text
                  x={node.x}
                  y={node.y + 4}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize="10"
                  fontWeight="bold"
                  fontFamily="monospace"
                >
                  {node.id.substring(0, 3)}
                </text>
                <text
                  x={node.x}
                  y={node.y + 36}
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="9"
                  fontFamily="monospace"
                >
                  {node.id}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Relationship List */}
      <div className="space-y-2">
        <div className="text-[11px] text-slate-400 font-bold uppercase tracking-wider mb-2">
          LINKED RELATIONSHIPS LIST ({relationships.length})
        </div>
        {relationships.map((rel, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-3 bg-slate-950/80 border border-slate-800/80 rounded-md hover:border-cyan-500/50 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <button
                onClick={() => inspectEntityById(rel.sourceId)}
                className="text-xs font-bold text-cyan-400 hover:underline bg-slate-900 px-2.5 py-1 rounded border border-cyan-900"
              >
                {rel.sourceId}
              </button>

              <span className="text-[11px] text-purple-400 font-bold px-2 py-0.5 bg-purple-950/60 border border-purple-800/60 rounded">
                ── {rel.relationshipType} ──▶
              </span>

              <button
                onClick={() => inspectEntityById(rel.targetId)}
                className="text-xs font-bold text-cyan-400 hover:underline bg-slate-900 px-2.5 py-1 rounded border border-cyan-900"
              >
                {rel.targetId}
              </button>
            </div>

            <span className="text-[10px] text-slate-500">
              {new Date(rel.timestamp).toISOString().substring(0, 10)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
