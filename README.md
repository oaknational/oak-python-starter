# Python Repo Template

`python-repo-template` is a reusable Python starter with:

- a canonical `src/` package layout
- strict quality gates driven by `uv`
- cross-platform agent infrastructure in `.agent/`, `.cursor/`, `.claude/`,
  `.gemini/`, `.github/`, `.agents/`, and `.codex/`
- a small demo CLI, `activity-report`, that exercises validation, file I/O,
  reporting, plotting, and repo audits

## Demo CLI

The seeded example works with a simple activity log contract:

- `date` — ISO date (`YYYY-MM-DD`)
- `category` — non-empty label
- `minutes` — positive integer
- `notes` — optional text

Prepare validated Parquet output:

```bash
uv run activity-report prepare \
  --input data/fixtures/activity_log.csv \
  --output data/fixtures/activity_log.parquet
```

Print a report:

```bash
uv run activity-report report --input data/fixtures/activity_log.csv
```

Run the same report via the package module entry point:

```bash
uv run python -m python_repo_template report --input data/fixtures/activity_log.csv
```

Print a report and render a chart:

```bash
uv run activity-report report \
  --input data/fixtures/activity_log.parquet \
  --chart activity-summary.png
```

## Development Commands

```bash
uv sync
uv run check
uv run test
uv run coverage
```

## Practice Surface

- Agent entry point: `.agent/directives/AGENT.md`
- Practice index: `.agent/practice-index.md`
- Capability roadmap: `.agent/plans/roadmap.md`

## Repo Shape

- `src/python_repo_template/` — the canonical Python package root
- `src/python_repo_template/data/` — validation and storage boundaries
- `src/python_repo_template/demo/` — the example CLI surface
- `tests/` — behaviour-first tests
- `tools/repo_audit.py` — tracked-file audit for repo identity and adapter
  integrity
