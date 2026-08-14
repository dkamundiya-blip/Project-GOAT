import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useTelemetryStore } from '../stores/telemetryStore';

export const EdgeDiscoveryPage: React.FC = () => {
  const telemetry = useTelemetryStore();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Quantitative Edge Discovery Engine</h2>
          <p className="text-xs text-slate-400 mt-1">
            Repeatable statistical anomaly mining without chart patterns or technical indicators (Step 9.9).
          </p>
        </div>
        <Badge variant={telemetry.edges.length > 0 ? 'success' : 'muted'}>
          {telemetry.edges.length} ACTIVE EDGES
        </Badge>
      </div>

      <Card title="Discovered Candidate Edges" subtitle="Source: SQLite / discovered_edges">
        {telemetry.edges.length === 0 ? (
          <div className="p-8 text-center space-y-3">
            <div className="text-2xl">🔍</div>
            <div className="text-sm font-semibold text-slate-200">
              WARMING UP — INSUFFICIENT GENUINE OBSERVATIONS
            </div>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              No genuine statistically discovered edges exist in the database.
              The engine requires at least 15 forward-return paired observations to execute hypothesis evaluation and significance screening.
            </p>
            <div className="pt-2 text-xs font-mono text-slate-500">
              Closed Candles: {telemetry.candlesClosed} &bull; Feature Vectors: {telemetry.featureVectorsGenerated} &bull; Edges Evaluated: {telemetry.edgesEvaluated}
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {telemetry.edges.map((edge) => (
              <div
                key={edge.id}
                className="flex items-center justify-between p-3 bg-surface-elevated rounded border border-border"
              >
                <div>
                  <div className="font-mono font-bold text-xs text-cyan-300">{edge.id}</div>
                  <p className="text-[11px] text-slate-400">
                    {edge.symbol} | Features: {edge.features} | EV: +{(edge.ev * 100).toFixed(2)}%
                  </p>
                </div>
                <div className="flex gap-2">
                  <Badge variant="purple">p = {edge.pval.toFixed(4)}</Badge>
                  <Badge variant="success">SHARPE {edge.sharpe.toFixed(2)}</Badge>
                  <Badge variant="primary">SCORE {edge.score.toFixed(2)}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
export default EdgeDiscoveryPage;
