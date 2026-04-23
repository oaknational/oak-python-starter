from __future__ import annotations

from pathlib import Path

import pytest

import oaknational.python_repo_template.devtools as subject


def test_clean_removes_repo_cache_without_touching_virtualenv_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(subject, "REPO_ROOT", tmp_path)

    repo_cache = tmp_path / "src" / "oaknational" / "python_repo_template" / "__pycache__"
    venv_cache = tmp_path / ".venv" / "lib" / "python3.14" / "site-packages" / "__pycache__"
    repo_cache.mkdir(parents=True)
    venv_cache.mkdir(parents=True)

    with pytest.raises(SystemExit) as exc_info:
        subject.clean()

    assert exc_info.value.code == 0
    assert not repo_cache.exists()
    assert venv_cache.exists()
