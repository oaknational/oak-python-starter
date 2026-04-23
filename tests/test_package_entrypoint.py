from __future__ import annotations

import io
from pathlib import Path

import oaknational.python_repo_template.__main__ as subject


def test_main_reports_fixture_summary() -> None:
    stdout = io.StringIO()

    assert (
        subject.main(
            [
                "report",
                "--input",
                str(Path("data/fixtures/activity_log.csv")),
            ],
            stdout=stdout,
        )
        == 0
    )

    output = stdout.getvalue()
    assert "Profile: activity-log" in output
    assert "Total entries: 4" in output
    assert "Busiest category: Deep focus" in output
