/**
 * Project GOAT v1.0 — Official Licensed TradingView Charting Library Container Widget
 * Step 1.6 Institutional TradingView Charting Engine
 *
 * Instantiates `new TradingView.widget({...})` with GOAT DataFeed when official library assets are installed.
 * Gracefully falls back to high-performance Canvas engine with audit notice when assets are pending.
 */

import React, { useEffect, useRef, useState } from 'react';
import { TradingViewLoader } from './TradingViewLoader';
import { TradingViewDataFeed } from './TradingViewDataFeed';
import { TradingViewWidget } from './TradingViewWidget';
import { TimeframeManager } from './TimeframeManager';
import { ShieldAlert } from 'lucide-react';

export interface OfficialTradingViewWidgetProps {
  symbol: string;
  timeframe: string;
  height?: number | string;
  theme?: 'dark' | 'light';
  containerId?: string;
}

export const OfficialTradingViewWidget: React.FC<OfficialTradingViewWidgetProps> = ({
  symbol,
  timeframe,
  height = '100%',
  theme = 'dark',
  containerId = 'official_tv_widget_container',
}) => {
  const [isLibraryAvailable, setIsLibraryAvailable] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const tvWidgetRef = useRef<any>(null);

  useEffect(() => {
    let isMounted = true;
    TradingViewLoader.loadOfficialLibrary().then((available) => {
      if (!isMounted) return;
      setIsLibraryAvailable(available);
      setIsLoading(false);

      if (available) {
        const resolution = TimeframeManager.goatTimeframeToResolution(timeframe);
        const datafeed = new TradingViewDataFeed();

        // Instantiate Official TradingView.widget
        const widgetOptions: any = {
          symbol: symbol,
          datafeed: datafeed,
          interval: resolution,
          container_id: containerId,
          library_path: '/charting_library/',
          locale: 'en',
          disabled_features: ['use_localstorage_for_settings'],
          enabled_features: ['study_templates'],
          charts_storage_url: 'https://savelayout.tradingview.com',
          charts_storage_api_version: '1.1',
          client_id: 'tradingview.com',
          user_id: 'public_user_id',
          fullscreen: false,
          autosize: true,
          theme: theme === 'dark' ? 'Dark' : 'Light',
        };

        if ((window as any).TradingView) {
          tvWidgetRef.current = new (window as any).TradingView.widget(widgetOptions);
        }
      }
    });

    return () => {
      isMounted = false;
      if (tvWidgetRef.current && typeof tvWidgetRef.current.remove === 'function') {
        tvWidgetRef.current.remove();
      }
    };
  }, [symbol, timeframe, theme, containerId]);

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-[#06090e] text-slate-400 font-mono text-xs">
        <span>Detecting TradingView Library Assets...</span>
      </div>
    );
  }

  if (!isLibraryAvailable) {
    return (
      <div className="w-full h-full flex flex-col relative">
        {/* Audit Notice Banner */}
        <div className="bg-amber-950/80 border-b border-amber-800/80 px-3 py-1.5 flex items-center justify-between text-[11px] font-mono text-amber-300 z-20">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
            <span>OFFICIAL TRADINGVIEW CHARTING LIBRARY ASSETS PENDING (/charting_library/)</span>
          </div>
          <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider">
            LIGHTWEIGHT CHARTS ENGINE ACTIVE
          </span>
        </div>

        {/* Embedded Lightweight Charts Engine */}
        <div className="flex-1 relative">
          <TradingViewWidget symbol={symbol} timeframe={timeframe} height={height} theme={theme} />
        </div>
      </div>
    );
  }

  return <div id={containerId} className="w-full h-full" style={{ height }} />;
};
