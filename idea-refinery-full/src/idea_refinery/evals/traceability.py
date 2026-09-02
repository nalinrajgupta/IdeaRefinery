"""Requirement/task bidirectional traceability."""

from __future__ import annotations

from typing import Any


def check_traceability(requirements: set[str], tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    mapped_requirements = {req for task in tasks.values() for req in task.get("requirement_ids", [])}
    unmapped_requirements = sorted(requirements - mapped_requirements)
    unmapped_tasks = sorted(
        task_id for task_id, value in tasks.items()
        if not value.get("requirement_ids") and not value.get("operational_need") and not value.get("risk")
    )
    evidence = [f"requirement {req} has no implementation task" for req in unmapped_requirements]
    evidence += [f"task {task_id} has no requirement, risk, or operational need" for task_id in unmapped_tasks]
    return {
        "passed": not evidence,
        "unmapped_requirements": unmapped_requirements,
        "unmapped_tasks": unmapped_tasks,
        "evidence": evidence,
    }
