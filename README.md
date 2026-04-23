# Oak Python Repo Template

`oaknational-python-repo-template` is a reusable Oak Python starter with:

- a canonical `src/` package layout
- strict quality gates driven by `uv`
- cross-platform agent infrastructure in `.agent/`, `.cursor/`, `.claude/`,
  `.gemini/`, `.github/`, `.agents/`, and `.codex/`
- a small demo CLI, `activity-report`, that exercises validation, file I/O,
  reporting, plotting, YAML sidecars, bounded HTTPS retrieval, and repo audits

Install the distribution as `oaknational-python-repo-template` and import it as
`oaknational.python_repo_template`. That is the baseline convention this repo
uses to define "Pythonic within Oak".

The package ships `py.typed`, and the repo type-checks `src/`, `tests/`, and
`tools/` under explicit strict `pyright` settings.

The canonical repo-local build and `check-ci` flow also smoke-tests the built
wheel in a temporary virtual environment outside the source tree, running the
installed package import plus the `activity-report` and
`python -m oaknational.python_repo_template` entry surfaces.

Dependency hygiene runs through `uv run deptry .` and is included as a blocking
step inside both aggregate gate commands. It is dependency hygiene, not vulnerability scanning.

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

The richer activity-pack demo also supports an optional same-stem YAML sidecar,
for example `activity_log.metadata.yaml`, for descriptive metadata, category
display labels, and simple per-category target minutes.

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

Override the auto-discovered metadata sidecar:

```bash
uv run activity-report report \
  --input data/fixtures/activity_log.csv \
  --metadata data/fixtures/activity_log.metadata.yaml
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

Report directly from a bounded HTTPS input:

```bash
uv run activity-report report --input https://example.test/activity_log.csv
```

## Development Commands

```bash
uv sync
uv run python -m oaknational.python_repo_template.devtools clean
uv run python -m oaknational.python_repo_template.devtools build
uv run python -m oaknational.python_repo_template.devtools dev
uv run deptry .
uv run python -m oaknational.python_repo_template.devtools check
uv run python -m oaknational.python_repo_template.devtools check-ci
uv run python -m oaknational.python_repo_template.devtools fix
uv run python -m oaknational.python_repo_template.devtools test
uv run python -m oaknational.python_repo_template.devtools coverage
```

Those developer commands are source-checkout workflows. The installed wheel
publishes only `activity-report` and `python -m oaknational.python_repo_template`.

## Commit Workflow

Install the repo hooks after cloning:

```bash
uv run pre-commit install
```

That installs the repo's `pre-commit`, `pre-push`, and `commit-msg` hooks from
`.pre-commit-config.yaml`.

Create a conventional commit with Commitizen:

```bash
uv run cz commit
```

Check a commit message manually:

```bash
uv run cz check --message "feat: add truthful commit-msg enforcement"
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
