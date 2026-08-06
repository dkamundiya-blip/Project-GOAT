export const iconStyles = {
  sizes: {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
    '2xl': 48,
  },
  colors: {
    primary: '#00f0ff',
    secondary: '#94a3b8',
    muted: '#475569',
    emerald: '#10b981',
    amber: '#f59e0b',
    rose: '#f43f5e',
    purple: '#a855f7',
  },
} as const;

export type IconStyles = typeof iconStyles;
