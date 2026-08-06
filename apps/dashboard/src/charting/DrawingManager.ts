/**
 * Project GOAT v1.0 — Drawing Tool Manager
 * Step 1.6 Institutional TradingView Charting Engine
 *
 * Prepared for Step 1.7 research artifact overlay attachments (Hypotheses, Evidence, Experiments).
 */

export type DrawingToolType =
  | 'cursor'
  | 'trendline'
  | 'ray'
  | 'horizontal_line'
  | 'vertical_line'
  | 'rectangle'
  | 'ellipse'
  | 'arrow'
  | 'text'
  | 'fib_retracement'
  | 'fib_extension'
  | 'fib_channel'
  | 'pitchfork'
  | 'measure';

export interface ChartDrawingPoint {
  time: number; // Unix ms timestamp
  price: number;
}

export interface ChartDrawingObject {
  id: string;
  tool: DrawingToolType;
  points: ChartDrawingPoint[];
  color: string;
  lineWidth: number;
  label?: string;
  visible: boolean;
  locked: boolean;

  // Interface fields for Step 1.7 Research Overlay Linkage
  researchOverlayRef?: {
    entityType: 'HYPOTHESIS' | 'EVIDENCE' | 'EXPERIMENT' | 'GOVERNANCE';
    entityId: string;
    annotationSummary?: string;
  };
}

export class DrawingManager {
  private drawings: Map<string, ChartDrawingObject> = new Map();
  private activeTool: DrawingToolType = 'cursor';
  private magnetMode: boolean = false;

  setActiveTool(tool: DrawingToolType): void {
    this.activeTool = tool;
  }

  getActiveTool(): DrawingToolType {
    return this.activeTool;
  }

  toggleMagnetMode(): boolean {
    this.magnetMode = !this.magnetMode;
    return this.magnetMode;
  }

  isMagnetMode(): boolean {
    return this.magnetMode;
  }

  addDrawing(drawing: Omit<ChartDrawingObject, 'id'>): ChartDrawingObject {
    const id = `DWG_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const obj: ChartDrawingObject = {
      ...drawing,
      id,
    };
    this.drawings.set(id, obj);
    return obj;
  }

  getDrawing(id: string): ChartDrawingObject | undefined {
    return this.drawings.get(id);
  }

  getAllDrawings(): ChartDrawingObject[] {
    return Array.from(this.drawings.values());
  }

  updateDrawing(id: string, updates: Partial<ChartDrawingObject>): ChartDrawingObject | undefined {
    const existing = this.drawings.get(id);
    if (!existing) return undefined;
    const updated = { ...existing, ...updates };
    this.drawings.set(id, updated);
    return updated;
  }

  removeDrawing(id: string): boolean {
    return this.drawings.delete(id);
  }

  clearAllDrawings(): void {
    this.drawings.clear();
  }
}
