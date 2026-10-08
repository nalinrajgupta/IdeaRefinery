"""Stable errors returned by the deterministic runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(eq=False)
class RefineryError(Exception):
    code: str
    message: str
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def as_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            value["details"] = self.details
        return value


class ContractError(RefineryError):
    """Input failed structural or semantic contract validation."""


class ConfigurationError(RefineryError):
    """Configuration could not be resolved against the session roster."""


class StateError(RefineryError):
    """Run state is invalid, stale, or unsafe to mutate."""
