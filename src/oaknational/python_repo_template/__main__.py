"""Allow the template package to be invoked with ``python -m``."""

from __future__ import annotations

from oaknational.python_repo_template.demo.activity_report import (
    main as activity_report_main,
)


def main() -> int:
    """Run the default package CLI."""

    return activity_report_main()


if __name__ == "__main__":
    raise SystemExit(main())
