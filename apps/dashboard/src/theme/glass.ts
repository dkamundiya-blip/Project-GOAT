export const glassStyles = {
  panel: {
    background: 'rgba(11, 16, 27, 0.75)',
    backdropFilter: 'blur(12px)',
    border: '1px solid rgba(39, 53, 82, 0.6)',
    boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
  },
  panelElevated: {
    background: 'rgba(18, 26, 45, 0.85)',
    backdropFilter: 'blur(16px)',
    border: '1px solid rgba(59, 130, 246, 0.3)',
    boxShadow: '0 12px 40px 0 rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 240, 255, 0.15)',
  },
  interactive: {
    background: 'rgba(15, 23, 42, 0.6)',
    backdropFilter: 'blur(8px)',
    border: '1px solid rgba(51, 65, 85, 0.5)',
    transition: 'all 200ms cubic-bezier(0.16, 1, 0.3, 1)',
    hover: {
      background: 'rgba(30, 41, 59, 0.8)',
      borderColor: 'rgba(0, 240, 255, 0.4)',
      boxShadow: '0 0 12px rgba(0, 240, 255, 0.2)',
    },
  },
} as const;

export type GlassStyles = typeof glassStyles;
