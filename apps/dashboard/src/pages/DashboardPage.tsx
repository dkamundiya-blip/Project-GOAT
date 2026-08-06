/**
 * Project GOAT v1.0 — Main Operator Control Room Dashboard Page
 */

import React from 'react';
import { LiveTelemetryChart } from '../components/widgets/LiveTelemetryChart';
import { PipelineSummaryTable } from '../components/widgets/PipelineSummaryTable';
import { SubsystemHealthWidget } from '../components/widgets/SubsystemHealthWidget';
import { SystemOverviewCards } from '../components/widgets/SystemOverviewCards';

export const DashboardPage: React.FC = () => {
  return (
    <div className="p-6 space-y-6 bg-slate-950 min-h-full text-slate-100">
      {/* Top Header */}
      <div className="flex justify-between items-center pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-100">
            Institutional Research Control Room
          </h1>
          <p className="text-xs text-slate-400">
            Real-time quantitative pipeline telemetry & governance overview.
          </p>
        </div>
        <div className="text-xs font-mono bg-slate-900 px-3 py-1.5 rounded border border-slate-800 text-cyan-300">
          CONNECTED TO STEP 1.1 BACKEND
        </div>
      </div>

      {/* Summary Cards */}
      <SystemOverviewCards />

      {/* Real-Time Telemetry Feed */}
      <LiveTelemetryChart />

      {/* Subsystem Health Matrix */}
      <SubsystemHealthWidget />

      {/* Research Pipeline Overview Table */}
      <PipelineSummaryTable />
    </div>
  );
};
