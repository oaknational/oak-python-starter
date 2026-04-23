"""Validation and storage helpers for the seeded activity demo."""

from __future__ import annotations

import io
import ntpath
from collections.abc import Callable, Collection
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast
from urllib.parse import SplitResult, urlsplit, urlunsplit

import pandas as pd
import requests
import yaml

REQUIRED_COLUMNS = ("date", "category", "minutes", "notes")
METADATA_SUFFIXES = {".yaml", ".yml"}
ALLOWED_METADATA_KEYS = {
    "name",
    "description",
    "source",
    "rows",
    "fields",
    "category_labels",
    "category_targets",
}
REMOTE_TIMEOUT_SECONDS = 10

CsvLoader = Callable[[Path], pd.DataFrame]
ParquetLoader = Callable[[Path], pd.DataFrame]
ParquetWriter = Callable[[pd.DataFrame, Path], None]
RemoteReader = Callable[[str], bytes]
LocalTextLoader = Callable[[Path], str]
HttpGet = Callable[..., requests.Response]


def _empty_category_labels() -> dict[str, str]:
    return {}


def _empty_category_targets() -> dict[str, int]:
    return {}


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


@dataclass(frozen=True)
class ActivityFieldDefinition:
    """Metadata field definition for the activity pack sidecar."""

    name: str
    type: str


@dataclass(frozen=True)
class ActivityMetadata:
    """Validated report-time metadata for one activity pack."""

    name: str | None = None
    description: str | None = None
    source: str | None = None
    rows: int | None = None
    fields: tuple[ActivityFieldDefinition, ...] = ()
    category_labels: dict[str, str] = field(default_factory=_empty_category_labels)
    category_targets: dict[str, int] = field(default_factory=_empty_category_targets)


@dataclass(frozen=True)
class ActivitySource:
    """Resolved local or remote source for activity artefacts."""

    raw: str
    suffix: str
    is_remote: bool


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


def default_remote_reader(
    url: str,
    *,
    http_get: HttpGet = requests.get,
) -> bytes:
    """Fetch one remote artefact over HTTPS."""

    response = http_get(url, timeout=REMOTE_TIMEOUT_SECONDS, allow_redirects=False)
    if 300 <= response.status_code < 400:
        msg = "Remote activity sources must not redirect."
        raise requests.HTTPError(msg, response=response)
    response.raise_for_status()
    return response.content


def default_local_text_loader(path: Path) -> str:
    """Read one local text artefact."""

    return path.read_text(encoding="utf-8")


def resolve_activity_source(source: str | Path) -> ActivitySource:
    """Resolve a local path or HTTPS URL into a validated source."""

    raw = str(source)
    if _is_unc_path(raw):
        msg = "UNC activity sources are not supported; use a local path or HTTPS URL."
        raise ActivityDataError(msg)
    if _is_windows_drive_path(raw):
        return ActivitySource(raw=raw, suffix=Path(raw).suffix.lower(), is_remote=False)
    parsed = urlsplit(raw)
    if parsed.scheme:
        return _resolve_remote_source(raw, parsed)
    return ActivitySource(raw=raw, suffix=Path(raw).suffix.lower(), is_remote=False)


def derive_metadata_source(source: str | Path) -> str | Path:
    """Derive the same-stem metadata sidecar for a local or remote source."""

    resolved = resolve_activity_source(source)
    if resolved.is_remote:
        parsed = urlsplit(resolved.raw)
        metadata_path = _derive_metadata_path(parsed.path)
        return urlunsplit((parsed.scheme, parsed.netloc, metadata_path, "", ""))

    path = Path(resolved.raw)
    return path.with_name(_derive_metadata_path(path.name))


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
    input_source: str | Path,
    output_path: Path,
    *,
    csv_loader: CsvLoader = default_csv_loader,
    parquet_writer: ParquetWriter = default_parquet_writer,
    remote_reader: RemoteReader = default_remote_reader,
) -> pd.DataFrame:
    """Validate a CSV activity log and persist a canonical Parquet copy."""

    source = resolve_activity_source(input_source)
    if source.suffix != ".csv":
        msg = "Prepare input must be a CSV source."
        raise ActivityDataError(msg)

    frame = _load_csv_source(source, csv_loader, remote_reader)
    canonical = validate_activity_frame(frame)
    parquet_writer(canonical, output_path)
    return canonical


