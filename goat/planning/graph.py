"""
Project GOAT v0.7 — Scientific Planning Graph

Defines ScientificPlanningGraph for building acyclic task DAGs, cycle checking, and topological sequence generation.
"""

from __future__ import annotations

from goat.planning.task import ScientificPlanTask


class ScientificPlanningGraph:
    """Acyclic directed graph connecting ScientificPlanTasks and establishing execution order."""

    def __init__(self) -> None:
        self._tasks: dict[str, ScientificPlanTask] = {}   # task_id -> ScientificPlanTask
        self._adjacency: dict[str, list[str]] = {}        # task_id -> list of dependent task_ids (children)
        self._in_degree: dict[str, int] = {}             # task_id -> in-degree count

    def add_task(self, task: ScientificPlanTask) -> None:
        """Add a ScientificPlanTask to the planning graph.

        Args:
            task: ScientificPlanTask instance.
        """
        tid = task.task_id
        if tid in self._tasks:
            raise ValueError(f"Task ID '{tid}' already exists in ScientificPlanningGraph")

        self._tasks[tid] = task
        if tid not in self._adjacency:
            self._adjacency[tid] = []
        if tid not in self._in_degree:
            self._in_degree[tid] = 0

        # Process dependencies
        for dep in task.dependencies:
            if dep not in self._adjacency:
                self._adjacency[dep] = []
            self._adjacency[dep].append(tid)
            self._in_degree[tid] += 1

        # Check for cycles via topological sort validation
        if not self._is_dag():
            # Rollback addition
            del self._tasks[tid]
            del self._adjacency[tid]
            del self._in_degree[tid]
            for dep in task.dependencies:
                self._adjacency[dep].remove(tid)
            raise ValueError(f"Cycle detected: adding task '{tid}' creates a cycle in ScientificPlanningGraph")

    def get_topological_order(self) -> list[str]:
        """Return task IDs in valid topological execution order."""
        in_degree_copy = dict(self._in_degree)
        zero_in_degree = [tid for tid, deg in in_degree_copy.items() if deg == 0]
        # Sort by execution_order attribute to ensure deterministic order among independent tasks
        zero_in_degree.sort(key=lambda t: (self._tasks[t].execution_order, t))

        topological_order: list[str] = []
        while zero_in_degree:
            curr = zero_in_degree.pop(0)
            topological_order.append(curr)

            for neighbor in self._adjacency.get(curr, []):
                in_degree_copy[neighbor] -= 1
                if in_degree_copy[neighbor] == 0:
                    zero_in_degree.append(neighbor)
            zero_in_degree.sort(key=lambda t: (self._tasks[t].execution_order, t))

        if len(topological_order) != len(self._tasks):
            raise ValueError("Graph contains a cycle; cannot perform topological sort")
        return topological_order

    def get_root_tasks(self) -> list[str]:
        """Return task IDs with zero in-degree (root tasks)."""
        roots = [tid for tid, deg in self._in_degree.items() if deg == 0]
        roots.sort(key=lambda t: (self._tasks[t].execution_order, t))
        return roots

    def get_terminal_tasks(self) -> list[str]:
        """Return task IDs with zero out-degree (terminal tasks)."""
        terminals = [tid for tid, children in self._adjacency.items() if not children]
        terminals.sort(key=lambda t: (self._tasks[t].execution_order, t))
        return terminals

    def _is_dag(self) -> bool:
        """Helper checking if the current graph is a DAG."""
        try:
            order = self.get_topological_order()
            return len(order) == len(self._tasks)
        except ValueError:
            return False
