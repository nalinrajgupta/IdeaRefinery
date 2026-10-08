from __future__ import annotations

import pytest

from idea_refinery.config import resolve_config
from idea_refinery.errors import ConfigurationError


def test_bundled_defaults_resolve_against_current_session(full_roster) -> None:
    resolved = resolve_config(full_roster)
    assert resolved["roles"]["ceo"]["selected_model"] == "gpt-5.5"
    assert resolved["roles"]["product"]["selected_model"] == "gpt-5.6-terra"
    assert resolved["roles"]["architect"]["selected_model"] == "gpt-5.6-sol"
    assert resolved["execution"]["concurrency_limit"] == 3


def test_invocation_overrides_repository_and_repository_overrides_defaults(full_roster) -> None:
    repository = {
        "schema_version": "1.0",
        "roles": {"product": {"model": "gpt-5.6-sol", "reasoning_effort": "medium"}},
    }
    invocation = {
        "schema_version": "1.0",
        "overrides": {"roles": {"product": {"model": "gpt-5.5", "reasoning_effort": "high"}}},
    }
    resolved = resolve_config(full_roster, repository=repository, invocation=invocation)
    product = resolved["roles"]["product"]
    assert product["selected_model"] == "gpt-5.5"
    assert product["source"] == "invocation"


def test_explicit_unavailable_model_without_explicit_fallback_fails(full_roster) -> None:
    invocation = {
        "schema_version": "1.0",
        "overrides": {"roles": {"ceo": {"model": "missing", "reasoning_effort": "high"}}},
    }
    with pytest.raises(ConfigurationError) as caught:
        resolve_config(full_roster, invocation=invocation)
    assert caught.value.code == "explicit-model-unavailable"
    assert "gpt-5.5" in caught.value.details["available_models"]


def test_explicit_fallback_and_effort_clamping_are_recorded(full_roster) -> None:
    invocation = {
        "schema_version": "1.0",
        "overrides": {
            "roles": {
                "product": {
                    "model": "missing",
                    "reasoning_effort": "ultra",
                    "fallbacks": ["gpt-5.5"],
                }
            }
        },
    }
    product = resolve_config(full_roster, invocation=invocation)["roles"]["product"]
    assert product["selected_model"] == "gpt-5.5"
    assert product["selected_reasoning_effort"] == "xhigh"
    assert product["status"] == "degraded-fallback"
    assert product["effort_adjustment"]


def test_unavailable_baseline_is_skipped(reduced_roster) -> None:
    baseline = resolve_config(reduced_roster)["roles"]["baseline"]
    assert baseline["status"] == "skipped-unavailable"
    assert baseline["selected_model"] is None