def load_activity_log(
    input_source: str | Path,
    *,
    csv_loader: CsvLoader = default_csv_loader,
    parquet_loader: ParquetLoader = default_parquet_loader,
    remote_reader: RemoteReader = default_remote_reader,
) -> pd.DataFrame:
    """Load and validate an activity log from CSV or Parquet."""

    source = resolve_activity_source(input_source)
    if source.suffix == ".csv":
        return validate_activity_frame(_load_csv_source(source, csv_loader, remote_reader))
    if source.suffix == ".parquet":
        return validate_activity_frame(_load_parquet_source(source, parquet_loader, remote_reader))

    msg = f"Unsupported activity input format: {source.suffix or '<none>'}."
    raise ActivityDataError(msg)


def load_activity_metadata(
    metadata_source: str | Path,
    *,
    categories: Collection[str],
    allow_missing: bool = False,
    remote_reader: RemoteReader = default_remote_reader,
    local_text_loader: LocalTextLoader = default_local_text_loader,
) -> ActivityMetadata | None:
    """Load and validate optional activity-pack metadata."""

    source = resolve_activity_source(metadata_source)
    if source.suffix not in METADATA_SUFFIXES:
        msg = "Activity metadata must use a YAML source."
        raise ActivityDataError(msg)

    if source.is_remote:
        try:
            text = _load_remote_text(source.raw, remote_reader)
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            if allow_missing and status_code == 404:
                return None
            msg = f"Could not load activity metadata from {source.raw}."
            raise ActivityDataError(msg) from exc
        except requests.RequestException as exc:
            msg = f"Could not load activity metadata from {source.raw}."
            raise ActivityDataError(msg) from exc
    else:
        path = Path(source.raw)
        try:
            text = local_text_loader(path)
        except OSError as exc:
            if allow_missing and isinstance(exc, FileNotFoundError):
                return None
            msg = f"Could not load activity metadata from {path}."
            raise ActivityDataError(msg) from exc

    return _parse_activity_metadata(text, categories)


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


def _resolve_remote_source(raw: str, parsed: SplitResult) -> ActivitySource:
    if parsed.scheme != "https":
        msg = "Remote activity sources must use HTTPS URLs."
        raise ActivityDataError(msg)
    if parsed.query or parsed.fragment:
        msg = "Remote activity sources must not include query strings or fragments."
        raise ActivityDataError(msg)
    if not parsed.netloc or not parsed.path:
        msg = "Remote activity sources must include a hostname and path."
        raise ActivityDataError(msg)
    return ActivitySource(raw=raw, suffix=Path(parsed.path).suffix.lower(), is_remote=True)


def _is_windows_drive_path(raw: str) -> bool:
    drive, _tail = ntpath.splitdrive(raw)
    return len(drive) == 2 and drive[1] == ":"


def _is_unc_path(raw: str) -> bool:
    return raw.startswith(("//", "\\\\"))


def _derive_metadata_path(path: str) -> str:
    return str(Path(path).with_name(f"{Path(path).stem}.metadata.yaml"))


def _load_csv_source(
    source: ActivitySource,
    csv_loader: CsvLoader,
    remote_reader: RemoteReader,
) -> pd.DataFrame:
    if not source.is_remote:
        try:
            return csv_loader(Path(source.raw))
        except (OSError, ValueError) as exc:
            msg = f"Could not load activity data from {source.raw}."
            raise ActivityDataError(msg) from exc

    try:
        payload = remote_reader(source.raw)
    except requests.RequestException as exc:
        msg = f"Could not load activity data from {source.raw}."
        raise ActivityDataError(msg) from exc
    text = payload.decode("utf-8")
    return pd.read_csv(io.StringIO(text))


def _load_parquet_source(
    source: ActivitySource,
    parquet_loader: ParquetLoader,
    remote_reader: RemoteReader,
) -> pd.DataFrame:
    if not source.is_remote:
        try:
            return parquet_loader(Path(source.raw))
        except (OSError, ValueError) as exc:
            msg = f"Could not load activity data from {source.raw}."
            raise ActivityDataError(msg) from exc

    try:
        payload = remote_reader(source.raw)
    except requests.RequestException as exc:
        msg = f"Could not load activity data from {source.raw}."
        raise ActivityDataError(msg) from exc
    return pd.read_parquet(io.BytesIO(payload))


