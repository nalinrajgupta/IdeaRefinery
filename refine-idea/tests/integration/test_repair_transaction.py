from __future__ import annotations

from pathlib import Path

import pytest

from idea_refinery.errors import StateError
from idea_refinery.repair import RepairTransaction


def active_tree(tmp_path: Path) -> Path:
    active = tmp_path / "active"
    active.mkdir()
    (active / "spec.md").write_text("old spec", encoding="utf-8")
    (active / "tasks.md").write_text("old tasks", encoding="utf-8")
    return active


def test_validation_failure_rolls_back_without_touching_active_tree(tmp_path: Path) -> None:
    active = active_tree(tmp_path)
    transaction = RepairTransaction.begin(active, tmp_path / "transaction")
    (transaction.staged_root / "spec.md").write_text("bad spec", encoding="utf-8")

    result = transaction.promote(lambda _: ["new high-severity contradiction"])

    assert result.status == "rolled-back"
    assert result.errors == ("new high-severity contradiction",)
    assert (active / "spec.md").read_text(encoding="utf-8") == "old spec"
    assert transaction.staged_root.exists()


def test_successful_validation_promotes_whole_staged_tree(tmp_path: Path) -> None:
    active = active_tree(tmp_path)
    transaction = RepairTransaction.begin(active, tmp_path / "transaction")
    (transaction.staged_root / "spec.md").write_text("new spec", encoding="utf-8")
    (transaction.staged_root / "tasks.md").write_text("new tasks", encoding="utf-8")

    result = transaction.promote(lambda _: [])

    assert result.status == "promoted"
    assert (active / "spec.md").read_text(encoding="utf-8") == "new spec"
    assert (active / "tasks.md").read_text(encoding="utf-8") == "new tasks"
    assert (transaction.checkpoint_root / "spec.md").read_text(encoding="utf-8") == "old spec"
    assert not transaction.staged_root.exists()


def test_explicit_rollback_restores_checkpoint_after_promotion(tmp_path: Path) -> None:
    active = active_tree(tmp_path)
    transaction = RepairTransaction.begin(active, tmp_path / "transaction")
    (transaction.staged_root / "spec.md").write_text("new spec", encoding="utf-8")
    transaction.promote(lambda _: [])

    result = transaction.rollback()

    assert result.status == "rolled-back"
    assert (active / "spec.md").read_text(encoding="utf-8") == "old spec"


def test_transaction_refuses_cross_device_or_non_sibling_staging(tmp_path: Path) -> None:
    active = active_tree(tmp_path)
    transaction = RepairTransaction.begin(active, tmp_path / "transaction")
    transaction.staged_root.rename(tmp_path / "moved-stage")
    with pytest.raises(StateError, match="staged artifact tree is missing"):
        transaction.promote(lambda _: [])

