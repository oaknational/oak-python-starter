from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

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
