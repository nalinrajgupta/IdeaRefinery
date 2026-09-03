#!/usr/bin/env python3
"""Synchronize portable Idea Refinery skill distributions.

GitHub Copilot can discover repository skills in ``.agents/skills``. Hermes
can use that directory as an external skill source or receive a copied skill
directory.  The generated directories intentionally contain the canonical
instruction body and its relative support documents so both hosts execute the
same complete workflow.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import tempfile
import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("idea-refinery-full", "idea-refinery-implement")
GENERATED_MARKER = "<!-- Generated from {source}; do not edit this copy. -->\n"


def rendered_skill(source: Path, repository_root: Path = REPOSITORY_ROOT) -> str:
    """Return a canonical skill body with an auditable generation marker."""

    lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    try:
        frontmatter_end = lines.index("---\n", 1)
    except ValueError as error:
        raise ValueError(f"{source} has no closed YAML frontmatter") from error

    source_path = source.relative_to(repository_root).as_posix()
    return "".join(
        lines[: frontmatter_end + 1]
        + [GENERATED_MARKER.format(source=source_path)]
        + lines[frontmatter_end + 1 :]
    )


def validate_relative_links(skill_root: Path) -> None:
    """Reject missing local Markdown targets before publishing a skill."""

    for markdown in skill_root.rglob("*.md"):
        for target in re.findall(r"\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)", markdown.read_text(encoding="utf-8")):
            if "://" not in target and not (markdown.parent / target).resolve().exists():
                raise ValueError(f"missing local reference {target!r} from {markdown}")


def write_distribution(destination_root: Path, repository_root: Path = REPOSITORY_ROOT) -> None:
    """Create a self-contained project-skill distribution below *destination_root*."""

    for skill_name in SKILLS:
        source_dir = repository_root / skill_name
        source_skill = source_dir / "SKILL.md"
        destination_dir = destination_root / skill_name
        destination_dir.mkdir(parents=True, exist_ok=True)
        (destination_dir / "SKILL.md").write_text(
            rendered_skill(source_skill, repository_root), encoding="utf-8"
        )

        source_references = source_dir / "references"
        if source_references.is_dir():
            shutil.copytree(
                source_references,
                destination_dir / "references",
                dirs_exist_ok=True,
            )
        validate_relative_links(destination_dir)


def distributions_match(expected: Path, actual: Path) -> bool:
    """Compare generated files byte-for-byte without treating cache files as input."""

    comparison = filecmp.dircmp(expected, actual)
    if comparison.left_only or comparison.right_only or comparison.diff_files:
        return False
    return all(
        distributions_match(expected / name, actual / name)
        for name in comparison.common_dirs
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed distribution without modifying it",
    )
    args = parser.parse_args(argv)

    distribution_root = REPOSITORY_ROOT / ".agents" / "skills"
    with tempfile.TemporaryDirectory(prefix="idea-refinery-skills-") as temporary:
        expected_root = Path(temporary)
        try:
            write_distribution(expected_root)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1

        if args.check:
            for skill_name in SKILLS:
                if not distributions_match(
                    expected_root / skill_name, distribution_root / skill_name
                ):
                    print(f"stale or missing generated skill: {skill_name}", file=sys.stderr)
                    return 1
            return 0

        for skill_name in SKILLS:
            destination = distribution_root / skill_name
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(expected_root / skill_name, destination)
            print(f"synchronized {destination.relative_to(REPOSITORY_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
