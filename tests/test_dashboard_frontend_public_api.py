"""
Project GOAT v1.0 — Test Suite: Dashboard Frontend Public Integration
"""

import pytest

FEATURE_MODULES = [
    "apps/dashboard/src/main.tsx",
    "apps/dashboard/src/App.tsx",
    "apps/dashboard/src/stores/dashboardStore.ts",
    "apps/dashboard/src/stores/telemetryStore.ts",
    "apps/dashboard/src/stores/healthStore.ts",
    "apps/dashboard/src/stores/sessionStore.ts",
    "apps/dashboard/src/stores/settingsStore.ts",
    "apps/dashboard/src/stores/connectionStore.ts",
    "apps/dashboard/src/stores/notificationStore.ts",
]


@pytest.mark.parametrize("module_path", FEATURE_MODULES)
def test_dashboard_frontend_module_paths_exist(module_path):
    import os
    abs_path = os.path.join("c:\\Users\\The Technologist Fx\\Desktop\\Project Goat", module_path)
    assert os.path.exists(abs_path), f"Frontend module missing: {module_path}"
