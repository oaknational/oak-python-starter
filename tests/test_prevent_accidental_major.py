from __future__ import annotations

from pathlib import Path

import pytest

import tools.prevent_accidental_major as subject


def _commit_msg(tmp_path: Path, text: str) -> str:
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_allows_conventional_non_breaking_commits(tmp_path: Path) -> None:
    allowed = [
        "feat: add a thing",
        "fix(parser): handle empty input",
        "chore: tidy the tree",
        # A prose mention of a breaking change (not a marker) must pass.
        "docs: explain the breaking change semantics for adopters",
    ]
    for message in allowed:
        assert subject.main([_commit_msg(tmp_path, message)]) == 0, message


def test_rejects_a_bang_breaking_subject(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = subject.main([_commit_msg(tmp_path, "feat!: drop the legacy API")])

    assert code == 1
    assert "MAJOR" in capsys.readouterr().err


def test_rejects_a_scoped_bang_subject(tmp_path: Path) -> None:
    assert subject.main([_commit_msg(tmp_path, "refactor(core)!: rename the entry point")]) == 1


def test_rejects_a_breaking_change_footer(tmp_path: Path) -> None:
    message = "feat: a new surface\n\nBREAKING CHANGE: removes the old one\n"

    assert subject.main([_commit_msg(tmp_path, message)]) == 1


def test_errors_without_a_path_argument(tmp_path: Path) -> None:
    assert subject.main([]) == 1
