"""
Project GOAT v0.9 — Dedicated Unit Tests for Statistical Reporting Generators
"""

import json
import pytest

from goat.statistics.core.canonical import compute_summary_id
from goat.statistics.core.enums import EvaluationConfidence, EvaluationStatus, ScientificDecision
from goat.statistics.core.models import EvaluationSummary
from goat.statistics.evaluation.engine import StatisticalEvaluationEngine
from goat.statistics.reporting.reports import (
    generate_confidence_report,
    generate_executive_report,
    generate_expectancy_report,
    generate_json_report,
    generate_significance_report,
    generate_statistical_report,
)


@pytest.fixture
def eval_engine():
    return StatisticalEvaluationEngine()


def test_generate_statistical_report(eval_engine: StatisticalEvaluationEngine):
    samples = [0.5] * 100
    ev, dec, conf, sig, exp = eval_engine.evaluate_experiment(
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        samples=samples,
    )

    report = generate_statistical_report(ev)
    assert "# STATISTICAL EVALUATION REPORT" in report
    assert ev.evaluation_id in report
    assert ev.experiment_id in report


def test_generate_confidence_report(eval_engine: StatisticalEvaluationEngine):
    samples = [0.5] * 100
    ev, dec, conf, sig, exp = eval_engine.evaluate_experiment(
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        samples=samples,
    )

    report = generate_confidence_report(conf)
    assert "# CONFIDENCE ASSESSMENT REPORT" in report
    assert conf.confidence_id in report


def test_generate_significance_report(eval_engine: StatisticalEvaluationEngine):
    samples = [0.5] * 100
    ev, dec, conf, sig, exp = eval_engine.evaluate_experiment(
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        samples=samples,
    )

    report = generate_significance_report(sig)
    assert "# SIGNIFICANCE ASSESSMENT REPORT" in report
    assert sig.significance_id in report


def test_generate_expectancy_report(eval_engine: StatisticalEvaluationEngine):
    samples = [0.5] * 100
    ev, dec, conf, sig, exp = eval_engine.evaluate_experiment(
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        samples=samples,
    )

    report = generate_expectancy_report(exp)
    assert "# EXPECTANCY ASSESSMENT REPORT" in report
    assert exp.expectancy_id in report


def test_generate_json_report(eval_engine: StatisticalEvaluationEngine):
    samples = [0.5] * 100
    ev, _, _, _, _ = eval_engine.evaluate_experiment(
        experiment_id="EXP_1234567890ABCDEF",
        hypothesis_id="HYP_1234567890ABCDEF",
        samples=samples,
    )

    json_str = generate_json_report(ev)
    data = json.loads(json_str)
    assert data["evaluation_id"] == ev.evaluation_id


@pytest.mark.parametrize("eval_count", range(1, 10))
def test_generate_executive_report(eval_engine: StatisticalEvaluationEngine, eval_count: int):
    evaluations = []
    for i in range(eval_count):
        ev, _, _, _, _ = eval_engine.evaluate_experiment(
            experiment_id=f"EXP_{i:016X}",
            hypothesis_id=f"HYP_{i:016X}",
            samples=[0.5 + i] * 50,
        )
        evaluations.append(ev)

    sum_id, sum_hash = compute_summary_id(total_evaluations=eval_count, total_decisions=eval_count)
    summary = EvaluationSummary(
        summary_id=sum_id,
        total_evaluations=eval_count,
        total_decisions=eval_count,
        decision_counts={"SUPPORTED": eval_count},
        confidence_counts={"HIGH": eval_count},
        status_counts={"COMPLETED": eval_count},
        timestamp="2026-08-04T12:00:00Z",
        canonical_hash=sum_hash,
    )

    report = generate_executive_report(summary, evaluations)
    assert "# PROJECT GOAT — STATISTICAL EVALUATION EXECUTIVE REPORT" in report
    assert f"Total Evaluations**: `{eval_count}`" in report
