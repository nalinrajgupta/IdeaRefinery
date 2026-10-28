"""Stable root-finding identities, canonicalization, and lineage validation."""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
from dataclasses import dataclass, replace
from typing import Iterable, Mapping


_SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3, "blocker": 4}


@dataclass(frozen=True)
class RootFinding:
    root_id: str
    severity: str
    summary: str
    completion_criterion: str
    requirement_ids: tuple[str, ...]
    artifact_paths: tuple[str, ...]
    coverage_ids: tuple[str, ...]
    aliases: tuple[str, ...]
    reviewers: tuple[str, ...]
    evidence: tuple[str, ...]
    caused_by: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()

    def with_lineage(
        self,
        *,
        caused_by: Iterable[str] | None = None,
        supersedes: Iterable[str] | None = None,
    ) -> "RootFinding":
        return replace(
            self,
            caused_by=(
                tuple(sorted(set(caused_by)))
                if caused_by is not None
                else self.caused_by
            ),
            supersedes=(
                tuple(sorted(set(supersedes)))
                if supersedes is not None
                else self.supersedes
            ),
        )


def completion_criterion_identity(
    requirement_ids: Iterable[str],
    artifact_paths: Iterable[str],
    completion_criterion: str,
) -> str:
    identity = {
        "requirement_ids": sorted(set(requirement_ids)),
        "artifact_paths": sorted({_normalize_path(path) for path in artifact_paths}),
        "completion_criterion": _normalize_text(completion_criterion),
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"ROOT-{digest[:24]}"


def canonicalize_findings(
    findings: Iterable[Mapping[str, object]],
    *,
    criterion_aliases: Mapping[str, str] | None = None,
) -> tuple[RootFinding, ...]:
    aliases = {
        _normalize_text(source): _normalize_text(target)
        for source, target in (criterion_aliases or {}).items()
    }
    grouped: dict[str, list[Mapping[str, object]]] = {}
    local_to_root: dict[str, str] = {}
    for finding in findings:
        criterion = _resolve_criterion_alias(
            _normalize_text(str(finding["completion_criterion"])), aliases
        )
        root_id = completion_criterion_identity(
            _strings(finding.get("affected_requirement_ids", ())),
            _strings(finding.get("artifact_paths", ())),
            criterion,
        )
        grouped.setdefault(root_id, []).append(finding)
        local_to_root[str(finding["local_id"])] = root_id

    roots: list[RootFinding] = []
    for root_id, members in sorted(grouped.items()):
        severity = max(
            (str(member["severity"]) for member in members),
            key=lambda value: _SEVERITY_RANK[value],
        )
        criterion = min(
            _resolve_criterion_alias(
                _normalize_text(str(member["completion_criterion"])), aliases
            )
            for member in members
        )
        caused_by = _lineage_ids(members, "caused_by", local_to_root, root_id)
        supersedes = _lineage_ids(members, "supersedes", local_to_root, root_id)
        roots.append(
            RootFinding(
                root_id=root_id,
                severity=severity,
                summary=min(str(member["summary"]) for member in members),
                completion_criterion=criterion,
                requirement_ids=_union(members, "affected_requirement_ids"),
                artifact_paths=tuple(
                    sorted(
                        {
                            _normalize_path(path)
                            for member in members
                            for path in _strings(member.get("artifact_paths", ()))
                        }
                    )
                ),
                coverage_ids=_union(members, "coverage_ids"),
                aliases=tuple(sorted(str(member["local_id"]) for member in members)),
                reviewers=tuple(sorted(str(member["reviewer"]) for member in members)),
                evidence=_union(members, "evidence"),
                caused_by=caused_by,
                supersedes=supersedes,
            )
        )
    validate_lineage(roots)
    return tuple(roots)


def validate_lineage(findings: Iterable[RootFinding]) -> None:
    roots = tuple(findings)
    graph = {
        root.root_id: {
            target
            for target in (*root.caused_by, *root.supersedes)
            if target in {candidate.root_id for candidate in roots}
        }
        for root in roots
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError(f"finding lineage contains a cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for target in sorted(graph[node]):
            visit(target)
        visiting.remove(node)
        visited.add(node)

    for root_id in sorted(graph):
        visit(root_id)


def _normalize_text(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", value.casefold())
    return " ".join(words)


def _normalize_path(value: str) -> str:
    normalized = posixpath.normpath(value.replace("\\", "/"))
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _resolve_criterion_alias(value: str, aliases: Mapping[str, str]) -> str:
    seen: set[str] = set()
    while value in aliases:
        if value in seen:
            raise ValueError("completion criterion aliases contain a cycle")
        seen.add(value)
        value = aliases[value]
    return value


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        raise ValueError("finding collection fields must be sequences")
    return tuple(str(item) for item in value)


def _union(members: Iterable[Mapping[str, object]], field: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                value
                for member in members
                for value in _strings(member.get(field, ()))
            }
        )
    )


def _lineage_ids(
    members: Iterable[Mapping[str, object]],
    field: str,
    local_to_root: Mapping[str, str],
    own_root: str,
) -> tuple[str, ...]:
    targets = {
        local_to_root.get(value, value)
        for member in members
        for value in _strings(member.get(field, ()))
    }
    targets.discard(own_root)
    return tuple(sorted(targets))
