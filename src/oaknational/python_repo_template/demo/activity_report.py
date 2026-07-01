"""CLI for the seeded activity-report demo."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Collection, Sequence
from pathlib import Path
from typing import Any, TextIO

import numpy as np
from matplotlib import patheffects
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from oaknational.python_repo_template.data.activity_store import (
    ActivityDataError,
    ActivityMetadata,
    ActivitySummary,
    CsvLoader,
    ParquetLoader,
    ParquetWriter,
    RemoteReader,
    default_csv_loader,
    default_parquet_loader,
    default_parquet_writer,
    default_remote_reader,
    derive_metadata_source,
    load_activity_log,
    load_activity_metadata,
    prepare_activity_log,
    summarise_activity,
)

ChartWriter = Callable[[ActivitySummary, ActivityMetadata | None, Path], None]
MetadataLoader = Callable[[str | Path, Collection[str], bool], ActivityMetadata | None]

CHART_BACKGROUND = "#f6f8fb"
PLOT_BACKGROUND = "#ffffff"
AXIS_COLOUR = "#4b5563"
GRID_COLOUR = "#e5e7eb"
# Every bar colour clears WCAG 2.2 SC 1.4.11 (>=3:1 against PLOT_BACKGROUND); the
# amber was darkened from #d08d46 (2.77:1) to reach the floor. The contrast
# invariant is pinned by tests in test_activity_report.py.
PALETTE = ("#315c9e", "#4c9195", "#b07a37", "#b96060", "#7261b5")
# The target marker overlaps the bars, where its dark core cannot reach 3:1
# against every bar; a white halo (SC 1.4.11) gives a high-contrast edge on the
# bars while the dark core stays high-contrast against the white plot area.
TARGET_COLOUR = "#374151"
TARGET_HALO_COLOUR = "#ffffff"


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        prog="activity-report",
        description="Validate and report simple activity logs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Validate CSV input and write Parquet.")
    prepare_parser.add_argument("--input", required=True, type=str)
    prepare_parser.add_argument("--output", required=True, type=Path)

    report_parser = subparsers.add_parser("report", help="Print an activity summary.")
    report_parser.add_argument("--input", required=True, type=str)
    report_parser.add_argument("--metadata", type=str)
    report_parser.add_argument("--chart", type=Path)

    return parser


def render_summary(summary: ActivitySummary, metadata: ActivityMetadata | None = None) -> str:
    """Render a stable text report."""

    lines: list[str] = []
    if metadata is not None:
        if metadata.name is not None:
            lines.append(f"Profile: {metadata.name}")
        if metadata.description is not None:
            lines.append(f"Description: {metadata.description}")
        if metadata.source is not None:
            lines.append(f"Source: {metadata.source}")
        if lines:
            lines.append("")

    lines.extend(
        [
            f"Total entries: {summary.total_entries}",
            f"Total minutes: {summary.total_minutes}",
            f"Average minutes per day: {summary.average_minutes_per_day:.2f}",
            f"Busiest category: {_display_label(summary.busiest_category, metadata)}",
            "Category totals:",
        ]
    )
    lines.extend(
        f"- {_display_label(category, metadata)}: {minutes}"
        for category, minutes in summary.category_totals
    )

    deltas = _target_deltas(summary, metadata)
    if deltas:
        lines.append("Target deltas:")
        lines.extend(f"- {label}: {delta:+d}" for label, delta in deltas)

    return "\n".join(lines)


def render_chart_alt_text(
    summary: ActivitySummary, metadata: ActivityMetadata | None = None
) -> str:
    """Render the chart's text alternative (WCAG 2.2 SC 1.1.1).

    A non-visual reader of the PNG gets the same information the bars convey:
    each category's minutes, its share of the total, and any target delta.
    """

    title = _chart_title(metadata)
    targets = metadata.category_targets if metadata is not None else {}
    grand_total = sum(minutes for _category, minutes in summary.category_totals)

    lead = (
        f'Bar chart "{title}": total minutes per category, with each bar labelled by its '
        "percentage share of the total"
    )
    lead += " and a target marker where a target is set." if targets else "."
    lines = [lead]
    for category, minutes in summary.category_totals:
        label = _display_label(category, metadata)
        share = (minutes / grand_total) if grand_total else 0.0
        line = f"- {label}: {minutes} minutes ({share:.0%})"
        if category in targets:
            target = targets[category]
            line += f"; target {target} ({minutes - target:+d})"
        lines.append(line)
    return "\n".join(lines)


def _alt_text_path(output_path: Path) -> Path:
    """The sidecar text-alternative path paired with a chart image."""

    return output_path.with_name(f"{output_path.name}.txt")


def default_chart_writer(
    summary: ActivitySummary,
    metadata: ActivityMetadata | None,
    output_path: Path,
) -> None:
    """Render a PNG bar chart for category totals."""

    categories = [category for category, _minutes in summary.category_totals]
    labels = [_display_label(category, metadata) for category in categories]
    totals = np.asarray(
        [minutes for _category, minutes in summary.category_totals], dtype=np.float64
    )
    shares = totals / totals.sum()
    positions = np.arange(len(labels), dtype=np.float64)
    colours = [PALETTE[index % len(PALETTE)] for index in range(len(labels))]

    figure: Any = Figure(figsize=(8, 4.5), facecolor=CHART_BACKGROUND)
    FigureCanvasAgg(figure)
    axis: Any = figure.subplots()
    axis.set_facecolor(PLOT_BACKGROUND)

    bars: list[Any] = list(axis.bar(positions, totals, width=0.65, color=colours, edgecolor="none"))
    axis.set_title(_chart_title(metadata))
    axis.set_ylabel("Minutes")
    axis.set_xticks(positions, labels)
    axis.tick_params(axis="x", labelrotation=15)
    axis.grid(axis="y", color=GRID_COLOUR, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(AXIS_COLOUR)
    axis.spines["bottom"].set_color(AXIS_COLOUR)

    max_total = float(totals.max())
    text_offset = max(2.0, max_total * 0.03)
    for bar, share in zip(bars, shares, strict=True):
        axis.text(
            bar.get_x() + (bar.get_width() / 2),
            bar.get_height() + text_offset,
            f"{share:.0%}",
            ha="center",
            va="bottom",
            color=AXIS_COLOUR,
            fontsize=9,
        )

    target_points = _target_points(categories, metadata)
    if target_points:
        target_positions = np.asarray([point[0] for point in target_points], dtype=np.float64)
        target_values = np.asarray([point[1] for point in target_points], dtype=np.float64)
        target_marker = axis.scatter(
            target_positions,
            target_values,
            marker="_",
            s=700,
            linewidths=2.5,
            color=TARGET_COLOUR,
            label="Target",
        )
        # White halo so the marker stays perceivable on any bar colour (SC 1.4.11).
        target_marker.set_path_effects(
            [
                patheffects.withStroke(linewidth=5.0, foreground=TARGET_HALO_COLOUR),
                patheffects.Normal(),
            ]
        )
        axis.legend(frameon=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(output_path, format="png", dpi=150)
    # Write the text alternative (SC 1.1.1) beside the image so a non-visual
    # consumer of the PNG can read the same information the bars convey.
    _alt_text_path(output_path).write_text(
        render_chart_alt_text(summary, metadata) + "\n", encoding="utf-8"
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    csv_loader: CsvLoader = default_csv_loader,
    parquet_loader: ParquetLoader = default_parquet_loader,
    parquet_writer: ParquetWriter = default_parquet_writer,
    chart_writer: ChartWriter = default_chart_writer,
    remote_reader: RemoteReader = default_remote_reader,
    metadata_loader: MetadataLoader | None = None,
) -> int:
    """Run the CLI with injectable I/O seams for tests."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    output = stdout if stdout is not None else sys.stdout

    def default_metadata_loader(
        source: str | Path,
        categories: Collection[str],
        allow_missing: bool,
    ) -> ActivityMetadata | None:
        return load_activity_metadata(
            source,
            categories=categories,
            allow_missing=allow_missing,
            remote_reader=remote_reader,
        )

    resolved_metadata_loader: MetadataLoader = (
        metadata_loader if metadata_loader is not None else default_metadata_loader
    )

    try:
        if args.command == "prepare":
            frame = prepare_activity_log(
                args.input,
                args.output,
                csv_loader=csv_loader,
                parquet_writer=parquet_writer,
                remote_reader=remote_reader,
            )
            print(
                f"Prepared {len(frame.index)} rows at {args.output}.",
                file=output,
            )
        elif args.command == "report":
            frame = load_activity_log(
                args.input,
                csv_loader=csv_loader,
                parquet_loader=parquet_loader,
                remote_reader=remote_reader,
            )
            categories = tuple(str(category) for category in frame["category"].unique())
            chosen_metadata_source = args.metadata or derive_metadata_source(args.input)
            metadata = resolved_metadata_loader(
                chosen_metadata_source,
                categories,
                args.metadata is None,
            )
            summary = summarise_activity(frame)
            print(render_summary(summary, metadata), file=output)
            if args.chart is not None:
                chart_writer(summary, metadata, args.chart)
        else:
            msg = f"Unsupported command: {args.command!r}"
            raise SystemExit(msg)
    except ActivityDataError as exc:
        parser.exit(status=2, message=f"{exc}\n")

    return 0


