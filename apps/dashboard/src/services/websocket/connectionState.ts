/**
 * Project GOAT v1.0 — WebSocket Connection State Engine
 */

export type ConnectionStatus =
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'CONNECTED'
  | 'RECONNECTING'
  | 'TERMINATED';

export class ConnectionStateMachine {
  private currentStatus: ConnectionStatus = 'DISCONNECTED';
  private listeners: ((status: ConnectionStatus) => void)[] = [];

  getStatus(): ConnectionStatus {
    return this.currentStatus;
  }

  transitionTo(nextStatus: ConnectionStatus): void {
    if (this.currentStatus !== nextStatus) {
      this.currentStatus = nextStatus;
      this.notifyListeners();
    }
  }

  onChange(listener: (status: ConnectionStatus) => void): void {
    this.listeners.push(listener);
  }

  private notifyListeners(): void {
    this.listeners.forEach((fn) => fn(this.currentStatus));
  }
}

export const connectionState = new ConnectionStateMachine();
