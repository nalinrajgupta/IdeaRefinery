"""Spec Kit artifact dependency and invalidation rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import Iterable


ARTIFACT_DAG: dict[str, frozenset[str]] = {
    "constitution": frozenset(
        {"plan", "research", "data-model", "contracts", "quickstart"}
    ),
    "spec": frozenset(
        {"plan", "research", "data-model", "contracts", "quickstart"}
    ),
    "plan": frozenset({"tasks", "analysis"}),
    "research": frozenset({"tasks", "analysis"}),
    "data-model": frozenset({"tasks", "analysis"}),
    "contracts": frozenset({"tasks", "analysis"}),
    "quickstart": frozenset({"tasks", "analysis"}),
    "tasks": frozenset({"analysis"}),
    "analysis": frozenset(),
}

_FILE_KEYS = {
    "constitution.md": "constitution",
    "spec.md": "spec",
    "plan.md": "plan",
    "research.md": "research",
    "data-model.md": "data-model",
    "quickstart.md": "quickstart",
    "tasks.md": "tasks",
}


class ChangeKind(str, Enum):
    REPAIR = "repair"
    SPEC_UPDATE = "spec-update"
    ARTIFACT_UPDATE = "artifact-update"
    SEPARATE_USER_DECISION = "separate-user-decision"


@dataclass(frozen=True)
class ChangeClassification:
    kind: ChangeKind
    changed: frozenset[str]
    invalidated: frozenset[str]
    repair_eligible: bool


def artifact_key(path_or_key: str) -> str:
    """Map an artifact path or canonical key to one DAG node."""

    normalized = path_or_key.strip().replace("\\", "/").rstrip("/")
    if normalized in ARTIFACT_DAG:
        return normalized
    path = PurePosixPath(normalized)
    if "contracts" in path.parts:
        return "contracts"
    if "analysis" in path.parts or path.name.startswith("analysis"):
        return "analysis"
    if path.name in _FILE_KEYS:
        return _FILE_KEYS[path.name]
    raise ValueError(f"unknown Spec Kit artifact: {path_or_key}")


def calculate_invalidation(
    changed_artifacts: Iterable[str], *, include_changed: bool = True
) -> frozenset[str]:
    """Return the transitive downstream closure for changed artifacts."""

    changed = {artifact_key(value) for value in changed_artifacts}
    invalidated = set(changed if include_changed else ())
    pending = list(changed)
    visited: set[str] = set()
    while pending:
        artifact = pending.pop()
        if artifact in visited:
            continue
        visited.add(artifact)
        downstream = ARTIFACT_DAG[artifact]
        invalidated.update(downstream)
        pending.extend(downstream - visited)
    return frozenset(invalidated)


def classify_change(source: str, changed_artifacts: Iterable[str]) -> ChangeClassification:
    """Classify a mutation before it can enter the bounded repair loop."""

    changed = frozenset(artifact_key(value) for value in changed_artifacts)
    if not changed:
        raise ValueError("at least one changed artifact is required")

    if "constitution" in changed:
        kind = ChangeKind.SEPARATE_USER_DECISION
        eligible = False
    elif source == "accepted-clarification":
        if "spec" not in changed:
            raise ValueError("an accepted clarification must update spec.md")
        kind = ChangeKind.SPEC_UPDATE
        eligible = False
    elif source == "analysis-finding":
        kind = ChangeKind.REPAIR
        eligible = True
    else:
        kind = ChangeKind.ARTIFACT_UPDATE
        eligible = False

    return ChangeClassification(
        kind=kind,
        changed=changed,
        invalidated=calculate_invalidation(changed),
        repair_eligible=eligible,
    )


__all__ = [
    "ARTIFACT_DAG",
    "ChangeClassification",
    "ChangeKind",
    "artifact_key",
    "calculate_invalidation",
    "classify_change",
]
