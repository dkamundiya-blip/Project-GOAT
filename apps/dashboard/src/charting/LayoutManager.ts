/**
 * Project GOAT v1.0 — Layout Manager
 * Step 1.6 Institutional TradingView Charting Engine
 */

import { LayoutModeType } from './ChartState';

export interface ChartPanelConfig {
  id: string;
  symbol: string;
  timeframe: string;
}

export class LayoutManager {
  static getPanelsForLayout(mode: LayoutModeType, primarySymbol: string, primaryTimeframe: string): ChartPanelConfig[] {
    switch (mode) {
      case 'split_h':
      case 'split_v':
        return [
          { id: 'panel_1', symbol: primarySymbol, timeframe: primaryTimeframe },
          { id: 'panel_2', symbol: primarySymbol, timeframe: '5M' },
        ];
      case 'grid_2x2':
        return [
          { id: 'panel_1', symbol: primarySymbol, timeframe: '1M' },
          { id: 'panel_2', symbol: primarySymbol, timeframe: '5M' },
          { id: 'panel_3', symbol: primarySymbol, timeframe: '15M' },
          { id: 'panel_4', symbol: primarySymbol, timeframe: '1H' },
        ];
      case 'single':
      default:
        return [{ id: 'panel_1', symbol: primarySymbol, timeframe: primaryTimeframe }];
    }
  }
}
