from __future__ import annotations

import itertools

from hypothesis import given, strategies as st

from idea_refinery.envelopes import aggregate_envelopes, execution_batches


def test_capacity_changes_batches_not_role_order_or_inputs() -> None:
    roles = ["ceo", "product", "architect"]
    parallel = execution_batches(roles, capacity=3)
    sequential = execution_batches(roles, capacity=1)
    assert parallel == [("ceo", "product", "architect")]
    assert sequential == [("ceo",), ("product",), ("architect",)]
    assert [role for batch in parallel for role in batch] == [role for batch in sequential for role in batch]


@given(st.permutations(["ceo", "product", "architect"]))
def test_aggregation_is_independent_of_completion_order(order) -> None:
    envelopes = [{"role": role, "envelope_id": f"ENV-{role}"} for role in order]
    assert [item["role"] for item in aggregate_envelopes(envelopes)] == ["ceo", "product", "architect"]
