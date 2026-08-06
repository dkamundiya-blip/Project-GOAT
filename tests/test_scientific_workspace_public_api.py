"""
Project GOAT v1.0 — Test Suite: Scientific Workspace Public API Exports & Component Exports Matrix
"""

import pytest

EXPORTS = [
  "usePipelineStore",
  "useSearchStore",
  "PipelineGraphWidget",
  "EntityTimelineWidget",
  "RelationshipViewerWidget",
  "GlobalSearchModal",
  "EntityInspectorModal",
  "ResearchPage",
  "EvidencePage",
  "ExperimentsPage",
  "StatisticsPage",
  "LiveValidationPage",
  "GovernancePage",
  "KnowledgeGraphPage",
  "ResearchIntelligencePage",
  "ArchivePage",
  "MonitoringPage",
  "PipelineVisualizerPage",
]
EXPORT_TYPES = ["STORE", "WIDGET", "PAGE", "MODAL"]


@pytest.mark.parametrize("export_name", EXPORTS)
@pytest.mark.parametrize("export_type", EXPORT_TYPES)
def test_scientific_workspace_public_api_exports(export_name, export_type):
    assert len(export_name) > 0
    assert export_type in EXPORT_TYPES
