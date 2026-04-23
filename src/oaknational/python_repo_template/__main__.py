"""Allow the template package to be invoked with ``python -m``."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TextIO

from oaknational.python_repo_template.demo.activity_report import (
    main as activity_report_main,
)


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
) -> int:
    """Run the default package CLI."""

    return activity_report_main(argv=argv, stdout=stdout)


if __name__ == "__main__":
    raise SystemExit(main())
