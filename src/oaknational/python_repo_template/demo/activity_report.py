"""CLI for the seeded activity-report demo."""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TextIO

from oaknational.python_repo_template.data.activity_store import (
    ActivityDataError,
    ActivitySummary,
    CsvLoader,
    ParquetLoader,
    ParquetWriter,
    default_csv_loader,
    default_parquet_loader,
    default_parquet_writer,
    load_activity_log,
    prepare_activity_log,
    summarise_activity,
)

ChartWriter = Callable[[ActivitySummary, Path], None]
type Rgb = tuple[int, int, int]
type Canvas = list[bytearray]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(
        prog="activity-report",
        description="Validate and report simple activity logs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Validate CSV input and write Parquet.")
    prepare_parser.add_argument("--input", required=True, type=Path)
    prepare_parser.add_argument("--output", required=True, type=Path)

    report_parser = subparsers.add_parser("report", help="Print an activity summary.")
    report_parser.add_argument("--input", required=True, type=Path)
    report_parser.add_argument("--chart", type=Path)

    return parser


def render_summary(summary: ActivitySummary) -> str:
    """Render a stable text report."""

    lines = [
        f"Total entries: {summary.total_entries}",
        f"Total minutes: {summary.total_minutes}",
        f"Average minutes per day: {summary.average_minutes_per_day:.2f}",
        f"Busiest category: {summary.busiest_category}",
        "Category totals:",
    ]
    lines.extend(f"- {category}: {minutes}" for category, minutes in summary.category_totals)
    return "\n".join(lines)


def default_chart_writer(summary: ActivitySummary, output_path: Path) -> None:
    """Render a PNG bar chart for category totals."""

    width = 800
    height = 450
    background = (246, 248, 251)
    plot_background = (255, 255, 255)
    axis_colour = (75, 85, 99)
    palette: tuple[Rgb, ...] = (
        (49, 92, 158),
        (76, 145, 149),
        (208, 141, 70),
        (185, 96, 96),
        (114, 97, 181),
    )

    canvas = _new_canvas(width, height, background)
    plot_left = 72
    plot_top = 36
    plot_right = width - 32
    plot_bottom = height - 72
    _fill_rect(canvas, plot_left, plot_top, plot_right, plot_bottom, plot_background)
    _fill_rect(canvas, plot_left - 2, plot_top, plot_left + 1, plot_bottom + 1, axis_colour)
    _fill_rect(canvas, plot_left - 2, plot_bottom - 1, plot_right + 1, plot_bottom + 2, axis_colour)

    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top - 12
    max_minutes = max(minutes for _category, minutes in summary.category_totals)
    count = len(summary.category_totals)
    inset_ratio = 0.18

    for index, (_category, minutes) in enumerate(summary.category_totals):
        slot_left = plot_left + (plot_width * index) // count
        slot_right = plot_left + (plot_width * (index + 1)) // count
        slot_width = max(1, slot_right - slot_left)
        inset = max(6, int(slot_width * inset_ratio))
        bar_left = slot_left + inset
        bar_right = max(bar_left + 1, slot_right - inset)
        bar_height = max(1, round((minutes / max_minutes) * plot_height))
        bar_top = plot_bottom - bar_height
        colour = palette[index % len(palette)]
        _fill_rect(canvas, bar_left, bar_top, bar_right, plot_bottom, colour)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_png(canvas, output_path)


def _new_canvas(width: int, height: int, colour: Rgb) -> Canvas:
    row = bytearray(bytes(colour * width))
    return [row.copy() for _index in range(height)]


def _fill_rect(
    canvas: Canvas,
    left: int,
    top: int,
    right: int,
    bottom: int,
    colour: Rgb,
) -> None:
    width = len(canvas[0]) // 3
    height = len(canvas)
    x0 = max(0, min(left, right))
    x1 = min(width, max(left, right))
    y0 = max(0, min(top, bottom))
    y1 = min(height, max(top, bottom))
    if x0 >= x1 or y0 >= y1:
        return

    fill = bytes(colour * (x1 - x0))
    for row_index in range(y0, y1):
        row = canvas[row_index]
        row[x0 * 3 : x1 * 3] = fill


def _write_png(canvas: Canvas, output_path: Path) -> None:
    width = len(canvas[0]) // 3
    height = len(canvas)
    raw = b"".join(b"\x00" + bytes(row) for row in canvas)
    image = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
            _png_chunk(b"IDAT", zlib.compress(raw, level=9)),
            _png_chunk(b"IEND", b""),
        ]
    )
    output_path.write_bytes(image)


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    checksum = zlib.crc32(kind)
    checksum = zlib.crc32(payload, checksum) & 0xFFFFFFFF
    return len(payload).to_bytes(4, "big") + kind + payload + checksum.to_bytes(4, "big")


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    csv_loader: CsvLoader = default_csv_loader,
    parquet_loader: ParquetLoader = default_parquet_loader,
    parquet_writer: ParquetWriter = default_parquet_writer,
    chart_writer: ChartWriter = default_chart_writer,
) -> int:
    """Run the CLI with injectable I/O seams for tests."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    output = stdout if stdout is not None else sys.stdout

    try:
        if args.command == "prepare":
            frame = prepare_activity_log(
                args.input,
                args.output,
                csv_loader=csv_loader,
                parquet_writer=parquet_writer,
            )
            print(
                f"Prepared {len(frame.index)} rows at {args.output}.",
                file=output,
            )
            return 0

        if args.command == "report":
            frame = load_activity_log(
                args.input,
                csv_loader=csv_loader,
                parquet_loader=parquet_loader,
            )
            summary = summarise_activity(frame)
            print(render_summary(summary), file=output)
            if args.chart is not None:
                chart_writer(summary, args.chart)
            return 0
    except ActivityDataError as exc:
        parser.exit(status=2, message=f"{exc}\n")

    msg = f"Unsupported command: {args.command!r}"
    raise SystemExit(msg)


if __name__ == "__main__":
    raise SystemExit(main())
