/**
 * Project GOAT v1.0 — Live Market Data Hook
 */

import { useEffect } from 'react';
import { useMarketDataStore } from '../stores/marketDataStore';
import { marketDataApi } from '../services/marketData/marketDataApi';

export function useMarketData(pollIntervalMs: number = 2000) {
  const { quotes, telemetry, connectionState, setQuotes, setTelemetry, setConnectionState, setIsPolling } =
    useMarketDataStore();

  useEffect(() => {
    let isMounted = true;
    setIsPolling(true);

    async function pollData() {
      try {
        const [symbolsRes, metricsRes] = await Promise.all([
          marketDataApi.getSymbols(),
          marketDataApi.getMetrics(),
        ]);

        if (isMounted) {
          setQuotes(symbolsRes.symbols);
          setTelemetry(metricsRes);
          if (symbolsRes.symbols.length > 0) {
            setConnectionState(symbolsRes.symbols[0].connection_status);
          }
        }
      } catch (err) {
        if (isMounted) {
          setConnectionState('DEGRADED');
        }
      }
    }

    pollData();
    const interval = setInterval(pollData, pollIntervalMs);

    return () => {
      isMounted = false;
      setIsPolling(false);
      clearInterval(interval);
    };
  }, [pollIntervalMs, setQuotes, setTelemetry, setConnectionState, setIsPolling]);

  return {
    quotes: Object.values(quotes),
    quoteMap: quotes,
    telemetry,
    connectionState,
    connect: marketDataApi.postConnect,
    disconnect: marketDataApi.postDisconnect,
    reconnect: marketDataApi.postReconnect,
    subscribe: marketDataApi.postSubscribe,
    unsubscribe: marketDataApi.postUnsubscribe,
  };
}
