"""Shared immutable domain types."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class Role(str, Enum):
    CEO = "ceo"
    PRODUCT = "product"
    ARCHITECT = "architect"
    EVAL = "eval"
    BASELINE = "baseline"


class ReasoningEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"
    MAX = "max"
    ULTRA = "ultra"


EFFORT_ORDER = tuple(ReasoningEffort)


@dataclass(frozen=True)
class RoleAssignment:
    role: Role
    requested_model: str
    selected_model: str | None
    requested_reasoning_effort: ReasoningEffort
    selected_reasoning_effort: ReasoningEffort | None
    fallbacks: tuple[str, ...]
    source: str
    status: str
    degradation_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def enum_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): enum_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [enum_value(item) for item in value]
    return value
