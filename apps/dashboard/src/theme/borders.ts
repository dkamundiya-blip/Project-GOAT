import { tokens } from './tokens';

export const borders = {
  radius: tokens.borderRadius,
  width: {
    thin: '1px',
    medium: '2px',
    thick: '3px',
  },
  style: {
    solid: '1px solid #273552',
    dashed: '1px dashed #3b82f6',
    glow: '1px solid #00f0ff',
  },
} as const;

export type BorderTokens = typeof borders;
