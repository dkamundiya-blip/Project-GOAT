/**
 * Project GOAT v1.0 — Presentation Layer Chart Settings
 * Stage 1.5 Clean Institutional Chart UI
 *
 * Controls optional overlay toggles for SMC, structural signals, and indicators.
 * Default presentation matches Bloomberg / TradingView / Sierra Chart terminal:
 * - Candlesticks, Grid, Time axis, Price axis, Crosshair, Price Lines
 * - All structural overlays disabled by default (dormant)
 */

export interface ChartSettings {
  showFVG: boolean;
  showOrderBlocks: boolean;
  showLiquidity: boolean;
  showVWAP: boolean;
  showSessionBoxes: boolean;
  showSwingLabels: boolean;
  showVolumeProfile: boolean;
  showMarketStructure: boolean;
  showInstitutionalOverlays: boolean;
}

export const defaultChartSettings: ChartSettings = {
  showFVG: false,
  showOrderBlocks: false,
  showLiquidity: false,
  showVWAP: false,
  showSessionBoxes: false,
  showSwingLabels: false,
  showVolumeProfile: false,
  showMarketStructure: false,
  showInstitutionalOverlays: false,
};
