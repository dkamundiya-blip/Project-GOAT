/**
 * Project GOAT v1.0 — Crosshair Manager
 * Step 1.6 Institutional TradingView Charting Engine
 */

export interface CrosshairPosition {
  x: number;
  y: number;
  time: number | null;
  price: number | null;
  sourcePanelId: string;
}

export class CrosshairManager {
  private static currentPosition: CrosshairPosition | null = null;
  private static listeners: Set<(pos: CrosshairPosition | null) => void> = new Set();

  static setPosition(pos: CrosshairPosition | null): void {
    this.currentPosition = pos;
    this.listeners.forEach((fn) => {
      try {
        fn(pos);
      } catch {
        // Ignore
      }
    });
  }

  static getPosition(): CrosshairPosition | null {
    return this.currentPosition;
  }

  static subscribe(fn: (pos: CrosshairPosition | null) => void): () => void {
    this.listeners.add(fn);
    return () => {
      this.listeners.delete(fn);
    };
  }
}
