#!/usr/bin/env python3
"""Block accidental major-version markers in commit messages (a commit-msg hook).

Major releases are deliberate in this repo: the release workflow stands down on a
breaking-change marker, and a major is cut manually via "Run workflow"
(increment = MAJOR). A ``type!:`` subject or a ``BREAKING CHANGE`` footer would
therefore *not* cut a major automatically — it would silently stop the
auto-release until a human intervenes. This hook rejects the marker so it cannot
land by accident: describe the breaking change in prose and cut the major
deliberately from the workflow.

Run as a module (``python -m tools.prevent_accidental_major <commit-msg-file>``)
so it can reuse ``release_increment.is_breaking`` — keeping one definition of
"what counts as breaking", shared with the release workflow.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tools.release_increment import is_breaking

_REJECTION = (
    "Breaking-change markers (`type!:` or a `BREAKING CHANGE` footer) are not "
    "allowed in commits here.\n"
    "Major releases are cut manually: use the Release workflow (Run workflow -> "
    "increment = MAJOR).\n"
    "Describe the breaking change in prose without the marker, then cut the major "
    "deliberately.\n"
)


def main(argv: list[str] | None = None) -> int:
    """Reject a commit message that carries a breaking-change marker."""

    args = sys.argv[1:] if argv is None else argv
    if not args:
        sys.stderr.write("prevent_accidental_major: expected a commit-message file path\n")
        return 1
    try:
        message = Path(args[0]).read_text(encoding="utf-8")
    except OSError as error:
        sys.stderr.write(f"prevent_accidental_major: cannot read {args[0]!r}: {error}\n")
        return 1
    if is_breaking([message]):
        sys.stderr.write(_REJECTION)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
