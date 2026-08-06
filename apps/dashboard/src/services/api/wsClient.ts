/**
 * Project GOAT v1.0 — Dashboard WebSocket Client Abstraction Layer
 * Interfaces only — no WebSocket stream connections established in Step 1.0.
 */

export type WSEventCallback = (data: unknown) => void;

export class WSClient {
  private url: string;
  private isConnected: boolean = false;
  private listeners: Map<string, WSEventCallback[]> = new Map();

  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url;
  }

  connect(): void {
    this.isConnected = true;
  }

  disconnect(): void {
    this.isConnected = false;
  }

  on(event: string, callback: WSEventCallback): void {
    const existing = this.listeners.get(event) || [];
    this.listeners.set(event, [...existing, callback]);
  }

  get status(): 'connected' | 'disconnected' {
    return this.isConnected ? 'connected' : 'disconnected';
  }
}

export const wsClient = new WSClient();
