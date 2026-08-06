export type NotificationType = 'info' | 'success' | 'warning' | 'error' | 'INFO' | 'WARN' | 'CRITICAL';

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  severity?: 'INFO' | 'WARN' | 'CRITICAL' | string;
  detail?: string;
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
