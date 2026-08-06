export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  timestamp: string;
  read: boolean;
}

export type SymbolName =
  | 'VOLATILITY_10'
  | 'VOLATILITY_25'
  | 'VOLATILITY_50'
  | 'VOLATILITY_75'
  | 'VOLATILITY_100'
  | 'BOOM_500'
  | 'BOOM_1000'
  | 'CRASH_500'
  | 'CRASH_1000'
  | 'JUMP_10'
  | 'JUMP_25'
  | 'JUMP_50'
  | 'JUMP_75'
  | 'JUMP_100'
  | 'STEP_INDEX';

export interface WorkspaceConfig {
  id: string;
  name: string;
  activeSymbol: SymbolName;
  layoutPreset: 'default' | 'analytics' | 'scientific' | 'full';
}
