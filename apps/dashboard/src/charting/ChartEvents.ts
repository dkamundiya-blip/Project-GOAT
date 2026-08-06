/**
 * Project GOAT v1.0 — Chart Event Bus
 * Step 1.6 Institutional TradingView Charting Engine
 */

export type ChartEventType =
  | 'SYMBOL_CHANGED'
  | 'TIMEFRAME_CHANGED'
  | 'CROSSHAIR_MOVED'
  | 'BAR_CLICKED'
  | 'VISIBLE_RANGE_CHANGED'
  | 'DRAWING_ADDED'
  | 'DRAWING_REMOVED'
  | 'LAYOUT_CHANGED';

export interface ChartEventPayload {
  type: ChartEventType;
  timestamp: string;
  data: any;
}

type EventListener = (payload: ChartEventPayload) => void;

export class ChartEvents {
  private static listeners: Map<ChartEventType, Set<EventListener>> = new Map();

  static on(type: ChartEventType, listener: EventListener): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(listener);

    return () => {
      this.listeners.get(type)?.delete(listener);
    };
  }

  static emit(type: ChartEventType, data: any): void {
    const payload: ChartEventPayload = {
      type,
      timestamp: new Date().toISOString(),
      data,
    };
    const set = this.listeners.get(type);
    if (set) {
      set.forEach((fn) => {
        try {
          fn(payload);
        } catch {
          // Ignore error
        }
      });
    }
  }

  static clear(): void {
    this.listeners.clear();
  }
}
