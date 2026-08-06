"""
Project GOAT v0.7 — Scientific Planning Engine

Implements ScientificPlanningEngine for transforming research priorities into executable scientific plans,
generating plan tasks, building planning graphs, and replaying plans.
"""

from __future__ import annotations

import datetime
from typing import Any

from goat.planning.enums import ScientificPlanStage
from goat.planning.graph import ScientificPlanningGraph
from goat.planning.model import (
    ScientificPlan,
    compute_plan_fingerprint,
    compute_plan_id,
)
from goat.planning.task import ScientificPlanTask, compute_task_id
from goat.research.edge.canonical import compute_canonical_sha256


class ScientificPlanningValidationError(ValueError):
    """Raised when scientific plan generation, task creation, or graph ordering fails."""
    pass


class ScientificPlanningEngine:
    """Master engine transforming research priorities into deterministic execution plans and task DAGs."""

    def __init__(self) -> None:
        self._plans: dict[str, ScientificPlan] = {}
        self._tasks: dict[str, ScientificPlanTask] = {}
        self._graphs: dict[str, ScientificPlanningGraph] = {}

    def create_plan(
        self,
        research_objective: str,
        source_priority_ids: list[str],
        version: str = "1.0.0",
    ) -> tuple[ScientificPlan, ScientificPlanningGraph]:
        """Create a ScientificPlan and generate standard task pipeline DAG.

        Args:
            research_objective: Statement of research objective.
            source_priority_ids: Source Research Priority IDs (RPR_<HEX16>).
            version: Version string.

        Returns:
            Tuple of (ScientificPlan, ScientificPlanningGraph).
        """
        if not source_priority_ids:
            raise ScientificPlanningValidationError("Cannot create ScientificPlan without source_priority_ids")

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        fingerprint = compute_plan_fingerprint(research_objective, source_priority_ids, version)
        plan_id, canon_hash = compute_plan_id(fingerprint, version)

        # Build Standard 6-Stage Task Sequence:
        # INITIALIZATION -> DATA_PREPARATION -> EXPERIMENT_DESIGN -> EXECUTION -> VALIDATION -> SYNTHESIS
        graph = ScientificPlanningGraph()
        stages = [
            ScientificPlanStage.INITIALIZATION,
            ScientificPlanStage.DATA_PREPARATION,
            ScientificPlanStage.EXPERIMENT_DESIGN,
            ScientificPlanStage.EXECUTION,
            ScientificPlanStage.VALIDATION,
            ScientificPlanStage.SYNTHESIS,
        ]

        task_ids: list[str] = []
        prev_tid = ""
        for order, stg in enumerate(stages, start=1):
            tid, t_hash = compute_task_id(plan_id, order, stg.value)
            deps = [prev_tid] if prev_tid else []
            task = ScientificPlanTask(
                task_id=tid,
                parent_plan_id=plan_id,
                stage=stg,
                dependencies=deps,
                execution_order=order,
                status="pending",
                task_hash=t_hash,
            )
            graph.add_task(task)
            self._tasks[tid] = task
            task_ids.append(tid)
            prev_tid = tid

        plan = ScientificPlan(
            plan_id=plan_id,
            canonical_hash=canon_hash,
            scientific_fingerprint=fingerprint,
            semantic_version=version,
            creation_timestamp=timestamp,
            source_priority_ids=source_priority_ids,
            research_objective=research_objective,
            dependency_graph_id=f"GRAPH_{plan_id[4:]}",
            execution_status="proposed",
        )

        self._plans[plan_id] = plan
        self._graphs[plan.dependency_graph_id] = graph
        return plan, graph

    def get_plan(self, plan_id: str) -> ScientificPlan:
        """Retrieve ScientificPlan by Plan ID."""
        if plan_id not in self._plans:
            raise KeyError(f"Plan ID '{plan_id}' not found in ScientificPlanningEngine")
        return self._plans[plan_id]

    def get_graph(self, graph_id: str) -> ScientificPlanningGraph:
        """Retrieve ScientificPlanningGraph by Graph ID."""
        if graph_id not in self._graphs:
            raise KeyError(f"Graph ID '{graph_id}' not found in ScientificPlanningEngine")
        return self._graphs[graph_id]

    def replay_planning(self, plan_id: str) -> tuple[ScientificPlan, list[str]]:
        """Replay scientific plan task sequence deterministically.

        Args:
            plan_id: Target Plan ID (PLN_<HEX16>).

        Returns:
            Tuple of (ScientificPlan, list of task IDs in topological order).
        """
        plan = self.get_plan(plan_id)
        graph = self.get_graph(plan.dependency_graph_id)
        topological_order = graph.get_topological_order()
        return plan, topological_order
