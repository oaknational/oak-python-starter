from __future__ import annotations

import tools.release_increment as subject

BUMP_MAP = {"^feat": "MINOR", "^fix": "MINOR", "^.+": "PATCH"}


def test_feat_and_fix_map_to_minor() -> None:
    assert subject.increment_for_title("feat: add a thing", BUMP_MAP) == "MINOR"
    assert subject.increment_for_title("fix(api): correct a thing", BUMP_MAP) == "MINOR"


def test_other_types_map_to_patch() -> None:
    for title in ("docs: tweak", "chore: bump dep", "refactor: tidy", "ci: adjust", "perf: speed"):
        assert subject.increment_for_title(title, BUMP_MAP) == "PATCH"


def test_compute_increment_takes_the_highest_level() -> None:
    assert subject.compute_increment(["docs: a", "feat: b", "chore: c"], BUMP_MAP) == "MINOR"
    assert subject.compute_increment(["docs: a", "chore: b"], BUMP_MAP) == "PATCH"


def test_compute_increment_is_none_without_commits() -> None:
    assert subject.compute_increment([], BUMP_MAP) is None


def test_is_breaking_detects_bang_subjects_and_footers() -> None:
    assert subject.is_breaking(["feat!: drop support"])
    assert subject.is_breaking(["fix(api)!: change signature"])
    assert subject.is_breaking(["feat: x\n\nBREAKING CHANGE: removed the old path"])
    assert subject.is_breaking(["refactor: y\n\nBREAKING-CHANGE: renamed"])


def test_is_breaking_ignores_non_breaking_commits() -> None:
    assert not subject.is_breaking(["feat: a normal feature", "fix: a normal fix"])


def test_resolve_stands_down_for_breaking() -> None:
    assert subject.resolve(["feat!: drop a thing", "docs: note it"], BUMP_MAP) == "BREAKING"


def test_resolve_returns_minor_for_feat_or_fix() -> None:
    assert subject.resolve(["fix: a bug", "docs: a note"], BUMP_MAP) == "MINOR"


def test_resolve_returns_patch_for_other_types_only() -> None:
    assert subject.resolve(["docs: a note", "chore: a task"], BUMP_MAP) == "PATCH"


def test_resolve_returns_none_without_commits() -> None:
    assert subject.resolve([], BUMP_MAP) == "NONE"


def test_load_bump_map_reads_the_committed_policy() -> None:
    bump_map = subject.load_bump_map()

    assert bump_map.get("^feat") == "MINOR"
    assert bump_map.get("^fix") == "MINOR"
    assert bump_map.get("^.+") == "PATCH"
    assert "MAJOR" not in bump_map.values()
