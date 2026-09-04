"""Deterministic continuation contracts for implementation runs."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass, replace
import json
from pathlib import Path
from typing import Any

from .errors import ContractError, StateError


_INTERNAL_ORDER = {
    "protected-path-authorization": -2,
    "validator-prerequisite": -1,
    "task": 0,
    "review": 1,
    "review-correction": 2,
    "task-promotion": 3,
    "state-recording": 4,
    "convergence": 5,
    "after-hook": 6,
    "final-verification": 7,
}
_BLOCKER_VERDICTS = {
    "missing-authority": "BLOCKED ON DECISION",
    "material-decision": "BLOCKED ON DECISION",
    "external-state": "BLOCKED ON VERIFICATION",
}
_TERMINAL_VERDICTS = frozenset({"IMPLEMENTATION COMPLETE", *_BLOCKER_VERDICTS.values()})
_PREREQUISITE_OUTCOMES = frozenset({"exact-validator", "equivalent-evidence", "unavailable"})
_SATISFYING_PREREQUISITE_OUTCOMES = frozenset({"exact-validator", "equivalent-evidence"})


@dataclass(frozen=True)
class CompletionItem:
    """One independently observable implementation completion gate."""

    item_id: str
    kind: str
    completed: bool = False
    category: str | None = None
    evidence: str | None = None


@dataclass(frozen=True)
class Blocker:
    """A genuine stop that requires authority, a decision, or external recovery."""

    category: str
    detail: str


@dataclass(frozen=True)
class PrerequisiteResolution:
    """Persisted evidence that a validator prerequisite is met or unavailable."""

    category: str
    outcome: str
    evidence: str


@dataclass(frozen=True)
class ContinuationState:
    """Checklist snapshot consumed by the terminal-verdict drive loop."""

    checklist: tuple[CompletionItem, ...]
    requested_authorizations: frozenset[str] = frozenset()
    blockers: tuple[Blocker, ...] = ()
    prerequisite_resolutions: tuple[PrerequisiteResolution, ...] = ()
    terminal_verdict: str | None = None


@dataclass(frozen=True)
class ContinuationResult:
    """The terminal result of one deterministic continuation drive."""

    state: ContinuationState
    verdict: str
    completed_item_ids: tuple[str, ...]
    authorization_requests: tuple[str, ...] = ()


def _validate_contract(state: ContinuationState) -> None:
    invalid_item_ids = [
        item.item_id
        for item in state.checklist
        if not isinstance(item.item_id, str) or not item.item_id.strip()
    ]
    if invalid_item_ids:
        raise ContractError(
            "completion-item-id-invalid",
            "completion checklist item_id must be a non-empty string",
            {"item_ids": invalid_item_ids},
        )
    invalid_completed = [
        item.item_id for item in state.checklist if type(item.completed) is not bool
    ]
    if invalid_completed:
        raise ContractError(
            "completion-completed-invalid",
            "completion completed must be a boolean",
            {"item_ids": invalid_completed},
        )
    invalid_evidence = [
        item.item_id
        for item in state.checklist
        if item.evidence is not None and (not isinstance(item.evidence, str) or not item.evidence.strip())
    ]
    if invalid_evidence:
        raise ContractError(
            "completion-evidence-invalid",
            "completion evidence must be a non-empty string when present",
            {"item_ids": invalid_evidence},
        )
    unevidenced_completed = [item.item_id for item in state.checklist if item.completed and not item.evidence]
    if unevidenced_completed:
        raise ContractError(
            "completion-evidence-missing",
            "completed checklist items require recorded acceptance evidence",
            {"item_ids": unevidenced_completed},
        )
    seen_item_ids: set[str] = set()
    duplicate_item_ids: set[str] = set()
    for item in state.checklist:
        if item.item_id in seen_item_ids:
            duplicate_item_ids.add(item.item_id)
        seen_item_ids.add(item.item_id)
    if duplicate_item_ids:
        raise ContractError(
            "completion-item-id-duplicate",
            "completion checklist item ids must be unique",
            {"item_ids": sorted(duplicate_item_ids)},
        )
    unknown_kinds = sorted({item.kind for item in state.checklist} - set(_INTERNAL_ORDER))
    if unknown_kinds:
        raise ContractError("unknown-completion-kind", "unknown completion checklist kind", {"kinds": unknown_kinds})
    unscoped_preflight = sorted(
        item.item_id
        for item in state.checklist
        if item.kind in {"protected-path-authorization", "validator-prerequisite"} and not item.category
    )
    if unscoped_preflight:
        raise ContractError(
            "completion-category-missing",
            "completion category is required for preflight gates",
            {"item_ids": unscoped_preflight},
        )
    unknown_blockers = sorted({blocker.category for blocker in state.blockers} - set(_BLOCKER_VERDICTS))
    if unknown_blockers:
        raise ContractError("unknown-blocker-category", "unknown blocker category", {"categories": unknown_blockers})
    unknown_outcomes = sorted(
        {resolution.outcome for resolution in state.prerequisite_resolutions}
        - _PREREQUISITE_OUTCOMES
    )
    if unknown_outcomes:
        raise ContractError(
            "unknown-prerequisite-outcome",
            "unknown prerequisite resolution outcome",
            {"outcomes": unknown_outcomes},
        )
    invalid_resolutions = [
        resolution.category
        for resolution in state.prerequisite_resolutions
        if not resolution.category.strip() or not resolution.evidence.strip()
    ]
    if invalid_resolutions:
        raise ContractError(
            "prerequisite-resolution-invalid",
            "prerequisite resolution requires category and evidence",
            {"categories": invalid_resolutions},
        )


def validate_completion_checklist(state: ContinuationState) -> None:
    """Reject unsupported blockers and unsafe non-terminal pauses."""
    _validate_contract(state)
    pending_internal = [
        item.item_id
        for item in state.checklist
        if not item.completed and item.kind in _INTERNAL_ORDER and _INTERNAL_ORDER[item.kind] >= 0
    ]
    is_terminal = state.terminal_verdict in _TERMINAL_VERDICTS
    if not is_terminal and pending_internal:
        raise StateError(
            "actionable-internal-checklist",
            "non-terminal state has actionable internal checklist items",
            {"item_ids": pending_internal},
        )
    if state.terminal_verdict and not is_terminal:
        raise ContractError(
            "unknown-terminal-verdict",
            "unknown terminal verdict",
            {"terminal_verdict": state.terminal_verdict},
        )
    if state.terminal_verdict == "IMPLEMENTATION COMPLETE" and any(not item.completed for item in state.checklist):
        raise StateError(
            "incomplete-terminal-checklist",
            "completion verdict requires every checklist item to be complete",
        )


def _blocker_verdict(blockers: tuple[Blocker, ...]) -> str:
    verdicts = {_BLOCKER_VERDICTS[blocker.category] for blocker in blockers}
    return "BLOCKED ON DECISION" if "BLOCKED ON DECISION" in verdicts else "BLOCKED ON VERIFICATION"


def _new_authorization_requests(
    prefix: str,
    items: Collection[CompletionItem],
    requested: frozenset[str],
) -> tuple[str, ...]:
    scoped = dict.fromkeys(f"{prefix}:{item.category}" for item in items)
    return tuple(token for token in scoped if token not in requested)


def _resolution_tuple(
    resolutions: dict[str, PrerequisiteResolution],
) -> tuple[PrerequisiteResolution, ...]:
    return tuple(resolutions[category] for category in sorted(resolutions))


def _validated_action_results(action_results: Mapping[str, str] | None) -> dict[str, str]:
    """Reject malformed executed-action results before they authorize completion."""
    if action_results is None:
        return {}
    if not isinstance(action_results, Mapping):
        raise ContractError("action-results-invalid", "action results must be a mapping")
    invalid = sorted(
        str(item_id)
        for item_id, evidence in action_results.items()
        if not isinstance(item_id, str)
        or not item_id.strip()
        or not isinstance(evidence, str)
        or not evidence.strip()
    )
    if invalid:
        raise ContractError(
            "action-result-invalid",
            "action result requires an item id and non-empty evidence",
            {"item_ids": invalid},
        )
    return dict(action_results)


def _require_nonempty_string(value: Any, *, code: str, field: str, item_index: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(
            code,
            f"{field} must be a non-empty string",
            {"item_index": item_index, "field": field},
        )
    return value


def continuation_state_from_document(document: dict[str, Any]) -> ContinuationState:
    """Load a provider-independent continuation state from a replay document."""
    raw_checklist = document.get("checklist", [])
    if not isinstance(raw_checklist, list):
        raise ContractError("checklist-invalid", "checklist must be a list")
    checklist_items: list[CompletionItem] = []
    for item_index, item in enumerate(raw_checklist):
        if not isinstance(item, dict):
            raise ContractError(
                "completion-item-invalid",
                "completion checklist item must be an object",
                {"item_index": item_index},
            )
        item_id = _require_nonempty_string(
            item.get("item_id"),
            code="completion-item-id-invalid",
            field="item_id",
            item_index=item_index,
        )
        kind = _require_nonempty_string(
            item.get("kind"),
            code="completion-kind-invalid",
            field="kind",
            item_index=item_index,
        )
        completed = item.get("completed", False)
        if type(completed) is not bool:
            raise ContractError(
                "completion-completed-invalid",
                "completion completed must be a boolean",
                {"item_index": item_index},
            )
        category = item.get("category")
        if kind in {"protected-path-authorization", "validator-prerequisite"}:
            category = _require_nonempty_string(
                category,
                code="completion-category-invalid",
                field="category",
                item_index=item_index,
            )
        elif category is not None:
            category = _require_nonempty_string(
                category,
                code="completion-category-invalid",
                field="category",
                item_index=item_index,
            )
        evidence = item.get("evidence")
        if evidence is not None:
            evidence = _require_nonempty_string(
                evidence,
                code="completion-evidence-invalid",
                field="evidence",
                item_index=item_index,
            )
        checklist_items.append(CompletionItem(item_id, kind, completed, category, evidence))
    checklist = tuple(checklist_items)
    raw_blockers = document.get("blockers", [])
    if not isinstance(raw_blockers, list):
        raise ContractError("blockers-invalid", "blockers must be a list")
    blockers: list[Blocker] = []
    for item_index, item in enumerate(raw_blockers):
        if not isinstance(item, dict):
            raise ContractError(
                "blocker-invalid",
                "blocker must be an object",
                {"item_index": item_index},
            )
        category = _require_nonempty_string(
            item.get("category"),
            code="blocker-category-invalid",
            field="category",
            item_index=item_index,
        )
        if category not in _BLOCKER_VERDICTS:
            raise ContractError(
                "unknown-blocker-category",
                "unknown blocker category",
                {"item_index": item_index, "category": category},
            )
        detail = _require_nonempty_string(
            item.get("detail"),
            code="blocker-detail-invalid",
            field="detail",
            item_index=item_index,
        )
        blockers.append(Blocker(category, detail))
    raw_resolutions = document.get("prerequisite_resolutions", [])
    if not isinstance(raw_resolutions, list):
        raise ContractError(
            "prerequisite-resolutions-invalid",
            "prerequisite resolutions must be a list",
        )
    resolutions: list[PrerequisiteResolution] = []
    for item_index, item in enumerate(raw_resolutions):
        if not isinstance(item, dict):
            raise ContractError(
                "prerequisite-resolution-invalid",
                "prerequisite resolution must be an object",
                {"item_index": item_index},
            )
        category = _require_nonempty_string(
            item.get("category"),
            code="prerequisite-resolution-category-invalid",
            field="category",
            item_index=item_index,
        )
        outcome = _require_nonempty_string(
            item.get("outcome"),
            code="prerequisite-resolution-outcome-invalid",
            field="outcome",
            item_index=item_index,
        )
        if outcome not in _PREREQUISITE_OUTCOMES:
            raise ContractError(
                "prerequisite-resolution-outcome-invalid",
                "unknown prerequisite resolution outcome",
                {"item_index": item_index, "outcome": outcome},
            )
        evidence = _require_nonempty_string(
            item.get("evidence"),
            code="prerequisite-resolution-evidence-invalid",
            field="evidence",
            item_index=item_index,
        )
        resolutions.append(PrerequisiteResolution(category, outcome, evidence))
    raw_requested_authorizations = document.get("requested_authorizations", [])
    if not isinstance(raw_requested_authorizations, list):
        raise ContractError(
            "requested-authorizations-invalid",
            "requested authorizations must be a list",
        )
    requested_authorizations = frozenset(
        _require_nonempty_string(
            value,
            code="requested-authorization-invalid",
            field="requested_authorizations",
            item_index=item_index,
        )
        for item_index, value in enumerate(raw_requested_authorizations)
    )
    terminal_verdict = document.get("terminal_verdict")
    if terminal_verdict is not None and not isinstance(terminal_verdict, str):
        raise ContractError(
            "terminal-verdict-invalid",
            "terminal verdict must be a string or null",
        )
    return ContinuationState(
        checklist=checklist,
        requested_authorizations=requested_authorizations,
        blockers=tuple(blockers),
        prerequisite_resolutions=tuple(resolutions),
        terminal_verdict=terminal_verdict,
    )


def continuation_result_document(result: ContinuationResult) -> dict[str, Any]:
    """Serialize only the stable terminal-drive boundary for replay comparison."""
    return {
        "authorization_requests": list(result.authorization_requests),
        "completed_item_ids": list(result.completed_item_ids),
        "terminal_verdict": result.state.terminal_verdict,
        "verdict": result.verdict,
    }


def replay_continuation_fixture(path: Path) -> dict[str, Any]:
    """Execute a continuation replay fixture and compare its terminal boundary."""
    document = json.loads((path / "input.json").read_text(encoding="utf-8"))
    result = drive_terminal(
        continuation_state_from_document(document),
        granted_authorizations=document.get("granted_authorizations", []),
        available_validators=document.get("available_validators", []),
        action_results=document.get("action_results"),
    )
    actual = continuation_result_document(result)
    expected = json.loads((path / "expected.json").read_text(encoding="utf-8"))
    return {"passed": actual == expected, "expected": expected, "actual": actual}


def _transition_evidence(
    item: CompletionItem,
    results: Mapping[str, str],
    resolutions: Mapping[str, PrerequisiteResolution],
    granted: frozenset[str],
) -> str | None:
    """Return the recorded evidence that authorizes completing one gate."""
    if item.kind == "protected-path-authorization" and f"protected-path:{item.category}" in granted:
        return f"authorization granted: protected-path:{item.category}"
    if item.kind == "validator-prerequisite":
        resolution = resolutions.get(item.category or "")
        if resolution is not None and resolution.outcome in _SATISFYING_PREREQUISITE_OUTCOMES:
            return f"{resolution.outcome}: {resolution.evidence}"
        return None
    recorded = results.get(item.item_id) or item.evidence
    return recorded if isinstance(recorded, str) and recorded.strip() else None


def drive_terminal(
    state: ContinuationState,
    *,
    granted_authorizations: Collection[str] = (),
    available_validators: Collection[str] = (),
    action_results: Mapping[str, str] | None = None,
) -> ContinuationResult:
    """Complete every evidenced routine gate in deterministic workflow order."""
    _validate_contract(state)
    results = _validated_action_results(action_results)
    granted = frozenset(granted_authorizations)
    validators = frozenset(available_validators)
    if state.blockers:
        verdict = _blocker_verdict(state.blockers)
        next_state = replace(state, terminal_verdict=verdict)
        return ContinuationResult(next_state, verdict, ())
    protected_paths = sorted(
        (
            item
            for item in state.checklist
            if not item.completed and item.kind == "protected-path-authorization"
        ),
        key=lambda item: (item.category or "", item.item_id),
    )
    missing_paths = tuple(
        item
        for item in protected_paths
        if f"protected-path:{item.category}" not in granted
    )
    authorization_requests = _new_authorization_requests(
        "protected-path",
        missing_paths,
        state.requested_authorizations,
    )
    if missing_paths:
        verdict = "BLOCKED ON DECISION"
        return ContinuationResult(
            replace(
                state,
                requested_authorizations=state.requested_authorizations.union(authorization_requests),
                terminal_verdict=verdict,
            ),
            verdict,
            (),
            authorization_requests,
        )
    resolution_by_category = {
        resolution.category: resolution for resolution in state.prerequisite_resolutions
    }
    validator_items = tuple(
        item
        for item in state.checklist
        if not item.completed and item.kind == "validator-prerequisite"
    )
    for item in validator_items:
        if item.category in validators:
            resolution_by_category[item.category] = PrerequisiteResolution(
                item.category,
                "exact-validator",
                f"available validator: {item.category}",
            )
    missing_validators = sorted(
        (
            item
            for item in validator_items
            if resolution_by_category.get(item.category, PrerequisiteResolution("", "unavailable", "")).outcome
            not in _SATISFYING_PREREQUISITE_OUTCOMES
        ),
        key=lambda item: (item.category or "", item.item_id),
    )
    validator_requests = _new_authorization_requests(
        "validator",
        missing_validators,
        state.requested_authorizations,
    )
    if missing_validators:
        for item in missing_validators:
            resolution_by_category.setdefault(
                item.category,
                PrerequisiteResolution(
                    item.category,
                    "unavailable",
                    "no exact validator or equivalent evidence available",
                ),
            )
        verdict = "BLOCKED ON VERIFICATION"
        return ContinuationResult(
            replace(
                state,
                requested_authorizations=state.requested_authorizations.union(validator_requests),
                prerequisite_resolutions=_resolution_tuple(resolution_by_category),
                terminal_verdict=verdict,
            ),
            verdict,
            (),
            validator_requests,
        )
    pending = sorted(
        (item for item in state.checklist if not item.completed),
        key=lambda item: (_INTERNAL_ORDER[item.kind], item.item_id),
    )
    evidence_by_item: dict[str, str] = {}
    unevidenced: list[str] = []
    for item in pending:
        evidence = _transition_evidence(item, results, resolution_by_category, granted)
        if evidence:
            evidence_by_item[item.item_id] = evidence
        else:
            unevidenced.append(item.item_id)
    if unevidenced:
        blocker = Blocker(
            "external-state",
            "no recorded transition evidence for: " + ", ".join(unevidenced),
        )
        verdict = _BLOCKER_VERDICTS[blocker.category]
        return ContinuationResult(
            replace(
                state,
                blockers=state.blockers + (blocker,),
                prerequisite_resolutions=_resolution_tuple(resolution_by_category),
                terminal_verdict=verdict,
            ),
            verdict,
            (),
        )
    completed_item_ids = tuple(item.item_id for item in pending)
    next_state = replace(
        state,
        checklist=tuple(
            replace(item, completed=True, evidence=evidence_by_item[item.item_id])
            if item.item_id in evidence_by_item
            else item
            for item in state.checklist
        ),
        prerequisite_resolutions=_resolution_tuple(resolution_by_category),
        terminal_verdict="IMPLEMENTATION COMPLETE",
    )
    validate_completion_checklist(next_state)
    return ContinuationResult(next_state, "IMPLEMENTATION COMPLETE", completed_item_ids)
