"""Final finding/blind-spot disposition and readiness coverage gates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .coverage import CoverageMatrix, CoverageState


class Disposition(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected-with-rationale"
    DEFERRED = "deferred-with-trigger"
    DECISION_NEEDED = "decision-needed"


@dataclass(frozen=True)
class ReadinessResult:
    verdict: str
    undispositioned: tuple[str, ...]


def evaluate_readiness(
    matrix: CoverageMatrix,
    *,
    finding_dispositions: Mapping[str, Disposition | None],
    blind_spot_dispositions: Mapping[str, Disposition | None] | None = None,
) -> ReadinessResult:
    """Require explicit terminal dispositions for every material uncovered item."""

    blind_spot_dispositions = blind_spot_dispositions or {}
    undispositioned: set[str] = {
        root_id
        for root_id, disposition in finding_dispositions.items()
        if disposition is None
    }
    for entry in matrix.values():
        if not entry.applicable:
            continue
        needs_disposition = entry.state in {
            CoverageState.BLIND_SPOT,
            CoverageState.FOLLOWUP_PENDING,
        } or (entry.state is CoverageState.PENDING and entry.item.risk in {"critical", "high"})
        if needs_disposition and blind_spot_dispositions.get(entry.item.coverage_id) is None:
            undispositioned.add(entry.item.coverage_id)

    unresolved = tuple(sorted(undispositioned))
    verdict = "BLOCKED ON DECISION" if unresolved else "READY FOR IMPLEMENTATION"
    return ReadinessResult(verdict=verdict, undispositioned=unresolved)