def _load_remote_text(url: str, remote_reader: RemoteReader) -> str:
    payload = remote_reader(url)
    return payload.decode("utf-8")


def _parse_activity_metadata(text: str, categories: Collection[str]) -> ActivityMetadata:
    try:
        raw_metadata: object = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        msg = "Activity metadata must be valid YAML."
        raise ActivityDataError(msg) from exc
    if raw_metadata is None:
        raw_mapping: dict[str, object] = {}
    else:
        raw_mapping = _require_mapping(raw_metadata, "Activity metadata")

    unknown_keys = sorted(key for key in raw_mapping if key not in ALLOWED_METADATA_KEYS)
    if unknown_keys:
        msg = f"Unknown metadata keys: {', '.join(unknown_keys)}."
        raise ActivityDataError(msg)

    known_categories = set(categories)
    category_labels = _parse_string_mapping(raw_mapping.get("category_labels"), "category_labels")
    category_targets = _parse_positive_int_mapping(
        raw_mapping.get("category_targets"),
        "category_targets",
    )
    unknown_categories = sorted((set(category_labels) | set(category_targets)) - known_categories)
    if unknown_categories:
        detail = ", ".join(unknown_categories)
        msg = f"Activity metadata defines unknown activity categories: {detail}."
        raise ActivityDataError(msg)

    return ActivityMetadata(
        name=_parse_optional_string(raw_mapping.get("name"), "name"),
        description=_parse_optional_string(raw_mapping.get("description"), "description"),
        source=_parse_optional_string(raw_mapping.get("source"), "source"),
        rows=_parse_optional_positive_int(raw_mapping.get("rows"), "rows"),
        fields=_parse_fields(raw_mapping.get("fields")),
        category_labels=category_labels,
        category_targets=category_targets,
    )


def _require_mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        msg = f"{label} must be a YAML mapping."
        raise ActivityDataError(msg)
    mapping: dict[str, object] = {}
    for key, item in cast(dict[object, object], value).items():
        if not isinstance(key, str):
            msg = f"{label} keys must be strings."
            raise ActivityDataError(msg)
        mapping[key] = item
    return mapping


def _parse_optional_string(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or value.strip() == "":
        msg = f"Activity metadata {label} must be a non-empty string."
        raise ActivityDataError(msg)
    return value.strip()


def _parse_optional_positive_int(value: object, label: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        msg = f"Activity metadata {label} must be a positive integer."
        raise ActivityDataError(msg)
    return value


def _parse_fields(value: object) -> tuple[ActivityFieldDefinition, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        msg = "Activity metadata fields must be a list."
        raise ActivityDataError(msg)

    fields: list[ActivityFieldDefinition] = []
    for index, item in enumerate(cast(list[object], value)):
        field_mapping = _require_mapping(item, f"Activity metadata field {index}")
        unknown_keys = sorted(key for key in field_mapping if key not in {"name", "type"})
        if unknown_keys:
            msg = f"Activity metadata field {index} has unknown keys: {', '.join(unknown_keys)}."
            raise ActivityDataError(msg)
        name = _parse_optional_string(field_mapping.get("name"), f"fields[{index}].name")
        field_type = _parse_optional_string(field_mapping.get("type"), f"fields[{index}].type")
        if name is None or field_type is None:
            msg = f"Activity metadata field {index} must define name and type."
            raise ActivityDataError(msg)
        fields.append(ActivityFieldDefinition(name=name, type=field_type))
    return tuple(fields)


def _parse_string_mapping(value: object, label: str) -> dict[str, str]:
    if value is None:
        return {}
    mapping = _require_mapping(value, f"Activity metadata {label}")
    parsed: dict[str, str] = {}
    for key, item in mapping.items():
        if not isinstance(item, str) or item.strip() == "":
            msg = f"Activity metadata {label} values must be non-empty strings."
            raise ActivityDataError(msg)
        parsed[key] = item.strip()
    return parsed


def _parse_positive_int_mapping(value: object, label: str) -> dict[str, int]:
    if value is None:
        return {}
    mapping = _require_mapping(value, f"Activity metadata {label}")
    parsed: dict[str, int] = {}
    for key, item in mapping.items():
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            msg = f"Activity metadata {label} values must be positive integers."
            raise ActivityDataError(msg)
        parsed[key] = item
    return parsed


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
