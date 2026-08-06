/**
 * Project GOAT v1.0 — Scientific Pipeline & Entity Inspection TypeScript Definitions
 */

export type PipelineStage =
  | 'HYPOTHESIS'
  | 'EVIDENCE'
  | 'EXPERIMENT'
  | 'STATISTICAL_EVALUATION'
  | 'LIVE_VALIDATION'
  | 'GOVERNANCE'
  | 'ARCHIVE'
  | 'RESEARCH_INTELLIGENCE';

export interface EntityMetadata {
  id: string;
  canonicalId: string;
  name: string;
  stage: PipelineStage;
  status: 'DRAFT' | 'PENDING' | 'VALIDATING' | 'APPROVED' | 'REJECTED' | 'ARCHIVED';
  createdAt: string;
  updatedAt: string;
  sha256LineageHash: string;
  authorRole: string;
  versionTag: string;
  replayAvailable: boolean;
  properties: Record<string, string | number | boolean>;
}

export interface EntityRelationship {
  sourceId: string;
  targetId: string;
  relationshipType: 'PARENT_OF' | 'EVIDENCE_FOR' | 'EVALUATED_BY' | 'VALIDATED_IN' | 'APPROVED_BY' | 'DERIVED_FROM';
  timestamp: string;
}

export interface EntityHistoryItem {
  id: string;
  timestamp: string;
  action: string;
  operatorRole: string;
  previousState: string;
  newState: string;
  hashSignature: string;
}

export interface PipelineEdgeState {
  edgeId: string;
  hypothesisId: string;
  symbol: string;
  currentStage: PipelineStage;
  progressPercent: number;
  qualityScore: number;
  sharpeRatio: number;
  pValue: number;
  status: 'ACTIVE' | 'PROMOTED' | 'REJECTED' | 'DECAYED';
  stageTimestamps: Record<PipelineStage, string | null>;
  parentEdgeId?: string;
  childEdgeIds: string[];
}

export interface SearchResultItem {
  id: string;
  canonicalId: string;
  title: string;
  stage: PipelineStage;
  matchField: string;
  snippet: string;
}
