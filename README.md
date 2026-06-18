# Oak Python Repo Template

[![CI](https://github.com/oaknational/oak-python-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/oaknational/oak-python-starter/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/oaknational/oak-python-starter?label=release)](https://github.com/oaknational/oak-python-starter/releases/latest)

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
step inside both aggregate gate commands — it proves declared-dependency hygiene
(unused, missing, misplaced), which is distinct from vulnerability scanning.
Vulnerability scanning is a separate blocking gate: `pip-audit` checks the locked
dependencies for known advisories.

Secret scanning uses `gitleaks`. Because `gitleaks` is a Go binary rather than a
`uv` package, it runs alongside `check-ci` rather than inside it (so `uv sync`
stays sufficient for the gate sequence): a pinned pre-commit hook locally and a
pinned `secret-scan` job in CI, kept in lockstep by the `repo-audit`
`secret-scanning` check. The allowlist lives in `.gitleaks.toml`.

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

The chart is built to WCAG 2.2 AA: every bar clears a 3:1 non-text contrast
ratio and the target marker carries a contrasting halo (SC 1.4.11), and a text
alternative is written beside the image — `activity-summary.png.txt` — so a
non-visual reader gets the same per-category minutes, shares, and target deltas
(SC 1.1.1).

Report directly from a bounded HTTPS input:

```bash
uv run activity-report report --input https://example.test/activity_log.csv
```

## Prerequisites

Most tooling is managed through `uv`, so the usual setup is `uv sync` followed by
`uv run pre-commit install`. Two tools are binaries rather than Python packages,
so `uv sync` does not install them:

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — the
  toolchain every command below runs through; install it first.
- **[gitleaks](https://github.com/gitleaks/gitleaks#installing-gitleaks)** — the
  secret scanner. The pre-commit hook installs it automatically (pre-commit
  provisions its own Go toolchain), so no manual step is normally needed. Install
  it directly via the official instructions only if you want to run `gitleaks`
  outside pre-commit, or if the automatic install is unavailable in your
  environment.

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

## Releases

Releases are automated from Conventional Commits, with the version kept
**committed** in `pyproject.toml`. Because `main` is protected, the bump flows
through a one-click **release PR**:

1. Merging changes to `main` makes the Release workflow open or refresh a
   `chore(release): vX.Y.Z` PR that bumps `pyproject.toml`, `uv.lock`, and
   `CHANGELOG.md`.
2. Merging that release PR tags `vX.Y.Z` and publishes a GitHub Release with the
   built wheel + sdist attached.

The bump level is computed by Commitizen with this repo's policy:

| Commit type(s) | Bump |
| --- | --- |
| `feat`, `fix` | minor |
| everything else (`chore`, `docs`, `perf`, `refactor`, `build`, `ci`, …) | patch |
| `!` / `BREAKING CHANGE` | no auto-release — a **major** is required |

**Major versions are manual.** A breaking change makes the automation stand
down; cut the major deliberately via the Release workflow's *Run workflow*
button (`increment = MAJOR`). Releases publish to GitHub Releases only (no PyPI).

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

## Licence

Released under the [MIT licence](LICENCE), copyright Oak National Academy.

See [SECURITY.md](SECURITY.md) for vulnerability reporting and the credentials
policy.
