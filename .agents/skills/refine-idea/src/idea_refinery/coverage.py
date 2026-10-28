"""Coverage taxonomy, evidence aggregation, and focused follow-up selection."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence


class CoverageState(str, Enum):
    PENDING = "pending"
    INAPPLICABLE = "inapplicable"
    REVIEWED_NO_FINDING = "reviewed-no-finding"
    FINDING_RAISED = "finding-raised"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    BLIND_SPOT = "blind-spot"
    FOLLOWUP_PENDING = "follow-up-pending"


_TAXONOMY = (
    ("journeys", "User actors and journeys", "high", "product", "ceo"),
    ("requirements", "Requirements and acceptance criteria", "high", "product", "ceo"),
    ("interfaces", "Interfaces and integration contracts", "high", "architect", "product"),
    ("reliability", "Reliability and failure recovery", "high", "architect", "product"),
    ("security", "Security and trust boundaries", "high", "architect", "product"),
    ("operations", "Operations and auditability", "high", "architect", "product"),
    ("rollout", "Distribution, compatibility, and rollout", "medium", "architect", "product"),
    ("data", "Data model and persistence", "high", "architect", "product"),
    ("tests", "Test and evaluation strategy", "high", "architect", "product"),
)

_RISK_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


@dataclass(frozen=True, order=True)
class CoverageItem:
    coverage_id: str
    area: str
    description: str
    risk: str
    primary_role: str
    secondary_role: str
    requirement_ids: tuple[str, ...] = ()


@dataclass
class CoverageEntry:
    item: CoverageItem
    applicable: bool = True
    state: CoverageState = CoverageState.PENDING
    evidence: tuple[str, ...] = ()
    finding_ids: tuple[str, ...] = ()
    reviewers: tuple[str, ...] = ()

    @property
    def is_successful(self) -> bool:
        if self.state is CoverageState.INAPPLICABLE:
            return True
        return self.state in {CoverageState.REVIEWED_NO_FINDING, CoverageState.RESOLVED}

    def as_dict(self) -> dict[str, object]:
        return {
            "applicable": self.applicable,
            "evidence": list(self.evidence),
            "finding_ids": list(self.finding_ids),
            "reviewers": list(self.reviewers),
            "state": self.state.value,
        }


@dataclass(frozen=True)
class RoleAvailability:
    failed: bool = False
    degraded: bool = False
    scopes: frozenset[str] = frozenset()

    @property
    def available(self) -> bool:
        return not self.failed


@dataclass(frozen=True)
class FollowupRequest:
    role: str
    coverage_ids: tuple[str, ...]
    rationale: str


@dataclass
class CoverageMatrix:
    _entries: dict[str, CoverageEntry]
    followups: list[FollowupRequest] = field(default_factory=list)

    @classmethod
    def from_items(cls, items: Iterable[CoverageItem]) -> "CoverageMatrix":
        materialized = list(items)
        entries = {item.coverage_id: CoverageEntry(item=item) for item in materialized}
        if len(entries) != len(materialized):
            raise ValueError("coverage IDs must be unique")
        return cls(entries)

    def __getitem__(self, coverage_id: str) -> CoverageEntry:
        return self._entries[coverage_id]

    def values(self) -> tuple[CoverageEntry, ...]:
        return tuple(self._entries[key] for key in sorted(self._entries))

    def apply_attestation(self, attestation: Mapping[str, object], reviewer: str) -> None:
        coverage_id = str(attestation["coverage_id"])
        if coverage_id not in self._entries:
            raise KeyError(f"unknown coverage item {coverage_id}")
        entry = self._entries[coverage_id]
        applicable = bool(attestation["applicable"])
        reviewed = bool(attestation["reviewed"])
        evidence = _unique_strings(attestation.get("evidence", ()))
        finding_ids = _unique_strings(attestation.get("finding_ids", ()))

        if entry.state is CoverageState.INAPPLICABLE and applicable:
            raise ValueError(f"coverage item {coverage_id} is terminally inapplicable")
        if not applicable:
            if evidence or finding_ids or reviewed:
                raise ValueError("inapplicable attestations cannot be reviewed or cite findings")
            entry.applicable = False
            entry.state = CoverageState.INAPPLICABLE
        else:
            entry.applicable = True
            if finding_ids:
                entry.state = CoverageState.FINDING_RAISED
            elif reviewed and evidence:
                if entry.state is not CoverageState.FINDING_RAISED:
                    entry.state = CoverageState.REVIEWED_NO_FINDING
            else:
                if entry.state not in {
                    CoverageState.FINDING_RAISED,
                    CoverageState.REVIEWED_NO_FINDING,
                }:
                    entry.state = CoverageState.BLIND_SPOT

        entry.evidence = tuple(sorted(set(entry.evidence).union(evidence)))
        entry.finding_ids = tuple(sorted(set(entry.finding_ids).union(finding_ids)))
        entry.reviewers = tuple(sorted(set(entry.reviewers).union({reviewer})))

    def aggregate(
        self, attestations: Iterable[Mapping[str, object]], reviewer: str
    ) -> None:
        for attestation in sorted(attestations, key=lambda value: str(value["coverage_id"])):
            self.apply_attestation(attestation, reviewer)

    def as_dict(self) -> dict[str, dict[str, object]]:
        return {
            coverage_id: self._entries[coverage_id].as_dict()
            for coverage_id in sorted(self._entries)
        }


def derive_coverage_taxonomy(
    requirements: Iterable[Mapping[str, object]],
) -> tuple[CoverageItem, ...]:
    """Build the fixed v1 taxonomy and attach requirement IDs deterministically."""

    requirement_map: dict[str, set[str]] = {area: set() for area, *_ in _TAXONOMY}
    for requirement in requirements:
        requirement_id = str(requirement["id"])
        for area in requirement.get("areas", ()):  # type: ignore[union-attr]
            area_name = str(area)
            if area_name not in requirement_map:
                raise ValueError(f"unknown coverage area {area_name!r}")
            requirement_map[area_name].add(requirement_id)

    return tuple(
        CoverageItem(
            coverage_id=f"COV-{index:03d}",
            area=area,
            description=description,
            risk=risk,
            primary_role=primary,
            secondary_role=secondary,
            requirement_ids=tuple(sorted(requirement_map[area])),
        )
        for index, (area, description, risk, primary, secondary) in enumerate(
            _TAXONOMY, start=1
        )
    )


def select_followup(
    matrix: CoverageMatrix,
    roles: Mapping[str, RoleAvailability],
) -> FollowupRequest | None:
    """Select at most one owner/item pair for an uncovered high-risk item."""

    if matrix.followups:
        return None
    candidates = [
        entry
        for entry in matrix.values()
        if entry.applicable
        and entry.state is CoverageState.BLIND_SPOT
        and entry.item.risk in {"critical", "high"}
    ]
    candidates.sort(
        key=lambda entry: (_RISK_RANK[entry.item.risk], entry.item.coverage_id)
    )
    for entry in candidates:
        owner = _select_owner(entry.item, roles)
        if owner is None:
            continue
        role, rationale = owner
        request = FollowupRequest(role, (entry.item.coverage_id,), rationale)
        entry.state = CoverageState.FOLLOWUP_PENDING
        matrix.followups.append(request)
        return request
    return None


def _select_owner(
    item: CoverageItem, roles: Mapping[str, RoleAvailability]
) -> tuple[str, str] | None:
    primary = roles.get(item.primary_role)
    if primary is not None and primary.available:
        return item.primary_role, "primary owner available"
    secondary = roles.get(item.secondary_role)
    if secondary is not None and secondary.available:
        return item.secondary_role, "primary unavailable; secondary owner available"

    scoped = sorted(
        (
            role,
            availability,
        )
        for role, availability in roles.items()
        if availability.available and item.area in availability.scopes
    )
    non_degraded = [pair for pair in scoped if not pair[1].degraded]
    if non_degraded:
        return non_degraded[0][0], "scope tie-break selected first non-degraded role"
    if scoped:
        return scoped[0][0], "scope tie-break selected degraded role"
    return None


def _unique_strings(values: object) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple, set, frozenset)):
        raise ValueError("expected a sequence of strings")
    result = tuple(sorted({str(value) for value in values if str(value)}))
    return result
