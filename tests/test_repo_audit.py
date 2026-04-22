from __future__ import annotations

from pathlib import Path

import tools.repo_audit as subject


def test_iter_text_files_skips_binary_dotfiles(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Template\n", encoding="utf-8")
    (tmp_path / ".python-version").write_text("3.14\n", encoding="utf-8")
    (tmp_path / ".coverage").write_bytes(b"\x8dSQLITE")

    paths = subject.iter_text_files(tmp_path)

    assert tmp_path / "README.md" in paths
    assert tmp_path / ".python-version" in paths
    assert tmp_path / ".coverage" not in paths
