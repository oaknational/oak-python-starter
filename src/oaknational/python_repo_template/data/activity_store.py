"""Validation and storage helpers for the seeded activity demo."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ("date", "category", "minutes", "notes")

CsvLoader = Callable[[Path], pd.DataFrame]
ParquetLoader = Callable[[Path], pd.DataFrame]
ParquetWriter = Callable[[pd.DataFrame, Path], None]


class ActivityDataError(ValueError):
    """Raised when the activity log contract is violated."""


@dataclass(frozen=True)
class ActivitySummary:
    """Normalised summary for one activity log."""

    total_entries: int
    total_minutes: int
    average_minutes_per_day: float
    busiest_category: str
    category_totals: tuple[tuple[str, int], ...]


def default_csv_loader(path: Path) -> pd.DataFrame:
    """Load a CSV activity log."""

    return pd.read_csv(path)


def default_parquet_loader(path: Path) -> pd.DataFrame:
    """Load a Parquet activity log."""

    return pd.read_parquet(path)


def default_parquet_writer(frame: pd.DataFrame, path: Path) -> None:
    """Persist a validated activity log as Parquet."""

    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def validate_activity_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a canonical activity frame or raise an explicit validation error."""

    _require_columns(frame)
    if frame.empty:
        msg = "Activity data must contain at least one row."
        raise ActivityDataError(msg)

    canonical = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    canonical["date"] = _parse_dates(canonical["date"])
    canonical["category"] = _normalise_category(canonical["category"])
    canonical["minutes"] = _normalise_minutes(canonical["minutes"])
    canonical["notes"] = _normalise_notes(canonical["notes"])
    canonical = canonical.sort_values(
        by=["date", "category", "minutes", "notes"],
        kind="stable",
    ).reset_index(drop=True)
    return canonical


def prepare_activity_log(
    input_path: Path,
    output_path: Path,
    *,
    csv_loader: CsvLoader = default_csv_loader,
    parquet_writer: ParquetWriter = default_parquet_writer,
) -> pd.DataFrame:
    """Validate a CSV activity log and persist a canonical Parquet copy."""

    frame = validate_activity_frame(csv_loader(input_path))
    parquet_writer(frame, output_path)
    return frame


def load_activity_log(
    input_path: Path,
    *,
    csv_loader: CsvLoader = default_csv_loader,
    parquet_loader: ParquetLoader = default_parquet_loader,
) -> pd.DataFrame:
    """Load and validate an activity log from CSV or Parquet."""

    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return validate_activity_frame(csv_loader(input_path))
    if suffix == ".parquet":
        return validate_activity_frame(parquet_loader(input_path))
    msg = f"Unsupported activity input format: {input_path.suffix or '<none>'}."
    raise ActivityDataError(msg)


def summarise_activity(frame: pd.DataFrame) -> ActivitySummary:
    """Build a stable activity summary from a validated frame."""

    canonical = validate_activity_frame(frame)
    category_totals = _sorted_category_totals(canonical)
    total_entries = len(canonical.index)
    total_minutes = int(canonical["minutes"].sum())
    unique_days = canonical["date"].dt.normalize().nunique()
    average_minutes_per_day = round(total_minutes / unique_days, 2)
    busiest_category = category_totals[0][0]
    return ActivitySummary(
        total_entries=total_entries,
        total_minutes=total_minutes,
        average_minutes_per_day=average_minutes_per_day,
        busiest_category=busiest_category,
        category_totals=category_totals,
    )


def _require_columns(frame: pd.DataFrame) -> None:
    columns = tuple(str(column) for column in frame.columns)
    if columns == REQUIRED_COLUMNS:
        return
    missing = [column for column in REQUIRED_COLUMNS if column not in columns]
    extras = [column for column in columns if column not in REQUIRED_COLUMNS]
    parts: list[str] = []
    if missing:
        parts.append(f"missing columns: {', '.join(missing)}")
    if extras:
        parts.append(f"unexpected columns: {', '.join(extras)}")
    detail = "; ".join(parts) if parts else "unexpected column order"
    msg = f"Activity data must use the exact columns {', '.join(REQUIRED_COLUMNS)}; {detail}."
    raise ActivityDataError(msg)


def _parse_dates(series: pd.Series) -> pd.Series:
    raw = series.astype("string")
    parsed = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
    if parsed.isna().any():
        msg = "Activity dates must use ISO format YYYY-MM-DD."
        raise ActivityDataError(msg)
    return parsed


def _normalise_category(series: pd.Series) -> pd.Series:
    category = series.astype("string").fillna("").str.strip()
    if (category == "").any():
        msg = "Activity category values must be non-empty."
        raise ActivityDataError(msg)
    return category


def _normalise_minutes(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.isna().any():
        msg = "Activity minutes must be numeric."
        raise ActivityDataError(msg)
    if not (numeric % 1 == 0).all():
        msg = "Activity minutes must be whole numbers."
        raise ActivityDataError(msg)
    integer = numeric.astype("int64")
    if (integer <= 0).any():
        msg = "Activity minutes must be positive integers."
        raise ActivityDataError(msg)
    return integer


def _normalise_notes(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("").str.strip()


def _sorted_category_totals(frame: pd.DataFrame) -> tuple[tuple[str, int], ...]:
    grouped = frame.groupby("category", sort=False)["minutes"].sum()
    rows = ((str(category), int(total)) for category, total in grouped.items())
    return tuple(sorted(rows, key=lambda item: (-item[1], item[0])))
