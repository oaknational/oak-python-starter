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

## Tooling

- `pytest`
- `pytest-cov`
- `pyright`
- `ruff`
- `tools/repo_audit.py`

## Rules

- Unit and integration tests must prove useful behaviour.
- Mocks should be simple fakes passed in as arguments.
- Avoid global state changes in tests.
- Do not skip tests.
- Use the type checker, formatter, linter, and repo audit for their own
  concerns rather than forcing everything into one layer.
