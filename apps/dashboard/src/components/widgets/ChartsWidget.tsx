/**
 * Project GOAT v1.0 — Institutional Scientific Data Visualization & Chart Engine
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState } from 'react';

export interface ChartProps {
  title: string;
  subtitle?: string;
  type?: 'line' | 'bar' | 'area' | 'distribution';
}

export const ConfidenceDistributionChart: React.FC<ChartProps> = ({ title, subtitle }) => {
  const bins = [
    { range: '0.0-0.2', count: 12, pct: 5 },
    { range: '0.2-0.4', count: 48, pct: 15 },
    { range: '0.4-0.6', count: 120, pct: 35 },
    { range: '0.6-0.8', count: 180, pct: 60 },
    { range: '0.8-0.9', count: 240, pct: 85 },
    { range: '0.9-1.0', count: 310, pct: 100 },
  ];

  return (
    <div className="bg-[#0b101b]/90 border border-slate-800/80 p-5 rounded-xl shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h4 className="text-sm font-bold font-mono text-slate-100">{title}</h4>
          {subtitle && <p className="text-xs text-slate-400 font-sans">{subtitle}</p>}
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
          BAYESIAN DISTRIBUTION
        </span>
      </div>

      <div className="h-48 flex items-end justify-between gap-3 pt-6 pb-2 px-2 border-b border-slate-800">
        {bins.map((bin, idx) => (
          <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative">
            <div
              className="w-full bg-gradient-to-t from-cyan-900 via-cyan-500 to-emerald-400 rounded-t transition-all duration-300 group-hover:brightness-125"
              style={{ height: `${bin.pct}%` }}
            />
            <span className="text-[10px] font-mono text-slate-400 mt-1">{bin.range}</span>
            {/* Tooltip */}
            <div className="opacity-0 group-hover:opacity-100 absolute -top-8 bg-slate-900 border border-cyan-500 text-cyan-300 text-[10px] font-mono px-2 py-1 rounded shadow-lg pointer-events-none transition-opacity">
              Count: {bin.count}
            </div>
          </div>
        ))}
      </div>
      <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2">
        <span>Confidence Score Bin</span>
        <span>Frequency Distribution</span>
      </div>
    </div>
  );
};

export const ValidationTimelineChart: React.FC<ChartProps> = ({ title, subtitle }) => {
  const points = [
    { time: '00:00', val: 12 },
    { time: '04:00', val: 18 },
    { time: '08:00', val: 26 },
    { time: '12:00', val: 34 },
    { time: '16:00', val: 42 },
    { time: '20:00', val: 48 },
  ];

  return (
    <div className="bg-[#0b101b]/90 border border-slate-800/80 p-5 rounded-xl shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h4 className="text-sm font-bold font-mono text-slate-100">{title}</h4>
          {subtitle && <p className="text-xs text-slate-400 font-sans">{subtitle}</p>}
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
          HOLDOUT ISOLATED
        </span>
      </div>

      <div className="h-48 relative flex items-end pt-6 pb-2">
        <svg className="w-full h-full overflow-visible" viewBox="0 0 500 150">
          <polyline
            fill="none"
            stroke="#10b981"
            strokeWidth="3"
            strokeLinecap="round"
            points="0,130 100,110 200,85 300,60 400,35 500,20"
          />
          {points.map((pt, idx) => (
            <circle key={idx} cx={idx * 100} cy={140 - pt.val * 2.5} r="5" fill="#00f0ff" className="hover:r-7 transition-all cursor-pointer" />
          ))}
        </svg>
      </div>
      <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2 border-t border-slate-800 pt-2">
        {points.map((pt, idx) => (
          <span key={idx}>{pt.time}</span>
        ))}
      </div>
    </div>
  );
};

export const ResearchVelocityChart: React.FC<ChartProps> = ({ title, subtitle }) => {
  return (
    <div className="bg-[#0b101b]/90 border border-slate-800/80 p-5 rounded-xl shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h4 className="text-sm font-bold font-mono text-slate-100">{title}</h4>
          {subtitle && <p className="text-xs text-slate-400 font-sans">{subtitle}</p>}
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-400 border border-purple-800">
          DISCOVERY ACCELERATION
        </span>
      </div>
      <div className="h-48 flex items-end justify-between gap-2 pt-6 pb-2 border-b border-slate-800">
        {[40, 55, 65, 80, 95, 110, 135].map((val, idx) => (
          <div key={idx} className="flex-1 bg-purple-600/40 hover:bg-purple-500 rounded-t transition-all" style={{ height: `${(val / 150) * 100}%` }} />
        ))}
      </div>
      <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-2">
        <span>Mon</span>
        <span>Tue</span>
        <span>Wed</span>
        <span>Thu</span>
        <span>Fri</span>
        <span>Sat</span>
        <span>Sun</span>
      </div>
    </div>
  );
};

export const GovernanceOutcomesChart: React.FC<ChartProps> = ({ title, subtitle }) => {
  return (
    <div className="bg-[#0b101b]/90 border border-slate-800/80 p-5 rounded-xl shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h4 className="text-sm font-bold font-mono text-slate-100">{title}</h4>
          {subtitle && <p className="text-xs text-slate-400 font-sans">{subtitle}</p>}
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-800">
          CONSTITUTIONAL VOTES
        </span>
      </div>
      <div className="h-48 flex items-center justify-around">
        <div className="text-center">
          <div className="text-3xl font-bold text-emerald-400 font-mono">18</div>
          <div className="text-xs text-slate-400 font-mono">PROMOTED</div>
        </div>
        <div className="h-16 w-px bg-slate-800" />
        <div className="text-center">
          <div className="text-3xl font-bold text-rose-400 font-mono">3</div>
          <div className="text-xs text-slate-400 font-mono">REJECTED</div>
        </div>
        <div className="h-16 w-px bg-slate-800" />
        <div className="text-center">
          <div className="text-3xl font-bold text-amber-400 font-mono">2</div>
          <div className="text-xs text-slate-400 font-mono">PENDING</div>
        </div>
      </div>
    </div>
  );
};

export const MasterChartsGrid: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-6">
      <ConfidenceDistributionChart title="Confidence Score Distribution" subtitle="Empirical confidence across active hypothesis pool" />
      <ValidationTimelineChart title="Validation Progress Timeline" subtitle="Live holdout performance tracking over time" />
      <ResearchVelocityChart title="Research Discovery Velocity" subtitle="Hypotheses evaluated per day" />
      <GovernanceOutcomesChart title="Scientific Governance Decisions" subtitle="Promotions vs retirements vs active audits" />
    </div>
  );
};
