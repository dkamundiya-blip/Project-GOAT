/**
 * Project GOAT v1.0 — Typed Channel Subscription Definitions
 */

export type ChannelTopic =
  | 'system/*'
  | 'research/*'
  | 'evidence/*'
  | 'experiments/*'
  | 'statistics/*'
  | 'validation/*'
  | 'governance/*'
  | 'monitoring/*'
  | 'notifications/*'
  | 'archive/*'
  | 'portfolio/*'
  | 'microstructure/*'
  | 'dashboard/*';

export interface ChannelMessage<T = unknown> {
  topic: ChannelTopic | string;
  payload: T;
  timestamp: string;
}

export const VALID_CHANNEL_TOPICS: ChannelTopic[] = [
  'system/*',
  'research/*',
  'evidence/*',
  'experiments/*',
  'statistics/*',
  'validation/*',
  'governance/*',
  'monitoring/*',
  'notifications/*',
  'archive/*',
  'portfolio/*',
  'microstructure/*',
  'dashboard/*',
];
