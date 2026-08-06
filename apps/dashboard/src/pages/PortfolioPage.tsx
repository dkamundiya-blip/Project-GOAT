import React from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';

export const PortfolioPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100">Portfolio & Risk Management (Future Version 1.1 Preview)</h2>
        <p className="text-xs text-slate-400 mt-1">
          High-level preview workspace for future capital allocation and portfolio position tracking.
        </p>
      </div>

      <Card title="Version 1.1 Preview Placeholder">
        <div className="p-6 text-center">
          <Badge variant="warning">FUTURE FEATURE PREVIEW</Badge>
          <p className="text-xs text-slate-400 mt-2">
            No portfolio logic or lot-sizing models exist in Version 1.0.
          </p>
        </div>
      </Card>
    </div>
  );
};
export default PortfolioPage;
