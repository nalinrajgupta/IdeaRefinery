from __future__ import annotations

import json

from hypothesis import given, strategies as st

from idea_refinery.io import atomic_write_json, canonical_json, content_hash
from idea_refinery.run_store import RunStore


@given(st.dictionaries(st.text(min_size=1), st.integers(), max_size=10))
def test_canonical_hash_is_independent_of_mapping_order(value: dict[str, int]) -> None:
    reversed_value = dict(reversed(list(value.items())))
    assert canonical_json(value) == canonical_json(reversed_value)
    assert content_hash(value) == content_hash(reversed_value)


def test_atomic_json_write_never_leaves_temporary_file(tmp_path) -> None:
    target = tmp_path / "value.json"
    atomic_write_json(target, {"ok": True})
    assert json.loads(target.read_text()) == {"ok": True}
    assert not list(tmp_path.glob(".*.tmp"))


def test_trace_sequence_is_monotonic(feature_dir) -> None:
    store = RunStore.create(feature_dir, "run-1", "001-example", "0" * 64)
    first = store.append_event("configuration-resolved", "configuration", "controller")
    second = store.append_event("stage-transition", "review", "controller")
    assert (first["sequence"], second["sequence"]) == (1, 2)
