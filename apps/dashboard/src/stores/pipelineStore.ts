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

const SAMPLE_EDGES: PipelineEdgeState[] = [
  {
    edgeId: 'EDG_VOL10_MOMENTUM_001',
    hypothesisId: 'HYP_VOL10_001',
    symbol: 'VOLATILITY_10',
    currentStage: 'LIVE_VALIDATION',
    progressPercent: 78,
    qualityScore: 0.94,
    sharpeRatio: 2.85,
    pValue: 0.0012,
    status: 'ACTIVE',
    stageTimestamps: {
      HYPOTHESIS: '2026-08-01T08:00:00Z',
      EVIDENCE: '2026-08-02T10:30:00Z',
      EXPERIMENT: '2026-08-03T14:15:00Z',
      STATISTICAL_EVALUATION: '2026-08-04T09:00:00Z',
      LIVE_VALIDATION: '2026-08-05T12:00:00Z',
      GOVERNANCE: null,
      ARCHIVE: null,
      RESEARCH_INTELLIGENCE: null,
    },
    childEdgeIds: [],
  },
  {
    edgeId: 'EDG_BOOM500_REVERSION_002',
    hypothesisId: 'HYP_BOOM500_002',
    symbol: 'BOOM_500',
    currentStage: 'GOVERNANCE',
    progressPercent: 92,
    qualityScore: 0.98,
    sharpeRatio: 3.12,
    pValue: 0.0004,
    status: 'PROMOTED',
    stageTimestamps: {
      HYPOTHESIS: '2026-07-28T08:00:00Z',
      EVIDENCE: '2026-07-29T10:30:00Z',
      EXPERIMENT: '2026-07-30T14:15:00Z',
      STATISTICAL_EVALUATION: '2026-07-31T09:00:00Z',
      LIVE_VALIDATION: '2026-08-02T12:00:00Z',
      GOVERNANCE: '2026-08-04T16:00:00Z',
      ARCHIVE: null,
      RESEARCH_INTELLIGENCE: '2026-08-05T09:00:00Z',
    },
    childEdgeIds: [],
  },
  {
    edgeId: 'EDG_CRASH1000_REGIME_003',
    hypothesisId: 'HYP_CRASH1000_003',
    symbol: 'CRASH_1000',
    currentStage: 'STATISTICAL_EVALUATION',
    progressPercent: 62,
    qualityScore: 0.88,
    sharpeRatio: 2.15,
    pValue: 0.0085,
    status: 'ACTIVE',
    stageTimestamps: {
      HYPOTHESIS: '2026-08-03T08:00:00Z',
      EVIDENCE: '2026-08-04T10:30:00Z',
      EXPERIMENT: '2026-08-05T14:15:00Z',
      STATISTICAL_EVALUATION: '2026-08-06T09:00:00Z',
      LIVE_VALIDATION: null,
      GOVERNANCE: null,
      ARCHIVE: null,
      RESEARCH_INTELLIGENCE: null,
    },
    childEdgeIds: [],
  },
];

export const usePipelineStore = create<PipelineState>((set, get) => ({
  selectedEdgeId: 'EDG_VOL10_MOMENTUM_001',
  selectedEntity: {
    id: 'EDG_VOL10_MOMENTUM_001',
    canonicalId: 'EDG_VOL10_MOMENTUM_001',
    name: 'Volatility 10 Microstructure Momentum Edge',
    stage: 'LIVE_VALIDATION',
    status: 'VALIDATING',
    createdAt: '2026-08-01T08:00:00Z',
    updatedAt: '2026-08-05T12:00:00Z',
    sha256LineageHash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    authorRole: 'QUANT_RESEARCHER',
    versionTag: 'v1.0.0-certified',
    replayAvailable: true,
    properties: {
      symbol: 'VOLATILITY_10',
      sharpeRatio: 2.85,
      pValue: 0.0012,
      qualityScore: 0.94,
    },
  },
  selectedStage: null,
  inspectorOpen: false,
  edges: SAMPLE_EDGES,
  relationships: [
    { sourceId: 'HYP_VOL10_001', targetId: 'EDG_VOL10_MOMENTUM_001', relationshipType: 'PARENT_OF', timestamp: '2026-08-01T08:00:00Z' },
    { sourceId: 'EVI_VOL10_001', targetId: 'EDG_VOL10_MOMENTUM_001', relationshipType: 'EVIDENCE_FOR', timestamp: '2026-08-02T10:30:00Z' },
    { sourceId: 'VAL_VOL10_001', targetId: 'EDG_VOL10_MOMENTUM_001', relationshipType: 'VALIDATED_IN', timestamp: '2026-08-05T12:00:00Z' },
  ],
  history: [
    {
      id: 'HST_001',
      timestamp: '2026-08-01T08:00:00Z',
      action: 'HYPOTHESIS_CREATED',
      operatorRole: 'QUANT_RESEARCHER',
      previousState: 'NONE',
      newState: 'HYPOTHESIS',
      hashSignature: 'a1b2c3d4e5f6',
    },
    {
      id: 'HST_002',
      timestamp: '2026-08-02T10:30:00Z',
      action: 'EVIDENCE_COLLECTED',
      operatorRole: 'QUANT_RESEARCHER',
      previousState: 'HYPOTHESIS',
      newState: 'EVIDENCE',
      hashSignature: 'b2c3d4e5f6a1',
    },
    {
      id: 'HST_003',
      timestamp: '2026-08-05T12:00:00Z',
      action: 'LIVE_VALIDATION_STARTED',
      operatorRole: 'CQO',
      previousState: 'STATISTICAL_EVALUATION',
      newState: 'LIVE_VALIDATION',
      hashSignature: 'c3d4e5f6a1b2',
    },
  ],
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
