"""Regression tests for optional documentation automation prerequisites."""

import os
from pathlib import Path
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "docs-update.yml"


@pytest.mark.parametrize(
    ("token", "app_id", "private_key", "bot", "expected"),
    [
        ("", "", "", False, "false"),
        ("", "123", "test-key", False, "false"),
        ("test-token", "", "test-key", False, "false"),
        ("test-token", "123", "", False, "false"),
        ("test-token", "123", "test-key", False, "true"),
        ("test-token", "123", "test-key", True, "false"),
    ],
)
def test_docs_guard_checks_credentials(
    tmp_path, token, app_id, private_key, bot, expected
):
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["update-docs"]["steps"]
    guard = next(step for step in steps if step.get("id") == "guard")
    assert guard["env"] == {
        "COPILOT_GITHUB_TOKEN": "${{ secrets.COPILOT_DOCS_TOKEN }}",
        "DOCS_BOT_APP_ID": "${{ vars.DOCS_BOT_APP_ID }}",
        "DOCS_BOT_PRIVATE_KEY": "${{ secrets.DOCS_BOT_PRIVATE_KEY }}",
    }
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    name = "github-actions[bot]" if bot else "Test"
    email = (
        "41898282+github-actions[bot]@users.noreply.github.com"
        if bot else "test@example.com"
    )
    message = "docs: update documentation for pull request" if bot else "Test change"
    subprocess.run(
        [
            "git", "-c", f"user.name={name}", "-c", f"user.email={email}",
            "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", message,
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    output = tmp_path / "output"
    result = subprocess.run(
        ["bash", "-e", "-c", guard["run"]],
        cwd=tmp_path,
        env={
            **os.environ,
            "GITHUB_OUTPUT": str(output),
            "COPILOT_GITHUB_TOKEN": token,
            "DOCS_BOT_APP_ID": app_id,
            "DOCS_BOT_PRIVATE_KEY": private_key,
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text() == f"run={expected}\n"
    assert ("::warning::Skipping documentation updates" in result.stdout) == (
        expected == "false" and not bot
    )
    assert "test-token" not in result.stdout + result.stderr
    assert "test-key" not in result.stdout + result.stderr


def test_docs_steps_are_gated_on_prerequisites():
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["update-docs"]["steps"]
    guard_index = next(i for i, step in enumerate(steps) if step.get("id") == "guard")
    changes_index = next(i for i, step in enumerate(steps) if step.get("id") == "changes")
    for step in steps[guard_index + 1 : changes_index + 1]:
        assert step["if"] == "steps.guard.outputs.run == 'true'"
    for step in steps[changes_index + 1 :]:
        assert step["if"] == "steps.changes.outputs.changed == 'true'"
