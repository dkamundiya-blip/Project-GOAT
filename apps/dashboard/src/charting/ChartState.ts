/**
 * Project GOAT v1.0 — Chart State Store & Config
 * Step 1.6 Institutional TradingView Charting Engine
 */

import { create } from 'zustand';

export type ChartStyleType = 'candlestick' | 'line' | 'area' | 'heikin_ashi' | 'renko';
export type LayoutModeType = 'single' | 'split_h' | 'split_v' | 'grid_2x2';
export type CrosshairModeType = 'normal' | 'magnet' | 'hidden';
export type ThemeType = 'dark' | 'bloomberg' | 'light';

export interface ChartStateStore {
  activeSymbol: string;
  activeTimeframe: string;
  chartStyle: ChartStyleType;
  layoutMode: LayoutModeType;
  crosshairMode: CrosshairModeType;
  theme: ThemeType;
  isFullscreen: boolean;
  isReplayMode: boolean;
  zoomLevel: number;
  showVolume: boolean;
  showGridLines: boolean;

  setSymbol: (symbol: string) => void;
  setTimeframe: (timeframe: string) => void;
  setChartStyle: (style: ChartStyleType) => void;
  setLayoutMode: (layout: LayoutModeType) => void;
  setCrosshairMode: (mode: CrosshairModeType) => void;
  setTheme: (theme: ThemeType) => void;
  toggleFullscreen: () => void;
  toggleReplayMode: () => void;
  setZoomLevel: (zoom: number) => void;
  toggleVolume: () => void;
  toggleGridLines: () => void;
}

export const useChartStateStore = create<ChartStateStore>((set) => ({
  activeSymbol: 'VOLATILITY_100',
  activeTimeframe: '1M',
  chartStyle: 'candlestick',
  layoutMode: 'single',
  crosshairMode: 'normal',
  theme: 'dark',
  isFullscreen: false,
  isReplayMode: false,
  zoomLevel: 1.0,
  showVolume: true,
  showGridLines: true,

  setSymbol: (activeSymbol) => set({ activeSymbol }),
  setTimeframe: (activeTimeframe) => set({ activeTimeframe }),
  setChartStyle: (chartStyle) => set({ chartStyle }),
  setLayoutMode: (layoutMode) => set({ layoutMode }),
  setCrosshairMode: (crosshairMode) => set({ crosshairMode }),
  setTheme: (theme) => set({ theme }),
  toggleFullscreen: () => set((state) => ({ isFullscreen: !state.isFullscreen })),
  toggleReplayMode: () => set((state) => ({ isReplayMode: !state.isReplayMode })),
  setZoomLevel: (zoomLevel) => set({ zoomLevel }),
  toggleVolume: () => set((state) => ({ showVolume: !state.showVolume })),
  toggleGridLines: () => set((state) => ({ showGridLines: !state.showGridLines })),
}));
