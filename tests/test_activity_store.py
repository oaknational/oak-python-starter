from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pytest
import requests

from oaknational.python_repo_template.data import activity_store as subject


def make_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2026-01-02", "2026-01-01", "2026-01-02"],
            "category": ["focus", "learning", "exercise"],
            "minutes": [45, 30, 20],
            "notes": ["Implementation", "Read docs", "Walk"],
        }
    )


def make_categories() -> tuple[str, ...]:
    validated = subject.validate_activity_frame(make_frame())
    return tuple(str(category) for category in validated["category"].unique())


def make_parquet_bytes(frame: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    frame.to_parquet(buffer, index=False)
    return buffer.getvalue()


def make_http_error(url: str, status_code: int) -> requests.HTTPError:
    response = requests.Response()
    response.status_code = status_code
    response.url = url
    return requests.HTTPError(response=response)


def test_validate_activity_frame_rejects_contract_shape_mismatches() -> None:
    with pytest.raises(subject.ActivityDataError, match="missing columns: notes"):
        subject.validate_activity_frame(
            pd.DataFrame(
                {
                    "date": ["2026-01-01"],
                    "category": ["focus"],
                    "minutes": [30],
                }
            )
        )

    with pytest.raises(subject.ActivityDataError, match="unexpected columns: extra"):
        subject.validate_activity_frame(
            pd.DataFrame(
                {
                    "date": ["2026-01-01"],
                    "category": ["focus"],
                    "minutes": [30],
                    "notes": [""],
                    "extra": ["x"],
                }
            )
        )


def test_validate_activity_frame_rejects_invalid_values() -> None:
    with pytest.raises(subject.ActivityDataError, match="ISO format"):
        subject.validate_activity_frame(
            pd.DataFrame(
                {
                    "date": ["01/01/2026"],
                    "category": ["focus"],
                    "minutes": [30],
                    "notes": [""],
                }
            )
        )

    with pytest.raises(subject.ActivityDataError, match="non-empty"):
        subject.validate_activity_frame(
            pd.DataFrame(
                {
                    "date": ["2026-01-01"],
                    "category": [" "],
                    "minutes": [30],
                    "notes": [""],
                }
            )
        )

    with pytest.raises(subject.ActivityDataError, match="whole numbers"):
        subject.validate_activity_frame(
            pd.DataFrame(
                {
                    "date": ["2026-01-01"],
                    "category": ["focus"],
                    "minutes": [30.5],
                    "notes": [""],
                }
            )
        )

    with pytest.raises(subject.ActivityDataError, match="positive integers"):
        subject.validate_activity_frame(
            pd.DataFrame(
                {
                    "date": ["2026-01-01"],
                    "category": ["focus"],
                    "minutes": [0],
                    "notes": [""],
                }
            )
        )


def test_prepare_activity_log_writes_sorted_validated_frame() -> None:
    captured: dict[str, object] = {}

    def fake_loader(path: Path) -> pd.DataFrame:
        assert path == Path("input.csv")
        return make_frame()

    def fake_writer(frame: pd.DataFrame, path: Path) -> None:
        captured["path"] = path
        captured["frame"] = frame.copy()

    result = subject.prepare_activity_log(
        Path("input.csv"),
        Path("prepared/output.parquet"),
        csv_loader=fake_loader,
        parquet_writer=fake_writer,
    )

    assert captured["path"] == Path("prepared/output.parquet")
    written = captured["frame"]
    assert isinstance(written, pd.DataFrame)
    assert tuple(written["category"]) == ("learning", "exercise", "focus")
    assert tuple(written["minutes"]) == (30, 20, 45)
    assert result.equals(written)


def test_prepare_activity_log_accepts_https_csv_and_rejects_non_csv_inputs() -> None:
    captured: dict[str, object] = {}

    def fake_writer(frame: pd.DataFrame, path: Path) -> None:
        captured["frame"] = frame.copy()
        captured["path"] = path

    csv_bytes = make_frame().to_csv(index=False).encode("utf-8")
    result = subject.prepare_activity_log(
        "https://example.test/activity.csv",
        Path("prepared/output.parquet"),
        parquet_writer=fake_writer,
        remote_reader=lambda url: csv_bytes,
    )

    written = captured["frame"]
    assert isinstance(written, pd.DataFrame)
    assert captured["path"] == Path("prepared/output.parquet")
    assert result.equals(written)

    with pytest.raises(subject.ActivityDataError, match="Prepare input must be a CSV source"):
        subject.prepare_activity_log(
            "https://example.test/activity.parquet",
            Path("prepared/output.parquet"),
            remote_reader=lambda url: b"",
        )

    with pytest.raises(subject.ActivityDataError, match="HTTPS"):
        subject.prepare_activity_log(
            "http://example.test/activity.csv",
            Path("prepared/output.parquet"),
        )


def test_load_activity_log_dispatches_by_suffix() -> None:
    csv_frame = make_frame()
    parquet_frame = make_frame()

    assert subject.load_activity_log(
        Path("sample.csv"),
        csv_loader=lambda path: csv_frame,
    ).equals(subject.validate_activity_frame(csv_frame))

    assert subject.load_activity_log(
        Path("sample.parquet"),
        parquet_loader=lambda path: parquet_frame,
    ).equals(subject.validate_activity_frame(parquet_frame))

    with pytest.raises(subject.ActivityDataError, match="Unsupported activity input format"):
        subject.load_activity_log(Path("sample.txt"))


def test_load_activity_log_dispatches_remote_sources_by_suffix() -> None:
    csv_frame = make_frame()
    parquet_frame = subject.validate_activity_frame(make_frame())
    remote_payloads = {
        "https://example.test/activity.csv": csv_frame.to_csv(index=False).encode("utf-8"),
        "https://example.test/activity.parquet": make_parquet_bytes(parquet_frame),
    }

    remote_calls: list[str] = []

    def fake_remote_reader(url: str) -> bytes:
        remote_calls.append(url)
        return remote_payloads[url]

    loaded_csv = subject.load_activity_log(
        "https://example.test/activity.csv",
        remote_reader=fake_remote_reader,
    )
    loaded_parquet = subject.load_activity_log(
        "https://example.test/activity.parquet",
        remote_reader=fake_remote_reader,
    )

    assert remote_calls == [
        "https://example.test/activity.csv",
        "https://example.test/activity.parquet",
    ]
    assert loaded_csv.equals(subject.validate_activity_frame(csv_frame))
    assert loaded_parquet.equals(subject.validate_activity_frame(parquet_frame))


def test_derive_metadata_source_supports_local_and_https_inputs() -> None:
    assert subject.derive_metadata_source(Path("data/fixtures/activity_log.csv")) == Path(
        "data/fixtures/activity_log.metadata.yaml"
    )
    assert subject.derive_metadata_source("https://example.test/activity.csv") == (
        "https://example.test/activity.metadata.yaml"
    )
    assert subject.derive_metadata_source("https://example.test/reports/activity.parquet") == (
        "https://example.test/reports/activity.metadata.yaml"
    )


def test_load_activity_metadata_parses_labels_and_targets() -> None:
    metadata = subject.load_activity_metadata(
        Path("activity.metadata.yaml"),
        categories=make_categories(),
        local_text_loader=lambda path: "\n".join(
            [
                "name: weekly-activity",
                "description: Example profile",
                "source: seeded fixture",
                "rows: 3",
                "fields:",
                "  - name: date",
                "    type: iso-date",
                "category_labels:",
                "  focus: Deep focus",
                "category_targets:",
                "  focus: 90",
            ]
        ),
    )

    assert metadata is not None
    assert metadata.name == "weekly-activity"
    assert metadata.description == "Example profile"
    assert metadata.source == "seeded fixture"
    assert metadata.rows == 3
    assert metadata.fields[0].name == "date"
    assert metadata.fields[0].type == "iso-date"
    assert metadata.category_labels == {"focus": "Deep focus"}
    assert metadata.category_targets == {"focus": 90}


def test_load_activity_metadata_missing_behaviour_depends_on_allow_missing() -> None:
    url = "https://example.test/activity.metadata.yaml"

    assert (
        subject.load_activity_metadata(
            url,
            categories=make_categories(),
            allow_missing=True,
            remote_reader=lambda remote_url: (_ for _ in ()).throw(
                make_http_error(remote_url, 404)
            ),
        )
        is None
    )

    with pytest.raises(subject.ActivityDataError, match="Could not load activity metadata"):
        subject.load_activity_metadata(
            url,
            categories=make_categories(),
            remote_reader=lambda remote_url: (_ for _ in ()).throw(
                make_http_error(remote_url, 404)
            ),
        )


def test_load_activity_metadata_rejects_unknown_keys_and_categories() -> None:
    with pytest.raises(subject.ActivityDataError, match="Unknown metadata keys"):
        subject.load_activity_metadata(
            Path("activity.metadata.yaml"),
            categories=make_categories(),
            local_text_loader=lambda path: "unexpected: value",
        )

    with pytest.raises(subject.ActivityDataError, match="unknown activity categories"):
        subject.load_activity_metadata(
            Path("activity.metadata.yaml"),
            categories=make_categories(),
            local_text_loader=lambda path: "\n".join(
                [
                    "category_targets:",
                    "  reading: 30",
                ]
            ),
        )
