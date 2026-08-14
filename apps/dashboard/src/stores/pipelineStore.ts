/**
 * Project GOAT v1.0 — Scientific Pipeline & Lineage Zustand Store
 */

import { create } from 'zustand';
import { PipelineEdgeState, EntityMetadata, EntityRelationship, EntityHistoryItem, PipelineStage } from '../types/pipeline';

interface PipelineState {
  selectedEdgeId: string | null;
  selectedEntity: EntityMetadata | null;
  selectedStage: PipelineStage | null;
  inspectorOpen: boolean;
  edges: PipelineEdgeState[];
  relationships: EntityRelationship[];
  history: EntityHistoryItem[];
  filterStage: PipelineStage | 'ALL';

  // Actions
  setSelectedEdge: (edgeId: string | null) => void;
  setSelectedEntity: (entity: EntityMetadata | null) => void;
  setSelectedStage: (stage: PipelineStage | null) => void;
  setInspectorOpen: (open: boolean) => void;
  setFilterStage: (stage: PipelineStage | 'ALL') => void;
  updateEdgeStage: (edgeId: string, newStage: PipelineStage, progress: number) => void;
  inspectEntityById: (entityId: string) => void;
}

export const usePipelineStore = create<PipelineState>((set, get) => ({
  selectedEdgeId: null,
  selectedEntity: null,
  selectedStage: null,
  inspectorOpen: false,
  edges: [],
  relationships: [],
  history: [],
  filterStage: 'ALL',

  setSelectedEdge: (edgeId) => {
    const edge = get().edges.find((e) => e.edgeId === edgeId);
    set({
      selectedEdgeId: edgeId,
      selectedEntity: edge
        ? {
            id: edge.edgeId,
            canonicalId: edge.edgeId,
            name: `${edge.symbol} Edge Candidate`,
            stage: edge.currentStage,
            status: edge.status === 'PROMOTED' ? 'APPROVED' : 'VALIDATING',
            createdAt: edge.stageTimestamps.HYPOTHESIS || new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            sha256LineageHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            authorRole: 'QUANT_RESEARCHER',
            versionTag: 'v1.0.0-certified',
            replayAvailable: true,
            properties: {
              symbol: edge.symbol,
              sharpeRatio: edge.sharpeRatio,
              pValue: edge.pValue,
              qualityScore: edge.qualityScore,
            },
          }
        : null,
    });
  },

  setSelectedEntity: (entity) => set({ selectedEntity: entity }),
  setSelectedStage: (stage) => set({ selectedStage: stage }),
  setInspectorOpen: (open) => set({ inspectorOpen: open }),
  setFilterStage: (stage) => set({ filterStage: stage }),

  updateEdgeStage: (edgeId, newStage, progress) => {
    set((state) => ({
      edges: state.edges.map((e) =>
        e.edgeId === edgeId
          ? {
              ...e,
              currentStage: newStage,
              progressPercent: progress,
              stageTimestamps: { ...e.stageTimestamps, [newStage]: new Date().toISOString() },
            }
          : e
      ),
    }));
  },

  inspectEntityById: (entityId) => {
    set({
      inspectorOpen: true,
      selectedEntity: {
        id: entityId,
        canonicalId: entityId,
        name: `Entity ${entityId}`,
        stage: entityId.startsWith('HYP')
          ? 'HYPOTHESIS'
          : entityId.startsWith('EVI')
          ? 'EVIDENCE'
          : entityId.startsWith('EXP')
          ? 'EXPERIMENT'
          : entityId.startsWith('VAL')
          ? 'LIVE_VALIDATION'
          : entityId.startsWith('GOV')
          ? 'GOVERNANCE'
          : entityId.startsWith('ARC')
          ? 'ARCHIVE'
          : 'RESEARCH_INTELLIGENCE',
        status: 'APPROVED',
        createdAt: '2026-08-01T08:00:00Z',
        updatedAt: '2026-08-05T12:00:00Z',
        sha256LineageHash: 'f4c8996fb92427ae41e4649b934ca495991b7852b855e3b0c44298fc1c149afb',
        authorRole: 'SYSTEM_OPERATOR',
        versionTag: 'v1.0.0-certified',
        replayAvailable: true,
        properties: {
          canonicalPrefix: entityId.substring(0, 3),
          auditVerified: true,
          sqlitePersisted: true,
        },
      },
    });
  },
}));
