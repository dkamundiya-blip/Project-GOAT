/**
 * Project GOAT v1.0 — Master End-to-End Pipeline Visualizer Workspace
 */

import React from 'react';
import { PipelineGraphWidget } from '../components/widgets/PipelineGraphWidget';
import { EntityTimelineWidget } from '../components/widgets/EntityTimelineWidget';
import { RelationshipViewerWidget } from '../components/widgets/RelationshipViewerWidget';
import { TradingViewContainer } from '../charting/TradingViewContainer';

export const PipelineVisualizerPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <span>🔬</span>
            <span>END-TO-END RESEARCH PIPELINE VISUALIZER</span>
          </h1>
          <p className="text-xs text-slate-400">
            Interactive lifecycle visualizer for tracking candidate alpha edges from formulation through institutional governance.
          </p>
        </div>
      </div>

      <PipelineGraphWidget />

      <div className="bg-[#0b101b] border border-slate-800 p-4 rounded-xl space-y-3">
        <h3 className="text-sm font-bold font-mono text-slate-100">Pipeline Streaming Market Ingestion Chart</h3>
        <TradingViewContainer initialSymbol="VOLATILITY_75" initialTimeframe="5M" className="h-[420px]" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <EntityTimelineWidget />
        <RelationshipViewerWidget />
      </div>
    </div>
  );
};
