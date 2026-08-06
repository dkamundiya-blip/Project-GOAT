"""
Project GOAT v0.9 — Dedicated Unit Tests for Hypothesis Reporting Module
"""

import json
import pytest

from goat.research.core.canonical import compute_hypothesis_id
from goat.research.core.models import ScientificHypothesis
from goat.research.registry.engine import ScientificHypothesisRegistry
from goat.research.reporting.reports import (
    generate_executive_report,
    generate_json_report,
    generate_markdown_report,
    generate_registry_summary_report,
    generate_validation_report,
)


@pytest.fixture
def sample_hypothesis():
    hyp_id, canonical_hash = compute_hypothesis_id(
        title="Reporting Sample Hypothesis",
        null_hypothesis="H0: Sample Null Statement.",
        alternative_hypothesis="H1: Sample Alternative Statement.",
        author="REPORT_AUTHOR",
    )
    return ScientificHypothesis(
        hypothesis_id=hyp_id,
        title="Reporting Sample Hypothesis",
        research_question="Does sample reporting function as expected?",
        null_hypothesis="H0: Sample Null Statement.",
        alternative_hypothesis="H1: Sample Alternative Statement.",
        expected_behaviour="Expected sample markdown output formatting.",
        independent_variables=["sample_var_1", "sample_var_2"],
        dependent_variables=["sample_output_1"],
        assumptions=["Normal distribution assumption"],
        risk_statement="Sample tail risk statement.",
        success_criteria=["p < 0.01"],
        failure_criteria=["p >= 0.05"],
        author="REPORT_AUTHOR",
        created_timestamp="2026-08-04T12:00:00Z",
        updated_timestamp="2026-08-04T12:00:00Z",
        tags=["report", "sample"],
        canonical_hash=canonical_hash,
    )


def test_generate_markdown_report(sample_hypothesis):
    report = generate_markdown_report(sample_hypothesis)
    assert "# SCIENTIFIC HYPOTHESIS REPORT" in report
    assert sample_hypothesis.title in report
    assert sample_hypothesis.hypothesis_id in report
    assert "H0: Sample Null Statement." in report
    assert "sample_var_1" in report


def test_generate_json_report(sample_hypothesis):
    json_str = generate_json_report(sample_hypothesis)
    data = json.loads(json_str)
    assert data["hypothesis_id"] == sample_hypothesis.hypothesis_id
    assert data["title"] == sample_hypothesis.title


@pytest.mark.parametrize("hyp_count", range(1, 10))
def test_generate_executive_report(hyp_count: int):
    registry = ScientificHypothesisRegistry()
    for i in range(hyp_count):
        registry.register_hypothesis(
            title=f"Executive Hyp #{i}",
            research_question=f"Question #{i}?",
            null_hypothesis=f"H0: Null Statement #{i}",
            alternative_hypothesis=f"H1: Alternative Statement #{i}",
            expected_behaviour=f"Expected Behaviour #{i}",
            success_criteria=["p < 0.01"],
        )

    exec_report = generate_executive_report(registry)
    assert "EXECUTIVE REPORT" in exec_report
    assert f"Total Hypotheses**: `{hyp_count}`" in exec_report
    assert f"Executive Hyp #{hyp_count - 1}" in exec_report


def test_generate_summary_report(sample_hypothesis):
    registry = ScientificHypothesisRegistry()
    registry.register_hypothesis(
        title="Summary Target Title",
        research_question="Question for summary target?",
        null_hypothesis="H0: Null hypothesis for summary target.",
        alternative_hypothesis="H1: Alternative hypothesis for summary target.",
        expected_behaviour="Expected behaviour for summary target.",
        success_criteria=["p < 0.01"],
    )
    summary = registry.generate_summary()
    report = generate_registry_summary_report(summary)

    assert "REGISTRY SUMMARY REPORT" in report
    assert summary.summary_id in report
    assert "DRAFT" in report
