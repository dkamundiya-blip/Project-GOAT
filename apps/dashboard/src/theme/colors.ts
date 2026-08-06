/**
 * Institutional Quant Dark Mode & High-Contrast Color Palette
 * Version 1.0 — Step 1.4 Presentation Layer
 */

export const colors = {
  background: {
    primary: '#06090e',       // Deep obsidian dark
    secondary: '#0b101b',     // Institutional slate surface
    tertiary: '#121a2d',      // Elevated glass card background
    elevated: '#182239',      // Hover / active elevated state
    glass: 'rgba(11, 16, 27, 0.75)',
    glassHover: 'rgba(18, 26, 45, 0.85)',
  },
  border: {
    subtle: '#1b253b',        // Subtle panel divider
    default: '#273552',       // Standard component border
    focus: '#00f0ff',         // High contrast focus border
    glow: 'rgba(0, 240, 255, 0.3)',
    active: '#3b82f6',
  },
  text: {
    primary: '#f8fafc',       // High readability white/slate-50
    secondary: '#94a3b8',     // Muted label slate-400
    tertiary: '#64748b',      // Sub-label slate-500
    dimmed: '#475569',        // Inactive slate-600
    inverse: '#06090e',       // Dark text on light accent
  },
  accent: {
    cyan: '#00f0ff',          // Terminal neon cyan (Primary indicator)
    blue: '#3b82f6',          // Institutional blue
    emerald: '#10b981',       // High confidence / nominal green
    amber: '#f59e0b',         // Warning / elevated attention yellow
    rose: '#f43f5e',          // Error / critical status red
    purple: '#a855f7',        // Statistical / intelligence violet
    indigo: '#6366f1',        // Model / algorithm indicator
  },
  status: {
    nominal: {
      bg: 'rgba(16, 185, 129, 0.15)',
      border: 'rgba(16, 185, 129, 0.4)',
      text: '#34d399',
      glow: '0 0 10px rgba(16, 185, 129, 0.3)',
    },
    elevated: {
      bg: 'rgba(245, 158, 11, 0.15)',
      border: 'rgba(245, 158, 11, 0.4)',
      text: '#fbbf24',
      glow: '0 0 10px rgba(245, 158, 11, 0.3)',
    },
    critical: {
      bg: 'rgba(244, 63, 94, 0.15)',
      border: 'rgba(244, 63, 94, 0.4)',
      text: '#f87171',
      glow: '0 0 10px rgba(244, 63, 94, 0.3)',
    },
    active: {
      bg: 'rgba(0, 240, 255, 0.15)',
      border: 'rgba(0, 240, 255, 0.4)',
      text: '#38bdf8',
      glow: '0 0 10px rgba(0, 240, 255, 0.3)',
    },
    disabled: {
      bg: 'rgba(71, 85, 105, 0.15)',
      border: 'rgba(71, 85, 105, 0.3)',
      text: '#64748b',
      glow: 'none',
    },
  },
  chart: {
    line1: '#00f0ff',
    line2: '#10b981',
    line3: '#f59e0b',
    line4: '#a855f7',
    line5: '#f43f5e',
    gridLines: '#1b253b',
    tooltipBg: '#0e1626',
  },
} as const;

export type ColorPalette = typeof colors;
