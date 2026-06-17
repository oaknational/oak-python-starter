from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest
import requests

from oaknational.python_repo_template.data.activity_store import (
    ActivityMetadata,
    ActivitySummary,
    validate_activity_frame,
)
from oaknational.python_repo_template.demo import activity_report as subject


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


def make_metadata(
    *,
    name: str = "weekly-activity",
    description: str | None = "Bounded activity pack",
    source: str | None = "seeded fixture",
    category_labels: dict[str, str] | None = None,
    category_targets: dict[str, int] | None = None,
) -> ActivityMetadata:
    return ActivityMetadata(
        name=name,
        description=description,
        source=source,
        rows=4,
        fields=(),
        category_labels=category_labels or {"focus": "Deep focus"},
        category_targets=category_targets or {"focus": 90},
    )


def make_http_error(url: str, status_code: int) -> requests.HTTPError:
    response = requests.Response()
    response.status_code = status_code
    response.url = url
    return requests.HTTPError(response=response)


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


def test_render_summary_includes_metadata_header_and_target_deltas() -> None:
    summary = subject.summarise_activity(make_frame())
    metadata = make_metadata(
        category_labels={"focus": "Deep focus", "learning": "Reading", "exercise": "Exercise"},
        category_targets={"focus": 90, "learning": 20},
    )

    rendered = subject.render_summary(summary, metadata)

    assert "Profile: weekly-activity" in rendered
    assert "Description: Bounded activity pack" in rendered
    assert "Source: seeded fixture" in rendered
    assert "- Deep focus: 105" in rendered
    assert "- Reading: 30" in rendered
    assert "Target deltas:" in rendered
    assert "- Deep focus: +15" in rendered
    assert "- Reading: +10" in rendered


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
    chart_calls: list[tuple[str, tuple[tuple[str, int], ...], str | None, Path]] = []
    output = io.StringIO()

    def fake_chart_writer(
        summary: ActivitySummary,
        metadata: ActivityMetadata | None,
        path: Path,
    ) -> None:
        chart_calls.append(
            (
                summary.busiest_category,
                summary.category_totals,
                metadata.name if metadata is not None else None,
                path,
            )
        )

    exit_code = subject.main(
        ["report", "--input", "activity.csv", "--chart", "summary.png"],
        stdout=output,
        csv_loader=lambda path: make_frame(),
        metadata_loader=lambda source, categories, allow_missing: None,
        chart_writer=fake_chart_writer,
    )

    assert exit_code == 0
    assert "Total minutes: 155" in output.getvalue()
    assert chart_calls == [
        (
            "focus",
            (("focus", 105), ("learning", 30), ("exercise", 20)),
            None,
            Path("summary.png"),
        )
    ]


def test_default_chart_writer_creates_a_png_file(tmp_path: Path) -> None:
    output_path = tmp_path / "activity-summary.png"

    subject.default_chart_writer(
        subject.summarise_activity(make_frame()),
        make_metadata(),
        output_path,
    )

    assert output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_main_report_reads_parquet_when_requested() -> None:
    output = io.StringIO()

    exit_code = subject.main(
        ["report", "--input", "activity.parquet"],
        stdout=output,
        parquet_loader=lambda path: make_frame(),
        metadata_loader=lambda source, categories, allow_missing: None,
    )

    assert exit_code == 0
    assert "Busiest category: focus" in output.getvalue()


