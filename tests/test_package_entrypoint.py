from __future__ import annotations

import sys
from pathlib import Path

import pytest

import oaknational.python_repo_template.__main__ as subject


def test_main_reports_fixture_summary(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "python -m oaknational.python_repo_template",
            "report",
            "--input",
            str(Path("data/fixtures/activity_log.csv")),
        ],
    )

    assert subject.main() == 0

    captured = capsys.readouterr()
    assert "Total entries: 4" in captured.out
    assert "Busiest category: focus" in captured.out
