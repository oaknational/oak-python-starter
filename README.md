# Oak Python Repo Template

`oaknational-python-repo-template` is a reusable Oak Python starter with:

- a canonical `src/` package layout
- strict quality gates driven by `uv`
- cross-platform agent infrastructure in `.agent/`, `.cursor/`, `.claude/`,
  `.gemini/`, `.github/`, `.agents/`, and `.codex/`
- a small demo CLI, `activity-report`, that exercises validation, file I/O,
  reporting, plotting, and repo audits

Install the distribution as `oaknational-python-repo-template` and import it as
`oaknational.python_repo_template`. That is the baseline convention this repo
uses to define "Pythonic within Oak".

## Agentic Engineering

This repo is optimised for agentic engineering. Its Practice surfaces,
guardrails, and quality gates are designed so agents can plan, execute, review,
and close out work predictably and safely.

That does not make it agent-only. The same structure works well for
conventional human-led development, pair programming, and mixed human-agent
workflows.

The rules are intentionally strict because that strictness is part of the
safety model for agentic engineering. They are not convenience defaults and
should not be relaxed simply to make unsafe workflows easier.

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
uv run python -m oaknational.python_repo_template report --input data/fixtures/activity_log.csv
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
uv run clean
uv run build
uv run dev
uv run check
uv run check-ci
uv run fix
uv run test
uv run coverage
```

## Practice Surface

- Agent entry point: `.agent/directives/AGENT.md`
- Practice index: `.agent/practice-index.md`
- Capability roadmap: `.agent/plans/roadmap.md`

## Repo Shape

- `src/oaknational/python_repo_template/` — the canonical Oak namespace package root
- `src/oaknational/python_repo_template/data/` — validation and storage boundaries
- `src/oaknational/python_repo_template/demo/` — the example CLI surface
- `tests/` — behaviour-first tests
- `tools/repo_audit.py` — tracked-file audit for repo identity and adapter
  integrity
