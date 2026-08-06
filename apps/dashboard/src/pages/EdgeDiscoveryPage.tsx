import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

export const EdgeDiscoveryPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100">Quantitative Edge Discovery Engine</h2>
        <p className="text-xs text-slate-400 mt-1">
          Repeatable statistical anomaly mining without chart patterns or technical indicators (Step 9.9).
        </p>
      </div>

      <Card title="Discovered Candidate Edges">
        <div className="flex items-center justify-between p-3 bg-surface-elevated rounded border border-border">
          <div>
            <div className="font-mono font-bold text-xs">EDC_VOL_CLUSTER_STABILITY_01</div>
            <p className="text-[11px] text-slate-400">Microstructure volatility dispersion anomaly on Volatility 100 Index.</p>
          </div>
          <div className="flex gap-2">
            <Badge variant="purple">p = 0.0001</Badge>
            <Badge variant="success">STABILITY 94.2%</Badge>
          </div>
        </div>
      </Card>
    </div>
  );
};
export default EdgeDiscoveryPage;
