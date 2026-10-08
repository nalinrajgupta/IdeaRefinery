"""Resolve role configuration against a controller-captured session roster."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigurationError
from .io import content_hash
from .schemas import validate_document
from .types import EFFORT_ORDER

ROLE_NAMES = ("ceo", "product", "architect", "eval", "baseline")
EFFORT_NAMES = [effort.value for effort in EFFORT_ORDER]


def bundled_config_path() -> Path:
    candidates = (
        Path(__file__).resolve().parent / "defaults" / "config.yaml",
        Path(__file__).resolve().parents[2] / "defaults" / "config.yaml",
    )
    for path in candidates:
        if path.is_file():
            return path
    raise ConfigurationError("defaults-missing", "bundled default configuration is missing")


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ConfigurationError("config-invalid", f"configuration must be a mapping: {path}")
    return value


def _merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _roster_models(roster: dict[str, Any]) -> dict[str, list[str]]:
    models = roster.get("models")
    if not isinstance(models, dict):
        raise ConfigurationError("roster-invalid", "session roster must contain a models mapping")
    normalized: dict[str, list[str]] = {}
    for model, capabilities in models.items():
        if isinstance(capabilities, list):
            normalized[model] = [str(item) for item in capabilities]
        elif isinstance(capabilities, dict):
            normalized[model] = list(capabilities.get("reasoning_efforts", []))
        else:
            raise ConfigurationError("roster-invalid", f"invalid capabilities for model {model}")
    return normalized


def _select_effort(requested: str, supported: list[str]) -> tuple[str | None, str | None]:
    if requested in supported:
        return requested, None
    if requested not in EFFORT_NAMES:
        raise ConfigurationError("effort-invalid", f"unknown reasoning effort: {requested}")
    requested_index = EFFORT_NAMES.index(requested)
    candidates = [name for name in supported if name in EFFORT_NAMES and EFFORT_NAMES.index(name) <= requested_index]
    if not candidates:
        return None, "no-supported-effort-at-or-below-request"
    selected = max(candidates, key=EFFORT_NAMES.index)
    return selected, f"clamped-from-{requested}-to-{selected}"


def resolve_config(
    roster: dict[str, Any],
    *,
    repository: dict[str, Any] | None = None,
    invocation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    defaults = load_yaml(bundled_config_path())
    validate_document("config", defaults)
    repository = repository or {"schema_version": "1.0", "roles": {}}
    validate_document("config", repository)
    if invocation is None:
        invocation = {"schema_version": "1.0", "overrides": {"roles": {}}}
    else:
        validate_document("invocation", invocation)

    merged = _merge(defaults, repository)
    merged = _merge(merged, {"roles": invocation["overrides"]["roles"]})
    available = _roster_models(roster)
    repository_roles = repository.get("roles", {})
    invocation_roles = invocation["overrides"]["roles"]
    resolved_roles: dict[str, Any] = {}

    for role in ROLE_NAMES:
        requested = merged["roles"][role]
        if role in invocation_roles:
            source = "invocation"
        elif role in repository_roles:
            source = "repository"
        else:
            source = "bundled"
        requested_model = requested["model"]
        fallbacks = list(requested.get("fallbacks", []))
        if source == "invocation" and requested_model not in available and "fallbacks" not in invocation_roles[role]:
            raise ConfigurationError(
                "explicit-model-unavailable",
                f"explicit model {requested_model!r} is unavailable for {role}",
                {"role": role, "available_models": sorted(available)},
            )
        selected_model = next((candidate for candidate in [requested_model, *fallbacks] if candidate in available), None)
        if selected_model is None:
            status = "skipped-unavailable" if role == "baseline" else "failed-role"
            resolved_roles[role] = {
                "role": role,
                "requested_model": requested_model,
                "selected_model": None,
                "requested_reasoning_effort": requested["reasoning_effort"],
                "selected_reasoning_effort": None,
                "fallbacks": fallbacks,
                "source": source,
                "status": status,
                "degradation_reason": "all-candidates-unavailable",
                "effort_adjustment": None,
            }
            continue
        selected_effort, adjustment = _select_effort(requested["reasoning_effort"], available[selected_model])
        if selected_effort is None:
            raise ConfigurationError("effort-unavailable", f"model {selected_model} supports no acceptable reasoning effort")
        status = "validated" if selected_model == requested_model else "degraded-fallback"
        resolved_roles[role] = {
            "role": role,
            "requested_model": requested_model,
            "selected_model": selected_model,
            "requested_reasoning_effort": requested["reasoning_effort"],
            "selected_reasoning_effort": selected_effort,
            "fallbacks": fallbacks,
            "source": source,
            "status": status,
            "degradation_reason": None if status == "validated" else f"fallback-from-{requested_model}",
            "effort_adjustment": adjustment,
        }

    return {
        "schema_version": "1.0",
        "roles": resolved_roles,
        "execution": merged.get("execution", {}),
        "roster_snapshot": copy.deepcopy(roster),
        "roster_snapshot_hash": content_hash(roster),
        "sources": {
            "bundled": content_hash(defaults),
            "repository": content_hash(repository),
            "invocation": content_hash(invocation),
        },
    }
