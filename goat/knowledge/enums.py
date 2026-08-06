"""
Project GOAT v0.7 — Knowledge Taxonomy & Enums

Defines extensible taxonomy enums for Knowledge Objects, Evidence References, and Knowledge Graph Relationships.
"""

from __future__ import annotations

from enum import Enum


class KnowledgeType(str, Enum):
    """Extensible classification of scientific knowledge objects."""

    OBSERVATION = "observation"
    EXPERIMENTAL_FINDING = "experimental_finding"
    VALIDATED_RELATIONSHIP = "validated_relationship"
    SCIENTIFIC_RULE = "scientific_rule"
    SCIENTIFIC_CONSTRAINT = "scientific_constraint"
    STATISTICAL_FACT = "statistical_fact"
    VALIDATION_INSIGHT = "validation_insight"
    TRANSFORMATION_INSIGHT = "transformation_insight"
    EXPLORATION_INSIGHT = "exploration_insight"
    RESEARCH_NOTE = "research_note"
    METHODOLOGICAL_GUIDELINE = "methodological_guideline"


class KnowledgeStatus(str, Enum):
    """Lifecycle status of scientific knowledge objects."""

    PROVISIONAL = "provisional"
    VERIFIED = "verified"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    REJECTED = "rejected"


class EvidenceType(str, Enum):
    """Source classification of supporting evidence references."""

    CANDIDATE_FEATURE = "candidate_feature"
    EXPLORATION_DECISION = "exploration_decision"
    VALIDATION_REPORT = "validation_report"
    QUALITY_GATE_REPORT = "quality_gate_report"
    FEATURE_REGISTRY_RECORD = "feature_registry_record"
    KNOWLEDGE_OBJECT = "knowledge_object"
    EXPERIMENT_RECORD = "experiment_record"
    SIMULATION_RECORD = "simulation_record"
    MARKET_STUDY = "market_study"
    EXTERNAL_PUBLICATION = "external_publication"


class KnowledgeRelationshipType(str, Enum):
    """Relationship edge types in the Knowledge Graph."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFINES = "refines"
    EXTENDS = "extends"
    GENERALIZES = "generalizes"
    DERIVED_FROM = "derived_from"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