def test_main_report_auto_loads_same_stem_metadata_and_renders_targets(tmp_path: Path) -> None:
    input_path = tmp_path / "activity.csv"
    input_path.write_text(
        "\n".join(
            [
                "date,category,minutes,notes",
                "2026-01-01,focus,60,Deep work",
                "2026-01-01,learning,30,Read docs",
            ]
        ),
        encoding="utf-8",
    )
    metadata_path = tmp_path / "activity.metadata.yaml"
    metadata_path.write_text(
        "\n".join(
            [
                "name: fixture-pack",
                "description: auto-discovered metadata",
                "source: tmp fixture",
                "category_labels:",
                "  focus: Deep focus",
                "category_targets:",
                "  focus: 45",
            ]
        ),
        encoding="utf-8",
    )

    chart_calls: list[tuple[str | None, dict[str, int]]] = []
    output = io.StringIO()

    def fake_chart_writer(
        summary: ActivitySummary,
        metadata: ActivityMetadata | None,
        path: Path,
    ) -> None:
        assert summary.total_entries == 2
        assert path == Path("summary.png")
        assert metadata is not None
        chart_calls.append((metadata.name, metadata.category_targets))

    exit_code = subject.main(
        ["report", "--input", str(input_path), "--chart", "summary.png"],
        stdout=output,
        chart_writer=fake_chart_writer,
    )

    assert exit_code == 0
    rendered = output.getvalue()
    assert "Profile: fixture-pack" in rendered
    assert "Description: auto-discovered metadata" in rendered
    assert "Source: tmp fixture" in rendered
    assert "Target deltas:" in rendered
    assert "- Deep focus: +15" in rendered
    assert chart_calls == [("fixture-pack", {"focus": 45})]


def test_main_report_metadata_override_wins_over_auto_discovery(tmp_path: Path) -> None:
    input_path = tmp_path / "activity.csv"
    input_path.write_text(
        "\n".join(
            [
                "date,category,minutes,notes",
                "2026-01-01,focus,60,Deep work",
                "2026-01-01,learning,30,Read docs",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "activity.metadata.yaml").write_text("name: auto-profile", encoding="utf-8")
    override_path = tmp_path / "custom.metadata.yaml"
    override_path.write_text(
        "\n".join(
            [
                "name: override-profile",
                "category_labels:",
                "  focus: Override label",
            ]
        ),
        encoding="utf-8",
    )

    output = io.StringIO()

    exit_code = subject.main(
        [
            "report",
            "--input",
            str(input_path),
            "--metadata",
            str(override_path),
        ],
        stdout=output,
    )

    assert exit_code == 0
    rendered = output.getvalue()
    assert "Profile: override-profile" in rendered
    assert "Profile: auto-profile" not in rendered
    assert "- Override label: 60" in rendered


def test_main_report_accepts_https_input_and_ignores_missing_auto_metadata() -> None:
    remote_payloads = {
        "https://example.test/activity.csv": (
            b"date,category,minutes,notes\n"
            b"2026-01-01,focus,60,Deep work\n"
            b"2026-01-02,learning,30,Read docs\n"
        ),
    }

    remote_calls: list[str] = []
    output = io.StringIO()

    def fake_remote_reader(url: str) -> bytes:
        remote_calls.append(url)
        if url.endswith(".metadata.yaml"):
            raise make_http_error(url, 404)
        return remote_payloads[url]

    exit_code = subject.main(
        ["report", "--input", "https://example.test/activity.csv"],
        stdout=output,
        remote_reader=fake_remote_reader,
    )

    assert exit_code == 0
    assert "Total entries: 2" in output.getvalue()
    assert remote_calls == [
        "https://example.test/activity.csv",
        "https://example.test/activity.metadata.yaml",
    ]


def test_main_report_fails_for_missing_explicit_remote_metadata() -> None:
    output = io.StringIO()

    def fake_remote_reader(url: str) -> bytes:
        if url.endswith(".metadata.yaml"):
            raise make_http_error(url, 404)
        return b"date,category,minutes,notes\n2026-01-01,focus,60,Deep work\n"

    with pytest.raises(SystemExit) as exc_info:
        subject.main(
            [
                "report",
                "--input",
                "https://example.test/activity.csv",
                "--metadata",
                "https://example.test/custom.metadata.yaml",
            ],
            stdout=output,
            remote_reader=fake_remote_reader,
        )

    assert exc_info.value.code == 2


def test_build_parser_exposes_help_for_the_cli(capsys: pytest.CaptureFixture[str]) -> None:
    parser = subject.build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["report", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "activity-report" in captured.out
    assert "--input" in captured.out
    assert "--metadata" in captured.out
