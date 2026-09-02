from __future__ import annotations

from idea_refinery.run_store import RunStore


def test_resume_reuses_only_exact_committed_stage(feature_dir) -> None:
    store = RunStore.create(feature_dir, "run-1", "001-example", "a" * 64)
    store.commit_stage(
        "review",
        input_hashes={"spec": "b" * 64, "brief": "c" * 64, "config": "a" * 64},
        output_hashes={"ceo": "d" * 64},
        schema_hashes={"review-result": "e" * 64},
        protected_hashes={"spec.md": "b" * 64},
    )
    reusable, reasons = store.resume_eligibility(
        "review",
        input_hashes={"spec": "b" * 64, "brief": "c" * 64, "config": "a" * 64},
        schema_hashes={"review-result": "e" * 64},
        protected_hashes={"spec.md": "b" * 64},
    )
    assert reusable is True
    assert reasons == []


def test_resume_reports_every_mismatch(feature_dir) -> None:
    store = RunStore.create(feature_dir, "run-1", "001-example", "a" * 64)
    store.commit_stage(
        "review",
        input_hashes={"spec": "b" * 64},
        output_hashes={"ceo": "d" * 64},
        schema_hashes={"review-result": "e" * 64},
        protected_hashes={"spec.md": "b" * 64},
    )
    reusable, reasons = store.resume_eligibility(
        "review",
        input_hashes={"spec": "x" * 64},
        schema_hashes={"review-result": "y" * 64},
        protected_hashes={"spec.md": "z" * 64},
    )
    assert reusable is False
    assert set(reasons) == {"input-hash-mismatch", "schema-hash-mismatch", "protected-artifact-drift"}


def test_uncommitted_stage_is_never_reused(feature_dir) -> None:
    store = RunStore.create(feature_dir, "run-1", "001-example", "a" * 64)
    assert store.resume_eligibility("review", input_hashes={}, schema_hashes={}, protected_hashes={}) == (
        False,
        ["stage-not-committed"],
    )
