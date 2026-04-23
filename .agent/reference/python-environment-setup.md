# Python Environment Setup

Use `uv` for environment creation and command execution:

```bash
uv sync
uv run clean
uv run build
uv run dev
uv run check
uv run check-ci
uv run fix
uv run activity-report --help
```

The repo targets Python 3.14.

Use `uv run <script>` for the repo's managed command surface so the virtual
environment and installed console scripts stay aligned with the checked-in
tooling.
