import { lazy } from 'react';

export interface RouteDefinition {
  path: string;
  title: string;
  component: React.LazyExoticComponent<React.FC>;
}

export const routes: RouteDefinition[] = [
  { path: '/', title: 'Overview Dashboard', component: lazy(() => import('../pages/DashboardPage').then(m => ({ default: m.DashboardPage }))) },
  { path: '/control-room', title: 'Control Room', component: lazy(() => import('../pages/ControlRoomPage').then(m => ({ default: m.ControlRoomPage }))) },
  { path: '/markets', title: 'Markets Overview', component: lazy(() => import('../pages/MarketsPage').then(m => ({ default: m.MarketsPage }))) },
  { path: '/research', title: 'Hypothesis Registry', component: lazy(() => import('../pages/ResearchPage').then(m => ({ default: m.ResearchPage }))) },
  { path: '/evidence', title: 'Evidence Collection', component: lazy(() => import('../pages/EvidencePage').then(m => ({ default: m.EvidencePage }))) },
  { path: '/experiments', title: 'Experiment Engine', component: lazy(() => import('../pages/ExperimentsPage').then(m => ({ default: m.ExperimentsPage }))) },
  { path: '/statistics', title: 'Statistical Evaluator', component: lazy(() => import('../pages/StatisticsPage').then(m => ({ default: m.StatisticsPage }))) },
  { path: '/live-validation', title: 'Live Validation', component: lazy(() => import('../pages/LiveValidationPage').then(m => ({ default: m.LiveValidationPage }))) },
  { path: '/governance', title: 'Scientific Governance', component: lazy(() => import('../pages/GovernancePage').then(m => ({ default: m.GovernancePage }))) },
  { path: '/knowledge-graph', title: 'Knowledge Graph', component: lazy(() => import('../pages/KnowledgeGraphPage').then(m => ({ default: m.KnowledgeGraphPage }))) },
  { path: '/edge-discovery', title: 'Edge Discovery', component: lazy(() => import('../pages/EdgeDiscoveryPage').then(m => ({ default: m.EdgeDiscoveryPage }))) },
  { path: '/research-intelligence', title: 'Research Intelligence', component: lazy(() => import('../pages/ResearchIntelligencePage').then(m => ({ default: m.ResearchIntelligencePage }))) },
  { path: '/archive', title: 'Institutional Archive', component: lazy(() => import('../pages/ArchivePage').then(m => ({ default: m.ArchivePage }))) },
  { path: '/portfolio', title: 'Portfolio Preview', component: lazy(() => import('../pages/PortfolioPage').then(m => ({ default: m.PortfolioPage }))) },
  { path: '/monitoring', title: 'System Monitoring', component: lazy(() => import('../pages/MonitoringPage').then(m => ({ default: m.MonitoringPage }))) },
  { path: '/settings', title: 'Settings', component: lazy(() => import('../pages/SettingsPage').then(m => ({ default: m.SettingsPage }))) },
  { path: '/pipeline-visualizer', title: 'Pipeline Visualizer', component: lazy(() => import('../pages/PipelineVisualizerPage').then(m => ({ default: m.PipelineVisualizerPage }))) },
  { path: '*', title: '404 Not Found', component: lazy(() => import('../pages/NotFoundPage').then(m => ({ default: m.NotFoundPage }))) },
];
