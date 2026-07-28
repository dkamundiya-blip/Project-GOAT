"""
Project GOAT v0.6 — Production Public API Surface Regression Test

Verifies top-level production exports across domain models, persistence, engine, stages A-G, reporting, and packaging.
"""

from __future__ import annotations

import goat

# Persistence API
from goat.research.edge.persistence import (
    CURRENT_SCHEMA_VERSION,
    SQLiteEdgeRepository,
)

# Engine & Validation API
from goat.research.edge.validation import (
    HoldoutAccessGate,
    MultiStageValidationEngine,
    MultiplicityFamilyCoordinator,
    ParameterPerturbationCore,
    StageDecision,
    StageResult,
    TemporalLeakageGuard,
    ValidationLifecycleState,
    ValidationStage,
    ValidationStateMachine,
)

# Stage Validators API
from goat.research.edge.validation.stages import (
    BaseStageValidator,
    StageAValidator,
    StageBValidator,
    StageCValidator,
    StageDValidator,
    StageEValidator,
    StageFValidator,
    StageGValidator,
)

# Reporting & Evidence Packaging API
from goat.research.edge.reporting import (
    PACKAGE_SCHEMA_VERSION,
    EvidencePackageVerifier,
    EvidencePackageWriter,
    ReportIntegrityVerifier,
    ValidationReport,
    ValidationReportBuilder,
    compute_report_id,
    render_report_markdown,
    serialize_report_to_json,
    validate_path_component,
)


def test_public_api_symbols_are_importable_and_valid():
    assert goat.__version__ == "0.6.0"
    assert CURRENT_SCHEMA_VERSION == 2
    assert PACKAGE_SCHEMA_VERSION == 1

    # Verify instantiation capability of key facade components
    repo = SQLiteEdgeRepository(":memory:")
    assert repo is not None

    engine = MultiStageValidationEngine(repository=repo)
    assert engine is not None

    builder = ValidationReportBuilder(repository=repo)
    assert builder is not None

    verifier = ReportIntegrityVerifier()
    assert verifier is not None

    writer = EvidencePackageWriter()
    assert writer is not None

    pkg_verifier = EvidencePackageVerifier()
    assert pkg_verifier is not None

    stage_g = StageGValidator()
    assert stage_g is not None
