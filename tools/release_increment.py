#!/usr/bin/env python3
"""Compute the release increment from Conventional Commits for the custom policy.

The ``cz_conventional_commits`` plugin hardcodes its bump map (feat -> minor,
fix -> patch, breaking -> major) and ignores ``[tool.commitizen].bump_map`` in
config (it reads ``self.cz.bump_map``, a class attribute). This repo wants a
custom policy — feat/fix -> minor, everything else -> patch, breaking -> a
manual major — so the release workflow computes the increment here from the
single policy source (``[tool.commitizen].bump_map``) and passes it to
``cz bump --increment``.

Reads NUL-separated commit messages on stdin (``git log --pretty=format:'%B%x00'``)
and prints exactly one of: ``BREAKING``, ``MAJOR``, ``MINOR``, ``PATCH``, ``NONE``.
``BREAKING`` signals that a deliberate major is required and the auto-release
must stand down.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# A breaking marker: a `type!:`/`type(scope)!:` subject, or a BREAKING CHANGE footer.
BREAKING_MARKER = re.compile(r"^([a-z]+(\([^)]+\))?!:|BREAKING[ -]CHANGE)", re.IGNORECASE)

_RANK = {"PATCH": 1, "MINOR": 2, "MAJOR": 3}


def load_bump_map(root: Path = REPO_ROOT) -> dict[str, str]:
    """Return the ordered ``[tool.commitizen].bump_map`` policy from pyproject."""
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    bump_map = data["tool"]["commitizen"]["bump_map"]
    return {str(key): str(value) for key, value in bump_map.items()}


def increment_for_title(title: str, bump_map: dict[str, str]) -> str | None:
    """Map a single commit subject to a bump level via the first matching key."""
    for pattern, level in bump_map.items():
        if re.match(pattern, title):
            return level
    return None


def is_breaking(messages: list[str]) -> bool:
    """Whether any full commit message carries a breaking-change marker."""
    return any(BREAKING_MARKER.match(line) for message in messages for line in message.splitlines())


def compute_increment(titles: list[str], bump_map: dict[str, str]) -> str | None:
    """Return the highest bump level across the commit subjects, or None."""
    best: str | None = None
    for title in titles:
        level = increment_for_title(title, bump_map)
        if level is not None and (best is None or _RANK[level] > _RANK[best]):
            best = level
    return best


def resolve(messages: list[str], bump_map: dict[str, str]) -> str:
    """Resolve the release decision for a set of full commit messages."""
    if is_breaking(messages):
        return "BREAKING"
    titles = [message.strip().splitlines()[0] for message in messages if message.strip()]
    return compute_increment(titles, bump_map) or "NONE"


def main() -> int:
    messages = [block for block in sys.stdin.read().split("\x00") if block.strip()]
    print(resolve(messages, load_bump_map()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
