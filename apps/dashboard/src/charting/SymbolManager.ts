/**
 * Project GOAT v1.0 — Symbol Manager
 * Step 1.6 Institutional TradingView Charting Engine
 */

export interface ChartSymbolMetadata {
  id: string;
  symbol: string;
  name: string;
  description: string;
  type: 'volatility' | 'spike' | 'step' | 'jump';
  pipSize: number;
  minMove: number;
  pricescale: number;
  hasIntraday: boolean;
  supportedResolutions: string[];
}

export const SUPPORTED_CHART_SYMBOLS: Record<string, ChartSymbolMetadata> = {
  VOLATILITY_10: {
    id: 'VOLATILITY_10',
    symbol: 'VOLATILITY_10',
    name: 'Volatility 10 Index',
    description: 'Continuous Volatility 10 Index',
    type: 'volatility',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  VOLATILITY_25: {
    id: 'VOLATILITY_25',
    symbol: 'VOLATILITY_25',
    name: 'Volatility 25 Index',
    description: 'Continuous Volatility 25 Index',
    type: 'volatility',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  VOLATILITY_50: {
    id: 'VOLATILITY_50',
    symbol: 'VOLATILITY_50',
    name: 'Volatility 50 Index',
    description: 'Continuous Volatility 50 Index',
    type: 'volatility',
    pipSize: 4,
    minMove: 1,
    pricescale: 10000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  VOLATILITY_75: {
    id: 'VOLATILITY_75',
    symbol: 'VOLATILITY_75',
    name: 'Volatility 75 Index',
    description: 'Continuous Volatility 75 Index',
    type: 'volatility',
    pipSize: 4,
    minMove: 1,
    pricescale: 10000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  VOLATILITY_100: {
    id: 'VOLATILITY_100',
    symbol: 'VOLATILITY_100',
    name: 'Volatility 100 Index',
    description: 'Continuous Volatility 100 Index',
    type: 'volatility',
    pipSize: 2,
    minMove: 1,
    pricescale: 100,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  BOOM_500: {
    id: 'BOOM_500',
    symbol: 'BOOM_500',
    name: 'Boom 500 Index',
    description: 'Spike Boom 500 Index',
    type: 'spike',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  BOOM_1000: {
    id: 'BOOM_1000',
    symbol: 'BOOM_1000',
    name: 'Boom 1000 Index',
    description: 'Spike Boom 1000 Index',
    type: 'spike',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  CRASH_500: {
    id: 'CRASH_500',
    symbol: 'CRASH_500',
    name: 'Crash 500 Index',
    description: 'Spike Crash 500 Index',
    type: 'spike',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  CRASH_1000: {
    id: 'CRASH_1000',
    symbol: 'CRASH_1000',
    name: 'Crash 1000 Index',
    description: 'Spike Crash 1000 Index',
    type: 'spike',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  STEP_INDEX: {
    id: 'STEP_INDEX',
    symbol: 'STEP_INDEX',
    name: 'Step Index',
    description: 'Equal Step Discrete Index',
    type: 'step',
    pipSize: 2,
    minMove: 1,
    pricescale: 100,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  JUMP_10: {
    id: 'JUMP_10',
    symbol: 'JUMP_10',
    name: 'Jump 10 Index',
    description: 'Jump 10 Volatility Index',
    type: 'jump',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  JUMP_25: {
    id: 'JUMP_25',
    symbol: 'JUMP_25',
    name: 'Jump 25 Index',
    description: 'Jump 25 Volatility Index',
    type: 'jump',
    pipSize: 3,
    minMove: 1,
    pricescale: 1000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  JUMP_50: {
    id: 'JUMP_50',
    symbol: 'JUMP_50',
    name: 'Jump 50 Index',
    description: 'Jump 50 Volatility Index',
    type: 'jump',
    pipSize: 4,
    minMove: 1,
    pricescale: 10000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  JUMP_75: {
    id: 'JUMP_75',
    symbol: 'JUMP_75',
    name: 'Jump 75 Index',
    description: 'Jump 75 Volatility Index',
    type: 'jump',
    pipSize: 4,
    minMove: 1,
    pricescale: 10000,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
  JUMP_100: {
    id: 'JUMP_100',
    symbol: 'JUMP_100',
    name: 'Jump 100 Index',
    description: 'Jump 100 Volatility Index',
    type: 'jump',
    pipSize: 2,
    minMove: 1,
    pricescale: 100,
    hasIntraday: true,
    supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
  },
};

export class SymbolManager {
  static getSymbolMetadata(symbolId: string): ChartSymbolMetadata {
    const sym = symbolId.toUpperCase();
    return (
      SUPPORTED_CHART_SYMBOLS[sym] || {
        id: sym,
        symbol: sym,
        name: sym,
        description: `${sym} Synthetic Instrument`,
        type: 'volatility',
        pipSize: 2,
        minMove: 1,
        pricescale: 100,
        hasIntraday: true,
        supportedResolutions: ['1', '5', '15', '30', '60', '240', 'D'],
      }
    );
  }

  static getAllSymbols(): ChartSymbolMetadata[] {
    return Object.values(SUPPORTED_CHART_SYMBOLS);
  }

  static formatPrice(price: number, symbolId: string): string {
    const meta = this.getSymbolMetadata(symbolId);
    return price.toFixed(meta.pipSize);
  }
}
