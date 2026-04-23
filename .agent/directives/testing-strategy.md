---
fitness_line_count: 220
fitness_char_count: 14000
fitness_line_length: 100
split_strategy: "Keep behaviour doctrine here and move examples out if needed"
---

# Testing Strategy

## Philosophy

- Use TDD at every level: red, green, refactor.
- Test behaviour, not implementation details.
- Prefer in-process tests with simple injected seams.
- Keep repo-state audits in dedicated tooling rather than `pytest`.

## Validation Taxonomy

- **Static analysis** checks source code without executing the program. In this
  repo that includes formatting, linting, type checking, import-boundary
  validation, and tracked-repo audits.
- **Unit tests** verify the behaviour of a small unit in isolation, with
  collaborators replaced by simple fakes or fixtures.
- **Integration tests** verify that real components work together across a
  meaningful boundary such as parsing, storage, filesystem I/O, or CLI wiring.
- **System or end-to-end tests** verify a user-visible workflow from entry
  point to observable outcome.
- **Regression tests** lock in behaviour after a bug, edge case, or design
  failure has been understood.
- **Smoke tests** are narrow, high-signal checks that the main workflow still
  runs after change.
- **Contract validation** verifies that interfaces and data shapes remain
  compatible with their declared schema or protocol.

## Data Validation Expectations

- For data engineering work, automatic validation should cover schema, column
  presence, dtypes, nullability, uniqueness, value ranges, referential
  integrity, ordering assumptions, idempotence, and failure handling at
  pipeline boundaries.
- For analytical and data science work, automatic validation should also cover
  dataset splits where relevant, feature expectations, reproducibility,
  determinism where promised, and checks for drift or quality regressions when
  the workflow makes those risks meaningful.
- Backfills, migrations, and format conversions should be verified with
  deterministic fixtures or equivalent repeatable evidence, not spot-checking
  by eye.
- Data quality checks complement tests; they do not replace unit, integration,
  or system-level proof.

## Tooling

- `pytest`
- `pytest-cov`
- `pyright`
- `ruff`
- `import-linter`
- `tools/repo_audit.py`

## Rules

- Use the smallest validation layer that can prove the claim, then add broader
  coverage only where the risk justifies it.
- Unit, integration, and system tests must prove useful behaviour rather than
  merely execute lines.
- Mocks should be simple fakes passed in as arguments.
- Avoid global state changes in tests.
- Do not skip tests.
- Prefer deterministic fixtures, seeded inputs, and reproducible execution.
- New data boundaries must have explicit contract validation.
- Changes to pipelines, storage formats, or transformation logic must consider
  regression coverage for malformed input, boundary values, and round-trip
  correctness.
- Use the type checker, formatter, linter, and repo audit for their own
  concerns rather than forcing everything into one layer.
