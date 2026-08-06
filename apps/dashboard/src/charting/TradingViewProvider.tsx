/**
 * Project GOAT v1.0 — TradingView Context Provider
 * Step 1.6 Institutional TradingView Charting Engine
 */

import React, { createContext, useContext, useState } from 'react';
import { TradingViewDataFeed } from './TradingViewDataFeed';
import { DrawingManager } from './DrawingManager';

export interface TradingViewContextValue {
  datafeed: TradingViewDataFeed;
  drawingManager: DrawingManager;
  activeSymbol: string;
  setActiveSymbol: (symbol: string) => void;
  activeTimeframe: string;
  setActiveTimeframe: (timeframe: string) => void;
}

const TradingViewContext = createContext<TradingViewContextValue | null>(null);

export const TradingViewProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [datafeed] = useState<TradingViewDataFeed>(new TradingViewDataFeed());
  const [drawingManager] = useState<DrawingManager>(new DrawingManager());
  const [activeSymbol, setActiveSymbol] = useState<string>('VOLATILITY_100');
  const [activeTimeframe, setActiveTimeframe] = useState<string>('1M');

  return (
    <TradingViewContext.Provider
      value={{
        datafeed,
        drawingManager,
        activeSymbol,
        setActiveSymbol,
        activeTimeframe,
        setActiveTimeframe,
      }}
    >
      {children}
    </TradingViewContext.Provider>
  );
};

export function useTradingViewContext(): TradingViewContextValue {
  const context = useContext(TradingViewContext);
  if (!context) {
    throw new Error('useTradingViewContext must be used within a TradingViewProvider');
  }
  return context;
}
