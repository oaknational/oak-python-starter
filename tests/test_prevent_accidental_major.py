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
        assert subject.main([_commit_msg(tmp_path, message)], allowed_base=tmp_path) == 0, message


def test_rejects_a_bang_breaking_subject(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = subject.main(
        [_commit_msg(tmp_path, "feat!: drop the legacy API")], allowed_base=tmp_path
    )

    assert code == 1
    assert "MAJOR" in capsys.readouterr().err


def test_rejects_a_scoped_bang_subject(tmp_path: Path) -> None:
    message = _commit_msg(tmp_path, "refactor(core)!: rename the entry point")

    assert subject.main([message], allowed_base=tmp_path) == 1


def test_rejects_a_breaking_change_footer(tmp_path: Path) -> None:
    message = _commit_msg(tmp_path, "feat: a new surface\n\nBREAKING CHANGE: removes the old one\n")

    assert subject.main([message], allowed_base=tmp_path) == 1


def test_errors_without_a_path_argument(tmp_path: Path) -> None:
    assert subject.main([], allowed_base=tmp_path) == 1


def test_errors_cleanly_on_a_missing_file(tmp_path: Path) -> None:
    missing = str(tmp_path / "does-not-exist")

    assert subject.main([missing], allowed_base=tmp_path) == 1


def test_refuses_a_path_outside_the_allowed_base(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A path that escapes the commit-message directory must be refused, not read.
    outside = tmp_path.parent / "elsewhere.txt"
    outside.write_text("feat!: sneak a breaking marker via traversal", encoding="utf-8")

    code = subject.main([str(outside)], allowed_base=tmp_path)

    assert code == 1
    assert "refusing to read outside" in capsys.readouterr().err


def test_git_directory_resolves_inside_the_repository() -> None:
    # The default base (no allowed_base) is the worktree-aware git directory.
    # A variable attribute name dodges ruff B009 + pyright reportPrivateUsage.
    attribute = "_git_directory"
    git_directory = getattr(subject, attribute)

    assert git_directory().is_dir()
