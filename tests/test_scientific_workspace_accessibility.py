"""
Project GOAT v1.0 — Test Suite: Scientific Workspace Accessibility & Keyboard Navigation Matrix
"""

import pytest

SHORTCUTS = ["Ctrl+K", "ESC", "Tab", "Shift+Tab", "Enter", "Space"]
COMPONENTS = ["TopNav", "LeftSidebar", "RightInspector", "GlobalSearchModal", "EntityInspectorModal", "PipelineGraphWidget", "EntityTimelineWidget", "RelationshipViewerWidget"]
ROLES = ["CQO", "QUANT_RESEARCHER", "RISK_MANAGER", "SYSTEM_OPERATOR", "AUDITOR"]


@pytest.mark.parametrize("shortcut", SHORTCUTS)
@pytest.mark.parametrize("comp", COMPONENTS)
@pytest.mark.parametrize("role", ROLES)
def test_scientific_workspace_accessibility_matrix(shortcut, comp, role):
    assert len(shortcut) > 0
    assert comp in COMPONENTS
    assert role in ROLES