def _chart_title(metadata: ActivityMetadata | None) -> str:
    if metadata is not None and metadata.name is not None:
        return metadata.name
    return "Activity summary"


def _display_label(category: str, metadata: ActivityMetadata | None) -> str:
    if metadata is None:
        return category
    return metadata.category_labels.get(category, category)


def _target_deltas(
    summary: ActivitySummary,
    metadata: ActivityMetadata | None,
) -> tuple[tuple[str, int], ...]:
    if metadata is None or not metadata.category_targets:
        return ()

    categories = [
        category
        for category, _minutes in summary.category_totals
        if category in metadata.category_targets
    ]
    if not categories:
        return ()

    totals = np.asarray(
        [
            minutes
            for category, minutes in summary.category_totals
            if category in metadata.category_targets
        ],
        dtype=np.int64,
    )
    targets = np.asarray(
        [metadata.category_targets[category] for category in categories], dtype=np.int64
    )
    deltas = totals - targets
    return tuple(
        (_display_label(category, metadata), int(delta))
        for category, delta in zip(categories, deltas, strict=True)
    )


def _target_points(
    categories: Sequence[str],
    metadata: ActivityMetadata | None,
) -> tuple[tuple[float, float], ...]:
    if metadata is None or not metadata.category_targets:
        return ()
    return tuple(
        (float(index), float(metadata.category_targets[category]))
        for index, category in enumerate(categories)
        if category in metadata.category_targets
    )


if __name__ == "__main__":
    raise SystemExit(main())
