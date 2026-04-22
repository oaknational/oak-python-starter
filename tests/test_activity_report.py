from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest

from python_repo_template.data.activity_store import ActivitySummary, validate_activity_frame
from python_repo_template.demo import activity_report as subject


def make_frame() -> pd.DataFrame:
    return validate_activity_frame(
        pd.DataFrame(
            {
                "date": ["2026-01-01", "2026-01-01", "2026-01-02", "2026-01-02"],
                "category": ["focus", "learning", "focus", "exercise"],
                "minutes": [60, 30, 45, 20],
                "notes": ["Deep work", "Read docs", "Implementation", "Walk"],
            }
        )
    )


def test_render_summary_reports_expected_totals() -> None:
    summary = subject.summarise_activity(make_frame())

    assert subject.render_summary(summary) == "\n".join(
        [
            "Total entries: 4",
            "Total minutes: 155",
            "Average minutes per day: 77.50",
            "Busiest category: focus",
            "Category totals:",
            "- focus: 105",
            "- learning: 30",
            "- exercise: 20",
        ]
    )


def test_main_prepare_uses_injected_writer() -> None:
    captured: dict[str, object] = {}
    output = io.StringIO()

    def fake_loader(path: Path) -> pd.DataFrame:
        assert path == Path("activity.csv")
        return make_frame()

    def fake_writer(frame: pd.DataFrame, path: Path) -> None:
        captured["frame"] = frame.copy()
        captured["path"] = path

    exit_code = subject.main(
        ["prepare", "--input", "activity.csv", "--output", "prepared/activity.parquet"],
        stdout=output,
        csv_loader=fake_loader,
        parquet_writer=fake_writer,
    )

    assert exit_code == 0
    assert captured["path"] == Path("prepared/activity.parquet")
    written = captured["frame"]
    assert isinstance(written, pd.DataFrame)
    assert "Prepared 4 rows at prepared/activity.parquet." in output.getvalue()


def test_main_report_renders_summary_and_chart_from_csv() -> None:
    chart_calls: list[tuple[str, tuple[tuple[str, int], ...], Path]] = []
    output = io.StringIO()

    def fake_chart_writer(summary: ActivitySummary, path: Path) -> None:
        chart_calls.append((summary.busiest_category, summary.category_totals, path))

    exit_code = subject.main(
        ["report", "--input", "activity.csv", "--chart", "summary.png"],
        stdout=output,
        csv_loader=lambda path: make_frame(),
        chart_writer=fake_chart_writer,
    )

    assert exit_code == 0
    assert "Total minutes: 155" in output.getvalue()
    assert chart_calls == [
        (
            "focus",
            (("focus", 105), ("learning", 30), ("exercise", 20)),
            Path("summary.png"),
        )
    ]


def test_default_chart_writer_creates_a_png_file(tmp_path: Path) -> None:
    output_path = tmp_path / "activity-summary.png"

    subject.default_chart_writer(subject.summarise_activity(make_frame()), output_path)

    assert output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_main_report_reads_parquet_when_requested() -> None:
    output = io.StringIO()

    exit_code = subject.main(
        ["report", "--input", "activity.parquet"],
        stdout=output,
        parquet_loader=lambda path: make_frame(),
    )

    assert exit_code == 0
    assert "Busiest category: focus" in output.getvalue()


def test_build_parser_exposes_help_for_the_cli(capsys: pytest.CaptureFixture[str]) -> None:
    parser = subject.build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "activity-report" in captured.out
    assert "prepare" in captured.out
    assert "report" in captured.out
