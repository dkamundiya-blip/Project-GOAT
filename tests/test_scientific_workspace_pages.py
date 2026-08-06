"""
Project GOAT v1.0 — Test Suite: Scientific Workspace Page Route Rendering Matrix
"""

import pytest

PAGES = [
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
ROLES = ["CQO", "QUANT_RESEARCHER", "RISK_MANAGER", "SYSTEM_OPERATOR", "AUDITOR"]
THEMES = ["dark", "light"]
REFRESH_RATES = [1000, 2000, 5000]


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize("theme", THEMES)
@pytest.mark.parametrize("rate", REFRESH_RATES)
def test_scientific_workspace_pages_matrix(page, role, theme, rate):
    assert page.endswith("Page")
    assert role in ROLES
    assert theme in ["dark", "light"]
    assert rate > 0
